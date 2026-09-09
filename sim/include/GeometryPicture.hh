#ifndef GRAACE_GEOMETRYPICTURE_HH
#define GRAACE_GEOMETRYPICTURE_HH

// Writes a picture of the setup — the sample, the detectors, any shielding, and
// where the neutrons come from — to a file next to the run's output. It is
// written at the start of the run, before the first neutron is fired, so a setup
// that is not what was intended shows up straight away instead of after a long
// run.
//
// There is nothing to switch on and nothing to tune. The camera angle and the
// zoom are worked out from how big the setup actually is, so the picture is
// framed correctly whatever is in it.
//
// Nothing is drawn if a viewer is already open, which covers the two cases where
// a picture would be unwanted or duplicated: an interactive session, where the
// setup is already on screen, and sim/macros/draw_geometry.mac, which opens its
// own viewer to make a picture with particle paths in it.
//
// No particles are fired to make the picture, so it cannot affect a run's
// results. Calling this more than once writes the picture once.
void WriteGeometryPicture();

#endif
