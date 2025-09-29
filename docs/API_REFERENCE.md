# API Reference - Validator Package

## 📦 **Module Overview**

The `validator` package provides a clean, modular API for GHX price validation functionality. All modules follow consistent patterns and provide comprehensive error handling.

## 🎯 **Main Entry Points**

### validate_pricelist()
**Primary validation function**

```python
from validator import validate_pricelist

def validate_pricelist(
    input_excel_path: str,
    mapping_json_path: str = "field_validation_v20.json",
    validation_json_path: str = "field_validation_v20.json", 
    original_input_filename: str = None,
    reference_json_path: str = "reference_lists.json"
) -> Optional[str]:
    """
    Main entry point for price list validation.
    
    Args:
        input_excel_path: Path to Excel file to validate
        mapping_json_path: Path to field mapping configuration  
        validation_json_path: Path to validation rules configuration
        original_input_filename: Original filename for reporting
        reference_json_path: Path to reference lists file
        
    Returns:
        Path to generated validation report Excel file, or None on failure
        
    Example:
        report_path = validate_pricelist(
            "data/pricelist.xlsx",
            original_input_filename="supplier_pricelist.xlsx"
        )
    """
```

## 🔍 **Template Detection API**

### determine_template_type()
```python
from validator import determine_template_type

def determine_template_type(excel_path: str) -> str:
    """
    Determines template type using TG→N→O decision tree.
    
    Args:
        excel_path: Path to Excel template file
        
    Returns:
        'TG' = Template Generator (with GHX stamp)
        'N'  = Nieuwe Generatie (modern GHX template)
        'O'  = Oude/Alternative (legacy/custom template)
        
    Example:
        template_type = determine_template_type("template.xlsx")
        if template_type == "TG":
            # Handle Template Generator template
            pass
    """
```

### has_template_generator_stamp()
```python
from validator import has_template_generator_stamp

def has_template_generator_stamp(excel_path: str) -> bool:
    """
    Checks for Template Generator stamp in Excel file.
    
    Args:
        excel_path: Path to Excel file
        
    Returns:
        True if TG stamp detected, False otherwise
        
    Example:
        if has_template_generator_stamp("template.xlsx"):
            print("Template Generator template detected")
    """
```

### test_template_detection()
```python
from validator import test_template_detection

def test_template_detection(excel_path: str) -> Dict[str, Any]:
    """
    Comprehensive template detection testing utility.
    
    Args:
        excel_path: Path to Excel file
        
    Returns:
        Dict with detailed detection analysis:
        {
            'template_type': str,
            'has_tg_stamp': bool,
            'tg_stamp_value': str,
            'heeft_nieuwe_generatie_markers': bool,
            'gevonden_markers': List[str],
            'alle_kolommen': List[str],
            'debug_info': List[str]
        }
    """
```

## ⚙️ **Configuration Management API**

### load_field_mapping()
```python
from validator import load_field_mapping

def load_field_mapping() -> Optional[Dict[str, Any]]:
    """
    Loads field validation configuration from JSON.
    
    Returns:
        Configuration dict or None on failure
        
    Example:
        config = load_field_mapping()
        if config:
            fields = config.get('fields', {})
    """
```

### load_institution_codes()
```python
from validator import load_institution_codes

def load_institution_codes() -> Dict[str, str]:
    """
    Loads institution code mappings.
    
    Returns:
        Dict mapping institution codes to full names
        {
            'umcu': 'UMC Utrecht',
            'lumc': 'LUMC Leiden',
            ...
        }
    """
```

### get_fallback_institution_codes()
```python
from validator import get_fallback_institution_codes

def get_fallback_institution_codes() -> Dict[str, str]:
    """
    Returns hardcoded fallback institution codes.
    
    Returns:
        Dict with basic institution mappings
    """
```

## 🏗️ **Template Context API**

### extract_template_generator_context()
```python
from validator import extract_template_generator_context

def extract_template_generator_context(excel_path: str) -> Optional[Dict[str, Any]]:
    """
    Extracts Template Generator metadata and context.
    
    Args:
        excel_path: Path to TG Excel file
        
    Returns:
        Context dict with TG metadata:
        {
            'template_type': 'TG',
            'stamp_data': {
                'raw_code': str,
                'template_choice': str,
                'product_types': List[str],
                'has_chemicals': bool,
                'institutions': List[str],
                'visible_fields': int,
                'mandatory_fields': int
            },
            'version_info': Dict[str, str],
            'institution_info': Dict[str, str]
        }
    """
```

### parse_template_code()
```python
from validator import parse_template_code

def parse_template_code(template_code: str) -> Dict[str, Any]:
    """
    Parses Template Generator stamp code.
    
    Args:
        template_code: TG stamp (e.g., "S-LM-0-0-0-ul-V78-M18")
        
    Returns:
        Parsed configuration dict
        
    Example:
        parsed = parse_template_code("S-LM-0-0-0-ul-V78-M18")
        print(f"Institutions: {parsed['institutions']}")
        print(f"Product types: {parsed['product_types']}")
    """
```

## 🧠 **Field Logic API**

### apply_field_visibility()
```python
from validator import apply_field_visibility

def apply_field_visibility(
    field_mapping: Dict[str, Any], 
    context: Dict[str, Any], 
    excel_data: pd.DataFrame = None
) -> Dict[str, Any]:
    """
    Applies field visibility and mandatory logic.
    
    Args:
        field_mapping: Field configuration from JSON
        context: Template context
        excel_data: Excel data for depends_on checks
        
    Returns:
        Field analysis result:
        {
            'visible_fields': List[str],
            'mandatory_fields': List[str], 
            'hidden_fields': List[str],
            'field_decisions': Dict[str, Dict],
            'context_labels': List[str],
            'summary': Dict[str, int]
        }
    """
```

### evaluate_field_visibility()
```python
from validator import evaluate_field_visibility

def evaluate_field_visibility(
    field_config: Dict[str, Any],
    context_labels: List[str], 
    product_types: List[str]
) -> Tuple[bool, str]:
    """
    Evaluates if a field should be visible.
    
    Args:
        field_config: Field configuration dict
        context_labels: Context labels (institutions, etc.)
        product_types: Product types (medical, facility, etc.)
        
    Returns:
        Tuple of (is_visible: bool, reason: str)
    """
```

### evaluate_field_mandatory()
```python
from validator import evaluate_field_mandatory

def evaluate_field_mandatory(
    field_config: Dict[str, Any],
    context_labels: List[str],
    product_types: List[str], 
    excel_data: pd.DataFrame = None
) -> Tuple[bool, str]:
    """
    Evaluates if a field should be mandatory.
    
    Args:
        field_config: Field configuration dict
        context_labels: Context labels
        product_types: Product types
        excel_data: Excel data for depends_on checks
        
    Returns:
        Tuple of (is_mandatory: bool, reason: str)
    """
```

## 💾 **Data Processing API**

### map_headers()
```python
from validator import map_headers

def map_headers(
    df: pd.DataFrame, 
    mapping_config: Dict,
    return_mapping: bool = False
) -> Union[Tuple[pd.DataFrame, List[str], Dict[str, str]], 
           Tuple[pd.DataFrame, List[str], Dict[str, str], Dict[str, str]]]:
    """
    Maps supplier headers to standardized GHX headers.
    
    Args:
        df: DataFrame with supplier data
        mapping_config: Header mapping configuration
        return_mapping: Whether to return reverse mapping dict
        
    Returns:
        Tuple of (mapped_df, unmapped_columns, original_mapping [, reverse_mapping])
    """
```

### clean_dataframe()
```python
from validator import clean_dataframe

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs comprehensive data cleaning.
    
    Args:
        df: Raw DataFrame
        
    Returns:
        Cleaned DataFrame
        
    Operations:
        - Remove empty rows
        - Clean column names
        - Standardize string values
        - Handle NaN values
    """
```

### normalize_template_header()
```python
from validator import normalize_template_header

def normalize_template_header(header: str) -> str:
    """
    Normalizes header for comparison and matching.
    
    Args:
        header: Header string
        
    Returns:
        Normalized header (lowercase, cleaned)
    """
```

## 📋 **Mandatory Fields API**

### determine_mandatory_fields_for_template()
```python
from validator import determine_mandatory_fields_for_template

def determine_mandatory_fields_for_template(excel_path: str) -> List[str]:
    """
    Determines mandatory fields for specific template.
    
    Args:
        excel_path: Path to Excel template
        
    Returns:
        List of mandatory field names
        
    Logic:
        - TG templates: Use stamp metadata + institution rules
        - N templates: Use standard 17 GHX mandatory fields
        - O templates: Use full GHX mandatory field set
    """
```

### validate_mandatory_field_count()
```python
from validator import validate_mandatory_field_count

def validate_mandatory_field_count(
    expected_count: int, 
    actual_fields: List[str]
) -> Dict[str, Any]:
    """
    Validates mandatory field count against expectation.
    
    Args:
        expected_count: Expected number (e.g., from TG stamp M18)
        actual_fields: List of actual mandatory fields
        
    Returns:
        Validation result dict with match status and difference
    """
```

## ✅ **Validation Engine API**

### validate_dataframe()
```python
from validator import validate_dataframe

def validate_dataframe(
    df: pd.DataFrame,
    validation_config: Dict,
    original_column_mapping: Dict,
    template_context: Dict[str, Any] = None
) -> Tuple[List, Dict, List, Dict]:
    """
    Validates DataFrame against validation rules.
    
    Args:
        df: DataFrame to validate
        validation_config: Validation configuration
        original_column_mapping: Column mapping info
        template_context: Template context for conditional validation
        
    Returns:
        Tuple of (validation_results, validation_stats, failed_rows, summary_stats)
    """
```

### validate_field_v20_native()
```python
from validator import validate_field_v20_native

def validate_field_v20_native(
    field_name: str,
    value: Any, 
    field_config: Dict,
    invalid_values: List,
    row_data: Dict = None,
    reference_lists: Dict = None
) -> List:
    """
    Validates single field against V20 configuration.
    
    Args:
        field_name: Name of field
        value: Value to validate
        field_config: V20 field configuration
        invalid_values: List of invalid values
        row_data: Additional row data
        reference_lists: Reference lists for lookup validation
        
    Returns:
        List of validation errors
    """
```

## 🛠️ **Debug Tools API**

### debug_field_mapping_decisions()
```python
from validator import debug_field_mapping_decisions

def debug_field_mapping_decisions(
    excel_path: str,
    field_mapping: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Debug utility for field mapping decisions.
    
    Args:
        excel_path: Path to Excel file
        field_mapping: Field mapping configuration
        
    Returns:
        Detailed debug information about field mapping decisions
    """
```

### debug_template_detection_flow()
```python
from validator import debug_template_detection_flow

def debug_template_detection_flow(excel_path: str) -> Dict[str, Any]:
    """
    Debug utility for template detection flow.
    
    Args:
        excel_path: Path to Excel file
        
    Returns:
        Step-by-step template detection analysis
    """
```

## 🔧 **Utility Functions API**

### safe_get_nested_value()
```python
from validator import safe_get_nested_value

def safe_get_nested_value(data: Dict, key_path: str, default: Any = None) -> Any:
    """
    Safely retrieves nested dictionary values.
    
    Args:
        data: Source dictionary
        key_path: Dot-separated key path (e.g., "config.fields.name")
        default: Default value if key not found
        
    Returns:
        Retrieved value or default
    """
```

### is_empty_value()
```python
from validator import is_empty_value

def is_empty_value(value: Any) -> bool:
    """
    Checks if value is considered empty for validation.
    
    Args:
        value: Value to check
        
    Returns:
        True if value is empty (None, NaN, empty string, etc.)
    """
```

### format_error_message()
```python
from validator import format_error_message

def format_error_message(
    field_name: str,
    error_type: str, 
    details: Dict[str, Any]
) -> str:
    """
    Formats standardized error message.
    
    Args:
        field_name: Name of field with error
        error_type: Type of validation error
        details: Additional error details
        
    Returns:
        Formatted error message string
    """
```

## 📊 **Usage Examples**

### Basic Validation
```python
from validator import validate_pricelist

# Simple validation
report_path = validate_pricelist("data/pricelist.xlsx")
if report_path:
    print(f"Validation completed: {report_path}")
```

### Advanced Template Analysis
```python
from validator import (
    determine_template_type, 
    extract_template_generator_context,
    apply_field_visibility
)

# Analyze template
template_type = determine_template_type("template.xlsx")
print(f"Template type: {template_type}")

if template_type == "TG":
    # Extract TG context
    context = extract_template_generator_context("template.xlsx")
    print(f"Institutions: {context['stamp_data']['institutions']}")
    print(f"Product types: {context['stamp_data']['product_types']}")
    
    # Apply field logic
    field_mapping = load_field_mapping()
    field_decisions = apply_field_visibility(field_mapping, context)
    print(f"Visible fields: {len(field_decisions['visible_fields'])}")
    print(f"Mandatory fields: {len(field_decisions['mandatory_fields'])}")
```

### Custom Validation Pipeline
```python
from validator import (
    load_field_mapping, clean_dataframe, map_headers,
    determine_mandatory_fields_for_template, validate_dataframe
)
import pandas as pd

# Custom validation pipeline
df = pd.read_excel("data.xlsx")
config = load_field_mapping()

# Process data
df_clean = clean_dataframe(df)
df_mapped, unmapped, mapping = map_headers(df_clean, config)

# Determine mandatory fields
mandatory_fields = determine_mandatory_fields_for_template("data.xlsx")

# Validate
results, stats, failed_rows, summary = validate_dataframe(
    df_mapped, config, mapping, {'template_type': 'N'}
)

print(f"Validation complete: {summary['total_errors']} errors found")
```

This API provides comprehensive access to all validation functionality while maintaining clean separation of concerns and consistent error handling patterns.