#include "SimIO.hh"

#include "G4ios.hh"
#include "G4Threading.hh"

#include <arrow/api.h>
#include <arrow/io/file.h>
#include <parquet/arrow/writer.h>

#include <filesystem>
#include <iomanip>
#include <sstream>

SimIO& SimIO::Instance()
{
  // thread_local: each worker thread gets its own writer, so buffers and part
  // counts are never shared and the hit path needs no locking.
  static thread_local SimIO instance;
  return instance;
}

void SimIO::Open(const G4String& path)
{
  fPath = path;
  fBuckets.clear();
}

void SimIO::Add(const GammaHit& hit)
{
  Bucket& bucket = fBuckets[hit.detector];
  bucket.hits.push_back(hit);
  // Flush to a part file once this detector's buffer is full so memory use
  // stays bounded.
  if (bucket.hits.size() >= kMaxHitsPerFile) {
    WritePart(hit.detector, bucket);
  }
}

void SimIO::Write()
{
  // Write whatever is left in each detector's buffer as its final part.
  std::size_t totalHits = 0;
  std::size_t totalParts = 0;
  for (auto& entry : fBuckets) {
    if (!entry.second.hits.empty()) {
      WritePart(entry.first, entry.second);
    }
    totalHits += entry.second.totalHits;
    totalParts += static_cast<std::size_t>(entry.second.partIndex);
  }
  G4cout << "SimIO: wrote " << totalHits << " gamma hits in " << totalParts
         << " part file(s) across " << fBuckets.size() << " detector(s)" << G4endl;
}

void SimIO::WritePart(const G4String& detector, Bucket& bucket)
{
  // Build the columns from the buffered hits. The detector name is not a column:
  // every hit in this file is from the same detector, named by its directory.
  arrow::DoubleBuilder   energyBuilder;
  arrow::DoubleBuilder   timeBuilder;

  for (const auto& hit : bucket.hits) {
    if (auto st = energyBuilder.Append(hit.energy); !st.ok()) {
      G4cerr << "SimIO: failed to append energy value: " << st.ToString() << G4endl;
      return;
    }
    if (auto st = timeBuilder.Append(hit.time); !st.ok()) {
      G4cerr << "SimIO: failed to append time value: " << st.ToString() << G4endl;
      return;
    }
  }

  std::shared_ptr<arrow::Array> energyArray, timeArray;
  if (auto st = energyBuilder.Finish(&energyArray); !st.ok()) {
    G4cerr << "SimIO: failed to finish energy column: " << st.ToString() << G4endl;
    return;
  }
  if (auto st = timeBuilder.Finish(&timeArray); !st.ok()) {
    G4cerr << "SimIO: failed to finish time column: " << st.ToString() << G4endl;
    return;
  }

  auto schema = arrow::schema({
    arrow::field("energy", arrow::float64()),
    arrow::field("time", arrow::float64()),
  });
  auto table = arrow::Table::Make(schema, {energyArray, timeArray});

  // Turn "dir/gamma_hits.parquet" into
  // "dir/<detector>/gamma_hits-part-w000-00000.parquet": the detector name
  // becomes a subdirectory so each detector's parts live together, and the
  // "w<thread>" tag keeps two worker threads from ever writing the same file.
  // The master thread (id -1 under the MT run manager) writes nothing, so only
  // worker ids appear; a serial run reports id -1 too and is tagged "w000".
  const G4int threadId = G4Threading::G4GetThreadId();
  const int workerTag = threadId < 0 ? 0 : threadId;
  std::filesystem::path base(fPath.c_str());
  std::ostringstream name;
  name << base.stem().string() << "-part-"
       << 'w' << std::setw(3) << std::setfill('0') << workerTag << '-'
       << std::setw(5) << std::setfill('0') << bucket.partIndex
       << base.extension().string();
  std::filesystem::path detectorDir = base.has_parent_path()
    ? base.parent_path() / detector.c_str()
    : std::filesystem::path(detector.c_str());
  std::filesystem::path partPath = detectorDir / name.str();

  // Make sure the output directory exists.
  if (partPath.has_parent_path()) {
    try {
      std::filesystem::create_directories(partPath.parent_path());
    } catch (const std::filesystem::filesystem_error& e) {
      G4cerr << "SimIO: could not create output directory " << partPath.parent_path()
             << ": " << e.what() << G4endl;
      return;
    }
  }

  auto outfileResult = arrow::io::FileOutputStream::Open(partPath.string());
  if (!outfileResult.ok()) {
    G4cerr << "SimIO: could not open output file " << partPath.string()
           << ": " << outfileResult.status().ToString() << G4endl;
    return;
  }
  std::shared_ptr<arrow::io::FileOutputStream> outfile = *outfileResult;

  auto status = parquet::arrow::WriteTable(
    *table, arrow::default_memory_pool(), outfile, /*chunk_size=*/1024);
  if (!status.ok()) {
    G4cerr << "SimIO: could not write Parquet file " << partPath.string()
           << ": " << status.ToString() << G4endl;
    return;
  }

  G4cout << "SimIO: wrote " << bucket.hits.size() << " gamma hits to "
         << partPath.string() << G4endl;

  bucket.totalHits += bucket.hits.size();
  ++bucket.partIndex;
  bucket.hits.clear();
}
