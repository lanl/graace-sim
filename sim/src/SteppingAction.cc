#include "SteppingAction.hh"

#include "G4Step.hh"

void SteppingAction::UserSteppingAction(const G4Step*)
{
  // Gamma hits in the detector are recorded by the sensitive detector. No
  // per-step recording is needed for this first slice.
}
