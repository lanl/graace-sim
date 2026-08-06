#include "EventAction.hh"

#include "G4Event.hh"
#include "G4ios.hh"

void EventAction::EndOfEventAction(const G4Event* event)
{
  G4int id = event->GetEventID();
  if (id > 0 && id % 1000 == 0) {
    G4cout << "  ... processed " << id << " events" << G4endl;
  }
}
