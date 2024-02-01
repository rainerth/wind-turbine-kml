from xml.etree import ElementTree as ET
import pandas as pd
import os
import re as regex

def kml_extract_altitude_section(kml_path):
	"""
	Correctly extracts the first section of coordinates with altitudeMode set to 'absolute' from a KML file,
	maintaining the original order in the file: longitude, latitude, altitude.

	Parameters:
	- kml_path: Path to the KML file.

	Returns:
	- A pandas DataFrame with each row representing a coordinate (longitude, latitude, altitude),
	  or None if no such section is found.
	"""

	tree = ET.parse(kml_path)
	root = tree.getroot()

	# Parse the KML file for the link to the original KML file on the DHV website
	# Define the namespace for atom elements
	namespaces = {'atom': 'http://www.w3.org/2005/Atom'}

	# Find the <atom:link> tag and extract the href attribute
	link = root.find('.//atom:link', namespaces=namespaces).attrib['href']

	# Use a regular expression to extract the number
	number_match = regex.search(r'https://www.dhv-xc.de/flight/(\d+)', link)

	if number_match:
		extracted_number = number_match.group(1)
	else:
		extracted_number = None

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
					# Parse coordinates string into a pandas DataFrame
					data = []
					for coord_str in coordinates_str.split():
						lon, lat, alt = map(float, coord_str.split(','))
						data.append({'Longitude': lon, 'Latitude': lat, 'Altitude': alt})
					return pd.DataFrame(data), link, extracted_number

		return None, None, None
	except Exception as e:
		print(f"Error processing KML file: {e}")
		return None, None, None


def kml_extract_launch_phase(kml_path, min_altitude=710, max_altitude=1500, min_climb_rate=0):
	"""
	Extracts the first section of coordinates with altitudeMode set to 'absolute' from a KML file,
	maintaining the original order in the file: longitude, latitude, altitude.

	Parameters:
	- kml_path: Path to the KML file.

	Returns:
	- A pandas DataFrame with each row representing a coordinate (longitude, latitude, altitude),
	  or None if no such section is found.
	"""

	rolling_mean_window = 10

	try:
		coordinates_df, link, extracted_number = kml_extract_altitude_section(kml_path)

		# remove coordinates with altitude < 720 and altitude > 1000
		coordinates_df = coordinates_df[coordinates_df['Altitude'] >= min_altitude]
		coordinates_df = coordinates_df[coordinates_df['Altitude'] <= max_altitude]

		# add a column with the mean of the last 10 altitude differences between coordinates
		coordinates_df['Altitude_Diff'] = coordinates_df['Altitude'].diff()
		coordinates_df['Altitude_Diff'] = coordinates_df['Altitude_Diff'].rolling(rolling_mean_window).mean()
		coordinates_df = coordinates_df.reset_index(drop=True)

		# find first index where Altitude_Diff < 0
		release_towline = coordinates_df[coordinates_df['Altitude_Diff'] < 0].index[0]
		print (
			f"{kml_path}: Release towline at index {release_towline} with altitude {coordinates_df['Altitude'][release_towline]}"
		)

		# check if there are enough coordinates before the release of the towline
		if release_towline-rolling_mean_window > rolling_mean_window:
			# drop all rows after index 100
			coordinates_df = coordinates_df.drop(coordinates_df.index[release_towline-rolling_mean_window:])

			# write the coordinates to a csv file
			coordinates_df.to_csv(kml_path + '.csv', index=False)

			if (0):
				# Print the first 5 rows of the DataFrame
				print(coordinates_df.head(20))
				print(coordinates_df.tail(20))

			return coordinates_df, link, extracted_number

		else:
			return None, None, None

	except Exception as e:
		print(f"Error processing KML file: {e}")
		return None, None, None

