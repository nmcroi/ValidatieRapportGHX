# GHX Prijslijst Validatie Tool - IT Deployment Handbook

## 📋 Overzicht

Deze handleiding documenteert alle stappen en configuraties die nodig zijn voor het deployen van de GHX Prijslijst Validatie Tool op een productieserver. Dit package bevat de meest recente versie met alle nieuwe features.

## ⚠️ BELANGRIJK VOOR IT

**DEPLOYMENT AANPAK: VOLLEDIG VERVANGEN**
- **NIET** alleen files vervangen - dit is een complete upgrade naar versie 2.0
- **WEL** de hele `deployment_for_IT/` directory overnemen naar de server
- De mappenstructuur is volledig herzien voor server gebruik
- Alle configuratie files en modules zijn geüpdatet

**WAT IS ER VERANDERD:**
- Nieuwe modulaire architectuur 
- Server-compatibele pad configuraties
- CLI interface voor Lucy integratie
- Uitgebreide validatieregels (H-zinnen, multi-language templates)
- Verbeterde rapportage formatting

## 🆕 Nieuwe Features in deze Versie (v2.0)

- ✅ **H-zinnen validatie** met strikt H + 3 cijfers format (H300, H315, etc.)
- ✅ **Template versie detectie** voor TG, DT en AT templates  
- ✅ **Meertalige template ondersteuning** - Nederlandse én Engelse legacy templates (v24.07)
- ✅ **Template versie weergave** in validatierapporten met generatie tijden
- ✅ **Verbeterde header formatting** - links uitgelijnd met indentatie
- ✅ **Reference lists** in apart JSON bestand voor flexibiliteit
- ✅ **Configureerbare server paths** voor deployment flexibiliteit

## 📁 Package Structuur

```
deployment_for_IT/                     # HERKENBARE STRUCTUUR (zoals v1.0)
├── app/                               # Applicatie directory (zoals in v1.0)
│   └── cli_validate.py               # CLI interface (ENTRY POINT)
├── config/                            # Configuratiebestanden
│   ├── field_validation_v20.json     # Validatieregels v2.0 (met H-zinnen)
│   ├── header_mapping.json           # Kolomnaam mapping  
│   ├── reference_lists.json          # Externe referentielijsten
│   └── server_paths_template.json    # Server path configuratie template
├── validator/                         # Core validatie modules
│   ├── __init__.py
│   ├── price_tool.py                 # Hoofdvalidatie logica
│   ├── rapport_utils.py              # Rapportage (server-compatible)
│   ├── config_manager.py             # Configuratie management
│   ├── validation_engine.py          # Core validatie engine
│   └── template_context.py           # Template versie detectie
├── setup.sh                           # Setup script (zoals in v1.0)
├── requirements.txt                   # Python dependencies 
├── IT_DEPLOYMENT_HANDBOOK.md          # Deze handleiding
└── README_FOR_IT.md                   # Basis setup instructies
```

**BELANGRIJK:** Geen `static/` directory nodig - logo paths worden via server_paths.json geconfigureerd

## 🔧 KRITIEKE Server Configuratie

### 1. Server Paths Configuratie

**BELANGRIJK:** Kopieer `config/server_paths_template.json` naar `config/server_paths.json` en pas alle paths aan voor uw server:

```json
{
  "server_paths": {
    "logo_path": "/path/to/server/static/ghx_logo_2.png",
    "validation_log_file": "/path/to/server/reports/validaties_overzicht.xlsx", 
    "template_generator_files": "/path/to/server/Template_Generator_Files",
    "temp_reports_dir": "/tmp/validation_reports"
  }
}
```

### 2. Hardcoded Paths die AANGEPAST moeten worden:

| Bestand | Regel | Oude Path | Nieuwe Path (voorbeeld) |
|---------|-------|-----------|-------------------------|
| `server_paths.json` | logo_path | `/Users/ncroiset/.../static/ghx_logo_2.png` | `/var/www/ghx/static/ghx_logo_2.png` |
| `server_paths.json` | validation_log_file | `/Users/ghxnielscroiset/.../validaties_overzicht.xlsx` | `/data/ghx/reports/validaties_overzicht.xlsx` |
| `server_paths.json` | template_generator_files | `"Template Generator Files"` | `/data/ghx/Template_Generator_Files` |

### 3. Directory Permissions

Zorg dat de volgende directories beschrijfbaar zijn voor de applicatie:

```bash
# Rapport output directory
chmod 755 /path/to/server/reports/
chown www-data:www-data /path/to/server/reports/

# Temp directory voor validatie rapporten  
mkdir -p /tmp/validation_reports
chmod 755 /tmp/validation_reports
```

## 🚀 Installatie Stappen

### Stap 1: Dependencies Installeren

```bash
cd deployment_for_IT
pip install -r requirements.txt
```

### Stap 2: Server Paths Configureren

```bash
# Kopieer template naar productie config
cp config/server_paths_template.json config/server_paths.json

# Bewerk server_paths.json met uw server-specifieke paths
nano config/server_paths.json
```

### Stap 3: Logo File Plaatsen

Zorg dat het GHX logo beschikbaar is op de server:

```bash
# Voorbeeld: kopieer logo naar server locatie
cp /path/to/ghx_logo_2.png /var/www/ghx/static/ghx_logo_2.png
```

### Stap 4: Template Generator Files (indien gebruikt)

Als u Template Generator templates gebruikt, zorg dan dat de `Template Generator Files` directory beschikbaar is:

```bash
# Voorbeeld directory structuur
/data/ghx/Template_Generator_Files/
├── institution_codes.json
├── field_mapping.json  
└── templates/
```

## 💻 Gebruik

### Basic CLI Gebruik

```bash
python cli_validate.py \
    --input /path/to/prijslijst.xlsx \
    --output /path/to/reports/
```

### Met Custom Config Directory

```bash
python cli_validate.py \
    --input /path/to/prijslijst.xlsx \
    --output /path/to/reports/ \
    --config /path/to/custom/config/
```

### Lucy Integratie Voorbeeld

```bash
#!/bin/bash
# lucy_validation_script.sh

INPUT_FILE="$1"
OUTPUT_DIR="/data/ghx/reports/$(date +%Y%m%d)"
CONFIG_DIR="/opt/ghx-validation/config"

python /opt/ghx-validation/cli_validate.py \
    --input "$INPUT_FILE" \
    --output "$OUTPUT_DIR" \
    --config "$CONFIG_DIR"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "Validatie succesvol voltooid"
    echo "Rapport: $OUTPUT_DIR"
else
    echo "Validatie mislukt (exit code: $EXIT_CODE)"
fi

exit $EXIT_CODE
```

## 🔄 Exit Codes

| Code | Betekenis | Actie |
|------|-----------|-------|
| 0 | Succes | Rapport succesvol gegenereerd |
| 1 | Validatie error | Check logs voor details |
| 2 | Bestand niet gevonden | Controleer input/config paths |
| 3 | Geen rapport gegenereerd | Check schrijfrechten output directory |
| 4 | Rapport kopiëren mislukt | Check schrijfrechten target directory |

## 🧪 Testing

### Test Basic Functionality

```bash
# Test met voorbeeld bestand
python cli_validate.py \
    --input test_input.xlsx \
    --output /tmp/test_output/ \
    --config config/

echo "Exit code: $?"
ls -la /tmp/test_output/
```

### Test Server Paths Configuration

```bash
# Controleer of alle configured paths bestaan
python -c "
from validator.rapport_utils import SERVER_PATHS
import os

for key, path in SERVER_PATHS.items():
    if os.path.exists(path):
        print(f'✅ {key}: {path}')
    else:
        print(f'❌ {key}: {path} (NIET GEVONDEN)')
"
```

## 🔍 Troubleshooting

### Module Import Errors

```bash
# Voeg project root toe aan PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/opt/ghx-validation"
```

### Config File Errors

```bash
# Controleer of alle config bestanden bestaan
ls -la config/
# Verwacht: field_validation_v20.json, header_mapping.json, reference_lists.json, server_paths.json
```

### Logo/Path Issues

```bash
# Debug server paths
python -c "
from validator.rapport_utils import load_server_paths
paths = load_server_paths()
print('Loaded paths:', paths)
"
```

### Permission Issues

```bash
# Check directory permissions
ls -la /path/to/reports/
chmod 755 /path/to/reports/
chown correct_user:correct_group /path/to/reports/
```

## 📝 Logging

De applicatie logt naar de console en naar het validation log bestand (indien geconfigureerd). Voor debugging:

```bash
# Run met verbose logging
python cli_validate.py --input test.xlsx --output /tmp/ 2>&1 | tee validation.log
```

## 🔄 Updates

Bij toekomstige updates van de validatie tool:

1. Backup huidige config bestanden
2. Kopieer nieuwe validator modules
3. Merge configuratie wijzigingen
4. Test met test data
5. Deploy naar productie

## 📞 Support

Voor vragen over deze deployment:

- **Technische vragen:** Neem contact op met de ontwikkelaar
- **Server configuratie:** Raadpleeg uw systeembeheerder
- **Lucy integratie:** Check Lucy documentatie voor script integratie

---

**BELANGRIJK:** Test altijd eerst in een staging omgeving voordat je naar productie gaat!