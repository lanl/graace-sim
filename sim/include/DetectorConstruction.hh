#ifndef GRAACE_DETECTORCONSTRUCTION_HH
#define GRAACE_DETECTORCONSTRUCTION_HH

#include "G4VUserDetectorConstruction.hh"

class G4Material;

// DetectorConstruction builds the world from the configured values: a sample of
// a chosen composition and shape, and a single HPGe gamma detector marked as a
// sensitive detector. It reads everything from Config, so the same compiled
// engine builds different setups depending only on the macro.
class DetectorConstruction : public G4VUserDetectorConstruction
{
public:
  G4VPhysicalVolume* Construct() override;
  void ConstructSDandField() override;

private:
  // Build the sample material from the element mass-fraction composition and
  // density stored in Config.
  G4Material* BuildSampleMaterial();
};

#endif
