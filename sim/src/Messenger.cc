#include "Messenger.hh"
#include "Config.hh"

#include "G4UIdirectory.hh"
#include "G4UIcommand.hh"
#include "G4UIparameter.hh"
#include "G4ios.hh"
#include <sstream>
#include <vector>

namespace {
// Build a command with a single string parameter. All values arrive as text and
// are parsed in SetNewValue, which keeps every command uniform.
std::unique_ptr<G4UIcommand> MakeCommand(const char* path, const char* guidance,
                                         G4UImessenger* owner)
{
  auto cmd = std::make_unique<G4UIcommand>(path, owner);
  cmd->SetGuidance(guidance);
  auto param = new G4UIparameter("value", 's', false);
  cmd->SetParameter(param);
  return cmd;
}
}  // namespace

Messenger::Messenger()
{
  fSourceDir   = std::make_unique<G4UIdirectory>("/source/");
  fSourceDir->SetGuidance("Neutron source configuration");
  fSampleDir   = std::make_unique<G4UIdirectory>("/sample/");
  fSampleDir->SetGuidance("Sample configuration");
  fDetectorDir = std::make_unique<G4UIdirectory>("/detector/");
  fDetectorDir->SetGuidance("Gamma detector configuration");
  fShieldingDir = std::make_unique<G4UIdirectory>("/shielding/");
  fShieldingDir->SetGuidance("Shielding configuration");
  fOutputDir   = std::make_unique<G4UIdirectory>("/output/");
  fOutputDir->SetGuidance("Output configuration");

  fSourceParticle = MakeCommand("/source/particle", "Source particle name", this);
  fSourceEnergy   = MakeCommand("/source/energy", "Source energy in MeV", this);
  fSourcePosition = MakeCommand("/source/position", "Source position: x y z (mm)", this);
  fSourceShape    = MakeCommand("/source/shape", "Source emission shape: point | disk | beam", this);
  fSourceRadius   = MakeCommand("/source/radius", "Source disk/beam radius in mm", this);
  fSourceEnergyType = MakeCommand("/source/energyType", "Source energy type: mono | spectrum", this);
  fSourceSpectrumFile = MakeCommand(
    "/source/spectrumFile", "Path to an energy_mev intensity spectrum list file", this);
  fSourceTiming     = MakeCommand("/source/timing", "Source timing: continuous | single | periodic", this);
  fSourcePulseWidth = MakeCommand("/source/pulseWidth", "Pulse width in ns (single/periodic)", this);
  fSourcePulsePeriod = MakeCommand("/source/pulsePeriod", "Pulse period in ns (periodic)", this);

  fSampleComposition = MakeCommand(
    "/sample/composition",
    "Element mass fractions: Sym frac Sym frac ... (e.g. Fe 0.7 Cr 0.3)", this);
  fSampleDensity  = MakeCommand("/sample/density", "Sample density in g/cm3", this);
  fSampleShape    = MakeCommand("/sample/shape", "Sample shape: cube | sphere | cylinder", this);
  fSampleSize     = MakeCommand("/sample/size", "Cube side, or sphere/cylinder radius (mm)", this);
  fSampleHeight   = MakeCommand("/sample/height", "Cylinder height in mm", this);
  fSamplePosition = MakeCommand("/sample/position", "Sample position: x y z (mm)", this);

  fDetectorAdd = MakeCommand(
    "/detector/add",
    "Add a detector: radius_mm height_mm x y z (mm). Replaces the default set.", this);

  fShieldingAdd = MakeCommand(
    "/shielding/add",
    "Add shielding: material thickness_mm x y z (mm), e.g. G4_Pb 50 0 0 40", this);

  fOutputFile = MakeCommand("/output/file", "Output Parquet file path", this);
}

Messenger::~Messenger() = default;

namespace {
G4ThreeVector ParseVector(const G4String& value)
{
  std::istringstream in(value);
  double x = 0, y = 0, z = 0;
  in >> x >> y >> z;
  return {x, y, z};
}
}  // namespace

void Messenger::SetNewValue(G4UIcommand* command, G4String value)
{
  Config& config = Config::Instance();

  if (command == fSourceParticle.get()) {
    config.source_particle = value;
  } else if (command == fSourceEnergy.get()) {
    config.source_energy = std::stod(value);
  } else if (command == fSourcePosition.get()) {
    config.source_position = ParseVector(value);
  } else if (command == fSourceShape.get()) {
    config.source_shape = value;
  } else if (command == fSourceRadius.get()) {
    config.source_radius = std::stod(value);
  } else if (command == fSourceEnergyType.get()) {
    config.source_energy_type = value;
  } else if (command == fSourceSpectrumFile.get()) {
    config.source_spectrum_file = value;
  } else if (command == fSourceTiming.get()) {
    config.source_timing = value;
  } else if (command == fSourcePulseWidth.get()) {
    config.source_pulse_width_ns = std::stod(value);
  } else if (command == fSourcePulsePeriod.get()) {
    config.source_pulse_period_ns = std::stod(value);

  } else if (command == fSampleComposition.get()) {
    // Parse alternating element symbol and mass fraction.
    std::istringstream in(value);
    std::vector<std::pair<G4String, G4double>> composition;
    G4String symbol;
    double fraction;
    while (in >> symbol >> fraction) {
      composition.emplace_back(symbol, fraction);
    }
    config.sample_composition = composition;
  } else if (command == fSampleDensity.get()) {
    config.sample_density = std::stod(value);
  } else if (command == fSampleShape.get()) {
    config.sample_shape = value;
  } else if (command == fSampleSize.get()) {
    config.sample_size = std::stod(value);
  } else if (command == fSampleHeight.get()) {
    config.sample_height = std::stod(value);
  } else if (command == fSamplePosition.get()) {
    config.sample_position = ParseVector(value);

  } else if (command == fDetectorAdd.get()) {
    // radius_mm height_mm x y z. The first add replaces the default detector set.
    if (!fDetectorsCleared) {
      config.detectors.clear();
      fDetectorsCleared = true;
    }
    std::istringstream in(value);
    DetectorBlock detector;
    double x = 0, y = 0, z = 0;
    in >> detector.radius >> detector.height >> x >> y >> z;
    detector.position = {x, y, z};
    config.detectors.push_back(detector);

  } else if (command == fShieldingAdd.get()) {
    // material thickness_mm x y z.
    std::istringstream in(value);
    ShieldingBlock block;
    double x = 0, y = 0, z = 0;
    in >> block.material >> block.thickness >> x >> y >> z;
    block.position = {x, y, z};
    config.shielding.push_back(block);

  } else if (command == fOutputFile.get()) {
    config.output_file = value;
  }
}
