# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project generates 3D wind turbine visualizations for Google Earth Pro and analyzes flight safety impacts around the Bösingen airfield. It produces KML/KMZ files containing 3D COLLADA models of wind turbines, safety zones, flight corridors, and flight tracks.

## Development Environment

```bash
# Activate Python 3.11 conda environment
conda activate py311

# Install dependencies
pip install simplekml pycollada pandas numpy pyarrow ipykernel
```

## Running the Project

The main workflow is in the Jupyter notebook:
```bash
jupyter notebook wea-boesingen.ipynb
```

Execute cells sequentially - the notebook generates 3D models, processes location data, and outputs `output/WEA-boesingen.kmz` (Pro, mit COLLADA) und `output/WEA-boesingen-web.kmz`.

## Architecture

### Core Modules

- **collada_wt/** - Parametric 3D wind turbine generator using pycollada. Creates COLLADA (.dae) files with tower, nacelle, and rotor geometry. Key function: `create_turbine()` in `collada_wt.py`

- **kml2track/** - Flight track extraction from KML and IGC files
  - `kml2track.py` - Extracts coordinates from KML files (DHV-XC flight logs)
  - `igc2track.py` - Parses IGC flight recorder format, calculates flight metrics (haversine distance, climb rates)

### Data Flow

1. Wind turbine specs from `locations/*.csv` files
2. `collada_wt` generates 3D models to `models/*.dae`
3. Notebook assembles everything via `simplekml` into KML structure
4. Output saved as `output/WEA-boesingen.kml` and `.kmz`

## Data Formats

### Wind Turbine Locations (locations/*.csv)
```csv
Name,Model,Latitude,Longitude,height,diameter,visible
WEA01,vestas-v172.dae,48.237694,8.524661,199,172,1
```
- `height`: Hub height in meters
- `diameter`: Rotor diameter in meters
- `Model`: Reference to 3D model file in `models/`

### Turbine Types Modeled
- Vestas V172: 199m height, 172m diameter
- Enercon E66: 95m height, 66m diameter
- Enercon E160: 166m height, 160m diameter
- Testturm: 246m height

## Höhenregel für Google Earth (verbindlich)

Google Earths Geländemodell stimmt **nicht** mit echtem MSL überein. Absolute Höhen
treffen deshalb auf ein Gelände, das anders liegt als angenommen — die Geometrie
schwebt sichtbar über dem Boden, auch wenn der MSL-Wert der Quelle korrekt ist.
Dieselbe Erkenntnis steht in `~/prj/thermikdash/tools/incident_kml.py`
("GE-Terrain != echtes MSL sonst") und im Vorfall-KMZ 2026-08-08, das durchgängig
`relativeToGround` verwendet.

1. **Alles mit `relativeToGround` zeichnen**, Höhen in Metern über Grund.
   `absolute` nur mit belegtem Grund — in diesem Projekt derzeit nirgends.
2. **Bodenreferenz aus den Daten nehmen, nicht als Konstante annehmen.**
   Startpunkt am Boden = erster Fix der Trackdatei, erster Punkt der Platzrunden-CSV.
   Jeder Logger hat einen eigenen Offset (GPS-Ellipsoid vs. Geoid, Baro-Kalibrierung);
   für denselben Startplatz Bösingen wurden 692–697 m gemessen.
3. **Echte Bodenflächen** (Landebahn, Schutzzonen, Vorranggebiete) mit
   `clampToGround` und **immer** `tessellate=1`.
4. **Lange Kanten unterteilen.** Bei `relativeToGround` folgt die Geometrie dem
   Gelände nur an den Stützpunkten; dazwischen liegen Geraden. Vor dem Zeichnen
   durch `densify_path()` bzw. `terrain_grid_cells()` schicken, sonst überspannt
   eine Kante die nächste Senke.

Gegenprobe nach jedem Lauf:

```bash
grep -o "<altitudeMode>[^<]*" output/WEA-boesingen.kml | sort | uniq -c
```

Erwartung: nur `relativeToGround` und `clampToGround`, kein `absolute`.

## Key Configuration (in notebook)

```python
safety_distance_meter = 50      # Minimum safety buffer in meters
safety_distance_factor = 1.0    # Multiplier for rotor diameter
safety_distance_top = 100       # Distance above turbine tip
```

## Output Viewing

Generated KMZ files require **Google Earth Pro Desktop** for 3D model rendering. Web/mobile versions don't display COLLADA models.
