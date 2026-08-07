#include "DetectorConstruction.hh"
#include "SensitiveDetector.hh"
#include "Config.hh"

#include "G4NistManager.hh"
#include "G4Material.hh"
#include "G4Element.hh"
#include "G4Isotope.hh"
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

#include <string>

G4Material* DetectorConstruction::BuildSampleMaterial()
{
  const Config& config = Config::Instance();
  G4NistManager* nist = G4NistManager::Instance();

  G4Material* material = new G4Material(
    "sample_material", config.sample_density * g / cm3,
    static_cast<G4int>(config.sample_composition.size()));

  // Add each element by mass fraction. An element with no isotope breakdown comes
  // from the NIST database, so natural isotopic abundances are used. An element
  // with a breakdown is built from the specified isotopes by atom fraction.
  for (const auto& part : config.sample_composition) {
    const G4String& symbol = part.first;
    const G4double mass_fraction = part.second;

    auto found = config.sample_isotopes.find(symbol);
    if (found == config.sample_isotopes.end()) {
      G4Element* element = nist->FindOrBuildElement(symbol);
      material->AddElement(element, mass_fraction);
    } else {
      const std::vector<SampleIsotope>& isotopes = found->second;
      if (isotopes.empty()) {
        G4cerr << "DetectorConstruction: empty isotope list for element '" << symbol
               << "'; using natural abundances." << G4endl;
        G4Element* element = nist->FindOrBuildElement(symbol);
        material->AddElement(element, mass_fraction);
        continue;
      }

      // Validate that mass numbers are unique and atom fractions sum to 1.0.
      G4double total = 0.;
      bool invalid = false;
      for (std::size_t i = 0; i < isotopes.size(); ++i) {
        const auto& iso = isotopes[i];
        if (iso.mass_number <= 0 || iso.atom_fraction <= 0. || iso.atom_fraction > 1.) {
          invalid = true;
          break;
        }
        total += iso.atom_fraction;
        for (std::size_t j = i + 1; j < isotopes.size(); ++j) {
          if (iso.mass_number == isotopes[j].mass_number) {
            invalid = true;
            break;
          }
        }
        if (invalid) {
          break;
        }
      }
      if (invalid || total < 1.0 - 1e-6 || total > 1.0 + 1e-6) {
        G4cerr << "DetectorConstruction: invalid isotope breakdown for element '" << symbol
               << "' (unique mass numbers and atom fractions summing to 1.0 are required); using natural abundances." << G4endl;
        G4Element* element = nist->FindOrBuildElement(symbol);
        material->AddElement(element, mass_fraction);
        continue;
      }

      G4int Z = nist->FindOrBuildElement(symbol)->GetZasInt();
      G4Element* element = new G4Element(
        symbol + "_isotopic", symbol, static_cast<G4int>(isotopes.size()));
      for (const auto& isotope : isotopes) {
        // The isotope mass is taken from NIST data for the (Z, mass_number) pair.
        G4Isotope* nuclide = new G4Isotope(
          symbol + std::to_string(isotope.mass_number), Z, isotope.mass_number);
        element->AddIsotope(nuclide, isotope.atom_fraction);
      }
      material->AddElement(element, mass_fraction);
    }
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
  } else if (config.sample_shape == "cylinder") {
    sampleSolid = new G4Tubs("sample", 0., config.sample_size * mm,
                             0.5 * config.sample_height * mm, 0., twopi);
  } else {
    G4cerr << "DetectorConstruction: unknown sample shape '" << config.sample_shape
           << "'; expected cube|sphere|cylinder. Using cylinder." << G4endl;
    sampleSolid = new G4Tubs("sample", 0., config.sample_size * mm,
                             0.5 * config.sample_height * mm, 0., twopi);
  }
  G4LogicalVolume* sampleLV = new G4LogicalVolume(sampleSolid, sampleMat, "sample");
  sampleLV->SetVisAttributes(new G4VisAttributes(G4Colour(0.3, 0.6, 1.0)));
  new G4PVPlacement(nullptr, config.sample_position * mm, sampleLV, "sample",
                    worldLV, false, 0, true);

  // --- Shielding: optional slabs of a named material ---
  // Each slab is a square footprint kSlabHalfWidth on a side, the configured
  // thickness deep (along z). A fixed footprint keeps the command to material,
  // thickness, and position; a configurable footprint can be added later.
  for (std::size_t i = 0; i < config.shielding.size(); ++i) {
    const ShieldingBlock& block = config.shielding[i];
    G4Material* shieldMat = nist->FindOrBuildMaterial(block.material);
    if (shieldMat == nullptr) {
      G4cerr << "DetectorConstruction: unknown shielding material '"
             << block.material << "'; skipping this block." << G4endl;
      continue;
    }
    const std::string shieldName = "shielding_" + std::to_string(i);
    G4Box* shieldSolid = new G4Box(
      shieldName.c_str(), kSlabHalfWidth * mm, kSlabHalfWidth * mm,
      0.5 * block.thickness * mm);
    G4LogicalVolume* shieldLV =
      new G4LogicalVolume(shieldSolid, shieldMat, shieldName.c_str());
    shieldLV->SetVisAttributes(new G4VisAttributes(G4Colour(0.6, 0.6, 0.6)));
    new G4PVPlacement(nullptr, block.position * mm, shieldLV,
                      "shielding_" + std::to_string(i), worldLV, false,
                      static_cast<G4int>(i), true);
  }

  // --- Detectors: one or more HPGe (germanium) cylinders, made sensitive below.
  // Each takes its configured name so its hits are recorded under that name.
  G4Material* germanium = nist->FindOrBuildMaterial("G4_Ge");
  for (std::size_t i = 0; i < config.detectors.size(); ++i) {
    const DetectorBlock& detector = config.detectors[i];
    const G4String& name = detector.name;
    G4Tubs* detSolid = new G4Tubs(name, 0., detector.radius * mm,
                                  0.5 * detector.height * mm, 0., twopi);
    G4LogicalVolume* detLV = new G4LogicalVolume(detSolid, germanium, name);
    detLV->SetVisAttributes(new G4VisAttributes(G4Colour(1.0, 0.5, 0.0)));
    new G4PVPlacement(nullptr, detector.position * mm, detLV, name,
                      worldLV, false, static_cast<G4int>(i), true);
  }

  return worldPV;
}

void DetectorConstruction::ConstructSDandField()
{
  const Config& config = Config::Instance();

  // Mark each detector volume as sensitive so its gamma hits are recorded.
  for (const DetectorBlock& detector : config.detectors) {
    SensitiveDetector* sd = new SensitiveDetector(detector.name);
    G4SDManager::GetSDMpointer()->AddNewDetector(sd);
    SetSensitiveDetector(detector.name, sd);
  }
}
