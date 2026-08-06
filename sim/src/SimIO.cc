#include "SimIO.hh"

#include "G4ios.hh"

#include <arrow/api.h>
#include <arrow/io/file.h>
#include <parquet/arrow/writer.h>

#include <filesystem>

SimIO& SimIO::Instance()
{
  static SimIO instance;
  return instance;
}

void SimIO::Open(const G4String& path)
{
  fPath = path;
  fHits.clear();
}

void SimIO::Add(const GammaHit& hit)
{
  fHits.push_back(hit);
}

void SimIO::Write()
{
  // Build the three columns from the collected hits.
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

  // Make sure the output directory exists.
  std::filesystem::path outPath(fPath.c_str());
  if (outPath.has_parent_path()) {
    std::filesystem::create_directories(outPath.parent_path());
  }

  auto outfileResult = arrow::io::FileOutputStream::Open(fPath);
  if (!outfileResult.ok()) {
    G4cerr << "SimIO: could not open output file " << fPath
           << ": " << outfileResult.status().ToString() << G4endl;
    return;
  }
  std::shared_ptr<arrow::io::FileOutputStream> outfile = *outfileResult;

  auto status = parquet::arrow::WriteTable(
    *table, arrow::default_memory_pool(), outfile, /*chunk_size=*/1024);
  if (!status.ok()) {
    G4cerr << "SimIO: could not write Parquet file " << fPath
           << ": " << status.ToString() << G4endl;
    return;
  }

  G4cout << "SimIO: wrote " << fHits.size() << " gamma hits to " << fPath
         << G4endl;
}
