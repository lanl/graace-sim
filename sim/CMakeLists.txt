cmake_minimum_required(VERSION 3.16)
project(graace-sim)

# --- GEANT4 with UI and visualization drivers ---
set(GEANT4_HAVE_H5_HAVE_THREADSAFE TRUE CACHE INTERNAL "skip HDF5 thread-safety check")
find_package(Geant4 REQUIRED ui_all vis_all)
include(${Geant4_USE_FILE})

# --- Apache Arrow / Parquet for the output file ---
find_package(Arrow REQUIRED)
find_package(Parquet REQUIRED)

include_directories(${PROJECT_SOURCE_DIR}/include)

file(GLOB sources ${PROJECT_SOURCE_DIR}/src/*.cc)
file(GLOB headers ${PROJECT_SOURCE_DIR}/include/*.hh)

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

# Install the engine into <prefix>/bin so it lands on PATH. `build-sim` sets the
# prefix to the active pixi environment, so the runner finds it with
# `shutil.which("graace-sim")`.
install(TARGETS graace-sim RUNTIME DESTINATION bin)
