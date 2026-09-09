#include "GeometryPicture.hh"
#include "Config.hh"
#include "DetectorConstruction.hh"

#include "G4Scene.hh"
#include "G4ThreeVector.hh"
#include "G4UImanager.hh"
#include "G4VisExtent.hh"
#include "G4VisManager.hh"
#include "G4ios.hh"

#include <algorithm>
#include <cmath>
#include <filesystem>
#include <sstream>
#include <string>
#include <vector>

namespace
{

// How big the picture is, in pixels. Square, so that a setup which is tall (the
// detectors above and below the sample) and one which is long (a source well
// back from the sample) are both framed sensibly without changing anything.
constexpr int kPictureSize = 1800;

// Height of the label lettering, in pixels, and roughly how wide one letter is
// as a fraction of that height. The width is only used to reserve room for the
// longest label, so an approximation is enough.
constexpr double kLabelHeightPixels = 20.;
constexpr double kLetterWidthFraction = 0.55;

// How far a label sits from the part it names, as a fraction of the size of the
// whole setup, so the gap looks the same whatever scale the setup is built at.
constexpr double kLabelGapFraction = 0.04;

// Widths of the drawn lines, in pixels. A line one pixel wide is almost
// invisible in a picture this large, so the beam and the scale bar are both
// drawn heavier than the default.
constexpr int kBeamWidthPixels = 6;
constexpr int kScaleBarWidthPixels = 3;

// A part of the setup, and the words that name it. The half-size is of the box
// that just contains the part, which is all that is needed to place a label
// clear of it.
struct Part
{
  std::string   label;
  G4ThreeVector centre;
  G4ThreeVector halfSize;
};

// A label, once it has been given a place: where it goes in the picture,
// measured across and up from the middle of the setup, and which side of that
// point the words run.
struct PlacedLabel
{
  std::string text;
  double      across = 0.;
  double      up     = 0.;
  double      width  = 0.;   // of the words themselves, same units as across
  bool        runsRight = true;
};

void Apply(const std::string& command)
{
  G4UImanager::GetUIpointer()->ApplyCommand(command);
}

// Half the size of the box that just contains the sample, whatever shape it was
// built as.
G4ThreeVector SampleHalfSize()
{
  const Config& config = Config::Instance();
  if (config.sample_shape == "cube") {
    const double h = 0.5 * config.sample_size;
    return {h, h, h};
  }
  if (config.sample_shape == "sphere") {
    const double h = config.sample_size;
    return {h, h, h};
  }
  return {config.sample_size, config.sample_size, 0.5 * config.sample_height};
}

// Every part of the setup that is worth naming, read straight from the
// configuration the macro built.
std::vector<Part> CollectParts()
{
  const Config& config = Config::Instance();
  std::vector<Part> parts;

  parts.push_back({"neutron source", config.source_position, {0., 0., 0.}});

  if (!config.sample_composition.empty()) {
    // The name of the sample is its heaviest ingredient, which is the one a
    // reader would call it by.
    const auto heaviest = std::max_element(
      config.sample_composition.begin(), config.sample_composition.end(),
      [](const auto& a, const auto& b) { return a.second < b.second; });
    parts.push_back({std::string(heaviest->first) + " sample",
                     config.sample_position, SampleHalfSize()});
  }

  for (const ShieldingBlock& block : config.shielding) {
    // Material names arrive as GEANT4 spells them, G4_POLYETHYLENE; the label
    // reads better as plain lower-case words.
    std::string name = block.material;
    if (name.rfind("G4_", 0) == 0) {
      name = name.substr(3);
    }
    std::transform(name.begin(), name.end(), name.begin(),
                   [](unsigned char c) { return std::tolower(c); });
    parts.push_back({name,
                     block.position,
                     {DetectorConstruction::kSlabHalfWidth,
                      DetectorConstruction::kSlabHalfWidth,
                      0.5 * block.thickness}});
  }

  for (const DetectorBlock& detector : config.detectors) {
    parts.push_back({std::string(detector.name),
                     detector.position,
                     {detector.radius, detector.radius, 0.5 * detector.height}});
  }

  return parts;
}

// How far a part reaches from its own middle in a given direction. Used to push
// a label just past the edge of the part it names.
double ReachAlong(const G4ThreeVector& halfSize, const G4ThreeVector& direction)
{
  return std::abs(halfSize.x() * direction.x())
       + std::abs(halfSize.y() * direction.y())
       + std::abs(halfSize.z() * direction.z());
}

// A round number no larger than the given length, for the scale bar, so it
// reads 5 cm rather than 4.7 cm.
double RoundedLength(double length)
{
  const double choices[] = {1., 2., 5., 10., 20., 50., 100., 200., 500., 1000.};
  double best = choices[0];
  for (double choice : choices) {
    if (choice <= length) {
      best = choice;
    }
  }
  return best;
}

std::string Vector(const G4ThreeVector& v)
{
  std::ostringstream out;
  out << v.x() << ' ' << v.y() << ' ' << v.z();
  return out.str();
}

}  // namespace

void WriteGeometryPicture()
{
  // Once per run of the program: the setup cannot change between runs of the
  // beam, so a second picture would only overwrite the first with the same
  // thing.
  static bool written = false;
  if (written) {
    return;
  }
  written = true;

  // A viewer already being open means the setup is already being shown or drawn
  // by someone else, and a second picture is not wanted. See the header.
  G4VisManager* visManager = G4VisManager::GetInstance();
  if (visManager == nullptr || visManager->GetCurrentViewer() != nullptr) {
    return;
  }

  const Config& config = Config::Instance();

  // The picture goes beside the run's output, so it travels with the results it
  // describes.
  std::filesystem::path picture =
    std::filesystem::path(config.output_file.c_str()).parent_path() / "geometry.png";
  std::error_code ignored;
  std::filesystem::create_directories(picture.parent_path(), ignored);

  // A viewer that writes straight to a file: nothing is displayed and no window
  // opens, so this works over ssh and inside scripts.
  Apply("/vis/open TSG_OFFSCREEN");
  if (visManager->GetCurrentViewer() == nullptr) {
    G4cout << "GeometryPicture: this build cannot write pictures without a "
              "display, so no picture of the setup was written." << G4endl;
    return;
  }
  Apply("/vis/tsg/offscreen/set/size " + std::to_string(kPictureSize) + " "
        + std::to_string(kPictureSize));
  Apply("/vis/tsg/offscreen/set/file " + picture.string());

  // Held off while the view is being set up, so the file is written once, by the
  // flush at the end.
  Apply("/vis/viewer/set/autoRefresh false");
  Apply("/vis/drawVolume");
  Apply("/vis/viewer/set/background white");
  Apply("/vis/viewer/set/style surface");
  Apply("/vis/viewer/set/hiddenEdge true");
  // Light from the camera, or every surface facing us is left in shadow.
  Apply("/vis/viewer/set/lightsMove with-camera");

  // --- How big the setup is ---
  // GEANT4 has already worked out the box that just contains everything visible.
  // Because the world volume is invisible, that is the sample, the detectors and
  // the shielding, not the surrounding metre of air.
  const G4VisExtent& extent = visManager->GetCurrentScene()->GetExtent();
  const double radius = extent.GetExtentRadius();
  if (radius <= 0.) {
    G4cout << "GeometryPicture: the setup is empty, so no picture was written."
           << G4endl;
    return;
  }
  G4ThreeVector boxLow(extent.GetXmin(), extent.GetYmin(), extent.GetZmin());
  G4ThreeVector boxHigh(extent.GetXmax(), extent.GetYmax(), extent.GetZmax());
  // The source is a point rather than a volume, so it is not in the box GEANT4
  // worked out. Without this it can sit outside the picture.
  for (int axis = 0; axis < 3; ++axis) {
    boxLow[axis] = std::min(boxLow[axis], config.source_position[axis]);
    boxHigh[axis] = std::max(boxHigh[axis], config.source_position[axis]);
  }
  const G4ThreeVector centre = 0.5 * (boxLow + boxHigh);

  // --- Where the camera goes ---
  // Across the beam rather than down it: looking down the beam would hide
  // everything behind the sample.
  G4ThreeVector beam = config.sample_position - config.source_position;
  if (beam.mag() < 1e-9) {
    beam = G4ThreeVector(0., 0., 1.);
  }
  beam = beam.unit();
  // Up is whichever way is world "up" without lying along the beam.
  G4ThreeVector up(0., 1., 0.);
  if (std::abs(beam.dot(up)) > 0.9) {
    up = G4ThreeVector(1., 0., 0.);
  }
  // The beam crossed with up, rather than up crossed with the beam, so that the
  // beam runs from left to right across the picture and not right to left.
  const G4ThreeVector across = beam.cross(up).unit();
  // Swung round and lifted a little, so the parts read as solid objects instead
  // of flat rectangles. The beam runs left to right.
  const double swing = 15. * M_PI / 180.;
  const double lift = 10. * M_PI / 180.;
  const G4ThreeVector viewpoint =
    (std::cos(lift) * (std::cos(swing) * across + std::sin(swing) * beam)
     + std::sin(lift) * up).unit();
  Apply("/vis/viewer/set/viewpointVector " + Vector(viewpoint));
  Apply("/vis/viewer/set/upVector " + Vector(up));

  // The two directions of the picture itself: right and up as seen on the page.
  const G4ThreeVector pageUp = (up - viewpoint * up.dot(viewpoint)).unit();
  const G4ThreeVector pageRight = pageUp.cross(viewpoint).unit();

  // Everything that has to be inside the picture, as positions on the page
  // measured from the middle of the setup. The shapes come first: the eight
  // corners of the box around them, which between them reach as far across and
  // as far up the page as the shapes do.
  std::vector<std::pair<double, double>> mustFit;
  double shapesHalfWide = 0.;
  double shapesHalfTall = 0.;
  for (int corner = 0; corner < 8; ++corner) {
    const G4ThreeVector point((corner & 1) ? boxHigh.x() : boxLow.x(),
                              (corner & 2) ? boxHigh.y() : boxLow.y(),
                              (corner & 4) ? boxHigh.z() : boxLow.z());
    const G4ThreeVector offset = point - centre;
    mustFit.emplace_back(offset.dot(pageRight), offset.dot(pageUp));
    shapesHalfWide = std::max(shapesHalfWide, std::abs(mustFit.back().first));
    shapesHalfTall = std::max(shapesHalfTall, std::abs(mustFit.back().second));
  }

  // --- Where the labels go ---
  // Each label is pushed away from the middle of the setup, just past the edge
  // of the part it names, which lands it in clear space beside that part.
  const std::vector<Part> parts = CollectParts();
  const double gap = kLabelGapFraction * 2. * radius;
  std::vector<PlacedLabel> labels;
  std::size_t longestLabel = 0;
  for (const Part& part : parts) {
    const G4ThreeVector offset = part.centre - centre;
    double outAcross = offset.dot(pageRight);
    double outUp = offset.dot(pageUp);
    if (std::hypot(outAcross, outUp) < 1e-6) {
      // A part sitting dead in the middle has no outward direction of its own.
      outAcross = 1.;
      outUp = 0.;
    }
    const double length = std::hypot(outAcross, outUp);
    outAcross /= length;
    outUp /= length;
    const G4ThreeVector outward = outAcross * pageRight + outUp * pageUp;
    const double push = ReachAlong(part.halfSize, outward) + gap;

    PlacedLabel placed;
    placed.text = part.label;
    placed.across = offset.dot(pageRight) + outAcross * push;
    placed.up = offset.dot(pageUp) + outUp * push;
    placed.runsRight = outAcross >= 0.;
    labels.push_back(placed);
    longestLabel = std::max(longestLabel, part.label.size());
  }

  // --- How much room a line of text takes up in the setup's own units ---
  // Text is drawn at a fixed size in pixels, so how much of the setup a line of
  // it covers depends on the zoom. This is the zoom the shapes on their own
  // would need, which is close enough to measure the text against; the zoom
  // actually used is worked out at the end, once everything is in place.
  const double roughZoom = std::min(radius / std::max(shapesHalfWide, 1e-9),
                                    radius / std::max(shapesHalfTall, 1e-9));
  const double millimetresPerPixel = 2. * radius / (roughZoom * kPictureSize);
  const double lineHeight = 1.4 * kLabelHeightPixels * millimetresPerPixel;
  for (PlacedLabel& label : labels) {
    label.width = kLetterWidthFraction * kLabelHeightPixels
                  * static_cast<double>(label.text.size()) * millimetresPerPixel;
  }

  // --- Nudge apart any labels that landed on top of each other ---
  // Parts in a line along the beam — the source, the moderator, the sample —
  // all push outward the same way, so their labels can coincide.
  std::sort(labels.begin(), labels.end(),
            [](const PlacedLabel& a, const PlacedLabel& b) { return a.up > b.up; });
  for (std::size_t i = 1; i < labels.size(); ++i) {
    for (std::size_t j = 0; j < i; ++j) {
      const PlacedLabel& above = labels[j];
      PlacedLabel& below = labels[i];
      const double aLeft = above.runsRight ? above.across : above.across - above.width;
      const double bLeft = below.runsRight ? below.across : below.across - below.width;
      const bool sideBySide = aLeft + above.width < bLeft || bLeft + below.width < aLeft;
      if (!sideBySide && above.up - below.up < lineHeight) {
        below.up = above.up - lineHeight;
      }
    }
  }
  for (const PlacedLabel& label : labels) {
    mustFit.emplace_back(label.across, label.up);
  }

  // --- The scale bar, below everything else ---
  double lowestUp = 0.;
  for (const auto& point : mustFit) {
    lowestUp = std::min(lowestUp, point.second);
  }
  const double barLength = RoundedLength(0.5 * radius);
  const double barUp = lowestUp - gap;
  mustFit.emplace_back(-0.5 * barLength, barUp);
  mustFit.emplace_back(0.5 * barLength, barUp);

  // --- Draw where the neutrons come from ---
  // The source is a point rather than a shape, so nothing in the picture marks
  // it and its label would point at empty space. An arrow from the source to the
  // face of the sample the neutrons arrive at shows both where they start and
  // which way they travel. Red, the colour the tracks are drawn in.
  if (!config.sample_composition.empty()
      && (config.sample_position - config.source_position).mag() > 1e-9) {
    const G4ThreeVector arrowEnd =
      config.sample_position - beam * ReachAlong(SampleHalfSize(), beam);
    Apply("/vis/set/colour red");
    Apply("/vis/set/lineWidth " + std::to_string(kBeamWidthPixels));
    Apply("/vis/scene/add/arrow " + Vector(config.source_position) + " "
          + Vector(arrowEnd) + " mm");
  }

  // --- Draw the labels and the scale bar ---
  Apply("/vis/set/textColour black");
  for (const PlacedLabel& label : labels) {
    // Words run away from the setup, so they never lie back across it.
    Apply(std::string("/vis/set/textLayout ") + (label.runsRight ? "left" : "right"));
    const G4ThreeVector at = centre + label.across * pageRight + label.up * pageUp;
    std::ostringstream command;
    command << "/vis/scene/add/text " << Vector(at) << " mm "
            << kLabelHeightPixels << " 0 0 " << label.text;
    Apply(command.str());
  }
  Apply("/vis/set/textLayout left");

  // The bar is drawn along whichever axis of the setup runs most nearly across
  // the page, since it can only be drawn along x, y or z.
  const char axisNames[] = {'x', 'y', 'z'};
  int barAxis = 0;
  for (int axis = 1; axis < 3; ++axis) {
    if (std::abs(pageRight[axis]) > std::abs(pageRight[barAxis])) {
      barAxis = axis;
    }
  }
  const G4ThreeVector barAt = centre + barUp * pageUp;
  Apply("/vis/set/lineWidth " + std::to_string(kScaleBarWidthPixels));
  std::ostringstream bar;
  bar << "/vis/scene/add/scale " << barLength << " mm " << axisNames[barAxis]
      << " 0 0 0 manual " << Vector(barAt) << " mm";
  Apply(bar.str());

  // --- Frame it, once everything that has to fit is in the picture ---
  // How far across and how far up the page the picture has to reach, and the
  // point halfway between those, which is what the camera aims at. Aiming at
  // the middle of everything rather than the middle of the shapes is what keeps
  // the margins even once the labels are added.
  double leastAcross = 0.;
  double mostAcross = 0.;
  double leastUp = 0.;
  double mostUp = 0.;
  for (const auto& point : mustFit) {
    leastAcross = std::min(leastAcross, point.first);
    mostAcross = std::max(mostAcross, point.first);
    leastUp = std::min(leastUp, point.second);
    mostUp = std::max(mostUp, point.second);
  }
  const double halfWide = 0.5 * (mostAcross - leastAcross);
  const double halfTall = 0.5 * (mostUp - leastUp);
  const G4ThreeVector aimAt = centre
                            + 0.5 * (leastAcross + mostAcross) * pageRight
                            + 0.5 * (leastUp + mostUp) * pageUp;

  // A zoom of one is GEANT4's standard view, which fits the ball that just
  // contains the scene into the picture. A ball inside a square picture wastes
  // the corners, so the zoom is worked out from how wide and how tall the
  // picture's contents actually are: the largest zoom at which both still fit,
  // so nothing can be cut off.
  //
  // The ball is measured now rather than earlier because adding the labels and
  // the scale bar grows the scene, and with it the ball the standard view fits.
  // A zoom worked out before they were added would be measured against a
  // smaller ball and would come out too far out once they were there.
  const double sceneRadius = visManager->GetCurrentScene()->GetExtent().GetExtentRadius();

  // Room for the words themselves. A label's position is the end of its text,
  // and text keeps the same size in the picture however far out the camera is,
  // so its length cannot be included in the measurements above.
  const double wordsPixels =
    kLabelHeightPixels * kLetterWidthFraction * static_cast<double>(longestLabel);
  const double linesPixels = 1.4 * kLabelHeightPixels;
  const double roomForWords =
    std::max(0.2, 1. - 2. * wordsPixels / static_cast<double>(kPictureSize));
  const double roomForLines =
    std::max(0.2, 1. - 2. * linesPixels / static_cast<double>(kPictureSize));
  double zoom = 1.;
  if (halfWide > 0. && halfTall > 0.) {
    zoom = std::min(sceneRadius / halfWide * roomForWords,
                    sceneRadius / halfTall * roomForLines)
           / 1.03;
  }
  Apply("/vis/viewer/set/targetPoint " + Vector(aimAt) + " mm");
  Apply("/vis/viewer/zoomTo " + std::to_string(zoom));

  // Draws the view and writes it to the file named above.
  Apply("/vis/viewer/flush");
  G4cout << "GeometryPicture: wrote " << picture.string() << G4endl;
}
