cmake_minimum_required(VERSION 3.16)
project(graace-sim)

find_package(Python REQUIRED COMPONENTS Interpreter)

# --- GEANT4 with UI and visualization drivers ---
# Required by GEANT4's own bundled CMake config: it runs a capability probe that
# aborts our configure step in multithreaded mode. Pre-seeding the probe result
# skips that check. Do not remove — the build fails to configure without it.
set(GEANT4_HAVE_H5_HAVE_THREADSAFE TRUE CACHE INTERNAL "pre-seed a GEANT4 config probe")


find_package(Geant4 REQUIRED ui_all vis_all)
include(${Geant4_USE_FILE})

# --- Apache Arrow / Parquet for the output file ---
find_package(Arrow REQUIRED)
find_package(Parquet REQUIRED)

include_directories(${PROJECT_SOURCE_DIR}/include)

file(GLOB sources CONFIGURE_DEPENDS ${PROJECT_SOURCE_DIR}/src/*.cc)
file(GLOB headers CONFIGURE_DEPENDS ${PROJECT_SOURCE_DIR}/include/*.hh)

add_executable(graace-sim apps/graace_sim_main.cc ${sources} ${headers})

target_link_libraries(graace-sim
  ${Geant4_LIBRARIES}
  Arrow::arrow_shared
  Parquet::parquet_shared
)

# Put the executable at the top of the build directory so `build/graace-sim`
# is a predictable path during development.
set_target_properties(graace-sim PROPERTIES
  RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
)

# Install the engine into <prefix>/bin so it lands on PATH. The package build
# backend sets the prefix to the target environment, so the runner finds it with
# `shutil.which("graace-sim")`.
install(TARGETS graace-sim RUNTIME DESTINATION bin)

# Install the Python control layer beside the engine in the target environment.
execute_process(
  COMMAND "${Python_EXECUTABLE}" -c
          "import sysconfig; print(sysconfig.get_path('purelib'))"
  OUTPUT_VARIABLE PYTHON_SITE_PACKAGES
  OUTPUT_STRIP_TRAILING_WHITESPACE
)
install(DIRECTORY ${PROJECT_SOURCE_DIR}/../src/graace_sim
        DESTINATION ${PYTHON_SITE_PACKAGES}
        FILES_MATCHING REGEX ".*\\.py$")
