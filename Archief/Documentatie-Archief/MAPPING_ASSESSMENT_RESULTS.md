# 📊 HEADER MAPPING ASSESSMENT RESULTATEN

**Bestand**: legacy_small.xlsx  
**Template Type**: AT (Alternatieve Template)  
**Datum Assessment**: 2025-09-28  
**Mapping Performance**: **11/36 kolommen = 30.6%**  

---

## ✅ SUCCESVOL GEMAPTE HEADERS (11)

| # | Excel Header | Mapped To | Method |
|---|-------------|-----------|--------|
| 1 | Artikelnummer | Artikelnummer | standard_headers (Cleaned match) |
| 2 | Artikelnaam | Artikelnaam | standard_headers (Cleaned match) |
| 9 | Naam Fabrikant | Naam Fabrikant | standard_headers (Cleaned match) |
| 10 | Artikelnummer Fabrikant | Artikelnummer Fabrikant | standard_headers (Cleaned match) |
| 12 | Levertijd | Levertijd | standard_headers (Cleaned match) |
| 13 | UNSPSC CODE | UNSPSC Code | standard_headers (Cleaned match) |
| 20 | Brutoprijs | Brutoprijs | standard_headers (Cleaned match) |

**Notitie**: 4 andere gemapte headers niet getoond in eerste 20 kolommen.

---

## ❌ KRITIEKE ONTBREKENDE HEADERS (25)

### **Multi-Line Headers Met NL/EN Tekst**
| # | Excel Header | Probleem Type |
|---|-------------|--------------|
| 3 | "Artikel informatie\n\nArticle information\n\n" | Multi-line NL/EN |
| 4 | "Link artikel omschrijving\n\nLink article description" | Multi-line NL/EN |
| 5 | "Netto prijs\nExcl. BTW/Incl. Korting\n\nNet price\nExcl. VAT/Incl. Discount" | Multi-line pricing |
| 6 | "Prijseenheid\n\nPriceunit" | Multi-line NL/EN |
| 7 | "Minimale bestelgrootte\n\nMinimum order quantity" | Multi-line NL/EN |
| 8 | "Aantal per verpakking\n\nNumber per package" | Multi-line NL/EN |
| 11 | "Product categorie\n\nProduct category" | Multi-line NL/EN |
| 14 | "Artikel foto\n\nArticle picture" | Multi-line NL/EN |
| 16 | "BTW code\n\nVAT code" | Multi-line NL/EN |
| 17 | "EAN – Barcodenummer\n\nEAN - Barcodenumber" | Multi-line NL/EN |
| 18 | "Startdatum\n\nStartdate" | Multi-line NL/EN |
| 19 | "Einddatum\n\nEnddate" | Multi-line NL/EN |
| 20 | "Actie code\n\nAction code" | Multi-line NL/EN |

### **University-Specific Headers (Voor Uni's)**
| # | Excel Header | Probleem Type |
|---|-------------|--------------|
| 22 | "Stofnaam\n(Voor Uni's)\n\nChemical Substance Name\n(For Universities)" | (Voor Uni's) + multi-line |
| 23 | "Brutoformule\n(Voor Uni's)\n\nChemical formula\n(For Universities)" | (Voor Uni's) + multi-line |
| 24 | "ADR Gevarenklasse\n(Voor Uni's)\n\nADR Dangercategory\n(For Universities)" | (Voor Uni's) + multi-line |

### **UOM Headers Met Complex Format**
| # | Excel Header | Probleem Type |
|---|-------------|--------------|
| 17 | "UOMPrijseenheid\n\nUOMPriceUnit" | UOM prefix + multi-line |
| 18 | "UOMkleinste eenheid\n(Eenheid voor Uni's)\n\nUOMSmallestUnit\n(Unit for Universities)" | UOM + (Voor Uni's) |
| 19 | "UOMaantalSIP\n(Aantal items in verkoopeenheid voor Uni's)\n\nUOMQuantitySIP" | UOM + long description |
| 20 | "UOMkleinsteInhoud\n(Aantal eenheden voor Uni's)\n\nUOMSmallestContent" | UOM + (Voor Uni's) |
| 21 | "UOMkleinsteBasisEenheid\n\nUOMSmallestBaseUnit" | UOM prefix |

### **Special Cases**
| # | Excel Header | Probleem Type |
|---|-------------|--------------|
| 15 | "NZI_Code" | Underscore separator |
| 25 | "Risicoklasse\n(medische hulpmiddelen)" | Dutch medical term |

---

## 🔍 PATROON ANALYSE

### **Root Causes Geïdentificeerd:**

1. **Multi-line Headers**: `clean_column_name()` gebruikt alleen eerste regel (`col.split('\n')[0]`)
2. **University Extensions**: "(Voor Uni's)" patterns niet in header_mapping.json
3. **UOM Prefixes**: UOM* kolommen missen in mapping configuration  
4. **Underscore Issues**: NZI_Code wordt mogelijk verkeerd gecleaned
5. **Complex Descriptions**: Lange descriptions in parentheses

### **Mapping Methods Working:**
- ✅ **standard_headers**: Werkt goed voor simpele 1-regel headers
- ✅ **Cleaned match**: Basis normalisatie werkt

### **Mapping Methods Failing:**
- ❌ **Multi-line parsing**: Alleen eerste regel wordt gebruikt
- ❌ **Alternative matching**: Uni-specific variants ontbreken
- ❌ **UOM detection**: Prefix patterns niet herkend

---

## 📋 PRIORITEIT FIXES NODIG

### **Hoge Prioriteit (Critical Business Data)**
1. "Netto prijs Excl. BTW/Incl. Korting" - **Pricing data**
2. "Stofnaam (Voor Uni's)" - **Chemical data** 
3. "Brutoformule (Voor Uni's)" - **Chemical data**
4. "ADR Gevarenklasse (Voor Uni's)" - **Safety data**

### **Medium Prioriteit (Operational Data)**  
5. UOM* headers - **Unit of Measure data**
6. "EAN – Barcodenummer" - **Product identification**
7. "BTW code" - **Tax information**

### **Lage Prioriteit (Metadata)**
8. "Product categorie" - **Classification**
9. "Artikel foto" - **Media links**
10. Date fields (Start/End datum) - **Lifecycle data**

---

## 🎯 VOLGENDE STAPPEN

Based op deze assessment gaan we **Header Cleaning Strategy** bepalen die:

1. **Multi-line support** - Alle regels verwerken, niet alleen eerste
2. **University pattern support** - "(Voor Uni's)" variations toevoegen  
3. **UOM prefix handling** - UOM* headers correct mappen
4. **Fallback strategy** - Graceful degradation voor onbekende headers

**Target improvement**: Van 30.6% naar minimaal 80% mapping ratio.