# 🎯 ArchiMate Designer Frontend - Skutočná Business Logika

**Autor:** Claude Code Assistant
**Dátum:** 2025-11-14
**Status:** ✅ Kompletná analýza

---

## 🚨 KRITICKÝ PROBLÉM S TESTAMI

**Testy v `test_frontend_e2e.py` sú založené na úplne nesprávnej predstave o tom, čo designer.html robí!**

### ❌ Čo testy OČAKÁVAJÚ (ale NEEXISTUJE):
```python
# Testy hľadajú CRUD formular na vytváranie nových elementov:
page.fill("input[name='element-name']", "Test Business Actor")  # ❌ Neexistuje!
page.select_option("select[name='element-type']", "Business_Actor")  # ❌ Neexistuje!
page.click("button:has-text('Add Element')")  # ❌ Neexistuje!
page.click("button:has-text('Regenerate')")  # ❌ Neexistuje!
```

### ✅ Čo designer.html SKUTOČNE ROBÍ:

**Designer je VIEWER + EDITOR pre už existujúce diagramy, NIE formular na vytváranie nových elementov!**

---

## 📋 SKUTOČNÁ ARCHITEKTÚRA

### 1. **Načítanie Modelu**
```javascript
// Designer načíta existujúci diagram z exports/
async function loadCurrentModel(forceUpdate = false) {
    const jsonResponse = await fetch(`exports/${currentDiagramTimestamp}/input.json`);
    const model = await jsonResponse.json();
    // model obsahuje:
    // - elements: [{id, name, type, description}, ...]
    // - relationships: [{id, source, target, type, label}, ...]
    // - title, description, layout options
}
```

**INPUT:** Diagram vygenerovaný cez MCP tool `generate_archimate_diagram`
**OUTPUT:** Zobrazenie PNG + možnosť editácie metadát

---

### 2. **Editor Panel (Rename Panel)**

**Skutočné HTML elementy:**
```html
<!-- Diagram-level editing -->
<input id="diagram-title" type="text" />
<textarea id="diagram-description"></textarea>

<!-- Element selection dropdown -->
<select id="element-select" onchange="loadElementForEdit()">
    <option value="">-- Choose Element --</option>
    <option value="elem1">Customer (Business_Actor)</option>
    <option value="elem2">Web Portal (Application_Component)</option>
    ...
</select>

<!-- Element editing form (pre-populated po výbere) -->
<input id="element-name" type="text" value="Customer" />
<textarea id="element-description">Description...</textarea>
<span id="element-type-display">Business_Actor</span>  <!-- READONLY! -->

<!-- Relationships editing (pre vybraný element) -->
<div id="relationships-list">
    <input data-rel-id="rel1" data-field="label" placeholder="Label..." />
    <textarea data-rel-id="rel1" data-field="description">...</textarea>
</div>

<!-- Save button -->
<button id="rename-apply-btn" onclick="applyRename()">💾 Save Changes</button>
```

**WORKFLOW:**
1. Designer načíta `exports/AI/input.json` (najnovší diagram)
2. Užívateľ **vyberá existujúci element** z dropdown `#element-select`
3. Edituje `name` a `description` (NIE type!)
4. Edituje labels/descriptions pre relationships
5. Klikne **💾 Save Changes** → volá `applyRename()`
6. `applyRename()` → `POST /api/save_input` → `POST /api/regenerate`
7. Designer zobrazí aktualizovaný PNG

**Kľúčové ID selektory:**
- `#element-select` (NIE `select[name='element-type']`)
- `#element-name` (NIE `input[name='element-name']`)
- `#element-description` (NIE `textarea[name='element-description']`)
- `#element-type-display` - **READONLY span, nie select!**
- `#rename-apply-btn` - Save button (NIE "Add Element")

---

### 3. **Layout Controls**

**Skutočné HTML elementy:**
```html
<select id="direction">
    <option value="vertical">Vertical (Top to Bottom)</option>
    <option value="horizontal">Horizontal (Left to Right)</option>
</select>

<select id="spacing">
    <option value="compact">Compact</option>
    <option value="normal">Normal</option>
    <option value="relaxed">Relaxed</option>
</select>

<label><input type="checkbox" id="show-legend" /> Show Legend</label>
<label><input type="checkbox" id="enable-grouping" /> Group by Layer</label>
<label><input type="checkbox" id="show-stereotypes" /> Show Stereotypes</label>

<button id="regenerate-btn" onclick="regenerate()">🔄 Regenerate Diagram</button>
```

**WORKFLOW:**
1. Užívateľ zmení layout options (direction, spacing, checkboxy)
2. Klikne **🔄 Regenerate Diagram** → volá `regenerate()`
3. `regenerate()` → `POST /api/regenerate` s novými options
4. Designer zobrazí aktualizovaný PNG

---

### 4. **History Browser**

**Skutočné HTML elementy:**
```html
<!-- History trigger button -->
<button onclick="showHistory()" class="history-btn">📜 View Diagram History</button>

<!-- History view (skrytý overlay) -->
<div id="history-view" style="display: none;">
    <button id="close-history-btn" onclick="closeHistory()">✕</button>

    <!-- Filters -->
    <input id="history-search" placeholder="Search diagrams..." />
    <input id="history-from-date" type="date" />
    <input id="history-to-date" type="date" />
    <select id="history-layer-filter">...</select>
    <button onclick="applyHistoryFilters()">Apply Filters</button>

    <!-- Diagram cards -->
    <div id="history-list">
        <div class="history-item" data-timestamp="20241114_153000">
            <img src="exports/20241114_153000/diagram.png" />
            <button onclick="viewDiagram('20241114_153000')">👁️ View</button>
            <button onclick="deleteDiagram('20241114_153000')">🗑 Delete</button>
        </div>
        ...
    </div>

    <!-- Bulk operations -->
    <input type="checkbox" class="diagram-checkbox" data-timestamp="..." />
    <button onclick="bulkDeleteHistory()" id="bulk-delete-btn">Delete Selected</button>
</div>
```

**WORKFLOW:**
1. Klik na `.history-btn` → `showHistory()` zobrazí overlay
2. História načítaná z `GET /api/history`
3. Užívateľ môže:
   - Filtrovať (`applyHistoryFilters()`)
   - Prezerať diagram (`viewDiagram(timestamp)`)
   - Mazať diagram (`deleteDiagram(timestamp)` → `DELETE /api/history/{timestamp}`)
   - Bulk delete (checkboxy + `bulkDeleteHistory()`)
4. Zatvorenie histórie → `closeHistory()` vráti na aktuálny diagram

---

### 5. **Navigation & Zoom**

**Skutočné HTML elementy:**
```html
<!-- Navigation controls -->
<div id="nav-controls">
    <button onclick="navigatePrevDiagram()" id="nav-prev">◀</button>
    <button onclick="navigateNextDiagram()" id="nav-next">▶</button>
    <button onclick="deleteCurrentDiagram()" id="nav-delete">🗑</button>
</div>

<!-- Zoom controls -->
<div id="zoom-controls">
    <button class="zoom-btn" onclick="zoomIn()">+</button>
    <button class="zoom-btn" onclick="zoomOut()">-</button>
    <button class="zoom-btn" onclick="zoomReset()">⟲</button>
    <span id="zoom-level">100%</span>
</div>

<!-- Diagram image -->
<img id="diagram" src="exports/AI/diagram.png" />
```

**WORKFLOW:**
- Zoom: `zoomIn()`, `zoomOut()`, `zoomReset()` → CSS transform scale
- Navigation: `◀` / `▶` browsuje chronologicky cez všetky timestampy

---

### 6. **Download Operations**

**Skutočné funkcie:**
```javascript
async function exportFile(type) {
    // type: 'png', 'svg', 'puml', 'xml'
    const url = `exports/${diagramTimestamp}/diagram.${extension}`;

    // Ak súbor neexistuje, zavolá regeneráciu:
    await fetch(`${API_BASE}/regenerate_puml`, {...});  // pre .puml/.svg
    await fetch(`${API_BASE}/regenerate`, {...});       // pre .png

    // Download file
    const response = await fetch(url);
    const blob = await response.blob();
    // Trigger download...
}

async function exportAllAsZip() {
    // Stiahne všetky súbory ako ZIP
}
```

**Dostupné formáty:**
- PNG (`diagram.png`)
- SVG (`diagram.svg`)
- PlantUML (`diagram.puml`)
- ArchiMate XML (`archimate_model.archimate`)
- ZIP (všetky súbory)

---

## 🔌 BACKEND API ENDPOINTY

**Designer.html komunikuje s týmito endpointami:**

```javascript
const API_BASE = 'http://127.0.0.1:8080/api';

// Status check
GET /api/status
→ {"status": "ok", "timestamp": "..."}

// History management
GET /api/history?limit=50&offset=0&search=Banking&from=2024-01-01&to=2024-12-31&layer=Business
→ {"items": [{timestamp, title, description, element_count, ...}], "total": 123}

// Diagram operations
POST /api/regenerate
BODY: {direction: "vertical", spacing: "normal", show_legend: true, ...}
→ Regeneruje diagram s novými options

POST /api/history/{timestamp}/fork
→ Forkne historical diagram do AI/

DELETE /api/history/{timestamp}
→ Zmaže diagram z histórie

// Model editing
POST /api/save_input
BODY: {title, description, elements: [...], relationships: [...]}
→ Uloží zmeny do input.json

POST /api/regenerate_puml
BODY: {diagram_timestamp}
→ Regeneruje PlantUML kód
```

---

## ✅ AKO BY MALI VYZERAŤ SPRÁVNE TESTY

### **Test 1: Page Load & Structure**
```python
def test_designer_page_loads(page, designer_url):
    page.goto(designer_url)
    expect(page).to_have_title("ArchiMate Interactive Designer")

    # Sidebar je viditeľný
    expect(page.locator("#sidebar")).to_be_visible()

    # Diagram container je viditeľný
    expect(page.locator("#diagram-container")).to_be_visible()

    # History button existuje
    expect(page.locator(".history-btn")).to_be_visible()
```

### **Test 2: Element Editing (NIE vytváranie!)**
```python
def test_edit_existing_element(page, designer_url):
    """Test editácie existujúceho elementu v diagrame."""
    page.goto(designer_url)

    # Počkaj na načítanie modelu
    page.wait_for_selector("#element-select option[value!='']", timeout=5000)

    # Vyber prvý element z dropdownu
    page.select_option("#element-select", index=1)

    # Element form sa zobrazí
    expect(page.locator("#element-edit-form")).to_be_visible()

    # Edituj názov
    page.fill("#element-name", "Updated Element Name")
    page.fill("#element-description", "Updated description")

    # Ulož zmeny
    page.click("#rename-apply-btn")

    # Počkaj na regeneráciu (5-10s)
    page.wait_for_timeout(8000)

    # Diagram sa aktualizoval (nový timestamp v src)
    img = page.locator("#diagram")
    expect(img).to_have_attribute("src", re.compile(r"exports/.+/diagram\.png"))
```

### **Test 3: Layout Controls**
```python
def test_change_layout_direction(page, designer_url):
    """Test zmeny layout direction."""
    page.goto(designer_url)

    # Zmena direction
    page.select_option("#direction", "horizontal")

    # Regenerate
    page.click("#regenerate-btn")

    # Počkaj na regeneráciu
    page.wait_for_timeout(8000)

    # Diagram sa aktualizoval
    img = page.locator("#diagram")
    expect(img).to_have_attribute("src", re.compile(r"diagram\.png\?t=\d+"))
```

### **Test 4: History Browsing**
```python
def test_view_history(page, designer_url):
    """Test otvorenia histórie diagramov."""
    page.goto(designer_url)

    # Klik na history button
    page.click(".history-btn")

    # History view sa zobrazí
    expect(page.locator("#history-view")).to_be_visible()

    # History list sa načíta
    page.wait_for_selector(".history-item", timeout=5000)

    # Zatvor históriu
    page.click("#close-history-btn")

    # History view je skrytý
    expect(page.locator("#history-view")).not_to_be_visible()
```

### **Test 5: Download PNG**
```python
def test_download_png(page, designer_url):
    """Test stiahnutia PNG súboru."""
    page.goto(designer_url)

    # Počkaj na načítanie
    page.wait_for_load_state("networkidle")

    # Klik na download PNG button (musíme nájsť správny selector)
    with page.expect_download() as download_info:
        page.evaluate("""
            exportFile('png')
        """)

    download = download_info.value
    assert download.suggested_filename.endswith(".png")
```

### **Test 6: Zoom Controls**
```python
def test_zoom_controls(page, designer_url):
    """Test zoom in/out/reset."""
    page.goto(designer_url)

    # Zoom in
    page.click("button.zoom-btn:has-text('+')")
    zoom_level = page.locator("#zoom-level").text_content()
    assert zoom_level != "100%"  # Zoom sa zmenil

    # Reset
    page.click("button.zoom-btn:has-text('⟲')")
    expect(page.locator("#zoom-level")).to_have_text("100%")
```

---

## 🚫 ČO TESTY **NEMAJÚ** TESTOVAŤ

### ❌ Vytváranie nových elementov cez UI
**Dôvod:** Designer NEVYTVÁRA nové elementy. Nové diagramy sa vytvárajú cez MCP tools!

**Správny workflow:**
1. **Claude Desktop** → Užívateľ píše: "Create a banking architecture diagram"
2. **MCP Tool** → `generate_archimate_diagram()` vytvorí diagram
3. **Server** → Vygeneruje PlantUML → PNG → uloží do `exports/AI/`
4. **Designer.html** → Zobrazí vygenerovaný diagram + umožní editáciu metadát

### ❌ CRUD operácie pre relationships
**Dôvod:** Designer iba edituje **labels a descriptions** existujúcich relationships. Nové relationships sa vytvárajú len cez MCP tools.

### ❌ Validácia elementov
**Dôvod:** Validácia prebieha na backende pri volaní MCP tools, NIE vo frontende.

---

## 📊 SPRÁVNA TESTOVACIA STRATÉGIA

### **Unit Tests (Backend)** - `pytest tests/test_*.py`
- ✅ Validácia ArchiMate elementov
- ✅ PlantUML generácia
- ✅ XML export
- ✅ MCP protocol

### **API Tests** - `tests/test_api_endpoints.py`
- ✅ GET /api/history
- ✅ POST /api/regenerate
- ✅ POST /api/save_input
- ✅ DELETE /api/history/{timestamp}
- ✅ POST /api/history/{timestamp}/fork

### **E2E Tests (Frontend)** - `tests/test_frontend_e2e.py` (OPRAVENÉ!)
- ✅ Page load & structure
- ✅ Element editing (názov, popis)
- ✅ Relationship editing (label, popis)
- ✅ Layout controls (direction, spacing, checkboxy)
- ✅ History browsing (view, filter, delete)
- ✅ Navigation (prev/next diagram)
- ✅ Zoom controls
- ✅ Download operations (PNG, SVG, PlantUML, ZIP)

### **Integration Tests (MCP → Frontend)** - Nové!
1. Zavolať `generate_archimate_diagram()` cez MCP
2. Overiť, že designer.html zobrazí vygenerovaný diagram
3. Editovať element cez UI
4. Overiť, že zmeny sa uložili do `input.json`
5. Overiť, že regenerácia vytvorí aktualizovaný PNG

---

## 🔧 ODPORÚČANIA NA OPRAVU

### 1. **Zabiť všetky orphan servery**
```bash
lsof -ti :8080 | xargs kill -9
```

### 2. **Implementovať server lifecycle fixture**
```python
@pytest.fixture(scope="session")
def http_server():
    """Start HTTP server for E2E tests."""
    import subprocess

    server_proc = subprocess.Popen([
        "uv", "run", "python", "-c",
        "from archi_mcp.server import start_http_server; "
        "import time; start_http_server(port=8080); "
        "time.sleep(600)"
    ])

    time.sleep(3)  # Wait for server startup
    yield "http://127.0.0.1:8080"

    server_proc.terminate()
    server_proc.wait()
```

### 3. **Aktualizovať test selektory**
```python
# ❌ ZLÉR
page.fill("input[name='element-name']", "Test")
page.click("button:has-text('Add Element')")

# ✅ SPRÁVNE
page.select_option("#element-select", index=1)
page.fill("#element-name", "Test")
page.click("#rename-apply-btn")
```

### 4. **Pridať wait strategies**
```python
# Počkaj na načítanie modelu
page.wait_for_selector("#element-select option[value!='']", timeout=5000)

# Počkaj na regeneráciu (PlantUML rendering trvá 5-10s)
page.wait_for_timeout(8000)

# Počkaj na network idle
page.wait_for_load_state("networkidle")
```

### 5. **Pridať data-testid atribúty do HTML**
```html
<!-- Lepšie pre testovanie -->
<button data-testid="save-changes-btn" onclick="applyRename()">💾 Save Changes</button>
<button data-testid="regenerate-btn" onclick="regenerate()">🔄 Regenerate</button>
<select data-testid="element-selector" id="element-select">...</select>
```

---

## 📈 ĎALŠIE KROKY

1. **Prepísať `test_frontend_e2e.py`** s použitím správnych selektorov
2. **Pridať integration testy** pre MCP → Frontend workflow
3. **Zvýšiť code coverage** pridaním unit testov pre generator/validator/xml_export
4. **Dokumentovať API** v OpenAPI/Swagger formáte
5. **Pridať CI/CD pipeline** s automatickými E2E testami

---

## 🎯 ZÁVER

**Designer.html je VIEWER + METADATA EDITOR, NIE CRUD aplikácia!**

- ✅ **Načítava** diagramy z `exports/`
- ✅ **Edituje** názvy, popisy, labels existujúcich elementov/relationships
- ✅ **Mení** layout options (direction, spacing, legend, grouping)
- ✅ **Prezerá** históriu diagramov
- ✅ **Sťahuje** rôzne formáty (PNG, SVG, PlantUML, XML, ZIP)
- ❌ **NEVYTVÁRA** nové elementy/relationships cez UI

**Testy musia byť prepísané, aby odrážali túto skutočnú funkcionalitu!**
