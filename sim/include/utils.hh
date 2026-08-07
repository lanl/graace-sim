#ifndef GRAACE_UTILS_HH
#define GRAACE_UTILS_HH

#include "G4String.hh"
#include "G4ThreeVector.hh"

// One recorded gamma hit in a detector. Energy is in keV and time in ns so the
// output columns carry familiar units.
struct GammaHit
{
  G4String detector;   // name of the detector volume that saw the hit
  double   energy;     // keV
  double   time;       // ns
};

// One gamma detector: an HPGe (germanium) cylinder of the given radius and
// height at the given position. Its name labels the detector volume and the
// output subdirectory its hits are written to. A run may hold more than one.
struct DetectorBlock
{
  G4String      name;      // detector name (volume and output subdirectory)
  double        radius;    // mm (crystal radius)
  double        height;    // mm (crystal length)
  G4ThreeVector position;  // mm
};

// One shielding block: a slab of the named material, the given thickness thick,
// at the given position. A run may hold none, one, or several.
struct ShieldingBlock
{
  G4String      material;   // NIST material name, e.g. "G4_Pb"
  double        thickness;  // mm (extent along z)
  G4ThreeVector position;   // mm
};

#endif
