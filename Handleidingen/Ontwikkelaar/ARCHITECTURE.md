# GHX Price Validation Tool - Clean Architecture

## 📊 **System Overview**

The GHX Price Validation Tool is a modern, modular Python application that validates Dutch healthcare pricing data according to GHX standards. The system follows clean architecture principles with clear separation of concerns and a template-aware decision tree approach.

## 🏗️ **Architecture Design**

### Core Philosophy: TG→N→O Decision Tree

The system implements a sophisticated template detection strategy that handles three distinct template types:

```
Template Detection Flow:
┌─────────────────┐
│   Input Excel   │
└─────────┬───────┘
          │
          v
┌─────────────────┐
│ 1. Check for TG │ ──Yes──> TG (Template Generator)
│   GHX_STAMP     │           ├─ Stamp parsing
│   in A1/Header  │           ├─ Context extraction  
└─────────┬───────┘           └─ Dynamic field logic
          │ No
          v
┌─────────────────┐
│ 2. Check for N  │ ──Yes──> N (Nieuwe Generatie)
│   "Is Bestelbare│           ├─ Modern GHX template
│   Eenheid" +     │           ├─ Standard validation
│   "Omschrijving │           └─ 17 mandatory fields
│   Verpakkings-  │
│   eenheid"      │
└─────────┬───────┘
          │ No
          v
┌─────────────────┐
│ 3. Default to O │ ────────> O (Oude/Alternative)
│   Legacy/Custom │           ├─ Header mapping
│   Template      │           ├─ Legacy compatibility
└─────────────────┘           └─ Full validation
```

### Module Structure

```
validator/                      # Core validation package
├── __init__.py                # Clean module exports and API
├── template_detector.py       # TG→N→O decision tree implementation
├── validation_engine.py       # Core validation pipeline
├── config_manager.py          # Configuration loading & validation
├── data_processor.py          # Data cleaning & header mapping
├── mandatory_fields.py        # Smart mandatory field detection
├── field_logic.py             # Conditional visibility & mandatory logic
├── template_context.py        # TG metadata parsing & context extraction
├── debug_tools.py             # Development & debugging utilities
├── utils.py                   # Common helper functions
└── price_tool.py              # Legacy compatibility interface
```

## 🔄 **Processing Pipeline**

### 1. Template Detection & Context Building
```python
# Step 1: Determine template type using TG→N→O decision tree
template_type = determine_template_type(excel_path)
# Result: 'TG', 'N', or 'O'

# Step 2: Extract relevant context
if template_type == "TG":
    context = extract_template_generator_context(excel_path)
    # Contains: stamp data, institutions, product types, field counts
else:
    context = {'template_type': template_type, 'excel_path': excel_path}
```

### 2. Configuration Loading & Field Mapping
```python
# Load and validate configuration files
field_mapping = load_field_mapping()          # from field_validation_v20.json
institution_codes = load_institution_codes()  # from Template Generator Files/

# Determine template-specific mandatory fields
mandatory_fields = determine_mandatory_fields_for_template(excel_path)
```

### 3. Data Processing & Header Mapping
```python
# Clean and standardize data
df_cleaned = clean_dataframe(df)

# Map supplier headers to GHX standard headers
df_mapped, unmapped_columns, mapping = map_headers(df_cleaned, field_mapping)
```

### 4. Field Visibility & Validation Logic
```python
# Apply template-specific field visibility rules
field_decisions = apply_field_visibility(field_mapping, context, excel_data)
visible_fields = field_decisions['visible_fields']
mandatory_fields = field_decisions['mandatory_fields']

# Validate data against rules with conditional logic
validation_results = validate_dataframe(df_mapped, field_mapping, context)
```

### 5. Report Generation
```python
# Generate comprehensive Excel validation report
report_path = generate_validation_report(
    validation_results, template_context, original_filename
)
```

## 🎯 **Key Design Principles**

### 1. Template-Aware Processing
Each template type has specific handling logic:
- **TG Templates**: Parse stamp metadata for dynamic field configuration
- **N Templates**: Use standard GHX validation with modern field structure
- **O Templates**: Apply header mapping with legacy compatibility

### 2. Modular Configuration
- **Field Mapping**: `field_validation_v20.json` defines all field rules
- **Institution Codes**: `Template Generator Files/institution_codes.json`
- **Header Mapping**: `header_mapping.json` for legacy template support
- **Reference Lists**: `reference_lists.json` for value validation

### 3. Conditional Field Logic
Fields can be conditionally visible or mandatory based on:
- Institution codes (NFU hospitals, research institutes)
- Product types (medical, facility, lab, other)
- Template context (chemicals, GS1 mode)
- Data dependencies (e.g., "Geregistreerd geneesmiddel == Ja")

### 4. Error Handling & Logging
- Comprehensive logging throughout the pipeline
- Graceful fallbacks for missing configurations
- Detailed error reporting with context information
- Validation reports with actionable error messages

## 🔧 **Technical Implementation**

### Template Generator Stamp Parsing
```python
# Example stamp: "S-LM-0-0-0-ul-V78-M18"
# S: Standard template (F = Staffel)
# LM: Medical + Lab products  
# 0-0-0: No chemicals, no staffel, GHX only
# ul: Universiteit Leiden
# V78: 78 visible fields
# M18: 18 mandatory fields
```

### Field Visibility Logic
```python
# Example visibility rule in field_validation_v20.json
{
  "ADR Gevarenklasse": {
    "visibility": {
      "show_if": ["chemicals", "medical"]
    },
    "mandatory": {
      "if": ["chemicals"],
      "depends_on": "Geregistreerd geneesmiddel == Ja"
    }
  }
}
```

### Performance Optimization
- Lazy loading of Excel data (headers first, then full data)
- Efficient field filtering based on visibility rules
- Minimal memory footprint for large datasets
- Caching of configuration data

## 📈 **Extensibility**

The architecture supports easy extension:
- **New Template Types**: Add detection logic to `template_detector.py`
- **New Validation Rules**: Extend `field_validation_v20.json`
- **New Institution Types**: Update `institution_codes.json`
- **Custom Field Logic**: Extend `field_logic.py` with new condition types

## 🔗 **Integration Points**

### Streamlit Web Interface
- `prijslijst_validatie_app.py` provides web UI
- Direct integration with `validator.validation_engine.validate_pricelist()`
- Real-time feedback and progress indication

### Template Generator Synchronization
- `Template Generator Files/` directory maintains sync with external system
- Automatic detection of institution codes and field mappings
- Version-controlled template configurations

### Report Generation
- Excel reports with multiple sheets (summary, errors, unmapped columns)
- Structured data for downstream processing
- Integration-ready output format

This architecture provides a robust, maintainable, and extensible foundation for GHX price validation while preserving the flexibility to handle diverse template formats and business requirements.