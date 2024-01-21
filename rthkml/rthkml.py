import simplekml
import math

def create_kml_cylinder (cyl_center, cyl_diameter = 1000, cyl_height = 100.0, cyl_color = simplekml.Color.green, cyl_name = 'cylinder', cyl_visibility = 1):

	kml = simplekml.Kml()

	# Mittelpunkt und Radius des Kreises
	center = cyl_center
	radius_m = cyl_diameter	# in Koordinaten-Einheiten (Grad)
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
	pol = kml.newpolygon(
		name=cyl_name,
		outerboundaryis=coords,
		altitudemode=simplekml.AltitudeMode.relativetoground,
		extrude=1,
		visibility=cyl_visibility
	)

	# Farbe und Transparenz des Polygons
	pol.style.polystyle.color = simplekml.Color.changealphaint(100, cyl_color)

	# Farbe und Transparenz der Linie
	pol.style.linestyle.width = 1

	# Farbe und Transparenz der Linie
	# pol.style.linestyle.color = simplekml.Color.red
	pol.style.linestyle.color = simplekml.Color.changealphaint(200, simplekml.Color.green)

	return kml

