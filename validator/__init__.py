"""
GHX Price Validation Tool - Clean Architecture Modules

Deze package bevat de modulaire clean architecture implementatie van de GHX prijslijst validatie tool.
"""

# Template Detection
from .template_detector import determine_template_type, has_template_generator_stamp, test_template_detection

# Configuration Management  
from .config_manager import load_field_mapping, load_institution_codes, get_fallback_institution_codes

# Template Context
from .template_context import extract_template_generator_context, parse_template_code

# Mandatory Fields
from .mandatory_fields import determine_mandatory_fields_for_template, validate_mandatory_field_count

# Field Logic
from .field_logic import apply_field_visibility, evaluate_field_visibility, evaluate_field_mandatory

# Data Processing
from .data_processor import map_headers, clean_dataframe, normalize_template_header

# Validation Engine
from .validation_engine import validate_pricelist, validate_dataframe

# Debug Tools
from .debug_tools import debug_field_mapping_decisions, debug_template_detection_flow

# Utils
from .utils import safe_get_nested_value, is_empty_value, format_error_message

__version__ = "2.0.0"
__author__ = "GHX Healthcare Exchange"