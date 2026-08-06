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
    detectorBuilder.Append(hit.detector).ok();
    energyBuilder.Append(hit.energy).ok();
    timeBuilder.Append(hit.time).ok();
  }

  std::shared_ptr<arrow::Array> detectorArray, energyArray, timeArray;
  detectorBuilder.Finish(&detectorArray).ok();
  energyBuilder.Finish(&energyArray).ok();
  timeBuilder.Finish(&timeArray).ok();

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
