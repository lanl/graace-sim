#include "DetectorConstruction.hh"
#include "SensitiveDetector.hh"
#include "Config.hh"

#include "G4NistManager.hh"
#include "G4Material.hh"
#include "G4Box.hh"
#include "G4Orb.hh"
#include "G4Tubs.hh"
#include "G4LogicalVolume.hh"
#include "G4PVPlacement.hh"
#include "G4SDManager.hh"
#include "G4SystemOfUnits.hh"
#include "G4PhysicalConstants.hh"
#include "G4VisAttributes.hh"
#include "G4ios.hh"
G4Material* DetectorConstruction::BuildSampleMaterial()
{
  const Config& config = Config::Instance();
  G4NistManager* nist = G4NistManager::Instance();

  G4Material* material = new G4Material(
    "sample_material", config.sample_density * g / cm3,
    static_cast<G4int>(config.sample_composition.size()));

  // Add each element by mass fraction. Elements come from the NIST database so
  // natural isotopic abundances are used.
  for (const auto& part : config.sample_composition) {
    G4Element* element = nist->FindOrBuildElement(part.first);
    material->AddElement(element, part.second);
  }
  return material;
}

G4VPhysicalVolume* DetectorConstruction::Construct()
{
  const Config& config = Config::Instance();
  G4NistManager* nist = G4NistManager::Instance();

  // --- World: a box of air, large enough to hold the sample and detector ---
  G4Material* air = nist->FindOrBuildMaterial("G4_AIR");
  G4double worldHalf = 0.5 * m;
  G4Box* worldSolid = new G4Box("world", worldHalf, worldHalf, worldHalf);
  G4LogicalVolume* worldLV = new G4LogicalVolume(worldSolid, air, "world");
  worldLV->SetVisAttributes(G4VisAttributes::GetInvisible());
  G4VPhysicalVolume* worldPV = new G4PVPlacement(
    nullptr, {}, worldLV, "world", nullptr, false, 0, true);

  // --- Sample: a simple shape of the configured material ---
  G4Material* sampleMat = BuildSampleMaterial();
  G4VSolid* sampleSolid = nullptr;
  if (config.sample_shape == "cube") {
    G4double half = 0.5 * config.sample_size * mm;
    sampleSolid = new G4Box("sample", half, half, half);
  } else if (config.sample_shape == "sphere") {
    sampleSolid = new G4Orb("sample", config.sample_size * mm);
  } else {  // cylinder (default)
    sampleSolid = new G4Tubs("sample", 0., config.sample_size * mm,
                             0.5 * config.sample_height * mm, 0., twopi);
  }
  G4LogicalVolume* sampleLV = new G4LogicalVolume(sampleSolid, sampleMat, "sample");
  sampleLV->SetVisAttributes(new G4VisAttributes(G4Colour(0.3, 0.6, 1.0)));
  new G4PVPlacement(nullptr, config.sample_position * mm, sampleLV, "sample",
                    worldLV, false, 0, true);

  // --- Detector: an HPGe (germanium) cylinder, made sensitive below ---
  G4Material* germanium = nist->FindOrBuildMaterial("G4_Ge");
  G4Tubs* detSolid = new G4Tubs("detector", 0., config.detector_radius * mm,
                                0.5 * config.detector_height * mm, 0., twopi);
  G4LogicalVolume* detLV = new G4LogicalVolume(detSolid, germanium, "detector");
  detLV->SetVisAttributes(new G4VisAttributes(G4Colour(1.0, 0.5, 0.0)));
  new G4PVPlacement(nullptr, config.detector_position * mm, detLV, "detector",
                    worldLV, false, 0, true);

  return worldPV;
}

void DetectorConstruction::ConstructSDandField()
{
  // Mark the detector volume as sensitive so gamma hits are recorded.
  SensitiveDetector* sd = new SensitiveDetector("detector");
  G4SDManager::GetSDMpointer()->AddNewDetector(sd);
  SetSensitiveDetector("detector", sd);
}
