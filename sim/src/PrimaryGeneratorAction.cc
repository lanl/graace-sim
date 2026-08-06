#include "PrimaryGeneratorAction.hh"
#include "Config.hh"

#include "G4GeneralParticleSource.hh"
#include "G4ParticleTable.hh"
#include "G4SystemOfUnits.hh"

PrimaryGeneratorAction::PrimaryGeneratorAction()
  : fSource(new G4GeneralParticleSource())
{
  const Config& config = Config::Instance();

  G4ParticleDefinition* particle =
    G4ParticleTable::GetParticleTable()->FindParticle(config.source_particle);
  fSource->SetParticleDefinition(particle);

  // A point source at the configured position, aimed at the sample (+z).
  G4SPSPosDistribution* pos = fSource->GetCurrentSource()->GetPosDist();
  pos->SetPosDisType("Point");
  pos->SetCentreCoords(config.source_position * mm);

  G4SPSAngDistribution* ang = fSource->GetCurrentSource()->GetAngDist();
  ang->SetAngDistType("planar");
  ang->SetParticleMomentumDirection({0., 0., 1.});

  // Mono-energetic neutron.
  G4SPSEneDistribution* ene = fSource->GetCurrentSource()->GetEneDist();
  ene->SetEnergyDisType("Mono");
  ene->SetMonoEnergy(config.source_energy * MeV);
}

PrimaryGeneratorAction::~PrimaryGeneratorAction()
{
  delete fSource;
}

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* event)
{
  fSource->GeneratePrimaryVertex(event);
}
