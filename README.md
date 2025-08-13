# Windpark Bösingen - 3D Visualisierung und Flugsicherheitsanalyse

Dieses Projekt erstellt 3D-Windturbinen-Modelle für Google Earth und analysiert deren Auswirkungen auf die Flugsicherheit am Flugplatz Bösingen.

## Projektbeschreibung

Das Tool generiert KML/KMZ-Dateien mit:
- 3D-Windturbinen-Modellen verschiedener Typen
- Sicherheitszonen und Abstandsanalysen
- Windvorranggebieten
- Flugkorridoren und Platzrunden
- Flugtracks aus IGC/KML-Dateien

## Hauptfunktionen

### 🌪️ Windturbinen-Modellierung
- **Vestas V172**: 199m Höhe, 172m Rotordurchmesser (Bösingen)
- **Enercon E66**: 95m Höhe, 66m Rotordurchmesser (Dunningen)
- **Enercon E160**: 166m Höhe, 160m Rotordurchmesser (Herrenzimmern)
- **Testturm**: 246m Höhe, 24.8m Durchmesser

### 🛩️ Flugsicherheitsanalyse
- Sicherheitsabstände nach DHV/NfL-Richtlinien
- Abflug- und Anflugkorridore
- Endanflugbereich-Visualisierung
- Schutzzone um Flugplatz (2km Radius)

### 📍 Windpark-Standorte
- **Badenova**: Geplante WEA-Standorte
- **iTerra**: Alternative Standorte
- **Dunningen**: Bestehende Anlagen
- **Herrenzimmern**: Alterric-Projekt

## Installation und Setup

### Python Umgebung
```bash
conda activate py311
# oder
source ~/conda/envs/py311/bin/activate
```

### Abhängigkeiten
```bash
pip install simplekml pycollada pandas numpy pyarrow
```

## Projektstruktur

```
├── wea-boesingen.ipynb          # Haupt-Notebook
├── collada_wt/                  # 3D-Modell-Generator
│   ├── collada_wt.py           # Windturbinen-Geometrie
│   └── __init__.py
├── kml2track/                   # Track-Analyse-Tools
│   ├── kml2track.py            # KML-Track-Extraktion
│   ├── igc2track.py            # IGC-Track-Verarbeitung
│   └── __init__.py
├── locations/                   # Windpark-Koordinaten
│   ├── badenova.csv
│   ├── iterra.csv
│   ├── dunningen.csv
│   ├── herrenzimmern.csv
│   └── testturm.csv
├── models/                      # Generierte 3D-Modelle
│   ├── vestas-v172.dae
│   ├── enercon-e-66.dae
│   ├── enercon-e-160.dae
│   └── testturm.dae
├── tracks/                      # Flugtrack-Daten
│   ├── igc/                    # IGC-Dateien
│   └── kml/                    # KML-Tracks
├── areas/                       # Flugbereiche
│   └── platzrunde.csv          # Platzrunden-Koordinaten
└── output/                      # Generierte KML/KMZ
    ├── WEA-boesingen.kml
    └── WEA-boesingen.kmz
```

## Verwendung

### 1. Notebook ausführen
```bash
jupyter notebook wea-boesingen.ipynb
```

### 2. Zellen der Reihe nach ausführen:
1. **Setup**: Bibliotheken laden, Konfiguration
2. **Geometrie**: `create_kml_cylinder` Funktion
3. **3D-Modelle**: Windturbinen generieren (DAE-Dateien)
4. **KML-Erstellung**: Standorte verarbeiten, Turbinen platzieren
5. **Flugplatz**: Landebahn, Schutzzone, Endanflugbereich
6. **Windvorranggebiete**: Planungsgebiete visualisieren
7. **Flugrouten**: Abflug-/Anflugkorridore
8. **Tracks**: IGC/KML-Flugdaten integrieren
9. **Export**: KML speichern, KMZ erstellen

### 3. Google Earth öffnen
- Datei → Öffnen → `output/WEA-boesingen.kmz`
- 3D-Modelle sind nur in Google Earth Pro Desktop sichtbar

## Datenformat der CSV-Dateien

### Windturbinen-Standorte (locations/*.csv)
```csv
Name,Model,Latitude,Longitude,height,diameter
WEA01,vestas-v172.dae,48.237694,8.524661,199,172
```

### Platzrunde (areas/platzrunde.csv)
```csv
Latitude,Longitude,Altitude
48.227697,8.534621,700
```

## Sicherheitsparameter

```python
safety_distance_meter = 50          # Mindestabstand in Metern
safety_distance_factor = 1.0        # Faktor × Rotordurchmesser
safety_distance_top = 100           # Abstand zur Turbinenspitze
```

## Rechtliche Grundlagen

- **DHV-Richtlinien**: Mindestabstand 600m zu Fluggeländen
- **NfL 92/13**: 400m Gegenanflug, 850m sonstige Bereiche
- **Baden-Württemberg**: 700m Abstand zu Wohn-/Mischgebieten

## Windvorranggebiete

Das Projekt visualisiert die aktuellen Planungsgebiete:
1. **Windvorranggebiet 1-4**: Regionale Planungsflächen
2. **Schutzabstände**: Nach aktueller Rechtslage
3. **Flugkorridore**: Basierend auf realen Flugdaten

## Ausgabe

### KML-Struktur
```
Windpark Bösingen/
├── Badenova/
│   ├── Modell/           # 3D-DAE-Modelle
│   ├── Umfang/           # Turbinen-Zylinder
│   ├── Sicherheitsabstand/
│   └── Standorte/        # Marker
├── iTerra/
├── Flugplatz/
│   ├── Landebahn
│   ├── Schutzzone
│   └── Endanflugbereich
├── Windvorranggebiete/
├── Flugrouten/
└── Tracks.IGC/
```

## Technische Details

### 3D-Modellierung
- **COLLADA**: Standard für 3D-Austauschformat
- **Parametrisch**: Turm, Gondel, Rotorblätter konfigurierbar
- **Realitätsnah**: Proportionen basierend auf Herstellerdaten

### Koordinatensystem
- **WGS84**: Standard GPS-Koordinaten
- **Höhenreferenz**: Meter über Meeresspiegel
- **Genauigkeit**: Sub-Meter für kritische Sicherheitszonen

### Performance
- **Batch-Verarbeitung**: Alle Standorte automatisch
- **Optimiert**: Für große Track-Datasets
- **Skalierbar**: Erweiterbar für weitere Windparks

## Erweiterungsmöglichkeiten

- **Weitere Turbinentypen**: Zusätzliche Hersteller-Modelle
- **Wetterintegration**: Wind-/Sichtbedingungen
- **Lärmanalyse**: Schallausbreitung visualisieren
- **Zeitreihen**: Historische Flugbewegungen
- **Automatisierung**: CI/CD für regelmäßige Updates

## Lizenz

Siehe LICENSE-Datei für Details.

## Kontakt

Projekt im Rahmen der Flugsicherheitsanalyse für den Flugplatz Bösingen.

