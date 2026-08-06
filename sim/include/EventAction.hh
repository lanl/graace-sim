#ifndef GRAACE_EVENTACTION_HH
#define GRAACE_EVENTACTION_HH

#include "G4UserEventAction.hh"

// EventAction does per-event bookkeeping. The gamma hits themselves are recorded
// by the sensitive detector; here we just report progress periodically.
class EventAction : public G4UserEventAction
{
public:
  void EndOfEventAction(const G4Event* event) override;
};

#endif
