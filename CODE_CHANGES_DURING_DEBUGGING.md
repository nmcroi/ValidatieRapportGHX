# 📝 CODE WIJZIGINGEN TIJDENS DEBUGGING SESSIE

**Datum**: 2025-09-28  
**Probleem**: AT template header mapping van 11/36 naar betere ratio  
**Status**: Wijzigingen hebben het systeem slechter gemaakt  

---

## 🔥 KRITIEKE VINDING: CLEAN_COLUMN_NAME KAPOT GEMAAKT

### **ORIGINELE VERSIE (werkend):** 
```python
def clean_column_name(col: str) -> str:
    """Schoont een kolomnaam op."""
    if not isinstance(col, str):
        return ''
    # Neem alleen deel voor newline, strip witruimte, maak lowercase
    return col.split('\n')[0].strip().lower()
```
**Regels code**: 5  
**Functionaliteit**: Simpel en werkt  

### **HUIDIGE VERSIE (kapot):**
```python
def clean_column_name(col: str) -> str:
    """Schoont een kolomnaam op voor mapping vergelijking."""
    if not isinstance(col, str):
        return ''
    
    # Vervang non-breaking spaces met normale spaces
    cleaned_col = col.replace('\xa0', ' ')
    
    # Split op newlines en verwerk alle regels
    lines = cleaned_col.split('\n')
    first_line = lines[0].strip()
    
    # Zoek naar haakjes op volgende regels en voeg toe aan eerste regel
    for line in lines[1:]:
        line = line.strip()
        if line.startswith('(') and line.endswith(')'):
            # Voeg haakjes toe aan eerste regel als het nog niet aanwezig is
            if line not in first_line:
                first_line = first_line.rstrip() + ' ' + line
            break  # Neem alleen de eerste haakjes
    
    # Intelligentere underscore behandeling - behoud volledige context voor belangrijke headers
    if '_' in first_line and not first_line.startswith('_'):
        # Lijst van prefixen die hun volledige naam moeten behouden
        keep_full_prefixes = ['artikel_', 'prijs_', 'unspsc_', 'gmdn_', 'emdn_', 'cas_', 'lot_', 'serie_', 'batch_', 'uom_', 'price_']
        
        # Check of dit een header is die volledig behouden moet worden
        should_keep_full = any(first_line.lower().startswith(prefix) for prefix in keep_full_prefixes)
        
        if should_keep_full:
            # Behoud volledige naam om mapping conflicts te voorkomen
            pass  # Geen truncatie voor belangrijke headers
        else:
            # Voor andere headers: gebruik oude truncatie logica
            first_line = first_line.split('_')[0].strip()
    
    return first_line.lower()
```
**Regels code**: 35+  
**Functionaliteit**: Complex en werkt NIET  

---

## 📝 WIJZIGING 1: HEADER_MAPPING.JSON UPDATES

### **Toegevoegde Multi-line Headers**

**Voor Stofnaam:**
```json
"Stofnaam": {
  "alternatives": [
    // ... bestaande alternatieven ...
    "Stofnaam\n(Voor Uni's)\n\nChemical Substance Name\n(For Universities)"
  ]
}
```

**Voor Brutoformule:**
```json
"Brutoformule": {
  "alternatives": [
    // ... bestaande alternatieven ...
    "Brutoformule\n(Voor Uni's)\n\nChemical formula\n(For Universities)"
  ]
}
```

**Status**: ✅ Partieel succesvol - deze specifieke headers zouden nu moeten mappen

---

## 📝 WIJZIGING 2: ORIGINAL_COLUMN_MAPPING FIXES

### **Probleem Geadresseerd**
Original_column_mapping werd niet correct gevuld voor onherkende headers, wat leidde tot verkeerde header weergave in rapporten.

### **Code Toevoeging**
```python
else:
    # Geen standaard header gevonden, gebruik originele (opgeschoonde?) naam
    # We gebruiken de *originele* naam in mapped_columns om te zorgen dat rename werkt
    mapped_columns[original_col] = original_col
    # BELANGRIJK: Ook voor onherkende headers moeten we de original_column_mapping vullen
    # Anders krijgen we in rapporten de verkeerde header weergegeven
    original_column_mapping[original_col] = original_col
    if not str(original_col).lower().startswith('algemeen'): # Negeer 'algemeen' kolom
         unrecognized.append(original_col) # Noteer als onherkend (indien niet 'algemeen')
```

**Status**: ✅ Deze fix zou correct moeten werken

---

## 📝 WIJZIGING 3: DEBUG LOGGING TOEVOEGINGEN

### **Debug Functions Toegevoegd**
- `test_template_detection()` - Template type detectie
- `debug_header_mapping()` - Gedetailleerde mapping analyse  
- Uitgebreide logging in mapping proces

**Status**: ✅ Handig voor debugging, geen negatieve impact

---

## 📊 IMPACT ANALYSE

### **Positieve Wijzigingen:**
1. ✅ **original_column_mapping fix** - Zou rapport weergave verbeteren
2. ✅ **Specifieke multi-line headers** - Stofnaam en Brutoformule zouden moeten mappen
3. ✅ **Debug tooling** - Helpt bij analyse

### **NEGATIEVE WIJZIGINGEN:**
1. ❌ **clean_column_name() complexiteit** - Van 5 naar 35+ regels
2. ❌ **"Intelligente" logica** - Haakjes processing die faalt
3. ❌ **Protected prefixes** - Complex underscore handling
4. ❌ **Multi-line processing** - Alleen eerste regel + haakjes logica

---

## 🎯 ROOT CAUSE ANALYSE

### **Waarom Mapping Ratio zo Slecht is (30.6%)**

1. **clean_column_name() is kapot** - Complexe logica werkt niet voor multi-line headers
2. **Alleen eerste regel wordt gebruikt** - `col.split('\n')[0]` mist context
3. **Haakjes logica faalt** - "(Voor Uni's)" wordt niet correct toegevoegd
4. **University patterns ontbreken** - Nog steeds veel "(Voor Uni's)" variants niet in mapping

### **Waarom Originele Versie Beter Was**
- **Simpel en voorspelbaar** - 5 regels, geen edge cases
- **Consistente output** - Altijd eerste regel, lowercase
- **Sneller** - Geen complexe conditionals
- **Minder bugs** - Minder code = minder problemen

---

## 🔄 AANBEVOLEN ROLLBACK

### **Terug naar Originele Versie**
```python
def clean_column_name(col: str) -> str:
    """Schoont een kolomnaam op."""
    if not isinstance(col, str):
        return ''
    return col.split('\n')[0].strip().lower()
```

### **Focus op Header_mapping.json Strategy**
In plaats van complex code schrijven, **uitbreiden van header_mapping.json** met:
- Alle "(Voor Uni's)" variants
- UOM prefix patterns  
- Multi-line alternatives
- EAN/BTW patterns

---

## 📋 CONCLUSIE

**De debugging sessie heeft geleid tot over-engineering** van de `clean_column_name()` functie. 

**Beter strategy**:
1. **Revert** naar simpele originele functie
2. **Uitbreiden** header_mapping.json met alle varianten  
3. **Fallback strategy** in mapping logic, niet in cleaning logic
4. **Test systematisch** met echte data

**Target**: Van 30.6% naar 80%+ mapping ratio door **data-driven** aanpak, niet code complexiteit.