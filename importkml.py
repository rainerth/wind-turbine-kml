from xml.etree import ElementTree as ET

def extract_first_absolute_altitude_section(kml_path):
	"""
	Extracts the first section of coordinates with altitudeMode set to 'absolute' from a KML file.

	Parameters:
	- kml_path: Path to the KML file.

	Returns:
	- A list of tuples, each representing a coordinate (latitude, longitude, altitude),
	  or None if no such section is found.
	"""
	try:
		# Parse the KML file
		tree = ET.parse(kml_path)
		root = tree.getroot()

		# Define namespaces to search for specific tags accurately
		namespaces = {'kml': 'http://www.opengis.net/kml/2.2'}

		# Find all Placemark elements
		for placemark in root.findall('.//kml:Placemark', namespaces):
			# Check if this Placemark has an altitudeMode of 'absolute'
			if placemark.find('.//kml:altitudeMode', namespaces) is not None:
				altitude_mode = placemark.find('.//kml:altitudeMode', namespaces).text
				if altitude_mode == 'absolute':
					# Extract the coordinates string
					coordinates_str = placemark.find('.//kml:coordinates', namespaces).text.strip()
					# Parse coordinates string into a list of tuples
					coordinates_list = []
					for coord_str in coordinates_str.split():
						lat, lon, alt = map(float, coord_str.split(','))
						coordinates_list.append((lat, lon, alt))
					return coordinates_list

		return None
	except Exception as e:
		print(f"Error processing KML file: {e}")
		return None

# Path to the uploaded KML file
kml_path = './tracks/dhv/2019_1061396.kml'

# Note: Uncomment the line below for testing the function
coordinates = extract_first_absolute_altitude_section(kml_path)

if coordinates is not None:
	print(f"First section of coordinates with altitudeMode set to 'absolute':\n{coordinates}")
else:
	print("No such section found.")

# 