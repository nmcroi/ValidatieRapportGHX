# 🎯 HEADER CLEANING STRATEGY DEFINITIE

**Datum**: 2025-09-28  
**Probleem**: AT template mapping 11/36 (30.6%) → target 80%+  
**Gekozen Strategy**: **FALLBACK STRATEGY** (Simpel + Data-driven)

---

## 📊 STRATEGY VERGELIJKING

### ❌ **SMART PARSING (Huidige - Gefaald)**
```python
# 35+ regels complexe logica
def clean_column_name(col: str) -> str:
    # Complex haakjes processing
    # "Intelligente" underscore handling  
    # Protected prefixes arrays
    # Multi-line processing
    # Edge case handling
```

**Problemen:**
- ❌ Over-engineered (5 → 35+ regels)
- ❌ Onvoorspelbare output
- ❌ Moeilijk te debuggen
- ❌ Edge cases creëren nieuwe bugs
- ❌ Performance impact

### ✅ **FALLBACK STRATEGY (Aanbevolen)**
```python
# 5 regels simpele logica
def clean_column_name(col: str) -> str:
    if not isinstance(col, str):
        return ''
    return col.split('\n')[0].strip().lower()
```

**Voordelen:**
- ✅ Simpel en voorspelbaar
- ✅ Snelle execution
- ✅ Makkelijk te debuggen
- ✅ Beproefd werkend (originele versie)
- ✅ Focus op data, niet code complexiteit

---

## 🎯 FALLBACK STRATEGY IMPLEMENTATIE

### **PRINCIPE: SIMPELE CODE + RIJKE DATA**

In plaats van complexe parsing logic bouwen we een **comprehensive mapping database** in header_mapping.json.

### **STAP 1: CLEAN_COLUMN_NAME ROLLBACK**
```python
def clean_column_name(col: str) -> str:
    """Schoont een kolomnaam op."""
    if not isinstance(col, str):
        return ''
    return col.split('\n')[0].strip().lower()
```

**Functionaliteit:**
- Neemt eerste regel van multi-line headers
- Stripped whitespace
- Lowercase voor consistent matching
- **Geen complexe edge case handling**

### **STAP 2: HEADER_MAPPING.JSON UITBREIDING**

Voor elk problematisch header type voegen we **alle varianten** toe:

#### **Multi-line NL/EN Headers**
```json
"Netto prijs": {
  "alternatives": [
    "Netto prijs",
    "Nettoprijs", 
    "Net price",
    "Netto prijs Excl. BTW/Incl. Korting",
    "Net price Excl. VAT/Incl. Discount"
  ]
}
```

#### **University-Specific Headers** 
```json
"Stofnaam": {
  "alternatives": [
    "Stofnaam",
    "Stofnaam (Voor Uni's)",
    "Stofnaam (Voor Unis)",
    "Stofnaam (voor Uni's)",
    "Chemical Substance Name",
    "Chemical Substance Name (For Universities)"
  ]
}
```

#### **UOM Pattern Headers**
```json
"UOM Prijseenheid": {
  "alternatives": [
    "UOMPrijseenheid",
    "UOM Prijseenheid", 
    "UOMPriceUnit",
    "UOM Price Unit",
    "Prijseenheid",
    "Price Unit"
  ]
}
```

#### **EAN/Barcode Headers**
```json
"EAN Barcode": {
  "alternatives": [
    "EAN – Barcodenummer",
    "EAN - Barcodenumber", 
    "EAN Barcode",
    "EAN",
    "Barcode",
    "Barcodenummer"
  ]
}
```

### **STAP 3: PATTERN-BASED GENERATION**

Voor systematische coverage genereren we alternatives programmatisch:

```python
def generate_university_alternatives(base_name: str) -> List[str]:
    """Genereer alle university varianten voor een header."""
    variants = [
        base_name,
        f"{base_name} (Voor Uni's)",
        f"{base_name} (Voor Unis)", 
        f"{base_name} (voor Uni's)",
        f"{base_name} (Voor Universiteiten)",
        # English variants
        f"{base_name} (For Universities)",
        f"{base_name} (For Unis)"
    ]
    return variants
```

---

## 📈 VERWACHTE IMPACT

### **Van 30.6% naar 80%+ Mapping**

**Huidige probleem headers (25) → Oplossingen:**

| Header Type | Huidige Staat | Na Fallback Strategy |
|------------|---------------|---------------------|
| Multi-line NL/EN (13) | ❌ 0% mapped | ✅ 90%+ via alternatives |
| University patterns (3) | ❌ 0% mapped | ✅ 100% via patterns |
| UOM variants (5) | ❌ 0% mapped | ✅ 95% via systematic coverage |
| Special cases (4) | ❌ 0% mapped | ✅ 80% via specific alternatives |

**Target resultaat**: **29/36 headers mapped = 80.6%**

---

## 🔧 IMPLEMENTATIE PLAN

### **FASE 1: ROLLBACK (10 min)**
1. Revert `clean_column_name()` naar originele 5-regel versie
2. Test basic functionality met legacy_small.xlsx
3. Verificeer geen regressies in werkende headers

### **FASE 2: DATA EXPANSION (30 min)**
1. Identificeer alle 25 ontbrekende header patterns
2. Voeg systematic alternatives toe aan header_mapping.json
3. Focus op hoogste impact headers eerst:
   - Netto prijs (critical business data)
   - Stofnaam/Brutoformule (chemical data)
   - UOM variants (unit data)

### **FASE 3: VALIDATION (15 min)**
1. Test met legacy_small.xlsx
2. Measure mapping improvement (target: 25+ mapped vs 11)
3. Verify backwards compatibility met TG templates

### **FASE 4: DOCUMENTATION (10 min)**
1. Update MAPPING_ASSESSMENT_RESULTS.md
2. Document nieuwe header patterns
3. Create maintenance guide voor future additions

---

## 🎯 SUCCESS METRICS

### **Primary KPI**
- **Mapping Ratio**: 11/36 (30.6%) → **25+/36 (70%+)**

### **Secondary KPIs**  
- **Code Complexity**: 35+ regels → 5 regels
- **Maintenance Effort**: Hoog → Laag
- **Debug Time**: Lang → Kort
- **Performance**: Langzaam → Snel

### **Quality Metrics**
- **Backwards Compatibility**: 100% behouden
- **Test Coverage**: Alle header types
- **Documentation**: Complete patterns database

---

## 💡 WAAROM FALLBACK STRATEGY WINT

### **1. Simpliciteit**
- **Code is makkelijker te begrijpen** door toekomstige developers
- **Debugging wordt triviaal** - 5 regels vs 35+ regels
- **Minder bugs** door minder complexe logic

### **2. Schaalbaarheid** 
- **Nieuwe headers** → gewoon toevoegen aan JSON
- **Geen code changes** nodig voor nieuwe patterns
- **Business users** kunnen patterns toevoegen

### **3. Betrouwbaarheid**
- **Voorspelbare output** - altijd eerste regel, lowercase
- **Geen edge cases** die nieuwe bugs introduceren
- **Battle-tested** - originele versie werkte

### **4. Performance**
- **Sneller execution** - geen complexe conditionals
- **Minder memory** - geen grote prefix arrays
- **Parallel processing** friendly

### **5. Maintainability**
- **JSON is makkelijk te editeren** vs code changes
- **Clear separation** tussen logic en data
- **Version control** friendly voor pattern changes

---

## 🔄 FALLBACK VOOR EDGE CASES

### **Onbekende Headers Strategy**
Als een header niet gemapt kan worden:

1. **Gebruik originele naam** in rapporten (original_column_mapping fix)
2. **Log voor analyse** - welke patterns missen we?
3. **Graceful degradation** - systeem blijft werken
4. **Feedback loop** - periodiek header_mapping.json updaten

### **Backwards Compatibility**
- **TG templates** blijven 100% werken
- **Existing mapped headers** behouden mapping
- **No breaking changes** in API/output

---

## 📋 CONCLUSIE

**FALLBACK STRATEGY = WIN-WIN**

✅ **Simpeler code** (5 vs 35+ regels)  
✅ **Betere performance** (sneller execution)  
✅ **Hogere mapping ratio** (30% → 80%+)  
✅ **Makkelijker maintenance** (JSON vs code)  
✅ **Betrouwbaardere output** (voorspelbaar)  

**De echte kracht zit niet in slimme code, maar in complete data coverage.**