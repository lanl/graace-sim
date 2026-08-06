#ifndef GRAACE_SIMIO_HH
#define GRAACE_SIMIO_HH

#include "utils.hh"

#include "G4String.hh"

#include <vector>

// SimIO collects the gamma hits recorded during a run and writes them to
// Parquet. Columns: detector (string), energy (keV, double), time (ns, double).
//
// Hits are written in numbered part files rather than held in memory for the
// whole run: once the in-memory buffer reaches kMaxHitsPerFile hits it is
// written out and cleared, so memory use stays bounded no matter how long the
// run is. From an output path of "data/hits.parquet" the parts are named
// "data/hits-part-0000.parquet", "data/hits-part-0001.parquet", and so on; the
// analysis side reads the whole set back as one table.
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

  // Write the buffered hits to the next part file and clear the buffer.
  void WritePart();

  // How many hits to hold in memory before writing a part file. A constant for
  // now; promote to an /output/* command if per-run control is needed.
  static constexpr std::size_t kMaxHitsPerFile = 1000000;

  G4String              fPath;
  std::vector<GammaHit> fHits;
  int                   fPartIndex = 0;   // number of the next part file
  std::size_t           fTotalHits = 0;   // hits written across all parts
};

#endif
