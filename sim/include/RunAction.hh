#ifndef GRAACE_RUNACTION_HH
#define GRAACE_RUNACTION_HH

#include "G4UserRunAction.hh"

// RunAction opens the output writer at the start of a run and writes the
// collected gamma hits to the Parquet file when the run ends.
class RunAction : public G4UserRunAction
{
public:
  void BeginOfRunAction(const G4Run* run) override;
  void EndOfRunAction(const G4Run* run) override;
};

#endif
