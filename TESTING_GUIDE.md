# 🧪 Claude Desktop Configuration Testing Guide

## ✅ Implementované Možnosti

### **Layout Nastavenia**
| Environment Variable | Možné Hodnoty | Default | Popis |
|---------------------|---------------|---------|-------|
| `ARCHI_MCP_DEFAULT_DIRECTION` | `horizontal`, `vertical`, `layered` | `horizontal` | Smer diagramu |
| `ARCHI_MCP_DEFAULT_SHOW_LEGEND` | `true`, `false` | `true` | Zobrazenie legendy |
| `ARCHI_MCP_DEFAULT_SHOW_TITLE` | `true`, `false` | `true` | Zobrazenie titulu |
| `ARCHI_MCP_DEFAULT_GROUP_BY_LAYER` | `true`, `false` | `false` | Zoskupenie elementov podľa vrstvy |
| `ARCHI_MCP_DEFAULT_SPACING` | `compact`, `normal`, `wide` | `normal` | Rozostup elementov |

### **Jazykové Nastavenia**
| Environment Variable | Možné Hodnoty | Default | Popis |
|---------------------|---------------|---------|-------|
| `ARCHI_MCP_DEFAULT_LANGUAGE` | `en`, `sk` | `en` | Predvolený jazyk |
| `ARCHI_MCP_AUTO_DETECT_LANGUAGE` | `true`, `false` | `true` | Automatická detekcia jazyka |

### **Ostatné Nastavenia**
| Environment Variable | Možné Hodnoty | Default | Popis |
|---------------------|---------------|---------|-------|
| `ARCHI_MCP_LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` | Úroveň logovania |
| `ARCHI_MCP_STRICT_VALIDATION` | `true`, `false` | `true` | Prísna validácia |

## 📁 Dostupné Konfiguračné Profily

### **1. Kompaktný Slovenský** (`profile_compact_slovak.json`)
```json
{
  "env": {
    "ARCHI_MCP_DEFAULT_DIRECTION": "vertical",
    "ARCHI_MCP_DEFAULT_GROUP_BY_LAYER": "true",
    "ARCHI_MCP_DEFAULT_SPACING": "compact",
    "ARCHI_MCP_DEFAULT_LANGUAGE": "sk"
  }
}
```
**Efekt:** Vertikálny, zoskupený, kompaktný, slovenský jazyk

### **2. Horizontálny Bez Legendy** (`profile_horizontal_no_legend.json`)
```json
{
  "env": {
    "ARCHI_MCP_DEFAULT_DIRECTION": "horizontal",
    "ARCHI_MCP_DEFAULT_SHOW_LEGEND": "false",
    "ARCHI_MCP_DEFAULT_SPACING": "wide",
    "ARCHI_MCP_AUTO_DETECT_LANGUAGE": "false"
  }
}
```
**Efekt:** Horizontálny, bez legendy, široký rozostup, len angličtina

### **3. Vrstvený Zoskupený** (`profile_layered_grouped.json`)
```json
{
  "env": {
    "ARCHI_MCP_DEFAULT_DIRECTION": "layered",
    "ARCHI_MCP_DEFAULT_GROUP_BY_LAYER": "true",
    "ARCHI_MCP_LOG_LEVEL": "DEBUG"
  }
}
```
**Efekt:** Vrstvené rozloženie, zoskupené, debug režim

### **4. Debug Minimálny** (`profile_debug_minimal.json`)
```json
{
  "env": {
    "ARCHI_MCP_LOG_LEVEL": "DEBUG",
    "ARCHI_MCP_STRICT_VALIDATION": "false",
    "ARCHI_MCP_DEFAULT_SHOW_LEGEND": "false",
    "ARCHI_MCP_DEFAULT_SHOW_TITLE": "false",
    "ARCHI_MCP_AUTO_DETECT_LANGUAGE": "false"
  }
}
```
**Efekt:** Debug režim, minimálny výstup, bez validácie

## 🔄 Postup Testovania

### **Krok 1: Zálohuj Aktuálnu Konfiguráciu**
```bash
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json ~/claude_config_backup.json
```

### **Krok 2: Zvolte Profil na Testovanie**
```bash
# Príklad: Test compact Slovak profilu
cp /Users/patrik/Projects/archi-mcp/config_profiles/profile_compact_slovak.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### **Krok 3: Reštartuj Claude Desktop**
- Ukončite Claude Desktop úplne
- Spustite znovu

### **Krok 4: Testuj Diagram**
Použite tento test obsah:
```
Vytvor ArchiMate diagram s týmito prvkami:
- Podnikový zákazník (Business Actor)
- AI služba (Business Service) 
- Databáza (Technology Node)

Prepoj ich relationship typu Serving a Assignment.
```

### **Krok 5: Pozoruj Zmeny**
- **Compact Slovak:** Vertikálny, slovenské labels, zoskupené
- **No Legend:** Horizontálny, žiadna legenda
- **Layered:** Špeciálne vrstvené rozloženie
- **Debug:** Podrobné logy v generation.log

## 🎯 Očakávané Výsledky

### **Direction Testing**
- `horizontal`: Elementy zlava doprava
- `vertical`: Elementy zhora nadol  
- `layered`: Špeciálne ArchiMate vrstvené rozloženie

### **Group By Layer Testing**
- `true`: Elementy v package skupinách podľa vrstvy
- `false`: Všetky elementy voľne

### **Spacing Testing**
- `compact`: Malé rozostupy medzi elementmi
- `normal`: Štandardné rozostupy
- `wide`: Veľké rozostupy

### **Legend Testing**
- `true`: Legenda vpravo s názvami vrstiev
- `false`: Žiadna legenda

### **Language Testing**
- Auto detect: Slovenský obsah → slovenské labels
- Fixed SK: Vždy slovenčina
- Fixed EN + no auto: Vždy angličtina

## 🐛 Troubleshooting

### **Konfigurácia sa nenahrala**
1. Skontroluj JSON syntax (žiadne čiarky na konci)
2. Restartni Claude Desktop úplne
3. Skontroluj logs v generation.log

### **Environment variables sa nepoužívajú**
1. Skontroluj že cesta k projektu je správna
2. Skontroluj že `uv` je dostupné  
3. Pozri debug výstup s `ARCHI_MCP_LOG_LEVEL: "DEBUG"`

### **Zmeny nie sú viditeľné**
1. Niektoré zmeny sa prejavia len pri `group_by_layer: true`
2. `direction: layered` funguje len s viacerými vrstvami
3. Legenda sa nezobrazí ak je len jedna vrstva

## 🔄 Návrat na Pôvodnú Konfiguráciu
```bash
cp ~/claude_config_backup.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
```