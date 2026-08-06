#include "SensitiveDetector.hh"
#include "SimIO.hh"
#include "utils.hh"

#include "G4Step.hh"
#include "G4SystemOfUnits.hh"

SensitiveDetector::SensitiveDetector(const G4String& name)
  : G4VSensitiveDetector(name)
{
}

void SensitiveDetector::Initialize(G4HCofThisEvent*)
{
  fEnergyDeposit = 0.;
  fEarliestTime  = 0.;
}

G4bool SensitiveDetector::ProcessHits(G4Step* step, G4TouchableHistory*)
{
  // Sum the energy deposited by any particle in the detector this step. The
  // energy of an incoming gamma is shared among the electrons it sets in motion,
  // so summing every deposit recovers the full energy the detector measures.
  G4double edep = step->GetTotalEnergyDeposit();
  if (edep <= 0.) {
    return false;
  }

  const G4double time = step->GetPreStepPoint()->GetGlobalTime();
  if (fEnergyDeposit == 0. || time < fEarliestTime) {
    fEarliestTime = time;
  }
  fEnergyDeposit += edep;
  return true;
}

void SensitiveDetector::EndOfEvent(G4HCofThisEvent*)
{
  // Record one hit per event, but only if the detector saw energy.
  if (fEnergyDeposit <= 0.) {
    return;
  }

  GammaHit hit;
  hit.detector = GetName();
  hit.energy   = fEnergyDeposit / keV;
  hit.time     = fEarliestTime / ns;

  SimIO::Instance().Add(hit);
}
