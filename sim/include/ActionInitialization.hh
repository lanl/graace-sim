#ifndef GRAACE_ACTIONINITIALIZATION_HH
#define GRAACE_ACTIONINITIALIZATION_HH

#include "G4VUserActionInitialization.hh"

// ActionInitialization registers the user actions with the run manager. Under
// the multithreaded run manager Build() runs on each worker thread (the workers
// score hits and write their own output part files), while BuildForMaster() runs
// once on the master thread, which only opens and finishes the run.
class ActionInitialization : public G4VUserActionInitialization
{
public:
  void Build() const override;
  void BuildForMaster() const override;
};

#endif
