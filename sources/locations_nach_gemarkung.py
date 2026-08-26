#!/usr/bin/env python3
"""Standort-CSVs nach Gemarkung sortieren.

Liest alle locations/*.csv, ordnet jede Anlage über einen räumlichen Join der
Gemarkung zu (areas/gemarkungen.geojson) und schreibt sie in eine CSV je
Gemarkung zurück. Die bisherige Projekt- bzw. Betreiberzugehörigkeit bleibt in
der Spalte 'Projekt' erhalten - sie steckte vorher im Dateinamen und wird für
die Einfärbung im Notebook gebraucht.

Das Skript ist wiederholbar: es liest den aktuellen Bestand ein, sortiert neu
und ersetzt die Dateien. Nach dem Eintragen neuer Anlagen also einfach erneut
aufrufen.

    python sources/locations_nach_gemarkung.py [--dry-run]
"""
import glob
import os
import sys
import warnings

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

LOCATIONS = 'locations'
GEMARKUNGEN = 'areas/gemarkungen.geojson'
COLUMNS = ['Name', 'Model', 'Latitude', 'Longitude', 'height', 'diameter',
           'visible', 'Projekt']


def load_all():
    """Alle Standort-CSVs mit ihrer Herkunft in der Spalte 'Projekt'."""
    frames = []
    for path in sorted(glob.glob(f'{LOCATIONS}/*.csv')):
        frame = pd.read_csv(path)
        if 'Projekt' not in frame.columns:
            # Herkunft steckte bisher im Dateinamen
            frame['Projekt'] = os.path.splitext(os.path.basename(path))[0]
        frames.append(frame)
    if not frames:
        raise SystemExit(f'keine CSV-Dateien in {LOCATIONS}/')
    return pd.concat(frames, ignore_index=True)


def main():
    warnings.filterwarnings('ignore')
    dry_run = '--dry-run' in sys.argv

    turbines = load_all()
    zoning = gpd.read_file(GEMARKUNGEN)

    located = gpd.GeoDataFrame(
        turbines,
        geometry=[Point(float(lon), float(lat))
                  for lon, lat in zip(turbines['Longitude'], turbines['Latitude'])],
        crs='EPSG:4326')
    joined = gpd.sjoin(located, zoning[['Gemarkung', 'geometry']],
                       how='left', predicate='within')

    missing = joined[joined['Gemarkung'].isna()]
    if len(missing):
        print(f'ABBRUCH: {len(missing)} Anlagen liegen in keiner Gemarkung:')
        for name in missing['Name']:
            print(f'  {name}')
        print('Abfragebereich in sources/gemarkungen_abrufen.py erweitern.')
        raise SystemExit(1)

    print(f'{len(joined)} Anlagen auf {joined["Gemarkung"].nunique()} Gemarkungen')

    written = {f'{LOCATIONS}/{gemarkung}.csv'
               for gemarkung in joined['Gemarkung'].unique()}

    for gemarkung, group in sorted(joined.groupby('Gemarkung')):
        target = f'{LOCATIONS}/{gemarkung}.csv'
        out = group[COLUMNS].sort_values('Name')
        print(f'  {target:44} {len(out):2} Anlagen')
        if not dry_run:
            out.to_csv(target, index=False)

    # Dateien, die nach der Neusortierung keine Entsprechung mehr haben
    obsolete = sorted(set(glob.glob(f'{LOCATIONS}/*.csv')) - written)
    for path in obsolete:
        print(f'  entfernt: {path}')
        if not dry_run:
            os.remove(path)

    if dry_run:
        print('\n--dry-run: nichts geschrieben')


if __name__ == '__main__':
    main()
