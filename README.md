# GHX Price Validation Tool - Clean Architecture v2.0

Een geavanceerd prijslijst validatiesysteem gebouwd met **clean architecture** principes en intelligente template detectie.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Clean Architecture](https://img.shields.io/badge/architecture-clean-green.svg)](docs/ARCHITECTURE.md)

## 🏗️ Clean Architecture

**Template-Aware Processing:**
- **TG→N→O Decision Tree**: Intelligente template detectie
- **Modular Validator Package**: Clean separation of concerns
- **Configuration-Driven**: JSON-based flexible rules
- **Institution-Specific Logic**: NFU hospitals, research institutes

**Modern Development:**
- **Clean Code**: SOLID principles, dependency injection
- **Comprehensive Documentation**: Complete API reference
- **Extensive Testing**: Archived development scripts
- **Performance Optimized**: Lazy loading, efficient processing

## 🚀 Starten van de applicatie

### Development Mode (Streamlit)

1. **Activeer de virtuele omgeving**:
   ```bash
   source venv/bin/activate
   ```

2. **Start de Streamlit app**:
   ```bash
   streamlit run prijslijst_validatie_app.py
   ```

3. **Gebruik de applicatie** in je browser (opent automatisch)

### Production Mode (CLI)

Zie `deployment_for_IT/README_FOR_IT.md` voor server deployment instructies.

## ✨ Functies

- **Template-aware validatie**: Detecteert verschillende Excel template types
- **Multiline header support**: Ondersteunt complexe Excel headers
- **Cross-field validatie**: Controleert logische samenhang tussen velden
- **UOM conflict detection**: Identificeert eenheden-gerelateerde fouten
- **Excel error suppression**: Onderdrukt groene driehoekjes in output
- **Categorized error reporting**: Onderscheidt Afkeuringen, Aanpassingen, en Vlaggen
- **Database corrections**: Voorspellende suggesties voor veel voorkomende fouten

## 📂 Clean Architecture Structure

```
📁 Project PrijsValGem_WS app/
├── 🌐 prijslijst_validatie_app.py          # Streamlit web interface
├── 🏗️ validator/ - Clean Architecture Package:
│   ├── template_detector.py               # TG→N→O decision tree
│   ├── validation_engine.py               # Core validation pipeline
│   ├── config_manager.py                  # Configuration management
│   ├── data_processor.py                  # Data cleaning & header mapping
│   ├── mandatory_fields.py                # Smart mandatory field detection
│   ├── field_logic.py                     # Conditional visibility & logic
│   ├── template_context.py                # TG metadata parsing
│   ├── debug_tools.py                     # Development utilities
│   ├── utils.py                           # Helper functions
│   └── price_tool.py                      # Legacy compatibility
├── 📚 docs/ - Comprehensive Documentation:
│   ├── ARCHITECTURE.md                    # System design overview
│   ├── TEMPLATE_DETECTION.md              # TG→N→O decision tree
│   ├── VALIDATION_PIPELINE.md             # Processing workflow
│   ├── CONFIGURATION.md                   # Config management
│   └── API_REFERENCE.md                   # Complete API docs
├── 🗄️ archive/ - Development History:
│   ├── development_scripts/               # Debug & test scripts
│   └── README.md                          # Archive documentation
├── ⚙️ Configuration Files:
│   ├── field_validation_v20.json          # Core validation rules
│   ├── header_mapping.json                # Legacy header mapping
│   ├── reference_lists.json               # Value validation lists
│   └── Template Generator Files/          # TG synchronization
└── 🚀 deployment_for_IT/ - Server deployment
```

## 📖 Comprehensive Documentation

Volledige documentatie beschikbaar in de `docs/` directory:

- **[🏗️ Architecture](docs/ARCHITECTURE.md)** - Systeem ontwerp en clean architecture principes
- **[🌳 Template Detection](docs/TEMPLATE_DETECTION.md)** - TG→N→O beslissings boom logica  
- **[🔄 Validation Pipeline](docs/VALIDATION_PIPELINE.md)** - Complete processing workflow
- **[⚙️ Configuration](docs/CONFIGURATION.md)** - Configuratie management systeem
- **[📚 API Reference](docs/API_REFERENCE.md)** - Volledige API documentatie

## Git Workflow

### Wijzigingen bijhouden op GitHub

Volg deze stappen om wijzigingen naar GitHub te pushen:

1. **Open Terminal** (via Spotlight: cmd+spatie, typ 'Terminal')

2. **Navigeer naar de projectmap**:
   ```bash
   cd "/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project PrijsValGem_WS app"
   ```

3. **Controleer welke bestanden gewijzigd zijn**:
   ```bash
   git status
   ```

4. **Voeg gewijzigde bestanden toe aan staging**:
   ```bash
   git add .
   ```
   (of specifieke bestanden: `git add validator/price_tool.py validator/rapport_utils.py`)

5. **Commit met beschrijvende boodschap**:
   ```bash
   git commit -m "Duidelijke beschrijving van wijzigingen"
   ```

6. **Push wijzigingen naar GitHub**:
   ```bash
   git push origin main
   ```

### Opmerkingen

- Geef duidelijke commit messages die beschrijven WAT er is gewijzigd en WAAROM
- Voeg de versie toe in de commit message voor belangrijke releases, bijv.: `"Fix: rapportgeneratie verbeterd (versie6525-15.46)"`
- Test altijd wijzigingen voordat je ze commit

## 📋 Versiegeschiedenis

### v2.0 (September 2025)
- ✅ **JSON v20 architectuur**: Volledig nieuwe validatie configuratie structuur
- ✅ **Template-aware validatie**: Dynamische verplichte velden per template type
- ✅ **Excel error suppression**: Groene driehoekjes worden onderdrukt
- ✅ **UOM conflict detection**: Specifieke validaties voor eenheden-conflicten
- ✅ **Categorized error reporting**: Afkeuringen/Aanpassingen/Vlaggen onderscheid
- ✅ **Database corrections sheet**: Voorspellende correctie suggesties
- ✅ **Dual architecture**: Streamlit + CLI ready for server deployment

### Legacy Versies
- **versie6525(13:35)**: Rapport generatie en donut charts structuur gefixt
- **versie6525(15:46)**: Foutcode 76 exclusief voor Artikelnummer duplicaten gemaakt en template-check geïmplementeerd

## 🔗 Gerelateerde Documentatie

- `MAPSTRUCTUUR_DOCUMENTATIE.md` - Gedetailleerde projectstructuur uitleg
- `CONVERSION_REPORT.md` - Architectuur migratie strategie  
- `deployment_for_IT/README_FOR_IT.md` - Server deployment instructies
- `Handleiding_JSON.md` - JSON configuratie handleiding
