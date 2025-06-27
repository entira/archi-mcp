# 🧪 Komplexný Test ArchiMate MCP Servera - Enhanced Edition

**Verzia:** 2.0 Enhanced  
**Dátum:** 2025-06-27  
**Účel:** Rozsiahle testovanie všetkých funkcionalít ArchiMate MCP servera s enhanced validation a image generation v Claude Desktop

## 🚀 Nové Funkcie v Enhanced Edition

### ✅ Enhanced Validation System
- **4-stupňová validácia:** Syntax → ArchiMate → Rendering → Quality
- **Automatic element normalization:** `business-actor` → `Business_Actor`
- **Comprehensive error logging:** JSONL format s detailed context
- **PlantUML sample preservation:** Pre debugging a analysis

### 🖼️ Enhanced Image Generation
- **Local PNG files:** Automatic file generation s timestamp
- **Base64 data URLs:** Copy-paste ready pre browser viewing
- **Online preview URLs:** 3 rôzne PlantUML servery pre instant preview
- **Claude Desktop optimization:** Multiple viewing options

### 🔧 Improved Element Handling
- **Smart ID normalization:** Automatic fix of spaces, hyphens
- **Name quoting:** Proper handling of special characters
- **Slovak diacritics:** Full support pre národné znaky
- **40+ element type mappings:** Comprehensive ArchiMate coverage

---

## 📋 Testovacie Scenáre

### 1. ENHANCED ELEMENT TEST - Test automatickej normalizácie elementov

**Príkaz (test automatic normalization):**
```
Vytvorme test enhanced element normalization systému. Použij ZÁMERNE problematické formáty na otestovanie automatických opráv:

create_archimate_diagram s týmito elementmi (nech server opraví formáty):

1. Business Layer elementy (test kebab-case):
   - element_type: "business-actor", ID: "podnik-manazment", name: "Podnikový manažment"
   - element_type: "business-process", ID: "strategicke plánovanie", name: "Strategické plánovanie" 
   - element_type: "business-service", ID: "konzultacne_sluzby", name: "Konzultačné služby"

2. Application Layer elementy (test mixed formats):
   - element_type: "application-component", ID: "erp system", name: "ERP Systém"
   - element_type: "application-service", ID: "financne-reporty", name: "Finančné reporty"
   - element_type: "data-object", ID: "zakaznicke_data", name: "Zákaznícke údaje"

3. Technology Layer elementy (test system mapping):
   - element_type: "node", ID: "db-server", name: "Databázový server"
   - element_type: "system-software", ID: "oracle_db", name: "Oracle Database"
   - element_type: "technology-service", ID: "data storage", name: "Ukladanie dát"

Title: "Enhanced Element Normalization Test"
Description: "Test automatickej opravy element types a IDs"

Očakávam že server automaticky opraví všetky formáty na správne ArchiMate typy a zobrazí PNG obrázok!
```

### 2. RELATIONSHIPS - Test všetkých typov vzťahov

**Príkaz:**
```
Teraz otestujme všetky typy ArchiMate vzťahov. Použi elementy z predchádzajúceho testu a pridaj nasledovné relationships:

1. Structural relationships:
   - Composition: "erp_system" kompozuje "oracle_db"
   - Aggregation: "podnik_manazment" agreguje "strategicke_plánovanie"
   - Assignment: "podnik_manazment" je priradený k "strategicke_plánovanie"
   - Realization: "erp_system" realizuje "financne_reporty"

2. Dependency relationships:
   - Serving: "data_storage" slúži "erp_system"
   - Access: "erp_system" pristupuje k "zakaznicke_data"
   - Influence: "strategicke_plánovanie" ovplyvňuje "konzultacne_sluzby"

3. Dynamic relationships:
   - Triggering: "strategicke_plánovanie" spúšťa "financne_reporty"
   - Flow: dátový tok z "zakaznicke_data" do "financne_reporty"

4. Other relationships:
   - Association: "db_server" je asociovaný s "oracle_db"
   - Specialization: "oracle_db" je špecializáciou "data_storage"

Vyexportuj diagram s názvom "Test všetkých relationships".
```

### 3. ENHANCED VALIDATION - Test 4-stupňovej validácie

**Príkaz:**
```
Otestuj enhanced validation system:

1. Spusti validate_plantuml_syntax na aktuálnom diagrame - otestuje všetky 4 validačné kroky
2. Spusti validate_archimate_model v štandardnom móde
3. Spusti validate_archimate_model v strict móde s parametrom strict=true
4. Vykonaj export s popisom "Enhanced validation - 4-step verified ArchiMate model"

Očakávam:
- Detailné validation reporty s VERIFIED ✅ statusom
- Image quality validation results  
- Rendering test confirmations
- ArchiMate compliance check results
- Všetky validation kroky musia prejsť!
```

### 4. TEMPLATES - Test predpripravených šablón

**Príkaz:**
```
Otestujme predpripravené ArchiMate šablóny:

1. Viewpoint template:
   - Vygeneruj "layered_view" viewpoint template
   - Customizuj elementy: zmeň názov prvého elementu na "Moja organizácia"

2. Pattern template:
   - Vygeneruj "three_tier_architecture" pattern template
   - Customizuj: zmeň databázový server na "PostgreSQL Cluster"

3. Industry template:
   - Vygeneruj "banking" industry template
   - Customizuj: pridaj opis "Slovenská banka - digitálna transformácia"

Pre každú šablónu vyexportuj diagram s príslušným názvom.
```

### 5. KOMPLEXNÁ ARCHITEKTÚRA - Test generate_full_architecture

**Príkaz:**
```
Vygeneruj kompletnú podnikovú architektúru s nasledujúcimi parametrami:

system_description: "Modernizácia IT infrastruktúry slovenskej zdravotníckej organizácie s implementáciou elektronických zdravotných záznamov, telemedicíny a AI diagnostických nástrojov"

business_domain: "healthcare"

architecture_scope: "enterprise"

include_views: [
  "motivation",
  "business_model_canvas", 
  "strategy_capability",
  "layered_view",
  "application_structure",
  "technology_structure",
  "implementation_roadmap"
]

implementation_phases: 4

Očakávam kompletnú architektúru s všetkými požadovanými pohľadmi a implementačnou roadmapou.
```

### 6. EDGE CASES - Test okrajových prípadov

**Príkaz:**
```
Otestuj okrajové prípady a error handling:

1. Skús pridať element s duplicitným ID "duplicate_test"
2. Skús pridať relationship medzi neexistujúcimi elementmi
3. Skús vyexportovať prázdny diagram
4. Skús pridať element s nevalidným typom "invalid_element_type"
5. Skús pridať relationship s nevalidným typom "invalid_relationship"

Pre každý test očakávam buď úspešné vykonanie alebo zmysluplnú chybovú správu.
```

### 7. SLOVAK CONTENT - Test slovenskej lokalizácie

**Príkaz:**
```
Vytvorme slovensky lokalizovaný ArchiMate diagram:

Elementy:
1. Business Actor: "Slovenský zákazník" (ID: sk_zakaznik)
2. Business Process: "Schvaľovanie úveru" (ID: schvalovanie_uveru)
3. Business Service: "Online bankovníctvo" (ID: online_banking)
4. Application Component: "Bankový informačný systém" (ID: bis)
5. Data Object: "Údaje o úveroch" (ID: udaje_uvery)
6. Node: "Hlavný bankový server" (ID: hlavny_server)

Relationships:
- Zákazník používa online bankovníctvo (Serving)
- Online bankovníctvo realizuje schvaľovanie úveru (Realization)
- BIS pristupuje k údajom o úveroch (Access)
- Server hostuje BIS (Assignment)

Vyexportuj s názvom "Slovenské bankovníctvo - ArchiMate model" a popisom "Model procesov slovenského bankovníctva s podporou diakritiky a národných špecifík".
```

### 8. IMAGE GENERATION TEST - Test enhanced image generation

**Príkaz:**
```
Otestuj všetky nové image generation funkcie:

1. generate_diagram_image:
   - Vytvor PNG súbor s title "ArchiMate Image Test"
   - output_path: "/tmp/archimate_test.png"
   - format: "png"

2. get_diagram_as_base64:
   - Vygeneruj base64 encoded image
   - format: "png" 
   - Title: "Base64 Test Diagram"

3. validate_plantuml_syntax:
   - Spusti syntax validation s title "Syntax Validation Test"
   - Očakávam comprehensive validation report

4. get_plantuml_online_url:
   - Vygeneruj online preview URLs
   - format: "svg"
   - Title: "Online Preview Test"

Očakávam:
- Local PNG file creation s file size info
- Base64 data URL pre copy-paste do browser
- 3 online preview URLs (Official, Alternative, GitHub servers)
- Comprehensive validation report s image generation test
- Všetky 4 image tools musia fungovať!
```

### 9. LAYERED ARCHITECTURE - Test vrstevnatej architektúry

**Príkaz:**
```
Vytvorme kompletný príklad vrstevnatej architektúry pre e-commerce systém:

MOTIVATION Layer:
- Stakeholder: "E-commerce manažér" (ID: ecom_manager)
- Driver: "Zvýšenie online predaja" (ID: increase_sales)
- Goal: "20% nárast tržieb" (ID: revenue_goal)

BUSINESS Layer:
- Business Actor: "Online zákazník" (ID: online_customer)
- Business Process: "Spracovanie objednávky" (ID: order_processing)
- Business Service: "Online nákup" (ID: online_shopping)

APPLICATION Layer:
- Application Component: "E-commerce platforma" (ID: ecom_platform)
- Application Service: "Platobná brána" (ID: payment_gateway)
- Data Object: "Produktový katalóg" (ID: product_catalog)

TECHNOLOGY Layer:
- Node: "Web server cluster" (ID: web_cluster)
- System Software: "Kubernetes" (ID: k8s)
- Technology Service: "Load balancing" (ID: load_balancer)

IMPLEMENTATION Layer:
- Work Package: "Migrácia na cloud" (ID: cloud_migration)
- Plateau: "Aktuálny stav" (ID: current_state)
- Plateau: "Cieľový stav" (ID: target_state)

Pridaj logické relationships medzi vrstvami a vyexportuj s grupovaním podľa vrstiev.
```

### 10. FINAL INTEGRATION TEST - Finálny integračný test

**Príkaz:**
```
Vykonaj finálny integračný test kombinujúci všetky funkcionality:

1. Vymaž existujúci diagram (clear)
2. Vygeneruj banking industry template
3. Pridaj 5 custom elementov s vlastnými properties
4. Pridaj 8 relationships rôznych typov
5. Vykonaj strict validáciu
6. Vyexportuj do súboru "/tmp/final_test.puml"
7. Vytvor druhý diagram s pattern template "microservices"
8. Pridaj slovenské názvy elementov
9. Vykonaj export s clear_after_export=true
10. Vygeneruj full architecture pre "fintech" domenu s 6 implementačnými fázami

Očakávam úspešné vykonanie všetkých krokov s detailnými výstupmi.
```

---

## 🎯 Očakávané Výsledky

### ✅ Úspešné testy by mali obsahovať:
- **VERIFIED ✅ status** v každom diagrame
- **Automatic element normalization** (kebab-case → proper ArchiMate)
- **Multiple image formats:** Local PNG + Base64 URL + Online previews
- **Enhanced validation reports:** 4-step validation s detailed results
- **Slovak diacritics preservation:** Správna podpora národných znakov
- **Comprehensive error logging:** JSONL logs v /logs/validation_errors.jsonl
- **Image generation success:** PNG files, data URLs, online preview URLs

### ❌ Problémy, ktoré treba hlásiť:
- **Missing VERIFIED ✅ status** v diagram outputs
- **Failed element normalization** (nesprávne ArchiMate typy)
- **Image generation failures** (no PNG, no base64, no online URLs)
- **Validation step failures** (syntax, ArchiMate, render, quality)
- **Server crashes** alebo timeouts
- **Slovak encoding issues** (corrupted diacritics)
- **Missing error logs** (no validation_errors.jsonl entries)

---

## 📊 Reporting

Po dokončení enhanced testov zdokumentuj:

1. **Úspešnosť testov:** Koľko z 10 enhanced scenárov prešlo úspešne
2. **Validation performance:** Čas pre 4-step validation process
3. **Image generation success:** Koľko image formats bolo úspešne vygenerovaných
4. **Element normalization:** Koľko problematických elementov bolo automaticky opravených
5. **Error logging:** Koľko validation errors bolo zalogovaných v JSONL
6. **Slovak diacritics:** Complete preservation test results
7. **Enhanced features:** PNG files, base64 URLs, online previews working?

### 📈 Enhanced Metrics
- **Total VERIFIED ✅ confirmations:** _____/10 tests
- **Image files generated:** _____/4 formats per test
- **Element normalizations:** _____/30 problematic elements fixed
- **Validation logs created:** _____/10 JSONL entries
- **Online preview URLs:** _____/3 servers working

---

**Autor:** Mgr. Patrik Skovajsa, Claude Code Assistant  
**Test verzia:** Comprehensive MCP Test v2.0 Enhanced Edition