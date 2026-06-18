# QR Map PDF Exporter

An ArcGIS Pro Python script that generates one PDF map sheet per feature in a feature class. For each feature, the script creates a QR code linking to the feature's location on Google Maps, drops that QR code into the current layout, zooms the map to the feature, and exports the result as a PDF.

Works with **point, line, and polygon** feature classes.

## What it does

For every feature in the chosen feature class, the script:

1. Calculates the feature's centroid and reprojects it to WGS 1984 (lon/lat).
2. Builds a Google Maps URL for that location and turns it into a QR code image.
3. Inserts the QR code into a picture element in the layout.
4. Zooms the map frame to the feature's extent (with a margin), or to a fixed scale for single points.
5. Exports the layout to a PDF named after the feature.
6. Deletes the temporary QR image so the next feature gets a fresh one.

## Requirements

* **ArcGIS Pro** (the script uses `arcpy` and must run inside an open project).
* The **`qrcode`** Python library, installed into the ArcGIS Pro Python environment.
* An ArcGIS Pro **project with a layout** that contains:

  * a **map frame**, and
  * a **picture element** to hold the QR code (named `Picture` by default).

### Installing the qrcode library

Open the **Python Command Prompt** that comes with ArcGIS Pro (Start menu → ArcGIS → Python Command Prompt) and run:

```
pip install "qrcode\[pil]"
```

The `\[pil]` part installs Pillow, which `qrcode` needs to save the QR code as a PNG image.

## Configuration

All settings live in the `CONFIG` block at the top of the script. Edit only this block:

|Setting|Description|
|-|-|
|`GDB`|Full path to the geodatabase containing your data.|
|`FC\_NAME`|Name of the feature class to process (point, line, or polygon).|
|`NAME\_FIELD`|Field whose value is used to name each exported PDF.|
|`OUTPUT\_FOLDER`|Folder where the PDFs are saved (created automatically if missing).|
|`PICTURE\_ELEMENT`|Name of the picture element in the layout that holds the QR code.|
|`MARGIN`|Zoom-out factor around each feature. `1.0` is a tight fit; `1.2` adds 20% padding.|
|`POINT\_SCALE`|Map scale used for single points, e.g. `5000` means 1:5000.|

## How to run

1. Open your project in **ArcGIS Pro** and make sure the layout with the map frame and picture element is set up.
2. Edit the `CONFIG` block in the script to match your data and paths.
3. Open the **Python window** in ArcGIS Pro (Analysis tab → Python), then run the script there — or add it as a script tool.

> The script targets the \*\*currently open project\*\* (`"CURRENT"`) and uses the \*\*first layout\*\* in that project. It must be run from inside ArcGIS Pro, not as a standalone Python file.

## Output

One PDF per feature is written to `OUTPUT\_FOLDER`, named using the `NAME\_FIELD` value (for example, a feature named "Station 4" produces `Station 4.pdf`). Characters that aren't safe for filenames are replaced with underscores.

## Notes and tips

* **Coordinate systems are handled automatically.** The QR coordinates are always reprojected to WGS 1984, and the geometry is reprojected into the map frame's coordinate system before zooming, so your data can be in any CRS.
* **Single points** have no extent, so the script centers on them and uses the fixed `POINT\_SCALE` instead.
* If you see an error about a missing picture element, the script will list the picture element names it found in the layout — set `PICTURE\_ELEMENT` to one of those.
* Temporary QR images are removed after each export, so the output folder stays clean.

## Troubleshooting

|Problem|Likely cause / fix|
|-|-|
|`No picture element named 'Picture'`|The layout has no picture element with that name. Use one of the names listed in the error message.|
|`ModuleNotFoundError: qrcode`|The `qrcode` library isn't installed in the ArcGIS Pro Python environment. See *Installing the qrcode library* above.|
|QR codes all look the same / cached|Make sure you're running the unmodified script — it writes a uniquely named QR image per feature to avoid caching.|
|Script does nothing / errors on `"CURRENT"`|The script must be run from inside an open ArcGIS Pro project, not as a standalone file.|



