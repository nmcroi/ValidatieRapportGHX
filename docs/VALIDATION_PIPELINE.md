# Validation Pipeline - Processing Workflow

## 🔄 **Pipeline Overview**

The validation pipeline is a sophisticated, multi-stage process that transforms raw Excel input into comprehensive validation reports. The pipeline is template-aware and adapts its processing based on the detected template type (TG/N/O).

## 📊 **Pipeline Flow Diagram**

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
│ 7. Report       │ ──> Excel Report
│    Generation   │     Multiple Sheets
│                 │     Summary Statistics
└─────────────────┘
```

## 🏗️ **Stage-by-Stage Breakdown**

### Stage 1: Template Detection
```python
def stage_1_template_detection(excel_path: str) -> Dict[str, Any]:
    """
    Determines template type and initial context.
    """
    template_type = determine_template_type(excel_path)
    
    context = {
        'template_type': template_type,
        'excel_path': excel_path,
        'timestamp': datetime.now(),
        'pipeline_version': '2.0.0'
    }
    
    logging.info(f"Template detected: {template_type}")
    return context
```

**Output:** Template type classification and initial context

### Stage 2: Context Extraction
```python
def stage_2_context_extraction(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts template-specific metadata and context.
    """
    if context['template_type'] == 'TG':
        # Parse Template Generator stamp
        tg_context = extract_template_generator_context(context['excel_path'])
        context.update(tg_context)
        
        # Extracted data includes:
        # - Institution codes: ['umcu', 'lumc']
        # - Product types: ['medisch', 'laboratorium']
        # - Field counts: visible=78, mandatory=18
        # - Special flags: chemicals=True, gs1_mode='also_gs1'
        
    elif context['template_type'] == 'N':
        # Modern template - standard context
        context.update({
            'product_types': ['medisch'],  # Default
            'institutions': [],            # Will be determined
            'visible_fields': None,        # All fields visible
            'mandatory_fields': 17         # Standard count
        })
    
    else:  # 'O' - Legacy template
        # Legacy template - minimal context
        context.update({
            'requires_header_mapping': True,
            'legacy_compatibility': True
        })
    
    return context
```

**Output:** Enriched context with template-specific metadata

### Stage 3: Configuration Loading
```python
def stage_3_configuration_loading() -> Dict[str, Any]:
    """
    Loads and validates all configuration files.
    """
    configs = {}
    
    # Load field mapping (validation rules)
    configs['field_mapping'] = load_field_mapping()
    # From: field_validation_v20.json
    
    # Load institution codes
    configs['institution_codes'] = load_institution_codes()
    # From: Template Generator Files/institution_codes.json
    
    # Load header mapping (for legacy templates)
    configs['header_mapping'] = load_header_mapping()
    # From: header_mapping.json
    
    # Load reference lists (for value validation)
    configs['reference_lists'] = load_reference_lists()
    # From: reference_lists.json
    
    # Validate configuration integrity
    validate_configuration_consistency(configs)
    
    return configs
```

**Output:** Complete configuration set with validation

### Stage 4: Data Processing
```python
def stage_4_data_processing(excel_path: str, configs: Dict) -> Tuple[pd.DataFrame, Dict]:
    """
    Cleans and processes raw Excel data.
    """
    # Load raw Excel data
    df_raw = pd.read_excel(excel_path)
    logging.info(f"Raw data loaded: {df_raw.shape}")
    
    # Step 4.1: Data Cleaning
    df_cleaned = clean_dataframe(df_raw)
    # - Remove empty rows
    # - Clean column names
    # - Standardize string values
    # - Handle NaN values
    
    # Step 4.2: Header Mapping (for O templates)
    if context['template_type'] == 'O':
        df_mapped, unmapped_cols, mapping = map_headers(
            df_cleaned, configs['header_mapping']
        )
    else:
        df_mapped = df_cleaned
        unmapped_cols = []
        mapping = {}
    
    # Step 4.3: Data Type Standardization
    df_final = standardize_data_types(df_mapped, configs['field_mapping'])
    
    processing_info = {
        'original_shape': df_raw.shape,
        'cleaned_shape': df_cleaned.shape,
        'final_shape': df_final.shape,
        'unmapped_columns': unmapped_cols,
        'column_mapping': mapping
    }
    
    return df_final, processing_info
```

**Output:** Cleaned and standardized DataFrame with processing metadata

### Stage 5: Field Logic Application
```python
def stage_5_field_logic(df: pd.DataFrame, configs: Dict, context: Dict) -> Dict[str, Any]:
    """
    Applies template-specific field visibility and mandatory logic.
    """
    # Determine which fields should be visible/mandatory
    field_decisions = apply_field_visibility(
        configs['field_mapping'], 
        context, 
        df  # Needed for depends_on checks
    )
    
    # Results include:
    field_logic = {
        'visible_fields': field_decisions['visible_fields'],
        'mandatory_fields': field_decisions['mandatory_fields'],
        'hidden_fields': field_decisions['hidden_fields'],
        'field_decisions': field_decisions['field_decisions'],
        'context_labels': field_decisions['context_labels']
    }
    
    # Log field analysis
    logging.info(f"Field analysis: {len(field_logic['visible_fields'])} visible, "
                f"{len(field_logic['mandatory_fields'])} mandatory")
    
    return field_logic
```

**Output:** Complete field visibility and mandatory analysis

### Stage 6: Validation Execution
```python
def stage_6_validation_execution(df: pd.DataFrame, configs: Dict, 
                                context: Dict, field_logic: Dict) -> Dict[str, Any]:
    """
    Executes comprehensive field and row validation.
    """
    validation_results = []
    validation_stats = {}
    failed_rows = []
    
    # Get mandatory fields for this template
    mandatory_fields = determine_mandatory_fields_for_template(context['excel_path'])
    
    # Validate each row
    for index, row in df.iterrows():
        row_errors = []
        
        # 6.1: Mandatory Field Validation
        for field_name in mandatory_fields:
            if field_name in df.columns:
                if should_validate_field(field_name, context):
                    errors = validate_mandatory_field(
                        field_name, row.get(field_name), index + 1
                    )
                    row_errors.extend(errors)
        
        # 6.2: Field Rule Validation
        for field_name in df.columns:
            if should_validate_field(field_name, context):
                field_config = configs['field_mapping'].get('fields', {}).get(field_name, {})
                errors = validate_field_v20_native(
                    field_name, row.get(field_name), field_config,
                    configs.get('reference_lists', {}), {'row_index': index + 1}
                )
                row_errors.extend(errors)
        
        # Collect row results
        if row_errors:
            validation_results.extend(row_errors)
            failed_rows.append({
                'row_index': index + 1,
                'errors': row_errors,
                'error_count': len(row_errors)
            })
    
    # Generate validation statistics
    validation_stats = generate_validation_statistics(
        validation_results, failed_rows, mandatory_fields, df
    )
    
    return {
        'validation_results': validation_results,
        'validation_stats': validation_stats,
        'failed_rows': failed_rows,
        'summary_stats': validation_stats['summary']
    }
```

**Output:** Complete validation results with detailed error analysis

### Stage 7: Report Generation
```python
def stage_7_report_generation(validation_data: Dict, context: Dict, 
                             processing_info: Dict, original_filename: str) -> str:
    """
    Generates comprehensive Excel validation report.
    """
    # Determine output directory and filename
    output_dir = os.path.join(os.getcwd(), "validation_reports")
    os.makedirs(output_dir, exist_ok=True)
    
    base_name = os.path.splitext(original_filename)[0]
    report_filename = f"{base_name}_validation_report.xlsx"
    report_path = os.path.join(output_dir, report_filename)
    
    # Create multi-sheet Excel report
    with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
        # Sheet 1: Executive Summary
        create_summary_sheet(writer, context, validation_data['summary_stats'])
        
        # Sheet 2: Error Details (if errors exist)
        if validation_data['validation_results']:
            create_errors_sheet(writer, validation_data['validation_results'])
        
        # Sheet 3: Failed Rows Summary
        if validation_data['failed_rows']:
            create_failed_rows_sheet(writer, validation_data['failed_rows'])
        
        # Sheet 4: Field Analysis
        create_field_analysis_sheet(writer, context, processing_info)
        
        # Sheet 5: Configuration Info
        create_config_info_sheet(writer, context)
    
    logging.info(f"Validation report generated: {report_path}")
    return report_path
```

**Output:** Comprehensive Excel validation report with multiple analysis sheets

## ⚡ **Performance Optimizations**

### Lazy Loading Strategy
```python
# Load headers first for template detection
df_headers = pd.read_excel(excel_path, nrows=0)

# Load full data only when needed
if template_needs_full_data(template_type):
    df_full = pd.read_excel(excel_path)
```

### Parallel Processing (Future Enhancement)
```python
# Potential for row-level parallel validation
from concurrent.futures import ThreadPoolExecutor

def parallel_row_validation(df_chunks):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(validate_chunk, chunk) for chunk in df_chunks]
        results = [future.result() for future in futures]
    return combine_results(results)
```

### Memory Management
```python
# Process large files in chunks
chunk_size = 1000
for chunk in pd.read_excel(excel_path, chunksize=chunk_size):
    process_chunk(chunk)
```

## 📈 **Pipeline Metrics**

The pipeline tracks comprehensive metrics:

```python
pipeline_metrics = {
    'processing_time': {
        'template_detection': 0.1,    # seconds
        'context_extraction': 0.2,
        'configuration_loading': 0.3,
        'data_processing': 1.5,
        'field_logic': 0.5,
        'validation_execution': 3.2,
        'report_generation': 0.8,
        'total_time': 6.6
    },
    'data_metrics': {
        'input_rows': 1500,
        'processed_rows': 1485,      # After cleaning
        'validated_fields': 45,
        'error_count': 23,
        'failed_rows': 12
    },
    'quality_metrics': {
        'mandatory_field_coverage': 0.94,  # 94% coverage
        'data_completeness': 0.87,          # 87% complete
        'validation_success_rate': 0.92     # 92% pass rate
    }
}
```

## 🔄 **Error Handling Strategy**

### Graceful Degradation
```python
try:
    result = stage_n_processing(data)
except ConfigurationError:
    # Use fallback configuration
    result = stage_n_fallback(data)
except DataProcessingError:
    # Continue with partial results
    result = stage_n_partial(data)
```

### Comprehensive Logging
```python
logging.info("Pipeline stage started: Data Processing")
logging.warning("Partial data quality issue detected")
logging.error("Critical validation failure in row 123")
logging.debug("Field mapping details: {...}")
```

## 🎯 **Quality Assurance**

### Validation Checkpoints
- Configuration file integrity checks
- Data type consistency validation
- Template detection accuracy verification
- Field mapping completeness assessment
- Output report format validation

### Performance Benchmarks
- Template detection: < 0.5 seconds
- Data processing: < 2 seconds per 1000 rows
- Validation execution: < 5 seconds per 1000 rows
- Report generation: < 1 second

This pipeline architecture ensures reliable, efficient, and comprehensive validation processing while maintaining flexibility for different template types and business requirements.