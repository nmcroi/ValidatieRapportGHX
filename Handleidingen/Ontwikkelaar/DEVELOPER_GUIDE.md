# GHX Price Validation Tool - Developer Guide

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
├── template_context.py        # Metadata extraction from templates
├── config_manager.py          # Configuration loading and management
├── data_processor.py          # Data cleaning and transformation
├── field_logic.py             # Conditional field visibility logic
├── mandatory_fields.py        # Dynamic mandatory field detection
└── rapport_utils.py           # Report generation and formatting
```

## 🔄 **Validation Pipeline - Processing Workflow**

The validation pipeline is a sophisticated, multi-stage process that transforms raw Excel input into comprehensive validation reports. The pipeline is template-aware and adapts its processing based on the detected template type (TG/N/O).

### Pipeline Flow Diagram

```
Excel Input
     │
     ▼
┌─────────────────┐
│ 1. Template     │ ──> TG/N/O Detection
│    Detection    │     Decision Tree Logic
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ 2. Context      │ ──> Metadata Extraction
│    Extraction   │     Institution Codes
│                 │     Product Types
└─────────┬───────┘     Field Counts
          │
          ▼
┌─────────────────┐
│ 3. Configuration│ ──> Load JSON Configs
│    Loading      │     Field Mappings
│                 │     Validation Rules
└─────────┬───────┘     Reference Lists
          │
          ▼
┌─────────────────┐
│ 4. Data         │ ──> Clean DataFrame
│    Processing   │     Header Mapping
│                 │     Type Conversion
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ 5. Field Logic  │ ──> Visibility Rules
│    Application  │     Mandatory Detection
│                 │     Conditional Logic
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ 6. Validation   │ ──> Field-by-Field
│    Execution    │     Row-by-Row
│                 │     Error Collection
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ 7. Report       │ ──> Multi-Sheet Excel
│    Generation   │     Statistics Dashboard
│                 │     Error Details
└─────────────────┘     Quality Scoring
```

### Stage Details

#### Stage 1: Template Detection
- **Function:** `determine_template_type(excel_path)`
- **Logic:** Sequential checks for TG stamp, N generation markers, fallback to O
- **Output:** Template type string ('TG', 'N', 'O')

#### Stage 2: Context Extraction  
- **Function:** `extract_template_generator_context(excel_path)` (TG only)
- **Process:** Parse GHX_STAMP metadata for institution codes, product types
- **Output:** Context dictionary with parsed metadata

#### Stage 3: Configuration Loading
- **Functions:** `load_field_mapping()`, `load_institution_codes()`
- **Files:** field_validation_v20.json, header_mapping.json, reference_lists.json
- **Output:** Configuration objects for validation rules

#### Stage 4: Data Processing
- **Function:** `clean_dataframe(df)`, `map_headers(df, field_mapping)`
- **Process:** Remove empty rows, normalize headers, map legacy column names
- **Output:** Clean, standardized DataFrame

#### Stage 5: Field Logic Application
- **Function:** `apply_field_visibility(field_mapping, context, excel_data)`
- **Process:** Determine visible/hidden/mandatory fields based on template and context
- **Output:** Field decision dictionaries

#### Stage 6: Validation Execution
- **Function:** `validate_pricelist(excel_path, ...)`
- **Process:** Apply validation rules field-by-field, row-by-row
- **Output:** Validation results and error collections

#### Stage 7: Report Generation
- **Function:** `genereer_rapport(...)`
- **Process:** Create multi-sheet Excel with dashboard, errors, statistics
- **Output:** Comprehensive validation report

## 📊 **Quality Scoring System**

### Score Calculation
The system uses a dual-factor methodology:

```
Core Score = Volledigheid (M%) × Juistheid (J%)
Final Score = Core Score + Template Penalty + UOM Penalties
```

### Quick Mode Processing
For datasets >5000 rows:
- **Automatic activation:** Limits processing to first 5000 rows
- **Accurate percentages:** Calculated on processed subset
- **Filename identifier:** _QM_ suffix in output filename

### Output Naming Convention
```
Normal: [file]_VR_[template]_M[%]_J[%]_[score]([grade]).xlsx
Quick:  [file]_VR_QM_[template]_M[%]_J[%]_[score]([grade]).xlsx
```

## 🛠️ **Development Guidelines**

### Adding New Template Types
1. Extend `determine_template_type()` in template_detector.py
2. Add context extraction logic if needed
3. Update field_logic.py for template-specific rules
4. Test with representative data files

### Modifying Validation Rules
1. Update field_validation_v20.json configuration
2. Test against existing validation sets
3. Document changes in configuration comments
4. Update reference documentation

### Performance Considerations
- **Template detection:** < 0.5 seconds
- **Data processing:** < 2 seconds per 1000 rows
- **Validation:** < 5 seconds per 1000 rows
- **Report generation:** < 1 second

### Testing Strategy
1. **Unit tests:** Individual module functions
2. **Integration tests:** Full pipeline validation
3. **Template tests:** Each template type validation
4. **Performance tests:** Large dataset processing

## 🔧 **Debugging and Troubleshooting**

### Common Issues
1. **Template misdetection:** Check detection logic order
2. **Header mapping failures:** Verify header_mapping.json completeness
3. **Field visibility errors:** Review conditional logic in field_logic.py
4. **Performance issues:** Check dataset size, consider Quick Mode

### Debug Tools
All debug scripts are archived in `Archief/Development-Scripts/`:
- `debug_template_detection.py` - Template detection testing
- `debug_field_visibility.py` - Field logic debugging
- `debug_mapping_bug.py` - Header mapping issues

### Logging
The system provides comprehensive logging at multiple levels:
- INFO: Processing stages and results
- WARNING: Potential issues and fallbacks  
- ERROR: Validation failures and exceptions
- DEBUG: Detailed processing information

## 🚀 **Future Extensions**

### Template System Extensions
- European template support (E type)
- Custom institution template types
- Multi-language template detection

### Validation Enhancements
- Real-time validation API
- Batch processing capabilities
- Advanced error classification

### Integration Possibilities
- GHX API integration
- Database storage backends
- Web service deployment

---

This developer guide provides comprehensive technical documentation for understanding, maintaining, and extending the GHX Price Validation Tool. The clean architecture and modular design ensure that modifications can be made safely while maintaining system reliability.