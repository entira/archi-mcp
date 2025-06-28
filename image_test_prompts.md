# 🧪 Testovacie prompty pre zobrazenie obrázkov v Claude Desktop

## Prehľad testov
Máme implementovaných 6 MCP nástrojov na testovanie rôznych prístupov k zobrazeniu obrázkov v Claude Desktop chat rozhraní.

## 📋 Jednotlivé testy

### Test 1: FastMCP Image Object
**Prompt na kopírovanie:**
```
Prosím použite nástroj test_image_display_approach_1 na otestovanie FastMCP Image objektu.
```

**Čo testujeme:** Priamy return FastMCP Image objektu  
**Očakávaný výsledok:** Obrázok by sa mal zobraziť inline v chate  
**Poznámka:** Toto je preferovaný prístup podľa FastMCP dokumentácie

---

### Test 2: Base64 Markdown Image
**Prompt na kopírovanie:**
```
Prosím použite nástroj test_image_display_approach_2 na otestovanie base64 encoded obrázkov v Markdown.
```

**Čo testujeme:** Base64 encoded image v Markdown formáte `![alt](data:image/png;base64,...)`  
**Očakávaný výsledok:** Obrázok by sa mal zobraziť ako inline Markdown image  
**Poznámka:** Funguje v štandardných Markdown prehliadačoch

---

### Test 3: Temporary File Path
**Prompt na kopírovanie:**
```
Prosím použite nástroj test_image_display_approach_3 na otestovanie temporary file paths.
```

**Čo testujeme:** Uloženie obrázku do `/tmp` a vrátenie file path  
**Očakávaný výsledok:** Užívateľ môže otvoriť súbor cez file path  
**Poznámka:** Požaduje manuálnu akciu používateľa

---

### Test 4: Multiple Formats
**Prompt na kopírovanie:**
```
Prosím použite nástroj test_image_display_approach_4 na otestovanie kombinovaných formátov.
```

**Čo testujeme:** Kombinácia base64 Markdown + file path + online URL  
**Očakávaný výsledok:** Aspoň jeden formát by mal fungovať  
**Poznámka:** Maximalizuje šance na úspešné zobrazenie

---

### Test 5: Text Visualization
**Prompt na kopírovanie:**
```
Prosím použite nástroj test_image_display_approach_5 na otestovanie text fallback vizualizácie.
```

**Čo testujeme:** ASCII/text reprezentácia diagramu  
**Očakávaný výsledok:** Vždy funguje, text-based vizualizácia  
**Poznámka:** Fallback riešenie pre prípad zlyhania obrázkov

---

### Test 6: Comprehensive Test
**Prompt na kopírovanie:**
```
Prosím použite nástroj test_all_image_approaches na spustenie komplexného testu všetkých prístupov.
```

**Čo testujeme:** Všetky prístupy naraz so sumárnym reportom  
**Očakávaný výsledok:** Prehľad o tom, ktoré prístupy fungujú  
**Poznámka:** Najlepší na začiatočné testovanie

---

## 🎯 Odporúčané testovanie

### Krok 1: Spustenie comprehensive testu
Začnite s komprehensívnym testom:
```
Prosím použite nástroj test_all_image_approaches na spustenie komplexného testu všetkých prístupov.
```

### Krok 2: Testovanie jednotlivých prístupov
Ak comprehensive test ukáže problémy, testujte jednotlivo:
1. Test 1 (FastMCP Image) - najprioritnejší
2. Test 2 (Base64 Markdown) - štandardný fallback
3. Test 3 (File Path) - manuálne riešenie

### Krok 3: Evaluácia výsledkov
Pre každý test si všimnite:
- ✅ **Zobrazuje sa obrázok inline v chate?**
- ⚠️ **Zobrazuje sa len text/markdown?** 
- ❌ **Chyba/žiadny výstup?**

---

## 📊 Očakávané výsledky

| Test | Prístup | Pravdepodobnosť úspechu | Poznámka |
|------|---------|-------------------------|----------|
| 1 | FastMCP Image | ⭐⭐⭐ Vysoká | Oficiálny prístup |
| 2 | Base64 Markdown | ⭐⭐ Stredná | Závisí od Markdown podpory |
| 3 | File Path | ⭐ Nízka | Manuálna akcia |
| 4 | Multiple | ⭐⭐⭐ Vysoká | Kombinácia prístupov |
| 5 | Text | ⭐⭐⭐ Vždy | Fallback riešenie |

---

## 🔧 Debugging informácie

### Ak testy zlyhávajú:
1. **Skontrolujte logs** - `tail -f ~/Library/Logs/Claude/mcp*.log`
2. **Skontrolujte /tmp súbory** - `ls -la /tmp/claude_*`
3. **Overte PlantUML** - `java -jar plantuml.jar -version`

### Úspešné indikátory:
- ✅ Obrázky sa zobrazujú priamo v Claude Desktop chate
- ✅ PNG súbory sa generujú v `/tmp` adresári  
- ✅ Žiadne chyby v MCP server logs

### Neúspešné indikátory:
- ❌ Iba text výstup namiesto obrázkov
- ❌ "Image not supported" správy
- ❌ PlantUML generation errors

---

## 📝 Reportovanie výsledkov

Po testovaní prosím zdieľajte:
1. **Ktorý test fungoval najlepšie?**
2. **Zobrazujú sa obrázky inline alebo iba text?**
3. **Akékoľvek chybové správy?**
4. **Screenshot Claude Desktop výstupu** (ak možno)

Tieto informácie pomôžu optimalizovať image display pre produkčné použitie.