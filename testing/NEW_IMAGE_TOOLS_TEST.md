# 🖼️ Nové Nástroje pre Zobrazenie Diagramov - Test

**Pridané 4 nové MCP nástroje pre prácu s obrázkami!**

---

## 🔧 Nové MCP Tools

### 1. `generate_diagram_image`
**Automatické generovanie PNG/SVG súborov**
```
generate_diagram_image(
    title="Môj Diagram",
    description="Popis diagramu",
    output_path="/Desktop/diagram.png",
    format="png"  # alebo "svg"
)
```
- ✅ Automaticky vygeneruje obrázok cez PlantUML jar
- ✅ Uloží do špecifikovaného súboru
- ✅ Podporuje PNG, SVG, PDF formáty

### 2. `get_diagram_as_base64`
**Base64 enkódovaný obrázok**
```
get_diagram_as_base64(
    title="Môj Diagram",
    format="png"
)
```
- ✅ Vráti diagram ako base64 string
- ✅ Možno skopírovať do prehliadača
- ✅ Data URL formát: `data:image/png;base64,...`

### 3. `validate_plantuml_syntax`
**Validácia a testovanie renderovateľnosti**
```
validate_plantuml_syntax(
    title="Test Diagram"
)
```
- ✅ Kontroluje PlantUML syntax
- ✅ Testuje či sa dá vygenerovať obrázok
- ✅ Detailný report s chybami

### 4. `get_plantuml_online_url`
**Online preview URLs**
```
get_plantuml_online_url(
    title="Môj Diagram",
    format="svg"  # alebo "png"
)
```
- ✅ Generuje URL pre PlantUML online servery
- ✅ 3 rôzne servery (Official, Alternative, GitHub)
- ✅ Okamžité zobrazenie v prehliadači

---

## 🧪 Testovací Prompt

```
Otestuj všetky nové nástroje pre zobrazenie diagramov:

1. Vytvor jednoduchý ArchiMate diagram s 3 elementmi
2. Použi validate_plantuml_syntax na kontrolu
3. Vygeneruj PNG obrázok s generate_diagram_image
4. Získaj base64 verziu s get_diagram_as_base64
5. Vygeneruj online preview URLs s get_plantuml_online_url

Očakávam funkčné výstupy pre všetky nástroje!
```

---

## 🎯 Výhody

### ✅ Okamžité Zobrazenie
- **Online URLs** - copy & paste do prehliadača
- **Base64 Data URLs** - paste priamo do address baru
- **Automatické súbory** - otvor lokálne

### ✅ Plná Kontrola
- **Syntax validácia** pred generovaním
- **Error handling** s detailnými správami
- **Rôzne formáty** (PNG, SVG, PDF)

### ✅ Flexibilita
- **Lokálne súbory** pre archivovanie
- **Online preview** pre quick check
- **Base64** pre embedding

---

**🚀 Teraz môžete vidieť ArchiMate diagramy priamo v Claude Desktop!**