from xml.etree import ElementTree as ET
import pandas as pd


def extract_first_absolute_altitude_section(kml_path):
    """
    Correctly extracts the first section of coordinates with altitudeMode set to 'absolute' from a KML file,
    maintaining the original order in the file: longitude, latitude, altitude.

    Parameters:
    - kml_path: Path to the KML file.

    Returns:
    - A pandas DataFrame with each row representing a coordinate (longitude, latitude, altitude),
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
                    # Parse coordinates string into a pandas DataFrame
                    data = []
                    for coord_str in coordinates_str.split():
                        lon, lat, alt = map(float, coord_str.split(','))
                        data.append({'Longitude': lon, 'Latitude': lat, 'Altitude': alt})
                    return pd.DataFrame(data)

        return None
    except Exception as e:
        print(f"Error processing KML file: {e}")
        return None

# Note: Uncomment the line below for testing the function
# coordinates_df_correct_order = extract_first_absolute_altitude_section_correct_order(kml_path)


# Path to the uploaded KML file
kml_path = './tracks/dhv/2019_1061396.kml'

coordinates_df = extract_first_absolute_altitude_section(kml_path).astype(float)

# remove coordinates with altitude < 720 and altitude > 1000
coordinates_df = coordinates_df[coordinates_df['Altitude'] >= 710]
coordinates_df = coordinates_df[coordinates_df['Altitude'] <= 1500]

# add a column with the mean of the last 10 altitude differences between coordinates
coordinates_df['Altitude_Diff'] = coordinates_df['Altitude'].diff()
coordinates_df['Altitude_Diff'] = coordinates_df['Altitude_Diff'].rolling(10).mean()

# find first index where Altitude_Diff < 0
release_towline = coordinates_df[coordinates_df['Altitude_Diff'] < 0].index[0]
print (
	f"Release towline at index {release_towline} with altitude {coordinates_df['Altitude'][release_towline]}"
)

# drop all rows after index 100
coordinates_df = coordinates_df.drop(coordinates_df.index[release_towline:])

# write the coordinates to a csv file
coordinates_df.to_csv(kml_path + '.csv', index=False)


# Print the first 5 rows of the DataFrame
print(coordinates_df.head(100))



