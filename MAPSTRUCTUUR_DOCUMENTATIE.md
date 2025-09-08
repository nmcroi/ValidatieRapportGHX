# 📁 **MAPSTRUCTUUR DOCUMENTATIE - Project PrijsValGem_WS app**

## 🎯 **Overzicht**
Deze map bevat een **prijslijst validatie systeem** dat Excel bestanden valideert tegen GHX standaarden. Het project is opgebouwd uit meerdere componenten en ondersteunt zowel Streamlit (ontwikkeling) als CLI (productie) implementaties.

---

## 📂 **Hoofdmap Structuur**

### **🔧 Core Applicatie Files**
```
📁 Project PrijsValGem_WS app/
├── 🐍 prijslijst_validatie_app.py          # Streamlit web applicatie (ontwikkeling)
├── 📋 requirements.txt                      # Python dependencies
├── 📖 README.md                            # Project documentatie
├── 🔧 .gitignore                           # Git ignore regels
└── 🗂️ .DS_Store                            # macOS systeem bestand
```

### **📊 Configuratie Files**
```
├── 📄 field_validation_v18.json            # Legacy validatie configuratie (v18)
├── 📄 field_validation_v19.json            # Legacy validatie configuratie (v19)
├── 📄 field_validation_v20.json            # **ACTUELE** validatie configuratie (v20)
├── 📄 header_mapping.json                  # Excel header mapping configuratie
├── 📄 reference_lists.json                 # Referentie lijsten (UOM codes, landen, etc.)
├── 📄 template_config.json                 # Template-specifieke configuratie
└── 📄 error_code_mapping.json              # Error code hernummering mapping
```

### **📚 Documentatie Files**
```
├── 📖 Handleiding_JSON.md                  # JSON configuratie handleiding
├── 📊 CONVERSION_REPORT.md                 # v18→v20 conversie rapport
├── 🔗 INTEGRATION_PLAN.md                  # Integratie plan voor IT
└── 🧪 JSON_V20_INTEGRATION_TEST.md         # v20 integratie test documentatie
```

---

## 📁 **Subdirectories**

### **🔧 `/validator/` - Core Validatie Engine**
```
validator/
├── __init__.py                             # Python package initialisatie
├── price_tool.py                           # **HOOFDMODULE** - Validatie logica
└── rapport_utils.py                        # Rapport generatie utilities
```

**Functies:**
- **`price_tool.py`**: Bevat alle validatie logica, JSON v20 ondersteuning, template-aware validatie
- **`rapport_utils.py`**: Genereert Excel rapporten met gekleurde sheets en statistieken

### **🚀 `/deployment_for_IT/` - Productie Deployment**
```
deployment_for_IT/
├── cli_validate.py                         # CLI interface voor server deployment
├── requirements.txt                        # Minimale dependencies voor productie
├── README_FOR_IT.md                        # IT deployment instructies
├── config/                                 # Configuratie bestanden
│   ├── field_validation_v20.json
│   ├── header_mapping.json
│   └── reference_lists.json
└── validator/                              # Validatie engine (kopie)
    ├── __init__.py
    ├── price_tool.py
    └── rapport_utils.py
```

**Doel:** Aparte map voor IT deployment - bevat alleen essentiële bestanden voor server-side uitvoering.

### **📦 `/Archief/` - Historische Bestanden**
```
Archief/
├── Chats/                                  # Chat conversaties en notities
├── Exports/                                # Geëxporteerde bestanden en scripts
├── Mariska/                                # Backup van eerdere versies
├── field_validation_v18 kopie.txt          # Text versie van v18 config
└── field_validation_v20.txt                # Text versie van v20 config
```

**Doel:** Opslag van historische bestanden, exports, en backup versies.

### **🌳 `/Project TemplateTree app v3/` - Template Generator**
```
Project TemplateTree app v3/
├── flask_api.py                            # Flask API voor template generatie
├── ghx_clean_generator.html                # Web interface voor template generator
├── README.md                               # Template generator documentatie
├── requirements.txt                        # Dependencies voor template generator
├── config/                                 # Template generator configuratie
├── src/                                    # Source code voor template generator
├── static/                                 # Static assets (CSS, JS)
├── templates/                              # HTML templates
├── out/                                    # Generated templates en outputs
└── venv/                                   # Python virtual environment
```

**Doel:** Integreert met het validatie systeem om dynamische Excel templates te genereren met context-specifieke velden.

---

## 🔄 **Data Flow Architectuur**

### **1. Ontwikkeling (Streamlit)**
```
Excel Upload → prijslijst_validatie_app.py → validator/ → Excel Rapport
```

### **2. Productie (CLI)**
```
Excel File → deployment_for_IT/cli_validate.py → validator/ → Excel Rapport
```

### **3. Template Generator Integratie**
```
Template Generator → Excel Template → Validatie Systeem → Validatie Rapport
```

---

## 📋 **Configuratie Bestanden Uitleg**

### **`field_validation_v20.json`** ⭐ **PRIMAIR**
- **Doel:** Definieert alle validatie regels voor 102 GHX velden
- **Structuur:** `field_validations` met `data_format` en `rules` arrays
- **Versie:** v20 (nieuwste architectuur)

### **`header_mapping.json`**
- **Doel:** Mapt Excel kolom headers naar standaard GHX headers
- **Functie:** Ondersteunt multiline headers en verschillende talen

### **`reference_lists.json`**
- **Doel:** Bevat referentie lijsten (UOM codes, landcodes, etc.)
- **Gebruik:** Wordt gebruikt door validatie regels met `list_ref`

### **`template_config.json`**
- **Doel:** Definieert verplichte velden per template type
- **Ondersteunt:** Default template (17 velden) en Template Generator templates

### **`error_code_mapping.json`**
- **Doel:** Mapping tussen oude en nieuwe error codes (700+ range)
- **Reden:** Voorkomt conflicten met externe database codes

---

## 🚀 **Deployment Strategie**

### **Ontwikkeling**
- **Tool:** Streamlit (`prijslijst_validatie_app.py`)
- **Doel:** Interactieve ontwikkeling en testing
- **Features:** File upload, real-time validatie, rapport download

### **Productie**
- **Tool:** CLI (`deployment_for_IT/cli_validate.py`)
- **Doel:** Server-side batch processing
- **Features:** Command-line interface, geoptimaliseerd voor automatisering

---

## 🔧 **Technische Dependencies**

### **Core Libraries**
- **pandas**: Data manipulatie en Excel processing
- **openpyxl**: Excel file generatie en formatting
- **streamlit**: Web interface (alleen ontwikkeling)
- **json**: Configuratie bestanden

### **Validatie Features**
- **Template-aware validatie**: Dynamische verplichte velden
- **Cross-field validatie**: Complexe business regels
- **Multiline header support**: Excel template compatibiliteit
- **Error code hernummering**: 700+ range voor database compatibiliteit

---

## 📊 **Status Overzicht**

### **✅ Voltooid**
- JSON v20 architectuur implementatie
- Native v20 validatie engine
- Template-aware validatie systeem
- Error code hernummering (700+ range)
- Streamlit en CLI deployment
- Template Generator integratie

### **🔄 In Progress**
- Sheet 8 column mapping fix (6 problematische multiline headers)
- Uitgebreide error reporting features

### **📋 TODO**
- Sheet 7 database corrections verbetering
- Excel groene driehoekjes verwijderen
- Dashboard donut charts verwijderen
- UOM conflict kleuring verbetering
- Global flags implementatie

---

## 🎯 **Gebruik Instructies**

### **Voor Ontwikkelaars**
1. Start Streamlit: `streamlit run prijslijst_validatie_app.py`
2. Upload Excel bestand via web interface
3. Download validatie rapport

### **Voor IT Deployment**
1. Kopieer `deployment_for_IT/` naar server
2. Installeer dependencies: `pip install -r requirements.txt`
3. Voer uit: `python cli_validate.py input.xlsx`

### **Voor Template Generator**
1. Start Flask API in `Project TemplateTree app v3/`
2. Genereer template via web interface
3. Valideer gegenereerde template met validatie systeem

---

*Laatste update: 8 september 2025*
*Versie: v2.0 (JSON v20 architectuur)*
