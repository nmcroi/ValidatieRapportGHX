# Documentation Index

This directory contains comprehensive documentation for the GHX Price Validation Tool's clean architecture implementation.

## 📚 **Documentation Overview**

### Core Development Guide
- **[🏗️ DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - Complete development documentation
  - System architecture and clean design principles
  - TG→N→O template detection philosophy  
  - Complete validation pipeline workflow
  - Quality scoring system and Quick Mode
  - Module structure and integration points
  - Development guidelines and debugging

### Template Detection System
- **[🌳 TEMPLATE_DETECTION.md](TEMPLATE_DETECTION.md)** - Detailed template detection logic
  - TG→N→O decision tree implementation
  - Stamp parsing and pattern recognition
  - Template characteristics and processing differences
  - Performance considerations and testing utilities

### Configuration Management
- **[⚙️ CONFIGURATION.md](../Configuratie/CONFIGURATION.md)** - Configuration system
- **[📋 Handleiding_JSON.md](../Configuratie/Handleiding_JSON.md)** - Complete field_validation_v20.json guide
  - JSON configuration file structure and relationships
  - Template Generator synchronization
  - Configuration validation and security
  - Environment-specific configurations

### API Reference
- **[📚 API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation
  - All public functions and their parameters
  - Usage examples and code snippets
  - Error handling and return value documentation
  - Integration patterns and best practices

## 🎯 **Quick Start Guide**

1. **New to the system?** Start with [ARCHITECTURE.md](ARCHITECTURE.md) for the big picture
2. **Understanding templates?** Read [TEMPLATE_DETECTION.md](TEMPLATE_DETECTION.md) for the TG→N→O logic
3. **Need to validate data?** Follow [VALIDATION_PIPELINE.md](VALIDATION_PIPELINE.md) for the process
4. **Configuring the system?** Refer to [CONFIGURATION.md](CONFIGURATION.md) for setup
5. **Building integrations?** Use [API_REFERENCE.md](API_REFERENCE.md) for function details

## 🏗️ **Architecture at a Glance**

```
Template Detection (TG→N→O)
         ↓
Context Extraction & Configuration Loading
         ↓
Data Processing & Header Mapping
         ↓
Field Logic Application
         ↓
Validation Execution
         ↓
Report Generation
```

## 📈 **Template Types Summary**

| Type | Detection Method | Processing | Use Case |
|------|------------------|------------|----------|
| **TG** | GHX_STAMP in A1/headers | Dynamic metadata-driven | Template Generator files |
| **N** | Modern column markers | Standard GHX validation | Post-Nov 2024 templates |
| **O** | Fallback detection | Header mapping required | Legacy/custom templates |

## 🔧 **Key Features**

- **Template-Aware**: Intelligent processing based on template type
- **Modular Design**: Clean separation of concerns with dependency injection
- **Configuration-Driven**: Flexible JSON-based rule system
- **Institution-Specific**: Support for NFU hospitals, research institutes
- **Performance Optimized**: Lazy loading and efficient processing
- **Comprehensive Testing**: Extensive validation and error handling

## 🚀 **Getting Started**

```python
# Quick validation example
from validator import validate_pricelist

report_path = validate_pricelist(
    "data/template.xlsx",
    original_input_filename="my_pricelist.xlsx"
)
print(f"Validation completed: {report_path}")
```

## 🔄 **Continuous Improvement**

This documentation is maintained alongside the codebase to ensure accuracy and completeness. Each major feature addition includes corresponding documentation updates.

For questions or clarifications, refer to the specific documentation files or the comprehensive API reference.