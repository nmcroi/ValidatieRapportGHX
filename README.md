# GHX Prijslijst Validatie App v2.0

Een prijslijst validatiesysteem met **dual architecture**: Streamlit web interface voor development en CLI interface voor server deployment.

## 🏗️ Architectuur

**Development (Streamlit):**
- Web interface voor interactief testen
- File upload via browser  
- Real-time validatie feedback

**Production (CLI):**
- Command-line interface voor server deployment
- Batch processing capabilities
- Automation-friendly design

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

## 📂 Projectstructuur

```
📁 Project PrijsValGem_WS app/
├── 🐍 prijslijst_validatie_app.py          # Streamlit web interface
├── 📊 Configuratie bestanden:
│   ├── field_validation_v20.json           # ⭐ JSON v20 validatie regels
│   ├── header_mapping.json                 # Excel header mapping
│   ├── reference_lists.json                # UOM codes, landen, etc.
│   ├── template_config.json                # Template-specifieke regels
│   └── error_code_mapping.json             # Error code hernummering
├── 🔧 validator/ - Core validatie engine:
│   ├── price_tool.py                       # Hoofdvalidatie logica
│   └── rapport_utils.py                    # Excel rapport generatie
├── 🚀 deployment_for_IT/ - Server deployment
└── 📖 Documentatie en archief bestanden
```

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
