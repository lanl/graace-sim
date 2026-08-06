#include "RunAction.hh"
#include "SimIO.hh"
#include "Config.hh"

#include "G4Run.hh"
#include "G4ios.hh"

void RunAction::BeginOfRunAction(const G4Run*)
{
  SimIO::Instance().Open(Config::Instance().output_file);
}

void RunAction::EndOfRunAction(const G4Run* run)
{
  G4cout << "Run finished: " << run->GetNumberOfEvent() << " events" << G4endl;
  SimIO::Instance().Write();
}
