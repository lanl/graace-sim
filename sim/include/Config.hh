#ifndef GRAACE_CONFIG_HH
#define GRAACE_CONFIG_HH

#include "utils.hh"

#include "G4ThreeVector.hh"
#include "G4String.hh"

#include <vector>
#include <utility>

// Config holds every value the engine reads back when it builds the world and
// runs. The Messenger writes into it from the macro commands; the geometry
// builder and actions read from it. It holds no physics, only configuration
// state. Defaults here are the DT-generator -> sample -> detector test case, so
// the engine runs sensibly even with a bare macro.
//
// Field names match the snake_case names used in the macro commands and in the
// Python Pydantic models.
class Config
{
public:
  // The single shared instance the whole engine reads and writes.
  static Config& Instance();

  // --- Source (/source/*) ---
  G4String     source_particle = "neutron";
  G4ThreeVector source_position{0., 0., -50.};  // mm, relative to sample center
  // Emission shape: point | disk | beam. A disk or beam uses source_radius.
  G4String     source_shape  = "point";
  G4double     source_radius = 0.;       // mm (disk / beam radius)
  // Energy: mono uses source_energy (MeV); spectrum reads source_spectrum_file,
  // a plain-text "energy_mev intensity" list, one pair per line.
  G4String     source_energy_type   = "mono";
  G4double     source_energy         = 14.1;  // MeV (DT generator)
  G4String     source_spectrum_file  = "";
  // Time structure: continuous | single | periodic. A single or periodic source
  // uses source_pulse_width_ns; periodic also uses source_pulse_period_ns.
  G4String     source_timing          = "continuous";
  G4double     source_pulse_width_ns  = 0.;
  G4double     source_pulse_period_ns = 0.;

  // --- Sample (/sample/*) ---
  // Composition as (element symbol, mass fraction) pairs; fractions sum to 1.
  std::vector<std::pair<G4String, G4double>> sample_composition{{"Fe", 1.0}};
  G4double     sample_density = 7.87;    // g/cm3
  G4String     sample_shape   = "cylinder";  // cube | sphere | cylinder
  G4double     sample_size    = 10.;     // mm (cube side / sphere or cyl radius)
  G4double     sample_height  = 20.;     // mm (cylinder height)
  G4ThreeVector sample_position{0., 0., 0.};  // mm

  // --- Detectors (/detector/*) ---
  // One HPGe cylinder per entry. Defaults to the single example detector; each
  // /detector/add command replaces this default set with the added detectors.
  std::vector<DetectorBlock> detectors{{"detector", 30., 50., {0., 80., 0.}}};

  // --- Shielding (/shielding/*) ---
  // Zero or more shielding slabs; empty by default.
  std::vector<ShieldingBlock> shielding;

  // --- Output (/output/*) ---
  G4String     output_file = "data/hits.parquet";

private:
  Config() = default;
};

#endif
