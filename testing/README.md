# 🧪 ArchiMate MCP Server Testing Suite

Táto zložka obsahuje kompletné testovacie materiály pre ArchiMate MCP server.

---

## 📁 Súbory

### 🔬 Testovacie Prompty
- **`COMPREHENSIVE_MCP_TEST_PROMPT.md`** - Rozsiahly test všetkých funkcionalít (30-45 minút)
- **`QUICK_TEST_PROMPT.md`** - Rýchly test základných funkcií (5 minút)

### 📋 Dokumentácia
- **`TEST_RESULTS_TEMPLATE.md`** - Šablóna pre zaznamenanie výsledkov
- **`README.md`** - Tento súbor

---

## 🚀 Ako Testovať

### 1. Príprava
```bash
# Uistite sa, že MCP server beží v Claude Desktop
# Skontrolujte config v ~/Library/Application Support/Claude/claude_desktop_config.json
```

### 2. Rýchly Test (5 min)
1. Otvorte Claude Desktop
2. Skopírujte obsah `QUICK_TEST_PROMPT.md`
3. Vložte do Claude Desktop
4. Vykonajte test

### 3. Komplexný Test (30-45 min)  
1. Otvorte Claude Desktop
2. Skopírujte postupne jednotlivé scenáre z `COMPREHENSIVE_MCP_TEST_PROMPT.md`
3. Vykonávajte test po scenároch
4. Zaznamenávajte výsledky do `TEST_RESULTS_TEMPLATE.md`

---

## 🎯 Očakávané Výsledky

### ✅ Úspešný Test
- Všetky MCP nástroje fungujú
- PlantUML kód je validný
- Slovenčina funguje správne
- Žiadne server errors

### ❌ Problémy na Riešenie
- MCP connection errors
- PlantUML syntax errors  
- Validation failures
- Performance issues

---

## 📊 Test Coverage

### Testované Funkcionality
- ✅ Základné ArchiMate elementy (všetky vrstvy)
- ✅ Všetky typy relationships
- ✅ Model validácia (standard + strict)
- ✅ Predpripravené templates
- ✅ Komplexná architektúra
- ✅ Error handling
- ✅ Slovenská lokalizácia
- ✅ Performance s veľkými modelmi
- ✅ Vrstevnatá architektúra
- ✅ Export funkcionalita

### MCP Tools Testované
1. `create_archimate_diagram`
2. `add_archimate_element`
3. `add_archimate_relationship`
4. `validate_archimate_model`
5. `generate_archimate_template`
7. `generate_full_architecture`

---

## 🔧 Troubleshooting

### MCP Server Nereaguje
```bash
# Reštart Claude Desktop
pkill -f "Claude" && sleep 3 && open -a "Claude"

# Skontroluj logy
tail -f ~/Library/Logs/Claude/mcp-server-archi-mcp.log
```

### PlantUML Syntax Errors
- Skontroluj či element types obsahují správne názvy
- Overte relationship syntax
- Pozrite si vygenerovaný kód

### Performance Issues
- Testujte s menšími modelmi
- Skontrolujte system resources
- Overte network latency

---

## 📈 Reportovanie Chýb

Ak nájdete problémy:

1. **Zaznamenajte** detaily do TEST_RESULTS_TEMPLATE.md
2. **Opíšte** kroky na reprodukciu
3. **Priložte** error logy a PlantUML kód
4. **Oznámte** problém vývojárovi

---

**Autor:** Mgr. Patrik Skovajsa, Claude Code Assistant  
**Verzia:** 1.0  
**Posledná aktualizácia:** 2025-06-27