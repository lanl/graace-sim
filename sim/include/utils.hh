#ifndef GRAACE_UTILS_HH
#define GRAACE_UTILS_HH

#include "G4String.hh"

// One recorded gamma hit in a detector. Energy is in keV and time in ns so the
// output columns carry familiar units.
struct GammaHit
{
  G4String detector;   // name of the detector volume that saw the hit
  double   energy;     // keV
  double   time;       // ns
};

#endif
