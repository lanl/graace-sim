#ifndef GRAACE_SIMIO_HH
#define GRAACE_SIMIO_HH

#include "utils.hh"

#include "G4String.hh"

#include <map>
#include <vector>

// SimIO collects the gamma hits recorded during a run and writes them to
// Parquet, one file set per detector. Columns: energy (keV, double), time (ns,
// double). The detector is not a column — every hit in a file is from the same
// detector, named by the subdirectory the file is written to.
//
// Each detector's hits are buffered separately and written in numbered part
// files rather than held in memory for the whole run: once a detector's buffer
// reaches kMaxHitsPerFile hits it is written out and cleared, so memory use
// stays bounded no matter how long the run is. From an output path of
// "results/gamma_hits.parquet" each detector's parts are written into its own
// subdirectory named after the detector:
// "results/<detector>/gamma_hits-part-00000.parquet", and so on; the analysis
// side reads a detector's whole set back as one table.
class SimIO
{
public:
  // The single shared writer used by the sensitive detector and run action.
  static SimIO& Instance();

  void Open(const G4String& path);   // start a fresh run
  void Add(const GammaHit& hit);     // record one gamma hit
  void Write();                      // write any remaining hits and finish

private:
  SimIO() = default;

  // One detector's buffered hits and its running part/total counts.
  struct Bucket
  {
    std::vector<GammaHit> hits;
    int                   partIndex = 0;   // number of the next part file
    std::size_t           totalHits = 0;   // hits written across all parts
  };

  // Write a detector's buffered hits to its next part file and clear the buffer.
  void WritePart(const G4String& detector, Bucket& bucket);

  // How many hits to hold in memory before writing a part file. A constant for
  // now; promote to an /output/* command if per-run control is needed.
  static constexpr std::size_t kMaxHitsPerFile = 1000000;

  G4String                     fPath;      // base output path; the detector name
                                           // becomes a subdirectory of its parent
  std::map<G4String, Bucket>   fBuckets;   // one buffer per detector name
};

#endif
