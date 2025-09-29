# Configuration Management

## 📋 **Configuration Overview**

The GHX Price Validation Tool uses a sophisticated configuration system that supports multiple JSON configuration files, each serving specific purposes in the validation pipeline. The configuration architecture is designed for flexibility, maintainability, and synchronization with external systems.

## 🗂️ **Configuration Files Structure**

```
Project Root/
├── field_validation_v20.json      # Core field validation rules
├── header_mapping.json            # Legacy template header mapping  
├── reference_lists.json           # Value validation lists
└── Template Generator Files/
    ├── field_mapping.json          # TG field definitions
    └── institution_codes.json      # Institution code mappings
```

## 📄 **Configuration File Details**

### 1. field_validation_v20.json
**Purpose:** Core field validation rules and business logic

```json
{
  "version": "v20",
  "template_config": {
    "default_template": {
      "mandatory_fields": [
        "Artikelnummer", "Artikelnaam", "Omschrijving",
        "Brutoprijs", "Nettoprijs", "Eenheid", "Verpakkingseenheid",
        "Producent", "Leverancier", "Leveranciernummer",
        "Catalogusnummer Producent", "GTIN", "Product groep",
        "Sub categorie", "Geregistreerd geneesmiddel",
        "MDR/MDD Klasse", "Conditie"
      ]
    }
  },
  "fields": {
    "Artikelnummer": {
      "col": "A",
      "visibility": {
        "show_if": ["all"]
      },
      "mandatory": {
        "always": true
      },
      "validation": {
        "required": true,
        "data_type": "text",
        "max_length": 50,
        "pattern": "^[A-Za-z0-9\\-_\\.]+$"
      }
    },
    "ADR Gevarenklasse": {
      "col": "AT",
      "visibility": {
        "show_if": ["chemicals", "medical"]
      },
      "mandatory": {
        "if": ["chemicals"],
        "depends_on": "Geregistreerd geneesmiddel == Ja"
      },
      "validation": {
        "data_type": "text",
        "reference_list": "adr_classes"
      }
    }
  }
}
```

**Key Sections:**
- `version`: Configuration format version
- `template_config`: Template-level settings
- `fields`: Individual field definitions with validation rules

### 2. header_mapping.json  
**Purpose:** Maps legacy template headers to standard GHX field names

```json
{
  "version": "1.0",
  "standard_headers": {
    "Artikelnummer": {
      "alternatives": [
        "Product Code",
        "Item Number", 
        "Artikel Nr",
        "SKU",
        "Product ID"
      ]
    },
    "Eenheidscode Gewicht": {
      "alternatives": [
        "Weight Unit",
        "Gewicht Eenheid",
        "Unit of Weight",
        "Gewichtseenheid"
      ]
    }
  }
}
```

**Usage:**
- Used only for 'O' (Oude/Alternative) templates
- Enables legacy template compatibility
- Supports fuzzy header matching

### 3. reference_lists.json
**Purpose:** Defines allowed values for validation

```json
{
  "version": "1.0",
  "lists": {
    "adr_classes": [
      "Klasse 1", "Klasse 2", "Klasse 3", "Klasse 4.1",
      "Klasse 4.2", "Klasse 4.3", "Klasse 5.1", "Klasse 5.2",
      "Klasse 6.1", "Klasse 6.2", "Klasse 7", "Klasse 8", "Klasse 9"
    ],
    "units": [
      "stuk", "gram", "kilogram", "liter", "milliliter",
      "meter", "centimeter", "millimeter", "pack", "box"
    ],
    "yes_no_values": ["Ja", "Nee", "Yes", "No", "1", "0"]
  }
}
```

### 4. Template Generator Files/field_mapping.json
**Purpose:** Template Generator field definitions (synchronized)

```json
{
  "version": "25.1",
  "last_updated": "2024-11-15",
  "sync_source": "GHX Template Generator System",
  "field_definitions": {
    "A": {
      "field_name": "Artikelnummer",
      "required": true,
      "data_type": "text"
    },
    "B": {
      "field_name": "Artikelnaam", 
      "required": true,
      "data_type": "text"
    }
  }
}
```

### 5. Template Generator Files/institution_codes.json
**Purpose:** Institution code mappings and metadata

```json
{
  "version": "2024.3",
  "last_updated": "2024-09-15",
  "institution_mapping": {
    "umcu": {
      "name": "UMC Utrecht",
      "type": "nfu_hospital",
      "region": "Utrecht",
      "contact": "procurement@umcutrecht.nl"
    },
    "ul": {
      "name": "Universiteit Leiden",
      "type": "research_institute", 
      "region": "Zuid-Holland",
      "contact": "inkoop@leidenuniv.nl"
    }
  }
}
```

## ⚙️ **Configuration Loading System**

### Config Manager Module
```python
# validator/config_manager.py

def load_field_mapping() -> Optional[Dict[str, Any]]:
    """
    Loads field validation configuration with error handling.
    """
    try:
        config_path = "field_validation_v20.json"
        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
            validate_config_schema(config)
            return config
    except Exception as e:
        logging.error(f"Failed to load field mapping: {e}")
        return None

def detect_json_version(config: Dict) -> str:
    """
    Auto-detects configuration format version.
    """
    if 'version' in config:
        return config['version']
    elif 'fields' in config and isinstance(config['fields'], dict):
        return "v20"  # Modern format
    else:
        return "v18"  # Legacy format
```

### Configuration Validation
```python
def validate_configuration_consistency(configs: Dict[str, Any]) -> bool:
    """
    Validates consistency across all configuration files.
    """
    checks = [
        validate_field_mapping_completeness(configs),
        validate_reference_list_integrity(configs),
        validate_institution_code_consistency(configs),
        validate_header_mapping_coverage(configs)
    ]
    
    return all(checks)
```

## 🔄 **Template Generator Synchronization**

### Sync Process
```python
def sync_template_generator_files():
    """
    Synchronizes local configs with Template Generator system.
    """
    # 1. Check for updates in Template Generator Files/
    tg_files = scan_template_generator_directory()
    
    # 2. Compare versions and timestamps
    local_version = get_local_config_version()
    remote_version = get_remote_config_version(tg_files)
    
    # 3. Update if newer version available
    if remote_version > local_version:
        update_local_configurations(tg_files)
        logging.info(f"Configurations updated to version {remote_version}")
```

### Configuration Versioning
```python
class ConfigVersion:
    def __init__(self, major: int, minor: int, patch: int = 0):
        self.major = major
        self.minor = minor  
        self.patch = patch
    
    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def is_compatible_with(self, other: 'ConfigVersion') -> bool:
        """Check backward compatibility."""
        return self.major == other.major
```

## 🎯 **Configuration Best Practices**

### 1. Schema Validation
```python
import jsonschema

field_validation_schema = {
    "type": "object",
    "required": ["version", "fields"],
    "properties": {
        "version": {"type": "string"},
        "fields": {
            "type": "object",
            "patternProperties": {
                "^.*$": {
                    "type": "object",
                    "properties": {
                        "col": {"type": "string"},
                        "visibility": {"type": "object"},
                        "mandatory": {"type": "object"},
                        "validation": {"type": "object"}
                    }
                }
            }
        }
    }
}

def validate_config_schema(config: Dict):
    jsonschema.validate(config, field_validation_schema)
```

### 2. Environment-Specific Configurations
```python
def load_environment_config(env: str = "production"):
    """
    Load environment-specific configuration overlays.
    """
    base_config = load_field_mapping()
    
    env_config_path = f"config/env/{env}.json"
    if os.path.exists(env_config_path):
        with open(env_config_path, 'r') as f:
            env_overrides = json.load(f)
            merge_configurations(base_config, env_overrides)
    
    return base_config
```

### 3. Configuration Caching
```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=1)
def get_cached_field_mapping():
    """Cache configuration with TTL."""
    return load_field_mapping()

def clear_config_cache():
    """Clear cache when configurations are updated."""
    get_cached_field_mapping.cache_clear()
```

## 🔐 **Configuration Security**

### 1. Input Validation
```python
def sanitize_config_input(config: Dict) -> Dict:
    """
    Sanitizes configuration input to prevent injection attacks.
    """
    # Remove potentially dangerous patterns
    dangerous_patterns = ['eval', 'exec', '__import__', 'subprocess']
    
    def clean_value(value):
        if isinstance(value, str):
            for pattern in dangerous_patterns:
                if pattern in value.lower():
                    raise SecurityError(f"Dangerous pattern detected: {pattern}")
        return value
    
    return recursive_apply(config, clean_value)
```

### 2. Configuration Backup
```python
def backup_configurations():
    """
    Creates timestamped backup of all configuration files.
    """
    backup_dir = f"config/backups/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    config_files = [
        "field_validation_v20.json",
        "header_mapping.json", 
        "reference_lists.json"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            shutil.copy2(config_file, backup_dir)
```

## 📊 **Configuration Monitoring**

### Health Checks
```python
def perform_config_health_check() -> Dict[str, bool]:
    """
    Performs comprehensive configuration health check.
    """
    health_status = {}
    
    # Check file existence
    health_status['files_exist'] = all_config_files_exist()
    
    # Check JSON validity
    health_status['valid_json'] = all_configs_valid_json()
    
    # Check schema compliance
    health_status['schema_valid'] = all_configs_schema_compliant()
    
    # Check cross-references
    health_status['references_valid'] = all_cross_references_valid()
    
    # Check synchronization
    health_status['sync_current'] = template_generator_sync_current()
    
    return health_status
```

### Configuration Metrics
```python
config_metrics = {
    'total_fields_defined': 127,
    'mandatory_fields_count': 17,
    'conditional_fields_count': 23,
    'reference_lists_count': 8,
    'institution_codes_count': 12,
    'header_alternatives_count': 234,
    'last_sync_timestamp': '2024-09-28T10:30:00Z',
    'config_version': 'v20.1.3'
}
```

This configuration management system provides a robust, flexible, and maintainable foundation for the validation system while ensuring consistency, security, and synchronization with external systems.