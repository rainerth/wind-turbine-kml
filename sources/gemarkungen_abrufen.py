#!/usr/bin/env python3
"""Gemarkungsgrenzen (Katasterbezirke) für den Projektbereich neu vom LGL holen.

Quelle: INSPIRE-WFS "Flurstücke/Grundstücke ALKIS" des Landesamts für
Geoinformation und Landentwicklung Baden-Württemberg, FeatureType
cp:CadastralZoning. Open Data, Datenlizenz Deutschland Namensnennung 2.0.

Aufruf:  python sources/gemarkungen_abrufen.py
Ergebnis: areas/gemarkungen.geojson

Das Notebook liest nur die GeoJSON-Datei; dieses Skript wird lediglich
gebraucht, wenn der Projektbereich sich ändert oder die Daten veraltet sind
(die Gemarkungsgrenzen ändern sich praktisch nie).
"""
import warnings

import geopandas as gpd
import requests
from pyproj import Transformer

WFS = 'https://owsproxy.lgl-bw.de/owsproxy/wfs/WFS_INSP_BW_Flst_ALKIS'
# Etwas großzügiger als CONFIG['area_*'] im Notebook: WEA-Wi1 liegt bei 48,334
# und damit nördlich des dortigen Projektbereichs. Der Puffer stellt sicher,
# dass jede Anlage aus locations/*.csv in einer geladenen Gemarkung liegt.
AREA = dict(lon_min=8.35, lon_max=8.65, lat_min=48.05, lat_max=48.40)
SIMPLIFY_M = 5      # Stützpunkte ausdünnen; Flächenabweichung unter 0,01 %
OUTPUT = 'areas/gemarkungen.geojson'


def main():
    warnings.filterwarnings('ignore')

    to_utm = Transformer.from_crs(4326, 25832, always_xy=True)
    x1, y1 = to_utm.transform(AREA['lon_min'], AREA['lat_min'])
    x2, y2 = to_utm.transform(AREA['lon_max'], AREA['lat_max'])
    crs = 'urn:ogc:def:crs:EPSG::25832'

    response = requests.get(WFS, params={
        'SERVICE': 'WFS', 'VERSION': '2.0.0', 'REQUEST': 'GetFeature',
        'TYPENAMES': 'cp:CadastralZoning', 'SRSNAME': crs,
        'BBOX': f'{x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f},{crs}', 'COUNT': 500,
    }, timeout=180)
    response.raise_for_status()

    with open('/tmp/gemarkungen.gml', 'wb') as handle:
        handle.write(response.content)

    gdf = gpd.read_file('/tmp/gemarkungen.gml')
    gdf['geometry'] = gdf.geometry.simplify(SIMPLIFY_M)   # vor der Umprojektion: Meter
    gdf = gdf.to_crs(4326)
    gdf = (gdf[['text', 'label', 'LocalisedCharacterString', 'geometry']]
           .rename(columns={'text': 'Gemarkung', 'label': 'Schluessel',
                            'LocalisedCharacterString': 'Ebene'})
           .sort_values('Gemarkung').reset_index(drop=True))
    gdf.to_file(OUTPUT, driver='GeoJSON')
    print(f'{OUTPUT}: {len(gdf)} Gemarkungen')


if __name__ == '__main__':
    main()
