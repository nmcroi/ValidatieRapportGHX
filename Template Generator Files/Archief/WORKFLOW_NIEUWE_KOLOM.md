# 🔧 WORKFLOW: NIEUWE KOLOM TOEVOEGEN AAN TEMPLATE GENERATOR

Deze handleiding beschrijft **alle stappen** die nodig zijn om een nieuwe kolom toe te voegen aan het GHX Template Generator systeem.

## ✅ CHECKLIST OVERZICHT

- [ ] **1. Field Mapping JSON** - Veld configuratie toevoegen
- [ ] **2. Excel Validatiematrix** - JSON snippet toevoegen (row 57)  
- [ ] **3. Template Excel** - Header toevoegen
- [ ] **4. Field Validation** - Validatieregels toevoegen (optioneel)
- [ ] **5. Tests** - Functionaliteit testen

---

## 📋 GEDETAILLEERDE STAPPEN

### **STAP 1: Field Mapping JSON** 
📁 `config/field_mapping.json`

Voeg de nieuwe veld configuratie toe:

```json
"Nieuwe Veldnaam": {
  "col": "XX",                    // Volgende beschikbare kolom letter
  "visible": "always",            // of visible_only/visible_except
  "mandatory": "never",           // of always/mandatory_only/mandatory_except
  "depends_on": [],              // Optioneel: dependencies
  "notes": "Beschrijving van het veld"
}
```

**Visibility opties:**
- `"visible": "always"` - Altijd zichtbaar
- `"visible": "never"` - Altijd verborgen  
- `"visible_only": ["label1", "label2"]` - Alleen zichtbaar voor specifieke labels
- `"visible_except": ["label1"]` - Zichtbaar behalve voor specifieke labels

**Mandatory opties:**
- `"mandatory": "always"` - Altijd verplicht
- `"mandatory": "never"` - Nooit verplicht
- `"mandatory_only": ["label1"]` - Verplicht alleen voor specifieke labels  
- `"mandatory_except": ["label1"]` - Verplicht behalve voor specifieke labels

**Context Labels:**
- Product types: `"medisch"`, `"lab"`, `"facilitair"`, `"overige"`
- GS1 modes: `"gs1"`, `"gs1_only"`, `"none"`
- Template: `"staffel"`
- Terminologie: `"orderable_true"`, `"orderable_false"`
- Features: `"chemicals"`
- Instellingen: instelling namen zoals `"UMCU"`, `"LUMC"`

---

### **STAP 2: Excel Validatiematrix**
📁 `templates/GHX Prijstemplate Validatiematrix v9TG.xlsx`

**Handmatige actie vereist:**
1. Open Excel file
2. Ga naar **row 57** 
3. Vind de kolom letter (bijv. kolom XX)
4. Voeg JSON snippet toe:

```json
{
  "col": "XX",
  "visible": "always",
  "notes": "Beschrijving van het veld"
}
```

**Verificatie:** Gebruik `python debug/compare_mapping_excel.py` om verschillen te checken.

---

### **STAP 3: Template Excel Files**
📁 `templates/GHXstandaardTemplate v25.1.xlsx`  
📁 `templates/template_staffel.xlsx`

**Handmatige actie vereist:**
1. Open template file(s)
2. Ga naar kolom XX (bijv. kolom BA)
3. Voeg header toe in **row 1**: "Nieuwe Veldnaam"
4. Optioneel: voeg Nederlandse vertaling toe in **row 2**
5. Sla op

---

### **STAP 4: Field Validation (Optioneel)**
📁 `../field_validation_v20.json` (in parent directory)
📁 `../header_mapping.json` (voor kolom detectie)

Voor inhoudelijke validaties voeg toe:

**4a. Field Validation Rules:**
```json
"Nieuwe Veldnaam": {
  "data_format": "string",
  "rules": [
    {
      "condition": "max_length",
      "code": "XXX",
      "params": 50,
      "message": "Nieuwe Veldnaam mag maximaal 50 karakters bevatten."
    }
  ]
}
```

**4b. Header Mapping (voor kolom detectie):**
```json
"Nieuwe Veldnaam": {
  "alternatives": [
    "Nieuwe Veldnaam",
    "New Field Name",
    "Alternative Name"
  ],
  "case_sensitive": false,
  "strip_whitespace": true
}
```

---

### **STAP 5: Testing**

**Functionele test:**
1. Start Flask API: `python flask_api.py`
2. Test met verschillende context configuraties:
   - GS1 only
   - Verschillende product types 
   - Met/zonder chemicals
   - Verschillende instellingen

**Verificatie tools:**
```bash
# Check mapping vs Excel verschillen
python debug/compare_mapping_excel.py

# Test specific context
curl -X POST http://localhost:8080/api/generate-template \
  -H "Content-Type: application/json" \
  -d '{
    "template_choice": "standard",
    "gs1_mode": "gs1", 
    "all_orderable": true,
    "product_types": ["medisch"],
    "has_chemicals": false,
    "is_staffel_file": false,
    "institutions": ["universitair_medisch_centrum_utrecht_(umc_utrecht)"]
  }'
```

---

## 🎯 VEELGEMAAKTE FOUTEN

### ❌ **Kolom letter conflict**
Zorg dat de kolom letter niet al gebruikt wordt:
```bash
grep -r '"col": "XX"' config/field_mapping.json
```

### ❌ **Excel sync probleem**  
Na field_mapping.json update altijd Excel updaten:
```bash
python debug/compare_mapping_excel.py  # Check verschillen
```

### ❌ **Template header vergeten**
Zonder header in template Excel wordt kolom niet correct gegenereerd.

### ❌ **Context label fout**
Gebruik alleen bestaande labels. Check `src/context.py` voor geldige labels.

### ❌ **Kolom volgorde in validatie rapporten**
**BELANGRIJK:** Validatie rapporten hebben verschillende logica voor kolom volgorde:

- **Sheet 6 "Optionele %"**: Gebruikt `non_mandatory_fields` uit config
- **Sheet 7 "Dataset Validatie"**: Gebruikt `visible_list` uit Template Generator decisions

**Mogelijke problemen:**
1. Kolom staat wel in TG template maar niet in input data
2. Kolom staat wel in `visible_list` maar niet als optional in config
3. Kolom volgorde verschilt tussen sheets

**Diagnose:** Controleer beide bronnen:
```bash
# Check Template Generator audit logs
ls -la audit/template_*.json

# Check field classification in rapport_utils.py lijn 982-992
grep -A 10 -B 5 "non_mandatory_fields.*=" ../validator/rapport_utils.py
```

---

## 🔄 ROLLBACK PROCEDURE

Als er problemen zijn:

1. **Revert field_mapping.json**
   ```bash
   git checkout HEAD -- config/field_mapping.json
   ```

2. **Excel handmatig terugzetten**
   - Verwijder JSON snippet uit row 57, kolom XX

3. **Template headers verwijderen**
   - Verwijder header uit template Excel files

---

## 📚 GERELATEERDE FILES

**Core configuratie:**
- `config/field_mapping.json` - Hoofdconfiguratie
- `src/mapping.py` - Validation logic
- `src/context.py` - Context labels
- `src/engine.py` - Template generation logic

**Templates:**
- `templates/GHXstandaardTemplate v25.1.xlsx`
- `templates/template_staffel.xlsx` 
- `templates/GHX Prijstemplate Validatiematrix v9TG.xlsx`

**Validation:**
- `../field_validation_v20.json` - Content validation rules
- `../header_mapping.json` - Column detection mapping
- `../validator/rapport_utils.py` - Report generation logic (kolom volgorde)

**Tools:**
- `debug/compare_mapping_excel.py` - Check mapping vs Excel sync
- `debug/check_excel_row57.py` - Check specific Excel areas
- `debug/validate_field_mapping.py` - Validate field mapping consistency

---

## 💡 TIPS

1. **Werk systematisch** - Volg alle stappen in volgorde
2. **Test direct** - Test na elke wijziging  
3. **Gebruik tools** - De verificatie scripts helpen fouten voorkomen
4. **Documenteer** - Update deze workflow als er nieuwe stappen bijkomen

---

**📞 Contact:** Bij vragen of problemen, documenteer het issue voor toekomstige reference.