# GHX Prijslijst Validatie Tool - Server Deployment

## 📁 Structuur

```
deployment_for_IT/
├── cli_validate.py          # Command line interface (ENTRY POINT)
├── requirements.txt         # Python dependencies (GEEN Streamlit)
├── README_FOR_IT.md        # Deze documentatie
├── config/                 # Configuratiebestanden
│   ├── field_validation_v20.json    # Nieuwe validatieregels v2.0
│   ├── reference_lists.json         # Externe referentielijsten  
│   └── header_mapping.json          # Kolomnaam mapping
└── validator/              # Core validatie modules
    ├── __init__.py
    ├── price_tool.py       # Hoofdvalidatie logica
    └── rapport_utils.py    # Rapportage functionaliteit

```

## 🚀 Installatie & Gebruik

### 1. Dependencies Installeren
```bash
pip install -r requirements.txt
```

### 2. Basic Usage
```bash
python cli_validate.py --input /path/to/prijslijst.xlsx --output /path/to/reports/
```

### 3. Met Custom Config
```bash
python cli_validate.py \
    --input /path/to/prijslijst.xlsx \
    --output /path/to/reports/ \
    --config /path/to/custom/config/
```

## 📋 Parameters

| Parameter | Required | Default | Beschrijving |
|-----------|----------|---------|--------------|
| `--input` | ✅ | - | Pad naar input Excel bestand (.xlsx) |
| `--output` | ✅ | - | Directory voor rapport output |
| `--config` | ❌ | `./config/` | Directory met configuratiebestanden |

## 🔧 Configuratie

### Vereiste Config Bestanden:
- **`field_validation_v20.json`** - Validatieregels (NIEUW v2.0 format)
- **`reference_lists.json`** - Externe referentielijsten (NIEUW)
- **`header_mapping.json`** - Kolomnaam mapping

### Server Paths
**BELANGRIJK**: Update de server-specifieke paden in `validator/rapport_utils.py`:

```python
# Regel 19 - Pas aan voor jouw server omgeving
VALIDATION_LOG_FILE = "/data/lucee/tomcat/webapps/ROOT/synqeps/webroot/upload/validatiePL_reports/validaties_overzicht.xlsx"
```

## 🔄 Exit Codes

| Code | Betekenis |
|------|-----------|
| 0 | Succes |
| 1 | Validatie error |
| 2 | Bestand niet gevonden |
| 3 | Geen rapport gegenereerd |
| 4 | Rapport kopiëren mislukt |

## ⚡ Automation Example

```bash
#!/bin/bash
# process_pricelist.sh

INPUT_FILE="$1"
OUTPUT_DIR="/reports/$(date +%Y%m%d)"
CONFIG_DIR="/config"

python cli_validate.py \
    --input "$INPUT_FILE" \
    --output "$OUTPUT_DIR" \
    --config "$CONFIG_DIR"

if [ $? -eq 0 ]; then
    echo "Validatie succesvol voltooid"
    echo "Rapport: $OUTPUT_DIR"
else
    echo "Validatie mislukt (exit code: $?)"
fi
```

## 🆕 Wijzigingen v2.0

### Nieuwe Features:
- ✅ **JSON v2.0 structuur** met `data_format` + `rules` arrays
- ✅ **Global validations** voor cross-field controles  
- ✅ **Reference lists** in apart bestand
- ✅ **Context rules** voor medische hulpmiddelen, chemicaliën, etc.

### Breaking Changes:
- ❌ **`field_validation_v18.json`** → **`field_validation_v20.json`**
- ✅ **Nieuw:** `reference_lists.json` vereist
- ✅ **Functie signature gewijzigd:** `validate_pricelist()` heeft nu `reference_json_path` parameter

## 🔍 Troubleshooting

### Module Import Errors
Als je `ModuleNotFoundError` krijgt:
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/deployment_for_IT"
```

### Config File Errors  
Controleer of alle config bestanden bestaan:
```bash
ls -la config/
# Verwacht: field_validation_v20.json, reference_lists.json, header_mapping.json
```

### Server Path Issues
Update de hardcoded paden in `validator/rapport_utils.py` voor je server omgeving.

---
**Contact:** Voor vragen over deze deployment, neem contact op met de ontwikkelaar.
