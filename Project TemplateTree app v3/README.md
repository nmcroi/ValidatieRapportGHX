# 🔧 GHX Template Generator v3.0

Een professionele web-applicatie voor het genereren van aangepaste Excel templates op basis van dynamische configuraties met geïntegreerde validatie.

## ✨ Features

### 🎯 **Kern Functionaliteit**
- **Dynamische template generatie** op basis van context (facilitair, medisch, lab, overige)
- **Institution-specific mandatory fields** - Automatische toevoeging van verplichte velden per ziekenhuis
- **Intelligente veld hiding** - Context-afhankelijke zichtbaarheid
- **Mandatory field styling** - Oranje headers (#f89a8c) voor verplichte velden
- **Template stamping** - Volledige context metadata in Excel
- **Configuratie codes** - Leesbare codes voor template traceability

### 🌐 **Web Interface**
- **Modern HTML5 interface** met GHX huisstijl
- **Stap-voor-stap wizard** voor eenvoudige configuratie
- **Real-time template generatie** via REST API
- **Direct download** van gegenereerde templates
- **NFU ziekenhuizen** - Speciale selectie voor Nederlandse universitaire medische centra

### ⚙️ **Backend**
- **Python Flask API** (poort 8080) voor template generatie
- **Streamlit validatie app** (poort 8502) voor template validatie
- **JSON-configuratie** in field_validation_v20.json
- **Excel processing** met openpyxl en XlsxWriter

### 🏥 **Institution-Specific Features**
- **NFU Ziekenhuizen**: Automatische Levertijd als mandatory field
  - Amsterdam UMC (AMC & VUmc)
  - Leids Universitair Medisch Centrum (LUMC)
  - Maastricht UMC+
  - Universitair Medisch Centrum Groningen (UMCG)
  - Universitair Medisch Centrum Utrecht (UMCU)
- **Sanquin**: Automatische "Bevat het Artikel Menselijk Weefsel" als mandatory
- **Research Institutes**: Prinses Máxima Centrum, Prothya Biosolutions
- **Universiteiten**: Leiden, Utrecht, Amsterdam
- **Algemeen gebruik**: Voor leveranciers zonder specifieke instelling

## 🚀 Quick Start

### **1. Template Generator starten**
```bash
cd "Project TemplateTree app v3"

# Activeer virtual environment
source new_venv/bin/activate

# Start Flask API
python flask_api.py
```

### **2. Validatie App starten**
```bash
cd "../"  # Ga naar hoofdmap

# Activeer validatie environment  
source validation_venv/bin/activate

# Start Streamlit app
streamlit run prijslijst_validatie_app.py --server.port=8502
```

### **3. Gebruik**
1. **Template Generator**: Open `ghx_clean_generator.html` en ga door de wizard
2. **Template Validatie**: Upload je Excel bestand op http://localhost:8502
3. **Geïntegreerde workflow**: Template Generator templates worden automatisch herkend

## 📁 Project Structuur

```
Project TemplateTree app v3/
├── 🔧 CORE
│   ├── src/                     # Backend modules
│   │   ├── context.py          # Context handling
│   │   ├── mapping.py          # Field mapping
│   │   ├── engine.py           # Template logic
│   │   ├── excel.py           # Excel processing
│   │   └── stamp.py           # Template metadata
│   ├── flask_api.py           # REST API (poort 8080)
│   └── ghx_clean_generator.html # Web interface
│
├── ⚙️ CONFIGURATIE
│   └── config/
│       ├── field_mapping.json        # Veld mapping
│       └── GHX JSON GT Handleiding v4.txt # JSON handleiding
│
├── 📄 TEMPLATES
│   └── templates/
│       ├── GHXstandaardTemplate v25.1.xlsx # Standard template
│       └── template_staffel.xlsx           # Staffel template
│
├── 🧪 TESTING
│   ├── generate_test_plan.py            # Test plan generator
│   ├── testplan_template_generator.xlsx # Excel testplan (8 testcases)
│   └── out/                             # Generated templates
│
└── 🔗 INTEGRATION
    └── ../field_validation_v20.json    # Gedeelde configuratie
    └── ../prijslijst_validatie_app.py  # Streamlit validatie app
```

## 🔌 API Endpoints

### **Flask API (http://127.0.0.1:8080)**

| Endpoint | Method | Beschrijving |
|----------|--------|--------------|
| `/api/health` | GET | Health check |
| `/api/generate-template` | POST | Genereer template |
| `/api/download/<file_id>` | GET | Download template |
| `/api/institutions` | GET | Institution mapping |

### **Template Generatie Request**
```json
{
  "template_choice": "standard",
  "gs1_mode": "none",
  "product_types": ["medisch"],
  "has_chemicals": true,
  "is_staffel_file": false,
  "institutions": ["universitair_medisch_centrum_utrecht_(umc_utrecht)"],
  "version": "v3.0"
}
```

### **Response met Template Code**
```json
{
  "success": true,
  "file_id": "abc123",
  "preset_code": "S-M-1-0-0-umcu-V87-M20",
  "stats": {
    "visible_fields": 87,
    "mandatory_fields": 20,
    "hidden_fields": 16
  }
}
```

## 🎨 Template Codes

### **Code Format**: `S-PT-CHEM-STAF-GS1-INST-V##-M##`

| Positie | Naam | Opties | Beschrijving |
|---------|------|--------|--------------|
| 1 | **Template Type** | S, F | Standard of Staffel |
| 2 | **Product Types** | F, M, L, O, FM, FML, FMLO | Facilitair, Medisch, Lab, Overige |
| 3 | **Chemicals** | 0, 1 | Geen/Met chemicals |
| 4 | **Staffel** | 0, 1 | Geen/Met staffel |
| 5 | **GS1 Mode** | 0, 1 | Alleen GHX/Ook GS1 GDSN |
| 6 | **Institutions** | umcu, sq, lumc+amcu, etc. | Specifieke institution codes |
| 7-8 | **Statistics** | V87-M20 | Visible & Mandatory field counts |

### **Voorbeelden**
- `S-F-0-0-0-algemeen-V95-M17` = Standard Facilitair, algemeen gebruik
- `S-M-1-0-0-umcu-V87-M20` = Standard Medisch + chemicals, UMC Utrecht
- `S-FMLO-1-0-1-alle_nfu-V97-M25` = Standard alle types, alle NFU ziekenhuizen, GS1

## 🏥 Institution Mandatory Fields

| Institution Code | Naam | Extra Mandatory Fields |
|------------------|------|----------------------|
| **umcu** | UMC Utrecht | Levertijd |
| **lumc** | LUMC Leiden | Levertijd |
| **amcu** | Amsterdam UMC | Levertijd |
| **mumc** | Maastricht UMC+ | Levertijd |
| **umcg** | UMCG Groningen | Levertijd |
| **sq** | Sanquin | Bevat het Artikel Menselijk Weefsel |
| **pmc** | Prinses Máxima Centrum | - |
| **pb** | Prothya Biosolutions | - |
| **ul** | Universiteit Leiden | - |
| **uu** | Universiteit Utrecht | - |
| **uva** | Universiteit van Amsterdam | - |
| **zxl** | ZorgService XL | - |
| **algemeen** | Algemeen gebruik | - |

## 🧪 Testing

### **Excel Testplan**
Het bestand `testplan_template_generator.xlsx` bevat 8 testcases:
- **TC01**: Basis facilitair, algemeen gebruik
- **TC02**: Medisch + chemicals, UMCU
- **TC03**: Facilitair+Medisch NFU, GS1  
- **TC04**: Lab + chemicals, Sanquin
- **TC05**: Medisch+Overige, research institutes
- **TC06**: Facilitair+Lab universiteiten, GS1
- **TC07**: Alle NFU, GS1
- **TC08**: Alleen overige, Prothya

### **Test Workflow**
1. Genereer templates via `generate_test_plan.py`
2. Valideer templates in Streamlit app
3. Controleer mandatory fields en zichtbaarheid

## 🔧 Configuration

### **JSON Configuratie** (`../field_validation_v20.json`)
Gedeelde configuratie voor:
- **Template Generator**: Veld zichtbaarheid en mandatory status
- **Validatie App**: Bedrijfsregels en validaties
- **Institution Mapping**: Ziekenhuis namen en codes
- **Code System**: Template code documentatie

### **Field Mapping** (`config/field_mapping.json`)
Definieert voor elk Excel veld:
- Zichtbaarheid regels
- Mandatory condities
- Kolom mapping
- Dependencies

## 🔗 Validatie Integratie

### **Template Detection**
1. **Stamp Detection**: `_GHX_META` sheet met `GHX_STAMP` named range
2. **Context Extraction**: Volledige wizard data uit Excel metadata
3. **Automatic Rules**: Template Generator templates krijgen aangepaste validatie
4. **Fallback**: Default validatie voor oude templates

### **Workflow**
```
Template Generator → Stamped Excel → Validatie App → Rapport
     ↓                   ↓              ↓           ↓
  Web Wizard         Context Meta    Auto Detect  Institution
  Institution         + Codes       Template Type  Specific Rules
  Selection           in Excel        & Settings    Applied
```

## 📊 Statistics

### **Template Types**
| Template | Avg Fields | Mandatory | Hidden | Use Case |
|----------|------------|-----------|--------|----------|
| **Standard** | V87-V97 | M17-M25 | 6-16 | Normale prijslijsten |
| **Staffel** | V115+ | M25+ | 0-5 | Volume-based pricing |

### **Institution Impact**
| Institution Type | Extra Mandatory | Field Count Impact |
|------------------|-----------------|-------------------|
| **NFU Hospitals** | +1 (Levertijd) | M17→M20+ |
| **Sanquin** | +1 (Menselijk Weefsel) | M17→M18+ |
| **Research/Uni** | None | M17 baseline |

## 🤝 Contributing

1. Clone repository
2. Setup environments (`new_venv` en `validation_venv`)
3. Test beide applicaties
4. Update JSON configuratie indien nodig
5. Regenereer testplan met nieuwe codes

## 📄 License

Dit project is onderdeel van de GHX template generator suite.

---

**GHX Template Generator v3.0** - Geïntegreerde template generatie en validatie voor healthcare sector 🏥✨