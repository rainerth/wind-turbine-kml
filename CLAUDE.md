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

**Eine Datei je Gemarkung**, benannt nach ihr (`Bösingen.csv`, `Epfendorf.csv`, …).
Die Zuordnung entsteht per räumlichem Join gegen `areas/gemarkungen.geojson`; nach dem
Eintragen neuer Anlagen neu sortieren mit:

```bash
python sources/locations_nach_gemarkung.py [--dry-run]
```

```csv
Name,Model,Latitude,Longitude,height,diameter,visible,Projekt
WEA-b01,vestas-v172.dae,48.251707,8.531437,199,172,1,Bösingen_Badenova
```
- `height`: Nabenhöhe in Metern
- `diameter`: Rotordurchmesser in Metern
- `Projekt`: Betreiber bzw. Vorhaben. Steuert die Einfärbung und die
  Sonderbehandlung des Testturms — **eine Gemarkung kann Anlagen mehrerer Projekte
  enthalten**, deshalb hängen Farbe und Sichtbarkeit an der Zeile, nicht an der Datei.
  Der Abgleich läuft über `project_key()` als Teilstring-Vergleich; ein exakter
  Vergleich (wie früher gegen den Ordnernamen) trifft bei `Bösingen_Badenova` nie.
- `Model`: Anlagen**typ**, nicht der Dateiname. Der konkrete Dateiname entsteht in
  Zelle 2 aus Typ + Maßen (`vestas-v172-h175-d172.dae`)

**Google Earth skaliert COLLADA-Modelle nicht.** `<Model>` wird mit `Scale 1,1,1`
platziert; `height` und `diameter` aus der CSV wirken sich nicht auf das Modell aus.
Deshalb erzeugt Zelle 2 **ein Modell je vorkommender Größe** statt eines je Anlagentyp
(derzeit 9 Modelle für 4 Typen). Turmdurchmesser skalieren mit der Höhe, Gondel- und
Blattmaße mit dem Rotordurchmesser; die rote Blattspitze bleibt bei absoluten 6 m.

Wer eine neue Anlagengröße in eine CSV einträgt, muss nichts weiter tun — das Modell
entsteht beim nächsten Lauf automatisch, verwaiste werden entfernt. Ausnahme ist der
Cesium-**ion**-Viewer: dessen `CESIUM_ASSET_IDS` in Zelle 16 sind manuell gepflegte
Upload-IDs der Basismodelle. Zelle 16 warnt, solange dort weniger IDs stehen als
Modelle existieren; KML, KMZ und die lokale CZML sind davon nicht betroffen.

### Gemarkungsgrenzen (areas/gemarkungen.geojson)

Katasterbezirke der Ebene "Gemarkung" aus dem INSPIRE-WFS **Flurstücke/Grundstücke
ALKIS** des Landesamts für Geoinformation und Landentwicklung Baden-Württemberg
(FeatureType `cp:CadastralZoning`), Open Data unter Datenlizenz Deutschland
Namensnennung 2.0.

Die Datei liegt im Repo, damit ein Notebook-Lauf ohne Netz reproduzierbar ist.
Neu holen — nur nötig, wenn sich der Abfragebereich ändert:

```bash
python sources/gemarkungen_abrufen.py
```

Das Skript fragt den WFS mit einer BBOX ab, dünnt die Stützpunkte auf 5 m aus
(Flächenabweichung unter 0,01 %) und schreibt WGS84-GeoJSON. Der Abfragebereich ist
bewusst größer als `CONFIG['area_*']`: WEA-Wi1 liegt bei 48,334 und damit nördlich
davon. Die Notebook-Zelle warnt, wenn eine Anlage in keiner geladenen Gemarkung liegt.

Welche Gemarkungen hervorgehoben werden, wird **nicht** fest eingetragen, sondern per
räumlichem Join aus `locations/*.csv` bestimmt — die Zuordnung bleibt damit richtig,
wenn Standorte dazukommen.

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

## COLLADA-Modelle sind in Google Earth grau — Farbe ist nicht erreichbar

**Nicht erneut versuchen.** Über mehrere Testreihen in Google Earth Pro wurde geprüft,
ob COLLADA-Modelle farbig darstellbar sind. Ergebnis: nein. Getestet und je einzeln
verworfen wurden

- Materialfarbe `diffuse` in vier Abstufungen bis zu vollem `(1, 0, 0)`,
- eine Bildtextur (PNG) statt der Materialfarbe, mit TEXCOORD-Quelle und Sampler,
- fünf verschiedene Normalenlängen für die farbigen Flächen (2,5 bis 0,3), um die
  Beleuchtung so weit abzusenken, dass die Farbe nicht ins Weiße geclampt wird.

Google Earth zeigt die Modelle in allen Fällen schwarz-weiß. Die Blattspitzen bleiben
deshalb weiß; die Aufteilung der Geometrie in zwei Körper mit eigenen Materialien ist
erhalten, kostet nichts und wäre die Ansatzstelle, falls sich das je ändert.

**Wo Farbe funktioniert:** in regulärer KML-Geometrie. Polygone und Linien mit
`PolyStyle`/`LineStyle` werden farbig dargestellt — die Windvorranggebiete, die gelben
Anflugkorridore, die rote Platzrunde und die roten Blattspitzen der vereinfachten
Darstellung in `WEA-boesingen-web.kmz` belegen das. Wer farbige Kennzeichnungen an den
3D-Modellen braucht, muss sie als KML-Geometrie darüberlegen, nicht ins Modell bauen.

## Normalenlänge steuert die Helligkeit

Google Earth normiert Flächennormalen nicht, sondern beleuchtet mit der übergebenen
Länge. `np.cross()` liefert Vektoren in Länge der doppelten Dreiecksfläche — im Turm
über 250, in den Dreiecken der Blattspitze unter 0,1. Daher waren die Spitzen schwarz,
während der Rest hell blieb.

`NORMAL_SCALE` in `collada_wt.py` bringt alle Normalen auf dieselbe Länge und wirkt
damit als Helligkeitsregler. Direkt verglichen: 1,0 ergibt ein flaues Dunkelgrau, ab
2,0 ist die Beleuchtung gesättigt und die Werte 2 bis 8 sehen gleich aus. Eingestellt
ist 2,5.

Die Sättigung ist auch der Grund für den harten Schwarz-Weiß-Kontrast: besonnte Flächen
laufen ins Weiße, abgewandte auf Null. Ein weicherer Verlauf ließe sich nur mit einem
Wert um 1 erreichen, der das ganze Modell grau macht — beides zusammen geht nicht.

## COLLADA-Material: was Google Earth tatsächlich auswertet

Empirisch ermittelt über Testreihen mit mehreren identischen Anlagen nebeneinander,
jede mit einem anderen Material (`output/material-testreihe.kmz`,
`output/schatten-testreihe.kmz`). Google Earth Pro verhält sich hier nicht wie ein
üblicher COLLADA-Renderer:

- **`diffuse` auf (1,1,1) lassen.** Mit 0,90 erschien das ganze Modell schwarz — nicht
  etwas dunkler, sondern schwarz. Gilt für das weiße Hauptmaterial; die rote
  Blattspitze mit (0,75, 0,08, 0,08) wird dagegen normal rot dargestellt.
- **`ambient` wirkt nicht.** Eine Variante mit ambient 0,6 sah exakt aus wie eine mit
  ambient 0. Umgebungslicht lässt sich darüber nicht anheben.
- **`double_sided` nicht setzen.** Es zeichnet auch die unbeleuchteten Rückseiten, die
  bei den dünnen Blattprofilen die Vorderseite überdecken können. Nötig ist es nicht,
  solange die Umlaufrichtung stimmt (siehe unten).
- **`specular`** stand ursprünglich auf (0,1,0), also grünem Glanz. Neutral auf 0.

Vor jeder Materialänderung eine Testreihe bauen und in Google Earth Pro ansehen —
lokale Renderings (matplotlib, trimesh) bilden dieses Verhalten nicht ab.

## COLLADA-Geometrie: Umlaufrichtung prüfen

Google Earth zeichnet nur Vorderseiten (Backface-Culling). Sind die Dreiecke eines
Körpers falsch herum umlaufen, zeigen alle Normalen nach innen und der Körper
verschwindet bis auf seine Silhouette — ein Rotorblatt wird dann zum Strich.

Jede neue Geometriefunktion in `collada_wt/` deshalb gegen das vorzeichenbehaftete
Volumen prüfen (Divergenz-Theorem). Für einen geschlossenen Körper mit
Außennormalen ist es **positiv**:

```python
def signed_volume(verts, indices):
    tri = verts[indices[:, [0, 2, 4]]]
    return np.einsum('ij,ij->i', tri[:,0], np.cross(tri[:,1], tri[:,2])).sum() / 6.0
```

`create_beam()` ist die Referenz für die richtige Umlaufrichtung; `create_lofted_body()`
folgt ihr. Ein Vergleich beider Funktionen auf demselben Zylinder muss denselben Wert
mit demselben Vorzeichen liefern.

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

Die beiden Dateien lassen sich am Turbinenmodell unterscheiden: **kastenförmige Gondel
und extrudierter Turm = Web-Version**, geschlossenes Profil mit runder Nabe =
COLLADA-Version. Wer die COLLADA-Modelle sehen will, muss `WEA-boesingen.kmz` öffnen —
in der Web-Datei sind sie nicht enthalten, die kennt nur die KML-Primitiven.

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
