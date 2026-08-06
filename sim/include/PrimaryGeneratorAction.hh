#ifndef GRAACE_PRIMARYGENERATORACTION_HH
#define GRAACE_PRIMARYGENERATORACTION_HH

#include "G4VUserPrimaryGeneratorAction.hh"

class G4GeneralParticleSource;
class G4Event;

// PrimaryGeneratorAction produces each event's starting neutron using the
// General Particle Source, configured from the source values in Config
// (particle, energy, position). Defaults to a 14.1 MeV DT neutron.
class PrimaryGeneratorAction : public G4VUserPrimaryGeneratorAction
{
public:
  PrimaryGeneratorAction();
  ~PrimaryGeneratorAction() override;

  void GeneratePrimaries(G4Event* event) override;

private:
  G4GeneralParticleSource* fSource;
};

#endif
