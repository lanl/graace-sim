#include "EventAction.hh"

#include "G4Event.hh"
#include "G4ios.hh"

void EventAction::EndOfEventAction(const G4Event* event)
{
  const G4int id = event->GetEventID();
  const G4int processed = id + 1;
  if (processed % 1000 == 0) {
    G4cout << "  ... processed " << processed << " events" << G4endl;
  }
}
