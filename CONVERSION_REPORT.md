# Conversion Report: Streamlit vs Server Architecture

## Executive Summary

De huidige codebase heeft **twee parallelle architecturen**:

1. **Streamlit Development Version** (voor jou om te testen)
2. **Server Production Version** (voor GHX IT-afdeling)

Dit rapport analyseert de verschillen en geeft een strategie om ze zo dicht mogelijk bij elkaar te houden.

---

## 🏗️ Architectuur Verschillen

### Current Streamlit Architecture (Huidige Development)
```
prijslijst_validatie_app.py (Streamlit GUI)
├── File upload interface
├── Session state management 
├── Web-based UI components
└── validator/
    ├── price_tool.py
    ├── rapport_utils.py
    └── __init__.py
```

### Server Architecture (Archief/Mariska - Production)
```
cli_validate.py (Command Line Interface)
├── Argparse voor parameters
├── File system input/output
├── Geen UI dependencies
└── validator/ (zelfde modules)
    ├── price_tool.py  
    ├── rapport_utils.py
    └── Hardcoded server paths
```

---

## 🔍 Kritieke Verschillen

### 1. **Entry Point & Interface**

| Aspect | Streamlit (Development) | Server (Production) |
|--------|------------------------|-------------------|
| **Entry Point** | `prijslijst_validatie_app.py` | `cli_validate.py` |
| **Interface** | Web UI via Streamlit | Command Line Interface |
| **File Input** | `st.file_uploader()` | `--input` argument |
| **File Output** | Session state + download | `--output` directory |
| **Configuration** | Hardcoded paths | `--config` argument |

### 2. **Dependencies & Requirements**

**Streamlit Version:**
- ✅ `streamlit==1.45.0` (GUI framework)  
- ✅ Alle visualisatie libraries (altair, pydeck, etc.)
- ✅ Interactive components

**Server Version:**
- ❌ **GEEN** Streamlit dependency
- ✅ Core libraries only (pandas, openpyxl, xlsxwriter)
- ✅ Minimale footprint voor server

### 3. **Configuration Management**

**Streamlit:**
```python
MAPPING_JSON = "header_mapping.json"           # Hardcoded
VALIDATION_JSON = "field_validation_v18.json"  # Hardcoded
```

**Server:**
```python
config_dir = args.config  # Via command line argument
mapping_json = os.path.join(config_dir, "header_mapping.json")
validation_json = os.path.join(config_dir, "field_validation_v18.json")
```

### 4. **File Handling**

**Streamlit:**
```python
# Upload via web interface
uploaded_files = st.file_uploader(...)
# Process in memory
with tempfile.NamedTemporaryFile() as temp_file:
    temp_file.write(uploaded_file.getbuffer())
```

**Server:**
```python
# Direct file system access
input_xlsx = os.path.abspath(args.input)
# Process directly from disk
validate_pricelist(input_excel_path=input_xlsx, ...)
```

### 5. **Output & Reporting**

**Streamlit:**
```python
# Session state storage
st.session_state.report_data = {}
# Download button in UI
st.download_button(...)
```

**Server:**
```python
# Direct file system output
target_path = os.path.join(output_dir, f"{base_no_ext}_rapport.xlsx")
shutil.copy2(report_path, target_path)
print(f"REPORT_PATH={target_path}")  # For automation
```

---

## 🚨 Kritieke Server-specifieke Elementen

### 1. **Hardcoded Server Paths** (rapport_utils.py regel 19)
```python
VALIDATION_LOG_FILE = "/data/lucee/tomcat/webapps/ROOT/synqeps/webroot/upload/validatiePL_reports/validaties_overzicht.xlsx"
```
☝️ **Dit is een GHX server-specifiek pad!**

### 2. **Error Handling**
Server versie heeft robuustere error codes:
```python
return 0  # Success
return 1  # Validation error  
return 2  # File not found
return 3  # No report generated
return 4  # Copy failed
```

### 3. **System Integration**
CLI interface is gebouwd voor automation:
```bash
./cli_validate.py --input file.xlsx --output /reports/ --config /config/
echo $?  # Exit code for success/failure
```

---

## 🎯 Strategie: Server-Ready Development

### Optie 1: **Dual Architecture Approach** (AANBEVOLEN)

**Voordelen:**
- ✅ Blijf Streamlit gebruiken voor development/testing
- ✅ Zorg dat core logic server-ready blijft
- ✅ Minimale verschillen tussen versies

**Implementation:**
```
project/
├── streamlit_app.py          # Development interface
├── cli_validate.py           # Server interface  
├── config/
│   ├── field_validation_v20.json
│   ├── reference_lists.json
│   └── header_mapping.json
└── validator/                # SHARED CORE LOGIC
    ├── price_tool.py         # No UI dependencies
    ├── rapport_utils.py      # No UI dependencies  
    └── config_loader.py      # NEW: Centralized config
```

### Optie 2: **Local Testing Without Streamlit**

**Voordelen:**
- ✅ Exact dezelfde code als server
- ✅ Eenvoudiger deployment
- ❌ Minder gebruiksvriendelijk voor jou

**Implementation:**
```bash
# Test lokaal met command line
python cli_validate.py --input test.xlsx --output ./reports/ --config ./config/
```

---

## 📋 Action Plan

### Fase 1: **Core Logic Server-Ready Maken**
1. ✅ **`validator/` modules updaten** voor JSON v2.0 
2. ✅ **Geen Streamlit dependencies** in validator modules
3. ✅ **Centralized config loader** maken
4. ✅ **Path handling** abstraheren

### Fase 2: **Dual Interface Development**  
1. ✅ **CLI versie** updaten voor v20 JSON
2. ✅ **Streamlit versie** updaten voor v20 JSON
3. ✅ **Shared core** tussen beide interfaces
4. ✅ **Server paths** configureerbaar maken

### Fase 3: **Testing & Validation**
1. ✅ **Unit tests** voor core logic
2. ✅ **CLI testing** met diverse bestanden
3. ✅ **Streamlit testing** voor development
4. ✅ **Server deployment** voorbereiding

---

## 🛠️ Recommended Immediate Changes

### 1. **Update Configuration System**
```python
# NEW: config/config_loader.py
def load_validation_config(config_dir=None, version="v20"):
    """Load configuration from specified directory"""
    if config_dir is None:
        config_dir = os.path.dirname(__file__)
    
    validation_file = f"field_validation_{version}.json"
    reference_file = "reference_lists.json"
    
    # Return both configs
    return load_json(validation_file), load_json(reference_file)
```

### 2. **Abstract File Handling**
```python
# NEW: validator/file_handler.py  
class FileHandler:
    @staticmethod
    def process_excel(input_source, output_dir=None):
        """Process Excel from file path OR uploaded file object"""
        if isinstance(input_source, str):
            # Server: Direct file path
            return process_file_path(input_source)
        else:
            # Streamlit: Uploaded file object
            return process_uploaded_file(input_source)
```

### 3. **Update Both Entry Points**
```python
# cli_validate.py - Update for v20
validation_json = os.path.join(config_dir, "field_validation_v20.json")  
reference_json = os.path.join(config_dir, "reference_lists.json")

# streamlit_app.py - Update for v20  
VALIDATION_JSON = "field_validation_v20.json"
REFERENCE_JSON = "reference_lists.json"
```

---

## 💡 Recommendation

**Start met Optie 1 (Dual Architecture)**:

1. **Behoud Streamlit** voor jouw development/testing
2. **Maak core logic server-ready** (geen Streamlit dependencies)
3. **Update CLI versie** parallel aan Streamlit
4. **Test beide versies** met dezelfde input files

Dit zorgt ervoor dat:
- ✅ Jij kunt blijven ontwikkelen met Streamlit
- ✅ IT krijgt precies dezelfde core logic
- ✅ Minimale deployment verschillen
- ✅ Eenvoudige handover naar IT

**Volgende stap:** Zullen we beginnen met het updaten van de core `validator/` modules voor JSON v2.0, zonder Streamlit dependencies?
