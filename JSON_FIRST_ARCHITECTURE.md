# 🏗️ JSON-First Architecture - GHX Validatie Tool

## 🎯 Filosofie & Doel

**Mission Statement:** "IT rust = Alleen JSON updates na initiële deployment"

### ✅ **Wat we WILLEN (ideale toekomst):**
- **Python code = stabiel op server** (max 1x per kwartaal updates)
- **JSON files = flexibel aanpasbaar** (wekelijks/maandelijks)
- **Niels ↔ Mariska workflow = alleen JSON uitwisseling**
- **Geen Python kennis vereist bij IT team**

### ❌ **Wat we VERMIJDEN:**
- Elke keer nieuwe Python code deployen voor validatie wijzigingen
- IT team lastigvallen met code updates
- Afhankelijkheid van developer bij elke wijziging

---

## 📋 **Architectuur Principes**

### 1. **Single Source of Truth = JSON**
Alle bedrijfslogica moet configureerbaar zijn via JSON:
- ✅ Validatieregels (`field_validation_v20.json`)
- ✅ Foutcodes & messages (`error_code_descriptions`)
- ✅ Reference lists (`reference_lists.json`)
- ✅ Header mapping (`header_mapping.json`)
- 🔄 **Future:** Template logic, conditional rules, etc.

### 2. **Robuuste Python Foundation**
De Python code moet alle edge cases afhandelen ZONDER wijzigingen:
- ✅ NaN/None/null string handling
- ✅ Flexible JSON parsing
- ✅ Graceful error handling
- ✅ Backward compatibility

### 3. **Configuration-Driven Logic**
Geen hardcoded business rules in Python:
```python
# ❌ SLECHT - hardcoded
if field_name == "UNSPSC" and len(value) != 8:
    return error

# ✅ GOED - JSON driven
if condition == "is_not_exact_length_numeric":
    return validate_from_json_rule(rule)
```

---

## 🔧 **Implementation Status**

### ✅ **Al geïmplementeerd:**
- **Field validation rules** - Complete JSON configuratie
- **Error codes & messages** - Alle foutmeldingen in JSON
- **Reference lists** - Externe JSON met lijsten
- **Robuuste NaN handling** - Laatste code fix (oktober 2025)

### 🔄 **Toekomstige JSON uitbreidingen:**
- **Template-specific rules** - Per template type verschillende validaties
- **Dynamic conditional logic** - Complex afhankelijkheden via JSON
- **Custom validation functions** - Plugin-achtige JSON configuratie
- **Report formatting** - Layout & styling via JSON

---

## 📊 **Workflow na JSON-First**

### **Huidige situatie (voor fix):**
```
Validatie wijziging → Python code aanpassing → IT deployment → Testing → Live
```

### **Toekomstige situatie (na JSON-First):**
```
Validatie wijziging → JSON aanpassing → Upload naar server → Live
```

### **Praktisch voorbeeld:**
```
Nieuwe UNSPSC regel nodig:
1. Niels past field_validation_v20.json aan
2. Niels stuurt JSON naar Mariska
3. Mariska upload JSON naar server
4. Klaar - nieuwe validatie actief
```

---

## 🛡️ **Disaster Recovery**

### **JSON Backup Strategy:**
- Altijd previous version bewaren
- Git versioning voor alle JSON changes
- Quick rollback via oude JSON restore

### **Code Stability:**
- Python code wijzigt ALLEEN voor:
  - Critical bugs (zoals NaN handling)
  - Security updates
  - Performance improvements
  - **NIET voor business logic changes**

---

## 📚 **Developer Guidelines**

### **Voor Niels (JSON Updates):**
1. Test JSON wijzigingen lokaal eerst
2. Documenteer changes in commit messages
3. Stuur alleen complete JSON set naar IT
4. Bewaar backup van vorige versie

### **Voor IT Team (Deployment):**
1. Vervang alleen JSON files in `config/` directory
2. **NOOIT** Python files aanraken (tenzij expliciet gevraagd)
3. Restart service na JSON update
4. Bewaar backup van vorige JSON set

### **Voor Future Developers:**
- **Denk eerst:** "Kan dit via JSON configuratie?"
- Hardcode NOOIT business logic in Python
- Alle nieuwe features moeten JSON-configureerbaar zijn
- Code reviews moeten JSON-First principle checken

---

## 🎯 **Success Metrics**

**Goal:** Max 1 Python deployment per kwartaal na Q4 2025

**KPI's:**
- **JSON updates per maand:** 2-4 (acceptabel)
- **Python deployments per kwartaal:** ≤1 (target)
- **IT escalations per maand:** 0 (target)
- **Time to deploy validatie wijziging:** <30 min (target)

---

## 💡 **Best Practices**

### **JSON Design Patterns:**
```json
{
  "flexible_parameter": {
    "type": "configurable",
    "default_value": 5000,
    "description": "Can be changed without code deployment"
  },
  
  "business_rule": {
    "condition": "json_configurable_condition",
    "params": ["field1", "field2"],
    "message": "User-friendly error message"
  }
}
```

### **Python Defensive Coding:**
```python
def validate_field(config):
    # Graceful fallback for missing JSON keys
    rule_type = config.get("type", "default_validation")
    
    # Handle all possible JSON value types
    if isinstance(params, (list, dict, str, int, float)):
        # Process accordingly
    
    # Never crash on unexpected JSON structure
    try:
        return apply_rule(rule_type, params)
    except Exception as e:
        logging.warning(f"Graceful fallback: {e}")
        return default_validation()
```

---

**Laatste update:** 13 oktober 2025 - Na UNSPSC dubbeltelling fix  
**Status:** 🎯 Deployment ready for JSON-First architecture