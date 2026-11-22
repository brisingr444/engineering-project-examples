[Download this editable project ZIP](synthcrew-planetary-gearbox.zip)

Extract the complete project folder before opening it. The source files are also available below.

ZIP SHA-256: `a28011e110419de014fcabeaba2a573407075485e8535513a1de0cab26e6c971`

# Meridian 05 planetary gearbox

Open **Planetary-Gearbox.FCStd** in FreeCAD 1.1 with its bundled PartDesign workbench. The assembled unit is in **Meridian 05 | Assembled**. Expand its input cartridge, output carrier, stationary parts and three planet stations to select installed components. Each installed link points to a named editable Body in **PartLibrary**. The three master involute features contain the gear definitions. The spreadsheet drives module, pressure angle, face extrusion and housing diameter. Pitch circles and backlash in the spreadsheet are layout references. After a design change recheck adjacent features and fits.

[Assembled view](Assembly.png) · [Exploded service view](Planet-service.png) · [Dimensioned section PDF](General-arrangement.pdf) · [Physical assembly STEP](Planetary-Gearbox.step)

Double-click **GeneralArrangement** for the editable A3 TechDraw sheet. Section A–A passes through the shaft axis and the first planet pin. The lower view locates the pins and the cover fasteners. The PDF is a vector print assembled from the saved BReps and TechDraw references. Its eight dimensions are checked against the native page. Keep the adjacent `scripts` folder with the model for its relative drawing resources.

The fixed 72-tooth ring and 18-tooth sun give a 5:1 reduction with the carrier turning in the same direction as the input. The three 27-tooth planets have centers at 0°, 120° and 240° on a Ø45 mm circle. The counts satisfy 72 = 18 + 2 × 27 and (72 + 18) / 3 = 30. Tooth faces span z = 0 to 12 mm. The input end is at negative z.

## Service from the input end

1. Disconnect the input coupling and mark the relative carrier, sun and ring positions. Remove the six socket screws from the front flange. Pull the cover, input bearings and sun together along the axis. Allow 60 mm of working travel.
2. Remove the three flush bridge screws. Lift the front carrier plate off the pin ends. Each planet now has an accessible clip and thrust washer.
3. Remove the clip and front washer, then slide the planet, its two bearings and inner spacer off the axle. Allow 30 mm of travel. Retain the rear washer. The housing shoulder and three radial dog points locate the ring independently of the cover. The rear carrier, axle pins and output bearings stay mounted.
4. Reverse the sequence. At the saved assembly index the sun dimple points toward station 1 (+X) and each planet dimple points radially outward. Restore the marked tooth relationships, seat the washers and clips, and check rotation after assembly.

## Measured reference geometry

| Check | Result |
|---|---:|
| Sun–planet and ring–planet center distances | 22.500 mm |
| Adjacent planet tip envelopes | 9.969 mm apart |
| Backlash at reference pitch circles, sun / ring mesh | 0.1005 / 0.0998 mm |
| Tip-to-root clearance, four directions | 0.249–0.250 mm |
| Bearing outer-seat diametral clearance, all three sizes | 0.020 mm |
| Bearing journal diametral clearance, all three sizes | 0.010 mm |
| Front pin support bore / diametral clearance | 8.020 / 0.030 mm |
| Planet face to each carrier plate | 1.000 mm |
| Sun-to-bridge radial clearance | 0.999 mm |
| Ring-to-case diametral clearance | 0.060 mm |

All 61 installed solids passed the kernel validity check. The mesh check uses solid end-face profiles sampled to a 0.00025 mm chord deflection. Nine input angles from 0° to 25° span one relative tooth pitch. The carrier advances from 0° to 5°. All 54 station/mesh comparisons returned zero section overlap. Backlash comes from rotating one planet to first flank engagement in each direction with centers fixed. The centered assembly leaves flank clearance. These are sampled unloaded geometric checks.

The housing shoulder, cover flange seats and carrier post ends are intended mating surfaces. Service tests recorded 118 named common-volume comparisons at specified axial offsets, with a maximum of 0 mm³. The planet tip envelope cleared the nearest post by 4.4 mm. STEP round-trip matched 61 solids by position, bounds and centroid with a maximum coordinate difference of 0.0013 mm. See [mesh and fit measurements](Geometry-checks.json), [service samples](Service-checks.json) and [exchange results](Exchange-checks.json).

Bearings have a single solid envelope with shield recesses and race lands. Threads and threaded collars use smooth engagement envelopes. The retaining clips show their groove and opening. Tool access outside the stated withdrawal space, fits under tolerance, loads, lubrication, seals, material strength and performance ratings are outside this geometric reference.

An unsaved editing test changed the housing diameter to 106 mm. The housing solid and its associated sheet dimension both changed to 106 mm. The delivered model retains 104 mm. [Drawing measurements](Drawing-checks.json)

FreeCAD reopened the packaged FCStd and regenerated the three master involutes and the section. All three outlines closed, all 61 installed solids were present, all eight dimensions matched the recorded values and the kernel reported zero invalid features.

