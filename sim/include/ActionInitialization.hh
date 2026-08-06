#ifndef GRAACE_ACTIONINITIALIZATION_HH
#define GRAACE_ACTIONINITIALIZATION_HH

#include "G4VUserActionInitialization.hh"

// ActionInitialization registers the primary generator and the run, event, and
// stepping actions with the run manager.
class ActionInitialization : public G4VUserActionInitialization
{
public:
  void Build() const override;
};

#endif
