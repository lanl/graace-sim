#include "Config.hh"

Config& Config::Instance()
{
  static Config instance;
  return instance;
}
