#include "seed.hh"

#include "Randomize.hh"

void SetRandomSeed(long seed)
{
  CLHEP::HepRandom::setTheSeed(seed);
}
