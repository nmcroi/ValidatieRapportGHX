# IT Requirements & Specifications Document
## GHX Price Validation Tool - Server Deployment

---

## 📋 Executive Summary

Dit document bevat alle technische requirements en specificaties voor de GHX Price Validation Tool deployment op de IT server infrastructure. Gebaseerd op feedback van IT team (8 oktober 2025) en praktijkervaring met de server deployment.

---

## 🖥️ Server Environment

### Python Version
- **Versie**: Python 3.9
- **Server**: Lucee server
- **Belangrijke restrictie**: GEEN Python 3.10+ syntax gebruiken

### Compatibility Issues Gevonden
1. **Match-case statements** (Python 3.10+) → Vervangen door if-elif chains
2. **Union type hints met |** (Python 3.10+) → Gebruik typing.Union
3. **Structural pattern matching** → Niet gebruiken

---

## 📦 Deployment Structure

### Vereiste Bestanden
```
deployment_for_IT/
├── cli_validate.py          # CLI interface voor Lucy
├── validator/
│   ├── __init__.py
│   ├── price_tool.py        # Core validation logic
│   ├── rapport_utils.py    # Excel rapport generatie
│   └── field_mapping.json  # Field configuratie
├── requirements.txt         # Python dependencies
└── IT_DEPLOYMENT_HANDBOOK.md
```

### Uitgesloten Bestanden (NIET deployen)
- `*.backup` files
- `__pycache__/` directories
- `.pyc` files
- Development/test files
- Streamlit interface files

---

## 🔧 Technische Requirements

### Character Encoding
- **Requirement**: UTF-8 encoding voor alle Python files
- **Implementation**: Add `# -*- coding: utf-8 -*-` aan top van CLI files
- **Toegepast op**: cli_validate.py

### Module Dependencies
```python
# Core dependencies (requirements.txt)
pandas>=1.3.0,<2.0.0
numpy>=1.21.0,<2.0.0
xlsxwriter>=3.0.0
openpyxl>=3.0.0
python-dateutil>=2.8.0
```

### Import Structure
- Gebruik relative imports binnen validator package
- Absolute imports voor externe libraries
- GEEN circular dependencies

---

## 🔌 Lucy Integration

### CLI Interface Requirements
1. **Input**: Excel bestand pad als command line argument
2. **Output**: 
   - Validation rapport Excel bestand
   - Console output met status messages
   - Exit codes (0=success, 1=error)

### Command Format
```bash
python cli_validate.py "path/to/pricelist.xlsx"
```

### Output Naming Convention
- Input: `pricelist.xlsx`
- Output: `pricelist_validation_rapport_YYYYMMDD_HHMMSS.xlsx`

---

## ⚡ Performance Requirements

### File Size Limits
- Maximum Excel input: 100MB
- Maximum rows: 100,000
- Timeout: 5 minuten voor complete validation

### Memory Usage
- Maximum heap: 2GB
- Gebruik chunking voor grote datasets

---

## 🔐 Security Requirements

### File Access
- Read-only access voor input files
- Write permissions alleen voor output directory
- Geen externe network calls

### Data Handling
- Geen sensitive data logging
- Temporary files cleanup na processing
- Geen data persistence tussen runs

---

## 📝 Logging & Monitoring

### Log Levels
```python
# Production configuration
logging.basicConfig(
    level=logging.INFO,  # INFO voor production
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Error Handling
- Catch alle exceptions op top level
- Return meaningful error messages
- Gebruik exit codes voor status communication

---

## 🚀 Deployment Checklist

### Pre-deployment
- [ ] Test met Python 3.9 environment
- [ ] Verwijder alle Python 3.10+ syntax
- [ ] Add UTF-8 encoding headers
- [ ] Remove backup files
- [ ] Clear __pycache__ directories

### Deployment Steps
1. Copy deployment_for_IT folder naar server
2. Install dependencies: `pip install -r requirements.txt`
3. Set execute permissions: `chmod +x cli_validate.py`
4. Test met sample file

### Post-deployment
- [ ] Verify Lucy integration werkt
- [ ] Check output file generation
- [ ] Monitor eerste productie runs
- [ ] Collect performance metrics

---

## 🔄 Update Procedure

### Version Management
- Gebruik semantic versioning (MAJOR.MINOR.PATCH)
- Maintain changelog in IT_DEPLOYMENT_HANDBOOK.md
- Tag releases in version control

### Rollback Strategy
1. Keep previous version backup
2. Quick switch mogelijk via symbolic links
3. Database rollback niet nodig (stateless application)

---

## 📊 Known Issues & Workarounds

### Python 3.9 Compatibility
**Issue**: Modern Python syntax niet supported
**Workaround**: Gebruik compatibility patterns:

```python
# NIET (Python 3.10+):
def process(value: str | None):
    match value:
        case "test":
            return True

# WEL (Python 3.9):
from typing import Optional
def process(value: Optional[str]):
    if value == "test":
        return True
```

### Excel File Locking
**Issue**: Windows file locking tijdens read
**Workaround**: Copy file naar temp location eerst

---

## 📞 Support Contact

Voor technische issues:
- **Primary**: IT Team via Slack
- **Escalation**: Development team
- **Documentation**: Deze repository

---

## 🎯 Deployment Resultaten & Lucy Requirements

### Succesvol Deployment (9 oktober 2025)
**Status**: ✅ Succesvol gedeployed door Mariska (IT) - 2 uur werk  
**Aanpassingen vereist**:
1. **UTF-8 Encoding**: `# -*- coding: utf-8 -*-` toegevoegd aan `cli_validate.py`
2. **Python 3.9 Compatibility**: Union syntax aangepast:
   - `str | None` → `Optional[str]`
   - `Tuple[...] | Tuple[...]` → `Union[Tuple[...], Tuple[...]]`

### Lucy Integration Requirements
**Nieuwe requirement**: Lucy moet validatie parameters kunnen controleren

**CLI Interface Uitbreidingen**:
```bash
# Volledige validatie (standaard)
python cli_validate.py --input template.xlsx --output ./reports/

# Quick validatie (beperkt aantal rijen)  
python cli_validate.py --input template.xlsx --output ./reports/ --max-rows 5000

# Lucy configureerbaar
python cli_validate.py --input template.xlsx --output ./reports/ --max-rows ${LUCY_MAX_ROWS}
```

**Implementatie Details**:
- `--max-rows` parameter toegevoegd aan CLI interface
- Automatische total_rows detectie voor rapportage
- Lucy kan kiezen tussen quick vs volledige validatie
- Parameters worden doorgegeven aan validatie engine

## 🔄 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 8 Oct 2025 | NC | Initial document based on IT feedback |
| 1.1 | 13 Oct 2025 | NC | Added deployment results and Lucy requirements |

---

## 📌 Important Notes

1. **ALTIJD testen met Python 3.9** voordat deployment
2. **Template Generator functionaliteit** is kritiek - niet refactoren zonder volledig begrip
3. **Field visibility logic** moet intact blijven voor correcte validatie
4. **Lucy integration** via CLI is de enige supported interface voor production

---

*Dit document wordt bijgewerkt op basis van nieuwe requirements en feedback van IT.*