#include "SimIO.hh"

#include "G4ios.hh"

#include <arrow/api.h>
#include <arrow/io/file.h>
#include <parquet/arrow/writer.h>

#include <filesystem>
#include <iomanip>
#include <sstream>

SimIO& SimIO::Instance()
{
  static SimIO instance;
  return instance;
}

void SimIO::Open(const G4String& path)
{
  fPath = path;
  fHits.clear();
  fPartIndex = 0;
  fTotalHits = 0;
}

void SimIO::Add(const GammaHit& hit)
{
  fHits.push_back(hit);
  // Flush to a part file once the buffer is full so memory use stays bounded.
  if (fHits.size() >= kMaxHitsPerFile) {
    WritePart();
  }
}

void SimIO::Write()
{
  // Write whatever is left in the buffer as the final part.
  if (!fHits.empty()) {
    WritePart();
  }
  G4cout << "SimIO: wrote " << fTotalHits << " gamma hits in " << fPartIndex
         << " part file(s)" << G4endl;
}

void SimIO::WritePart()
{
  // Build the three columns from the buffered hits.
  arrow::StringBuilder   detectorBuilder;
  arrow::DoubleBuilder   energyBuilder;
  arrow::DoubleBuilder   timeBuilder;

  for (const auto& hit : fHits) {
    if (auto st = detectorBuilder.Append(hit.detector); !st.ok()) {
      G4cerr << "SimIO: failed to append detector value: " << st.ToString() << G4endl;
      return;
    }
    if (auto st = energyBuilder.Append(hit.energy); !st.ok()) {
      G4cerr << "SimIO: failed to append energy value: " << st.ToString() << G4endl;
      return;
    }
    if (auto st = timeBuilder.Append(hit.time); !st.ok()) {
      G4cerr << "SimIO: failed to append time value: " << st.ToString() << G4endl;
      return;
    }
  }

  std::shared_ptr<arrow::Array> detectorArray, energyArray, timeArray;
  if (auto st = detectorBuilder.Finish(&detectorArray); !st.ok()) {
    G4cerr << "SimIO: failed to finish detector column: " << st.ToString() << G4endl;
    return;
  }
  if (auto st = energyBuilder.Finish(&energyArray); !st.ok()) {
    G4cerr << "SimIO: failed to finish energy column: " << st.ToString() << G4endl;
    return;
  }
  if (auto st = timeBuilder.Finish(&timeArray); !st.ok()) {
    G4cerr << "SimIO: failed to finish time column: " << st.ToString() << G4endl;
    return;
  }

  auto schema = arrow::schema({
    arrow::field("detector", arrow::utf8()),
    arrow::field("energy", arrow::float64()),
    arrow::field("time", arrow::float64()),
  });
  auto table = arrow::Table::Make(schema, {detectorArray, energyArray, timeArray});

  // Turn "dir/hits.parquet" into "dir/hits-part-0000.parquet".
  std::filesystem::path base(fPath.c_str());
  std::ostringstream name;
  name << base.stem().string() << "-part-"
       << std::setw(4) << std::setfill('0') << fPartIndex
       << base.extension().string();
  std::filesystem::path partPath = base.has_parent_path()
    ? base.parent_path() / name.str()
    : std::filesystem::path(name.str());

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

  G4cout << "SimIO: wrote " << fHits.size() << " gamma hits to "
         << partPath.string() << G4endl;

  fTotalHits += fHits.size();
  ++fPartIndex;
  fHits.clear();
}
