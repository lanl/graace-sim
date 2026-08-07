#include "ActionInitialization.hh"
#include "PrimaryGeneratorAction.hh"
#include "RunAction.hh"
#include "EventAction.hh"
#include "SteppingAction.hh"

void ActionInitialization::Build() const
{
  // Worker thread: generates primaries, scores hits, and writes its own output.
  SetUserAction(new PrimaryGeneratorAction());
  SetUserAction(new RunAction());
  SetUserAction(new EventAction());
  SetUserAction(new SteppingAction());
}

void ActionInitialization::BuildForMaster() const
{
  // Master thread: only opens the run and prints the final summary; the workers
  // do the scoring and write their own output part files.
  SetUserAction(new RunAction());
}
