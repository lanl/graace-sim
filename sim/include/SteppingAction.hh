#ifndef GRAACE_STEPPINGACTION_HH
#define GRAACE_STEPPINGACTION_HH

#include "G4UserSteppingAction.hh"

// SteppingAction is where per-step interactions could be inspected. Gamma hits
// in the detector are recorded by the sensitive detector, so this is currently
// a placeholder for future per-step recording (e.g. capture vertices).
class SteppingAction : public G4UserSteppingAction
{
public:
  void UserSteppingAction(const G4Step* step) override;
};

#endif
