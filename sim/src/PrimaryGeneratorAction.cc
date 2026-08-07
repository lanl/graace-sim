#include "PrimaryGeneratorAction.hh"
#include "Config.hh"

#include "G4GeneralParticleSource.hh"
#include "G4ParticleTable.hh"
#include "G4SystemOfUnits.hh"
#include "G4PrimaryVertex.hh"
#include "G4Event.hh"
#include "Randomize.hh"
#include "G4ios.hh"

#include <fstream>
#include <sstream>

PrimaryGeneratorAction::PrimaryGeneratorAction()
  : fSource(new G4GeneralParticleSource())
{
}

PrimaryGeneratorAction::~PrimaryGeneratorAction()
{
  delete fSource;
}

void PrimaryGeneratorAction::Configure()
{
  const Config& config = Config::Instance();

  G4ParticleDefinition* particle =
    G4ParticleTable::GetParticleTable()->FindParticle(config.source_particle);
  fSource->SetParticleDefinition(particle);

  // --- Position: a point, a disk, or a beam, aimed at the sample (+z) ---
  G4SPSPosDistribution* pos = fSource->GetCurrentSource()->GetPosDist();
  pos->SetCentreCoords(config.source_position * mm);
  if (config.source_shape == "point") {
    pos->SetPosDisType("Point");
  } else if (config.source_shape == "disk") {
    pos->SetPosDisType("Plane");
    pos->SetPosDisShape("Circle");
    pos->SetRadius(config.source_radius * mm);
  } else if (config.source_shape == "beam") {
    pos->SetPosDisType("Beam");
    pos->SetBeamSigmaInR(config.source_radius * mm);
  } else {
    G4cerr << "PrimaryGeneratorAction: unknown source shape '"
           << config.source_shape << "'; expected point|disk|beam. Using point."
           << G4endl;
    pos->SetPosDisType("Point");
  }

  G4SPSAngDistribution* ang = fSource->GetCurrentSource()->GetAngDist();
  ang->SetAngDistType("planar");
  ang->SetParticleMomentumDirection({0., 0., 1.});

  // --- Energy: a single value, or a spectrum read from a list file ---
  G4SPSEneDistribution* ene = fSource->GetCurrentSource()->GetEneDist();
  if (config.source_energy_type == "spectrum") {
    // Read "energy_mev intensity" pairs and feed them to the GPS as a
    // point-wise (Arb) energy distribution.
    std::ifstream file(config.source_spectrum_file.c_str());
    if (!file) {
      G4cerr << "PrimaryGeneratorAction: could not open spectrum file '"
             << config.source_spectrum_file << "'; using mono energy." << G4endl;
      ene->SetEnergyDisType("Mono");
      ene->SetMonoEnergy(config.source_energy * MeV);
    } else {
      ene->SetEnergyDisType("Arb");
      std::string line;
      while (std::getline(file, line)) {
        std::istringstream in(line);
        double energy_mev = 0., intensity = 0.;
        if (in >> energy_mev >> intensity) {
          ene->ArbEnergyHisto({energy_mev * MeV, intensity});
        }
      }
      ene->ArbInterpolate("Lin");
    }
  } else {
    ene->SetEnergyDisType("Mono");
    ene->SetMonoEnergy(config.source_energy * MeV);
  }
}

double PrimaryGeneratorAction::EventTime(int event_id)
{
  // Follows ScintiPix's per-vertex timing: place each event in a pulse and add
  // a random offset within the pulse width. A "single" source is one pulse; a
  // "periodic" source repeats every pulse_period.
  const Config& config = Config::Instance();
  const int safe_id = event_id < 0 ? 0 : event_id;
  const double width = config.source_pulse_width_ns * ns;

  if (config.source_timing == "single") {
    return width > 0. ? G4UniformRand() * width : 0.;
  }
  if (config.source_timing == "periodic") {
    const double pulse_start = safe_id * config.source_pulse_period_ns * ns;
    return pulse_start + (width > 0. ? G4UniformRand() * width : 0.);
  }
  // continuous: no time structure.
  return 0.;
}

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* event)
{
  if (!fConfigured) {
    Configure();
    fConfigured = true;
  }

  fSource->GeneratePrimaryVertex(event);

  // Stamp the event's vertices with the emission time from the configured
  // timing, so the recorded hit times carry the pulse structure.
  const double time = EventTime(event->GetEventID());
  if (time > 0.) {
    for (G4int i = 0; i < event->GetNumberOfPrimaryVertex(); ++i) {
      event->GetPrimaryVertex(i)->SetT0(time);
    }
  }
}
