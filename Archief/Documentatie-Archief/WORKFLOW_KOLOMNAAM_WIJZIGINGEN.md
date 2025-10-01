# 🔧 WORKFLOW: KOLOMNAAM WIJZIGINGEN & NIEUWE KOLOMMEN

Deze handleiding beschrijft **alle stappen** die nodig zijn om kolomnamen te wijzigen of nieuwe kolommen toe te voegen in het **volledige GHX systeem** (Template Generator + Validatie Tool).

## ⚠️ BELANGRIJK: IMPACTANALYSE
Bij elke kolomnaam wijziging raak je **meerdere systemen** tegelijk:
- **Template Generator** (genereert de Excel templates)  
- **Validatie Tool** (valideert ingevulde prijslijsten)
- **Dashboard & Rapporten** (toont statistieken en resultaten)

**Een incomplete wijziging kan leiden tot:**
- ❌ Mapping conflicts ("Artikel_Num" vs "Artikel_Latex" probleem)
- ❌ Inconsistente namen in charts ("UNSPSC" vs "UNSPSC Code")  
- ❌ Verkeerde mandatory fields tellingen
- ❌ Ontbrekende kolommen in rapporten

---

## 🎯 SCENARIO'S

### **A. NIEUWE KOLOM TOEVOEGEN**
☑️ Volg stappen 1-8 compleet

### **B. KOLOMNAAM WIJZIGEN**  
☑️ Volg stappen 2-8 + update bestaande namen in stap 9

### **C. KOLOM VERWIJDEREN**
☑️ Volg stappen 2-8 + cleanup in stap 10

---

## ✅ VOLLEDIGE CHECKLIST

**Template Generator Systeem:**
- [ ] **1. Field Mapping JSON** - Template Generator configuratie
- [ ] **2. Excel Validatiematrix** - Template Generator Excel (row 57)
- [ ] **3. Template Excel Files** - Headers in template bestanden

**Validatie Tool Systeem:**  
- [ ] **4. Field Validation JSON** - Validatieregels en veld definitie
- [ ] **5. Header Mapping JSON** - Kolom detectie mappings
- [ ] **6. Hardcoded Fallback Lists** - Python fallback lijsten  
- [ ] **7. Clean Column Name Logic** - String normalisatie functie

**Testing & Verificatie:**
- [ ] **8. Functionele Tests** - Beide systemen testen
- [ ] **9. Update Bestaande Namen** (alleen bij wijzigingen)
- [ ] **10. Cleanup** (alleen bij verwijderingen)

---

## 📋 GEDETAILLEERDE STAPPEN

### **STAP 1: Template Generator - Field Mapping JSON**
📁 `Template Generator Files/config/field_mapping.json`

Voor nieuwe kolommen - voeg configuratie toe:
```json
"Nieuwe Kolomnaam": {
  "col": "XX",                    // Volgende beschikbare kolom letter
  "visible": "always",            // of visible_only/visible_except  
  "mandatory": "never",           // of always/mandatory_only/mandatory_except
  "depends_on": [],              // Optioneel: dependencies
  "notes": "Beschrijving van de kolom"
}
```

**Voor wijzigingen:** Pas de bestaande entry aan.

---

### **STAP 2: Template Generator - Excel Validatiematrix**
📁 `Template Generator Files/templates/GHX Prijstemplate Validatiematrix v9TG.xlsx`

**Handmatige actie vereist:**
1. Open Excel file
2. Ga naar **row 57**, vind kolom XX  
3. Voeg/update JSON snippet:
```json
{
  "col": "XX",
  "visible": "always", 
  "notes": "Beschrijving van de kolom"
}
```

---

### **STAP 3: Template Generator - Template Excel Files**
📁 `Template Generator Files/templates/GHXstandaardTemplate v25.1.xlsx`
📁 `Template Generator Files/templates/template_staffel.xlsx`

**Handmatige actie vereist:**
1. Open template files
2. Ga naar kolom XX (bijv. kolom BA)
3. Voeg/update header in **row 1**: "Nieuwe Kolomnaam"
4. Optioneel: Nederlandse vertaling in **row 2**
5. Sla beide files op

---

### **STAP 4: Validatie Tool - Field Validation JSON**
📁 `field_validation_v20.json`

⚠️ **KRITIEK**: Deze bepaalt de **volgorde van alle 103 GHX kolommen** in rapporten!

**Voor nieuwe kolom - voeg toe in JUISTE VOLGORDE:**
```json
"field_validations": {
  "Nieuwe Kolomnaam": {
    "data_format": "string",
    "rules": [
      {
        "condition": "max_length",
        "code": "75", 
        "params": 50,
        "message": "Nieuwe Kolomnaam mag maximaal 50 karakters bevatten."
      }
    ]
  }
}
```

**Voor wijziging:** Update de bestaande key name en alle referenties.

**⚠️ Let op:** De volgorde in dit bestand bepaalt de volgorde in Sheet 8 "Kolom Mapping"!

---

### **STAP 5: Validatie Tool - Header Mapping JSON**  
📁 `header_mapping.json`

Voor kolom detectie mappings:
```json
"Nieuwe Kolomnaam": {
  "alternatives": [
    "Nieuwe Kolomnaam",
    "New Column Name", 
    "Alternative Name",
    "Variant Name"
  ],
  "case_sensitive": false,
  "strip_whitespace": true
}
```

**Voor wijziging:** Update de key name en voeg oude naam toe als alternative.

---

### **STAP 6: Validatie Tool - Hardcoded Fallback Lists**
📁 `validator/mandatory_fields.py`  
📁 `validator/price_tool.py`

⚠️ **KRITIEK PROBLEEM ONTDEKT**: Er zijn **meerdere** hardcoded fallback lijsten die synchroon gehouden moeten worden!

**6a. Mandatory Fields Fallback (mandatory_fields.py:229):**
```python
def get_fallback_mandatory_fields() -> List[str]:
    return [
        "Artikelnummer",
        "Artikelnaam", 
        "Omschrijving",
        "Brutoprijs",
        "Nettoprijs",
        # ... andere velden
        "Nieuwe Kolomnaam",  # Voeg toe indien mandatory
        # ... rest van lijst
    ]
```

**6b. Price Tool Fallback (price_tool.py:1144):**
```python 
def get_fallback_mandatory_fields() -> List[str]:
    return [
        "Artikelnummer", "Artikelnaam", "Brutoprijs", "Nettoprijs",
        # ... andere velden
        "Nieuwe Kolomnaam",  # Voeg toe indien mandatory  
        # ... rest van lijst
    ]
```

**⚠️ SYNC VEREIST**: Beide lijsten moeten identiek zijn! De "UNSPSC" vs "UNSPSC Code" bug kwam door inconsistentie hier.

---

### **STAP 7: Validatie Tool - Clean Column Name Logic**
📁 `validator/price_tool.py` (regels 1336-1351)

⚠️ **KRITIEK**: Als nieuwe kolomnaam **underscores** bevat, voeg toe aan protected prefixes!

**Probleem:** `clean_column_name()` trunceert headers bij underscores:
- `UOM_Base` → `uom` (FOUT!)
- `Artikel_Num` → `artikel` (FOUT!)

**Oplossing:** Voeg prefix toe aan `keep_full_prefixes`:
```python
keep_full_prefixes = [
    'artikel_', 'prijs_', 'unspsc_', 'gmdn_', 'emdn_', 
    'cas_', 'lot_', 'serie_', 'batch_', 'uom_', 'price_',
    'nieuwe_',  # Voeg toe voor "Nieuwe_Kolomnaam"
]
```

**Check nodig bij:** Elke kolomnaam met underscores!

---

### **STAP 8: Testing & Verificatie**

**8a. Template Generator Test:**
```bash
cd "Template Generator Files"
python flask_api.py
# Test API endpoint met verschillende contexten
```

**8b. Validatie Tool Test:**
```bash
cd "Validation Tool"
streamlit run prijslijst_validatie_app.py
# Upload test bestand met nieuwe kolom
```

**8c. Verificatie Tools:**
```bash
# Check Template Generator sync
cd "Template Generator Files"  
python debug/compare_mapping_excel.py

# Check kolom volgorde in rapporten
grep -n "Nieuwe Kolomnaam" field_validation_v20.json
```

**8d. End-to-End Test:**
1. Genereer template met Template Generator
2. Vul template in met test data  
3. Valideer met Validatie Tool
4. Controleer dat kolom verschijnt in:
   - Dashboard statistieken
   - Sheet 8 "Kolom Mapping" (in juiste volgorde!)
   - Charts en grafieken
   - Ontbrekende verplichte kolommen tabel

---

### **STAP 9: Update Bestaande Namen (alleen bij wijzigingen)**

Bij kolomnaam wijzigingen zoek en vervang **overal**:

```bash
# Zoek alle referenties naar oude naam
grep -r "Oude Kolomnaam" .

# Check deze specifieke locaties:
# - field_validation_v20.json (key name + referenties)
# - header_mapping.json (key name, behoud oude als alternative)  
# - mandatory_fields.py (fallback lijsten)
# - price_tool.py (fallback lijsten + dtype_spec mappings)
# - rapport_utils.py (chart data sources)
# - validation_engine.py (field processing logic)
```

**⚠️ TESTCASE**: Upload een bestand met **oude** kolomnaam om backward compatibility te testen.

---

### **STAP 10: Cleanup (alleen bij verwijderingen)**

Bij kolom verwijdering:
1. Verwijder uit alle JSON configs
2. Verwijder uit alle fallback lijsten  
3. Verwijder uit protected prefixes (indien van toepassing)
4. Update Excel templates
5. Test dat systeem niet crasht bij bestanden met oude kolom

---

## 🚨 VEEL VOORKOMENDE PROBLEMEN & OPLOSSINGEN

### **❌ Problem: Mapping Conflict**
**Symptoom:** "Artikel_Num" en "Artikel_Latex" mappen beide naar "artikel"
**Oorzaak:** `clean_column_name()` trunceert bij eerste underscore
**Oplossing:** Voeg prefix toe aan `keep_full_prefixes` in price_tool.py:1342

### **❌ Problem: Inconsistente Namen in Charts**  
**Symptoom:** Chart toont "UNSPSC" maar config heeft "UNSPSC Code"
**Oorzaak:** Meerdere fallback lijsten zijn niet gesynchroniseerd
**Oplossing:** Update ALLE fallback lijsten in stap 6a+6b

### **❌ Problem: Verkeerde Kolom Volgorde in Sheet 8**
**Symptoom:** Sheet 8 begint met verkeerde kolom of heeft verkeerde volgorde
**Oorzaak:** `field_validation_v20.json` bepaalt volgorde voor rapport generatie
**Oplossing:** Plaats nieuwe kolom op juiste positie in JSON (stap 4)

### **❌ Problem: Mandatory Fields Count Klopt Niet**
**Symptoom:** Dashboard toont verkeerd aantal mandatory fields  
**Oorzaak:** Nieuwe mandatory field niet toegevoegd aan fallback lijsten
**Oplossing:** Update beide fallback lijsten (stap 6a+6b)

### **❌ Problem: Header Niet Gedetecteerd**
**Symptoom:** Kolom wordt niet herkend ondanks juiste naam
**Oorzaak:** Ontbreekt in `header_mapping.json` of `clean_column_name()` probleem
**Oplossing:** Controleer stap 5 + stap 7

### **❌ Problem: Template Genereert Kolom Niet**
**Symptoom:** Kolom verschijnt niet in gegenereerde templates
**Oorzaak:** Ontbreekt in Template Generator configuratie  
**Oplossing:** Controleer stap 1 + stap 2 + stap 3

---

## 🔄 ROLLBACK PROCEDURE

**Template Generator:**
```bash
cd "Template Generator Files"
git checkout HEAD -- config/field_mapping.json
# Handmatig Excel files terugzetten (row 57 + headers)
```

**Validatie Tool:**
```bash
git checkout HEAD -- field_validation_v20.json header_mapping.json
git checkout HEAD -- validator/mandatory_fields.py validator/price_tool.py
```

---

## 📊 IMPACT MATRIX

| Wijziging Type | Template Generator | Validatie Tool | Dashboard | Rapporten |
|---|---|---|---|---|
| **Nieuwe kolom** | Stap 1-3 | Stap 4-7 | Auto | Stap 4 (volgorde) |
| **Naam wijziging** | Stap 1-3 | Stap 4-7 + Stap 9 | Stap 9 | Stap 4 + 9 |
| **Kolom verwijderen** | Stap 1-3 | Stap 10 | Stap 10 | Stap 10 |
| **Mandatory status** | Stap 1 | Stap 6a+6b | Auto | Auto |

---

## 📚 GERELATEERDE FILES OVERZICHT

**Template Generator Files:**
- `config/field_mapping.json` - Hoofdconfiguratie TG
- `templates/GHXstandaardTemplate v25.1.xlsx` - Template bestand
- `templates/template_staffel.xlsx` - Staffel template  
- `templates/GHX Prijstemplate Validatiematrix v9TG.xlsx` - Validatiematrix

**Validatie Tool Files:**  
- `field_validation_v20.json` - ⚠️ Bepaalt kolom volgorde + validaties
- `header_mapping.json` - Kolom detectie mapping
- `validator/mandatory_fields.py` - ⚠️ Fallback lijst #1
- `validator/price_tool.py` - ⚠️ Fallback lijst #2 + clean_column_name()
- `validator/rapport_utils.py` - Rapport generatie logic  
- `validator/validation_engine.py` - Validatie processing

**Critical Sync Points:**
🔄 `mandatory_fields.py:229` ↔ `price_tool.py:1144` (fallback lijsten)
🔄 `field_validation_v20.json` ↔ TG `field_mapping.json` (kolom namen)  
🔄 Template Excel headers ↔ JSON configuraties

---

## 💡 BEST PRACTICES

1. **Maak altijd backups** voordat je begint
2. **Test beide systemen** na elke wijziging  
3. **Gebruik git branches** voor grote wijzigingen
4. **Documenteer wijzigingen** in commit messages
5. **Test backward compatibility** met oude bestanden
6. **Controleer alle fallback lijsten** op consistency  
7. **Verificeer kolom volgorde** in rapporten
8. **Test met verschillende template contexten**

---

## 🆘 TROUBLESHOOTING SNELGIDS

**Kolom wordt niet gedetecteerd:**
1. Check `header_mapping.json` (stap 5)
2. Check `clean_column_name()` voor underscore truncatie (stap 7)  
3. Check case sensitivity & whitespace

**Verkeerde mandatory count:**
1. Check beide fallback lijsten synchroon (stap 6a+6b)
2. Check field_validation_v20.json (stap 4)

**Kolom verkeerde volgorde:**  
1. Check positie in `field_validation_v20.json` (stap 4)
2. Rapporten gebruiken deze JSON voor volgorde

**Template mist kolom:**
1. Check TG field_mapping.json (stap 1)  
2. Check Excel validatiematrix row 57 (stap 2)
3. Check template Excel headers (stap 3)

---

**📞 Contact:** Documenteer nieuwe issues voor toekomstige reference. Deze workflow is gebaseerd op real-world debugging van AT template validatie problemen (UNSPSC naming, mapping conflicts, Sheet 8 ordering).