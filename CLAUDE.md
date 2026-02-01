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

Execute cells sequentially - the notebook generates 3D models, processes location data, and outputs `output/WEA-boesingen.kmz`.

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

## Key Configuration (in notebook)

```python
safety_distance_meter = 50      # Minimum safety buffer in meters
safety_distance_factor = 1.0    # Multiplier for rotor diameter
safety_distance_top = 100       # Distance above turbine tip
```

## Output Viewing

Generated KMZ files require **Google Earth Pro Desktop** for 3D model rendering. Web/mobile versions don't display COLLADA models.
