import arcpy
import qrcode
import os

# ===================== CONFIG (edit only this block) =====================
GDB = r"C:\path\your\source.gdb"                    # path to your geodatabase
FC_NAME = "Location"                                # feature class name (point, line, or polygon)
NAME_FIELD = "name"                                 # field used for the PDF filename
OUTPUT_FOLDER = r"C:\path\your\output\folder"       # folder where PDFs are saved
PICTURE_ELEMENT = "Picture"                         # name of the qr picture element in layout
MARGIN = 1.2                                        # zoom-out factor around the feature (1.0 = tight)
POINT_SCALE = 5000                                  # map scale used for single points (1:5000)
# =========================================================================

FC = os.path.join(GDB, FC_NAME)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# This is to project any type of CRS to WGS 1984 (code: 4326) on the fly
WGS84 = arcpy.SpatialReference(4326)
source_sr = arcpy.Describe(FC).spatialReference
print(f"Input CRS: {source_sr.name} -> reprojecting QR coordinates to WGS 1984")

aprx = arcpy.mp.ArcGISProject("CURRENT")
layout = aprx.listLayouts()[0]          # uses first layout
map_frame = layout.listElements("MAPFRAME_ELEMENT")[0]

# The map frame may use a different CRS than the data. This is to reproject each
map_sr = map_frame.map.spatialReference

# Find the picture element.
qr_element = None
for el in layout.listElements("PICTURE_ELEMENT"):
    if el.name == PICTURE_ELEMENT:
        qr_element = el
        break
if qr_element is None:
    found = [el.name for el in layout.listElements("PICTURE_ELEMENT")]
    raise RuntimeError(
        f"No picture element named '{PICTURE_ELEMENT}'. Found: {found}. "
        "Set PICTURE_ELEMENT to one of these names."
    )

# SHAPE gives the geometry, so this works for point, line, and polygon.
with arcpy.da.SearchCursor(FC, [NAME_FIELD, "SHAPE@"]) as cursor:
    for name, shape in cursor:
        # Centroid drives the Google Maps QR; works for any geometry type.
        # Reproject it from the data's CRS to WGS 1984 to get lon/lat.
        center_wgs = arcpy.PointGeometry(shape.centroid, source_sr).projectAs(WGS84)
        x, y = center_wgs.centroid.X, center_wgs.centroid.Y

        # Build Google Maps URL and QR code.
        # Unique filename per feature so ArcGIS doesn't reuse a cached image.
        safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in str(name))
        qr_path = os.path.join(OUTPUT_FOLDER, f"_qr_{safe_name}.png")
        qrcode.make(f"https://www.google.com/maps?q={y},{x}").save(qr_path)

        # Reproject the geometry into the map's CRS, then zoom to its extent.
        shape_map = shape.projectAs(map_sr) if map_sr.name != source_sr.name else shape
        ext = shape_map.extent
        if ext.width == 0 and ext.height == 0:
            # A single point has no extent -> center on it and use a fixed scale.
            px, py = shape_map.centroid.X, shape_map.centroid.Y
            map_frame.camera.setExtent(arcpy.Extent(px, py, px, py))
            map_frame.camera.scale = POINT_SCALE
        else:
            # Pad the extent by MARGIN so the feature isn't touching the edges.
            dx = ext.width * (MARGIN - 1) / 2
            dy = ext.height * (MARGIN - 1) / 2
            map_frame.camera.setExtent(arcpy.Extent(
                ext.XMin - dx, ext.YMin - dy, ext.XMax + dx, ext.YMax + dy
            ))

        # Swap the QR image into the layout
        qr_element.sourceImage = qr_path

        # Export to PDF
        pdf_path = os.path.join(OUTPUT_FOLDER, f"{safe_name}.pdf")
        layout.exportToPDF(pdf_path)
        print(f"Exported: {pdf_path}")

        # Remove this feature's temporary QR image
        if os.path.exists(qr_path):
            os.remove(qr_path)

print("Done.")