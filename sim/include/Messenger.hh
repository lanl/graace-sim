#ifndef GRAACE_MESSENGER_HH
#define GRAACE_MESSENGER_HH

#include "G4UImessenger.hh"

#include <memory>

class G4UIdirectory;
class G4UIcommand;

// Messenger defines the GEANT4 UI commands the engine understands and stores
// each value into Config. It holds no physics — it only turns a line of a macro
// into a stored configuration value. Command argument names stay snake_case to
// match the Python Pydantic models.
class Messenger : public G4UImessenger
{
public:
  Messenger();
  ~Messenger() override;

  void SetNewValue(G4UIcommand* command, G4String value) override;

private:
  std::unique_ptr<G4UIdirectory> fSourceDir;
  std::unique_ptr<G4UIdirectory> fSampleDir;
  std::unique_ptr<G4UIdirectory> fDetectorDir;
  std::unique_ptr<G4UIdirectory> fShieldingDir;
  std::unique_ptr<G4UIdirectory> fOutputDir;

  // --- /source/* ---
  std::unique_ptr<G4UIcommand> fSourceParticle;
  std::unique_ptr<G4UIcommand> fSourceEnergy;
  std::unique_ptr<G4UIcommand> fSourcePosition;
  std::unique_ptr<G4UIcommand> fSourceShape;
  std::unique_ptr<G4UIcommand> fSourceRadius;
  std::unique_ptr<G4UIcommand> fSourceEnergyType;
  std::unique_ptr<G4UIcommand> fSourceSpectrumFile;
  std::unique_ptr<G4UIcommand> fSourceTiming;
  std::unique_ptr<G4UIcommand> fSourcePulseWidth;
  std::unique_ptr<G4UIcommand> fSourcePulsePeriod;

  // --- /sample/* ---
  std::unique_ptr<G4UIcommand> fSampleComposition;
  std::unique_ptr<G4UIcommand> fSampleIsotope;
  std::unique_ptr<G4UIcommand> fSampleDensity;
  std::unique_ptr<G4UIcommand> fSampleShape;
  std::unique_ptr<G4UIcommand> fSampleSize;
  std::unique_ptr<G4UIcommand> fSampleHeight;
  std::unique_ptr<G4UIcommand> fSamplePosition;

  // --- /detector/* ---
  std::unique_ptr<G4UIcommand> fDetectorAdd;

  // --- /shielding/* ---
  std::unique_ptr<G4UIcommand> fShieldingAdd;

  // --- /output/* ---
  std::unique_ptr<G4UIcommand> fOutputFile;

  // The default detector set is replaced by the first /detector/add.
  bool fDetectorsCleared = false;
};

#endif
