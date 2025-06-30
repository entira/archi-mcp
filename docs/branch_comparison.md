# Porovnanie zmien medzi branch refactor a refactor2

## Súhrn zmien
- **5 súborov zmenených**
- **214 pridaných riadkov**
- **12 odstránených riadkov**

## Detailné zmeny po súboroch

### 1. `src/archi_mcp/archimate/elements/base.py` (+36 riadkov)
**Kľúčové zmeny:**
- Rozšírené mapovanie elementov pre všetky ArchiMate vrstvy
- Pridané prefix mapping pre:
  - **Motivation layer**: Value, Goal, Outcome, Principle, Requirement, Constraint, Driver, Assessment, Stakeholder, Meaning
  - **Strategy layer**: Resource, Capability, CourseOfAction, ValueStream  
  - **Implementation layer**: WorkPackage, Deliverable, ImplementationEvent, Plateau, Gap
  - **Business layer**: Actor, Role, Collaboration, Interface, Process, Event, Service, Object, Contract, Representation
  - **Application layer**: Component, Collaboration, Interface, Process, Event, Service, DataObject
  - **Technology layer**: Node, Device, SystemSoftware, Interface, Process, Event, Service, Artifact, CommunicationNetwork, Path

**Význam:** Zabezpečuje správne PlantUML syntax pre všetky ArchiMate elementy (napr. `Motivation_Goal`, `Strategy_Resource`)

### 2. `src/archi_mcp/archimate/generator.py` (+24 riadkov)
**Kľúčové zmeny:**
- Pridané **slovenské názvy vrstiev**:
  ```python
  LAYER_SLOVAK_NAMES = {
      "Business": "Podniková",
      "Application": "Aplikačná", 
      "Technology": "Technologická",
      "Physical": "Fyzická",
      "Motivation": "Motivačná",
      "Strategy": "Strategická",
      "Implementation": "Implementačná"
  }
  ```
- Upravené generovanie packages: `"Business Layer"` → `"Podniková vrstva"`
- Upravená legenda na slovenčinu: `"Legend"` → `"Legenda"`

**Význam:** Lokalizácia diagramov do slovenčiny

### 3. `src/archi_mcp/archimate/relationships.py` (+31 riadkov)
**Kľúčové zmeny:**
- Pridaná metóda `_get_slovak_label()` pre slovenské popisky vzťahov
- Mapovanie anglických vzťahov na slovenské:
  ```python
  slovak_labels = {
      "Realization": "Realizácia",
      "Serving": "Poskytovanie služby", 
      "Composition": "Kompozícia",
      "Association": "Asociácia",
      "Access": "Prístup",
      "Aggregation": "Agregácia",
      "Assignment": "Priraďovanie", 
      "Flow": "Tok",
      "Influence": "Vplyv",
      "Specialization": "Špecializácia",
      "Triggering": "Spúšťanie"
  }
  ```

**Význam:** Automatické slovenské popisky pre vzťahy v diagramoch

### 4. `src/archi_mcp/server.py` (+129 riadkov)
**Kľúčové zmeny:**
- **Rozsiahle slovenské mapovanie vzťahov** (obojsmerné):
  - Slovenčina → Angličtina (s variantmi bez diakritiky)
  - Angličtina → Slovenčina pre zobrazenie
- **ASCII konverzia** pre PlantUML kompatibilitu:
  ```python
  def _convert_to_ascii_safe(plantuml_code: str) -> str:
      # Konverzia diakritiky: á→a, č→c, ď→d, é→e, atď.
      # Konverzia cyriliky: а→a, б→b, в→v, atď.
      # Španielske znaky: ñ→n
      # Poľské znaky: ą→a, ć→c, ę→e, ł→l
      # Nemecké znaky: ß→ss
  ```
- **Oprava multiline stringov** v PlantUML
- **Normalizácia ID** s pomlčkami: `equipos-desarrollo` → `equipos_desarrollo`
- Vylepšené PNG generovanie s debug logovaním

**Význam:** 
- Plná podpora slovenčiny v diagramoch
- Podpora medzinárodných znakov (ruština, španielčina, poľština)
- Riešenie PlantUML UTF-8 problémov

### 5. `tests/test_generator.py` (+6 riadkov)
**Kľúčové zmeny:**
- Upravené testy pre slovenské názvy:
  - `"Business Layer"` → `"Podniková vrstva"`
  - `"Application Layer"` → `"Aplikačná vrstva"`

**Význam:** Testy reflektujú slovenské názvy vrstiev

## Dôležité funkcionality v refactor2

### 1. **Kompletná slovenská lokalizácia**
- Názvy vrstiev v slovenčine
- Názvy vzťahov v slovenčine
- Obojsmerné mapovanie (vstup/výstup)

### 2. **Medzinárodná podpora**
- ASCII konverzia pre všetky diakritické znaky
- Podpora cyriliky (ruština)
- Španielske, poľské, nemecké znaky

### 3. **PlantUML kompatibilita**
- Oprava multiline stringov
- Normalizácia ID s pomlčkami
- Rozšírené element type prefixing

### 4. **Robustné spracovanie vstupov**
- Case-insensitive mapovanie
- Varianty bez diakritiky
- Automatická normalizácia

## Odporúčanie
Tieto zmeny sú **veľmi užitočné** pre:
1. Slovenskú lokalizáciu projektu
2. Medzinárodnú použiteľnosť
3. Riešenie PlantUML UTF-8 problémov
4. Robustnejšie spracovanie vstupov

**Možno by bolo dobré** zachovať aspoň:
- ASCII konverziu pre PlantUML kompatibilitu
- Rozšírené element type mapping
- Normalizáciu ID s pomlčkami