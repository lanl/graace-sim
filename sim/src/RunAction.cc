#include "RunAction.hh"
#include "GeometryPicture.hh"
#include "SimIO.hh"
#include "Config.hh"

#include "G4Run.hh"
#include "G4Threading.hh"
#include "G4ios.hh"

void RunAction::BeginOfRunAction(const G4Run*)
{
  // Each worker thread has its own SimIO (thread-local), so it opens its own
  // buffers and writes its own part files. The master thread scores no hits, so
  // it opens nothing.
  if (G4Threading::IsMasterThread()) {
    // The start of the run is the first moment every setting from the macro has
    // been applied and the geometry is built, and no neutron has been fired yet,
    // so it is where the picture of the setup is written.
    WriteGeometryPicture();
    return;
  }
  SimIO::Instance().Open(Config::Instance().output_file);
}

void RunAction::EndOfRunAction(const G4Run* run)
{
  // The master thread prints the run-level summary — its event count is the
  // total merged across all workers. Each worker flushes its own remaining hits
  // to its part files.
  if (G4Threading::IsMasterThread()) {
    G4cout << "Run finished: " << run->GetNumberOfEvent() << " events" << G4endl;
    return;
  }
  SimIO::Instance().Write();
}
