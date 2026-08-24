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

## Google Earth Web: Strukturregeln

Google Earth **Web** ist strenger als Google Earth **Pro**. Was in Pro lädt, muss in
Web nicht laden — Pro verzeiht Spezifikationsverstöße stillschweigend.

1. **Wurzel muss `simplekml.Document` sein, nie `Folder`.** Shared Styles (`<Style id>`,
   referenziert per `<styleUrl>`) sind laut KML-Spezifikation nur unter `<Document>`
   gültig. Mit `Folder` als Wurzel meldet Web für *jedes* Element
   „verweist auf den nicht vorhandenen Stil" und rendert alles ungestylt.
2. **Styles müssen direkt unter `<Document>` liegen.** simplekml legt einen Style in den
   Folder, in dem das erste nutzende Feature entstand — auch bei Document-Wurzel.
   `save_kml()` ruft deshalb `promote_styles_to_document()` auf, das sie nach dem
   Speichern hochzieht. Neue Ausgabedateien immer über `save_kml()` schreiben.
3. **`<Model>` (COLLADA) kann Web nicht.** Dafür existiert die Web-Variante mit
   `create_kml_turbine_simple()` aus KML-Primitiven.
4. **Linien brauchen zwei verschiedene Punkte.** Entartete LineStrings setzt Web auf
   Position 0,0. `add_flight_tracks()` sortiert solche Tracks aus.
5. **Linienbreiten sind Pixel und skalieren nicht mit der Entfernung.** Bei einem
   extrudierten Zylinder zeichnet Google Earth den Umriss *jeder* Seitenfläche — ein
   24-Segment-Turm behält aus jeder Distanz 24 nebeneinanderliegende 1-px-Linien und
   wirkt aus der Ferne wie ein massiver Balken, während die Füllfläche korrekt auf
   wenige Pixel schrumpft. Für schlanke Objekte, die aus der Ferne sichtbar sind,
   deshalb `polystyle.outline = 0` und `linestyle.width = 0` setzen; nur die Füllung
   skaliert perspektivisch richtig. Wo eine Linie das einzige Darstellungsmittel ist
   (Rotorblätter), Breite auf 1 halten.

Gegenprobe nach jedem Lauf — beide Zeilen müssen `0` unauflösbare Referenzen zeigen:

```bash
python3 - <<'EOF'
from xml.etree import ElementTree as ET
NS='{http://www.opengis.net/kml/2.2}'
for p in ['output/WEA-boesingen.kml','output/WEA-boesingen-web.kml']:
    root=ET.parse(p).getroot(); doc=root.find(NS+'Document')
    ids={s.get('id') for s in list(doc) if s.tag in (NS+'Style',NS+'StyleMap')}
    refs={u.text.lstrip('#') for u in root.iter(NS+'styleUrl') if u.text}
    print(p, 'unaufloesbar:', len(refs-ids))
EOF
```

### Welche Datei wofür

| Datei | Viewer | Inhalt |
|---|---|---|
| `output/WEA-boesingen.kmz` | Google Earth **Pro Desktop** | COLLADA-3D-Modelle, alles |
| `output/WEA-boesingen.kml` | dieselbe, unverpackt | braucht `output/models/*.dae` daneben — Zelle 12 spiegelt sie dorthin |
| `output/WEA-boesingen-web.kmz` | Google Earth **Web**, iPad, sonstige Viewer | vereinfachte WEA aus KML-Primitiven, sonst identisch (Flugplatz, Flugrouten, Tracks) |

## Key Configuration (in notebook)

```python
safety_distance_meter = 50      # Minimum safety buffer in meters
safety_distance_factor = 1.0    # Multiplier for rotor diameter
safety_distance_top = 100       # Distance above turbine tip
```

## Output Viewing

**Im Zweifel die `.kmz` öffnen, nicht die `.kml`.** Die KML verweist relativ auf
`models/*.dae`; Google Earth löst das gegen das Verzeichnis der KML auf, sucht also in
`output/models/`. Fehlt der Ordner, kommt „Datei konnte nicht gelesen werden" mit dem
Pfad des Modells. Zelle 12 spiegelt die Modelle deshalb nach `output/models/`. In der
KMZ tritt das Problem nicht auf, dort liegt `doc.kml` in der Archivwurzel.


Generated KMZ files require **Google Earth Pro Desktop** for 3D model rendering. Web/mobile versions don't display COLLADA models.
