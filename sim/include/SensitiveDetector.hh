#ifndef GRAACE_SENSITIVEDETECTOR_HH
#define GRAACE_SENSITIVEDETECTOR_HH

#include "G4VSensitiveDetector.hh"

// SensitiveDetector records the detector's response to each event. As particles
// move through the detector volume it sums the energy they deposit; at the end
// of the event it records one hit (detector name, total deposited energy, time)
// and hands it to SimIO. Summing over the event is what turns the many small
// deposits of the secondary electrons into the full gamma energy a real detector
// measures, so a spectrum can be built from the recorded energies.
class SensitiveDetector : public G4VSensitiveDetector
{
public:
  explicit SensitiveDetector(const G4String& name);

  void   Initialize(G4HCofThisEvent* hitCollections) override;
  G4bool ProcessHits(G4Step* step, G4TouchableHistory* history) override;
  void   EndOfEvent(G4HCofThisEvent* hitCollections) override;

private:
  G4double fEnergyDeposit = 0.;  // total energy deposited this event
  G4double fEarliestTime  = 0.;  // time of the first deposit this event
};

#endif
