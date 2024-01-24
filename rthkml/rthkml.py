import simplekml
import math

def create_kml_cylinder (kmlfolder, cyl_center, cyl_diameter = 1000, cyl_height = 100.0, cyl_color = simplekml.Color.green, cyl_name = 'cylinder', cyl_visibility = 1):

	# Mittelpunkt und Radius des Kreises
	center = cyl_center
	radius_m = cyl_diameter/2	# in m radius
	height = cyl_height

	# Umrechnung des Radius in Grad unter Berücksichtigung der Breitengrade
	radius_deg_lat = radius_m / 1000 / 111.32
	radius_deg_lon = radius_deg_lat / math.cos(math.radians(center[1]))

	# Koordinaten des Kreises
	coords = []
	for i in range(360):
		theta = math.radians(i)
		x = center[0] + radius_deg_lon * math.cos(theta)
		y = center[1] + radius_deg_lat * math.sin(theta)
		coords.append((x, y, height))

	# Polygon
	pol = kmlfolder.newpolygon(
		name=cyl_name,
		outerboundaryis=coords,
		altitudemode=simplekml.AltitudeMode.relativetoground,
		extrude=1,
		visibility=cyl_visibility
	)

	# Farbe und Transparenz des Polygons
	pol.style.polystyle.color = simplekml.Color.changealphaint(200, cyl_color)

	# Farbe und Transparenz der Linie
	pol.style.linestyle.width = 1

	# Farbe und Transparenz der Linie
	# pol.style.linestyle.color = simplekml.Color.red
	pol.style.linestyle.color = simplekml.Color.changealphaint(100, cyl_color)

	return


def xcreate_kml_cube(kml_folder, start_lat, start_lon, start_altitude, width=1.0, length=2.0, slope=4.0, color=simplekml.Color.yellow, name="cube"):
    import math
    import simplekml

    # Setzen Sie die Höhe des Quaders
    height = 100  # in Metern

    # Berechnen Sie die Länge des Quaders basierend auf der Steigung
    length = height / math.tan(math.radians(slope))  # in Kilometern

    # Berechnen Sie die Endkoordinaten
    end_lat = start_lat + length / 111.32  # Umrechnung von Kilometern in Grad
    end_lon = start_lon + width / 2 / 111.32  # Umrechnung von Kilometern in Grad

    # Erstellen Sie die Eckpunkte für jede Seite des Quaders
    coordinates_bottom = [
        (start_lon, start_lat, start_altitude),
        (end_lon, start_lat, start_altitude),
        (end_lon, end_lat, start_altitude + height),
        (start_lon, end_lat, start_altitude + height),
    ]

    coordinates_top = [
        (start_lon, start_lat, start_altitude + height),
        (end_lon, start_lat, start_altitude + height),
        (end_lon, end_lat, start_altitude + 2 * height),
        (start_lon, end_lat, start_altitude + 2 * height),
    ]

    # Fügen Sie die Polygone zum KML-Ordner hinzu
    for coords in [coordinates_bottom, coordinates_top]:
        pol = kml_folder.newpolygon(name=name, outerboundaryis=coords, altitudemode=simplekml.AltitudeMode.absolute)
        pol.style.polystyle.color = simplekml.Color.changealphaint(100, color)

