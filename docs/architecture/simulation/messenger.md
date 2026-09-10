# Command interface (Messenger)

`Messenger` is the GEANT4 UI command handler. It receives each macro line,
parses the text, and stores values in the shared `Config` object. It does not build
geometry or write output itself.

## Commands

Vectors are `x y z` in millimeters. Commands are applied through
`G4UImessenger` and use one string argument.

| Command | Argument | Meaning |
| --- | --- | --- |
| `/source/particle` | name | Particle name, normally `neutron` |
| `/source/position` | `x y z` | Source center in mm |
| `/source/shape` | `point \| disk \| beam` | Source emission shape |
| `/source/radius` | mm | Disk radius or beam radial sigma |
| `/source/energyType` | `mono \| spectrum` | Energy distribution |
| `/source/energy` | MeV | Mono energy |
| `/source/spectrumFile` | path | Text spectrum file |
| `/source/timing` | `continuous \| single \| periodic` | Pulse mode |
| `/source/pulseWidth` | ns | Pulse width |
| `/source/pulsePeriod` | ns | Period between pulses |
| `/sample/composition` | `Sym frac ...` | Element mass fractions |
| `/sample/isotope` | `symbol mass_number atom_fraction` | One isotope entry |
| `/sample/density` | g/cm³ | Sample density |
| `/sample/shape` | `cube \| sphere \| cylinder` | Sample shape |
| `/sample/size` | mm | Cube side or sphere/cylinder radius |
| `/sample/height` | mm | Cylinder height |
| `/sample/position` | `x y z` | Sample center in mm |
| `/detector/add` | `name radius height x y z` | Add an HPGe cylinder |
| `/shielding/add` | `material thickness x y z` | Add a square slab |
| `/output/file` | path | Base Parquet output path |

`/detector/add`, `/shielding/add`, and `/sample/isotope` can appear multiple
times. The first detector command clears the built-in default detector. Detector
names become output directory names and must not contain path separators. Sample
isotope entries for an element must use unique mass numbers and atom fractions
that sum to 1.0.

## How values are used

`Config` stores the values received by `Messenger`:

- `DetectorConstruction` reads sample, shielding, and detector settings while
  building the world;
- `PrimaryGeneratorAction` reads source settings on the first event;
- `RunAction` and `SimIO` read the output path;
- `SensitiveDetector` writes detector responses through `SimIO`.

The messenger accepts text and performs basic parsing and checks. The Python
Pydantic models perform the more complete validation before a generated macro is
written.

## Example

```text
/sample/composition Fe 1.0
/sample/density 7.87
/sample/shape cylinder
/sample/size 10
/sample/height 20
/sample/position 0 0 0
/detector/add hpge 30 50 0 80 0
/output/file data/results/gamma_hits.parquet
/run/initialize
/source/particle neutron
/source/position 0 0 -50
/source/shape point
/source/energyType mono
/source/energy 14.1
/source/timing continuous
/run/beamOn 10000
```
