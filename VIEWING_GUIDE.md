# 📖 ArchiMate Diagram Viewing Guide

Návod na lokálne prezeranie ArchiMate diagramov z tohto projektu.

## 🎯 Rýchly štart

```bash
# Spustiť layer-by-layer validáciu (generuje všetky formáty)
cd /Users/patrik/Projects/archi-mcp
python tools/layer_by_layer_validator.py

# Výsledky budú v priečinku architecture_diagrams/
ls architecture_diagrams/
```

## 📁 Formáty súborov

Po spustení validácie nájdete tieto formáty:

### 1. PlantUML súbory (`.puml`)
**Použitie**: Editácia a úpravy
- Otvorte v PlantUML editor/plugin
- Alebo upravte v ľubovoľnom text editore

### 2. SVG súbory (`.svg`) 
**Použitie**: Vysoká kvalita, škálovateľné
- Otvorte v web prehliadači: `open architecture_diagrams/motivation.svg`
- Vector graphics editor (Inkscape, Adobe Illustrator)
- Vložte do dokumentov bez straty kvality

### 3. PNG súbory (`.png`)
**Použitie**: Univerzálna kompatibilita
- Akýkoľvek image viewer
- Prezentácie, dokumenty, web stránky
- `open architecture_diagrams/motivation.png`

## 🌐 Online prezeranie

### PlantUML Web Server
1. Choďte na https://www.plantuml.com/plantuml/uml/
2. Skopírujte obsah `.puml` súboru
3. Vložte do textového poľa
4. Diagram sa automaticky vyrenderuje

### Lokálny PlantUML server
```bash
# Spustiť lokálny PlantUML server
java -jar plantuml.jar -picoweb:8080

# Otvorte http://localhost:8080 v prehliadači
```

## 🛠️ Nástroje na prezeranie

### macOS
```bash
# SVG v prehliadači
open architecture_diagrams/motivation.svg

# PNG v Preview
open architecture_diagrams/motivation.png

# Všetky PNG súbory
open architecture_diagrams/*.png
```

### VS Code extension
1. Nainštalujte "PlantUML" extension
2. Otvorte `.puml` súbor
3. `Cmd+Shift+P` → "PlantUML: Preview Current Diagram"

### IntelliJ/WebStorm plugin
1. Nainštalujte "PlantUML Integration" plugin
2. Otvorte `.puml` súbor
3. Automatický preview panel

## 📋 Dostupné vrstvy

Po spustení validácie získate tieto ArchiMate vrstvy:

1. **`motivation`** - Stakeholders, drivers, goals, requirements
2. **`business_model_canvas`** - Business model overview  
3. **`value_stream`** - Value creation flow
4. **`strategy_capability`** - Strategic capabilities
5. **`layered_view`** - Business/Application/Technology layers
6. **`interaction_view`** - Actor and process interactions
7. **`application_structure`** - Application components detail
8. **`technology_structure`** - Infrastructure detail
9. **`implementation_roadmap`** - Phased delivery plan

## 🎨 Kvalita renderingu

- **SVG**: Najlepšia kvalita, škálovateľné bez straty
- **PNG**: Dobrá kvalita pre bežné použitie
- **PlantUML**: Zdrojový kód pre úpravy

## 🔧 Troubleshooting

### Ak PNG/SVG generovanie zlyhá
```bash
# Skontrolujte či máte Graphviz
brew install graphviz  # macOS
sudo apt install graphviz  # Ubuntu
```

### Ak validácia otvára okná
- Náš nový validator používa `-Djava.awt.headless=true`
- Beží kompletne na pozadí
- Žiadne prerušenia focus

### Ak chcete len validovať bez renderovania
```bash
java -Djava.awt.headless=true -jar plantuml.jar -checkonly file.puml
```

## 📊 Výsledok validácie

Validator vám povie:
- ✅ Ktoré vrstvy sú syntax valid
- 🎨 Ktoré sa úspešne vyrenderovali
- ❌ Kde sú problémy a prečo
- 📁 Kde sú uložené súbory

Všetky súbory nájdete v `architecture_diagrams/` priečinku!