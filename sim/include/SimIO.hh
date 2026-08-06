#ifndef GRAACE_SIMIO_HH
#define GRAACE_SIMIO_HH

#include "utils.hh"

#include "G4String.hh"

#include <vector>

// SimIO collects the gamma hits recorded during a run and writes them to a
// Parquet file when the run ends. Columns: detector (string), energy (keV,
// double), time (ns, double).
class SimIO
{
public:
  // The single shared writer used by the sensitive detector and run action.
  static SimIO& Instance();

  void Open(const G4String& path);   // start a fresh run
  void Add(const GammaHit& hit);     // record one gamma hit
  void Write();                      // write everything to the Parquet file

private:
  SimIO() = default;

  G4String              fPath;
  std::vector<GammaHit> fHits;
};

#endif
