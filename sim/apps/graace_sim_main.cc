// graace-sim entry point.
//
// Creates the run manager, installs a neutron-capable physics list, registers
// the geometry and actions and the command interface, then either runs a macro
// (if one is given on the command line) or opens the interactive window.

#include "DetectorConstruction.hh"
#include "ActionInitialization.hh"
#include "Messenger.hh"
#include "seed.hh"

#include "G4RunManagerFactory.hh"
#include "G4UImanager.hh"
#include "G4UIExecutive.hh"
#include "G4VisExecutive.hh"
#include "FTFP_BERT_HP.hh"

int main(int argc, char** argv)
{
  // A macro is run in batch mode; with no argument we open the interactive UI.
  G4UIExecutive* ui = nullptr;
  if (argc == 1) {
    ui = new G4UIExecutive(argc, argv);
  }

  // Create the run manager before initializing the physics list and geometry.
  auto* runManager =
    G4RunManagerFactory::CreateRunManager(G4RunManagerType::MT);

  // High-precision neutron data so neutron capture and gamma production are modeled.
  runManager->SetUserInitialization(new FTFP_BERT_HP());

  // Detector geometry and action initialization.
  runManager->SetUserInitialization(new DetectorConstruction());

  // Action initialization must be set after the detector construction.
  runManager->SetUserInitialization(new ActionInitialization());

  // The command interface: /source, /sample, /detector, /output.
  Messenger messenger;

  SetRandomSeed(1);

  auto* visManager = new G4VisExecutive();
  visManager->Initialize();

  auto* uiManager = G4UImanager::GetUIpointer();

  if (ui) {
    // Interactive: load the visualization defaults, then hand over to the user.
    uiManager->ApplyCommand("/control/execute sim/macros/vis.mac");
    ui->SessionStart();
    delete ui;
  } else {
    // Batch: run the given macro.
    G4String command = "/control/execute ";
    G4String macro = argv[1];
    uiManager->ApplyCommand(command + macro);
  }

  delete visManager;
  delete runManager;
  return 0;
}
