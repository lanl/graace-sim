#ifndef GRAACE_PRIMARYGENERATORACTION_HH
#define GRAACE_PRIMARYGENERATORACTION_HH

#include "G4VUserPrimaryGeneratorAction.hh"

class G4GeneralParticleSource;
class G4Event;

// PrimaryGeneratorAction produces each event's starting neutron using the
// General Particle Source, configured from the source values in Config
// (particle, energy, position, shape, spectrum, timing). Defaults to a 14.1 MeV
// DT neutron. Config is read on the first event, not in the constructor, so
// /source/* commands take effect whatever their order relative to
// /run/initialize.
class PrimaryGeneratorAction : public G4VUserPrimaryGeneratorAction
{
public:
  PrimaryGeneratorAction();
  ~PrimaryGeneratorAction() override;

  void GeneratePrimaries(G4Event* event) override;

private:
  // Set up the GPS from the current Config. Called once on the first event.
  void Configure();

  // The emission time for the given event, from the configured timing. Keyed on
  // the event id (like ScintiPix) so the time is deterministic for each event.
  double EventTime(int event_id);

  G4GeneralParticleSource* fSource;
  bool fConfigured = false;
};

#endif
