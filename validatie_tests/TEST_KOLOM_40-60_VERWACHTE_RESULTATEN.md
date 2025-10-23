# Test Kolom 40-60 Validaties - Verwachte Resultaten

## Test Bestand: TEST_KOLOM_40-60_VALIDATIES.xlsx

### Doelstelling
Test alle geïmplementeerde validaties voor kolom 40-60:
40. **Artikelnummer Alternatief Artikel**
41. **Artikelnaam Alternatief Artikel**
42. **Barcode Alternatief Artikel**
43. **UNSPSC**
44. **GMDN Code**
45. **EMDN Code**
46. **GPCCategoryCode**
47. **Code voor Aanvullende Productclassificatie**
48. **Aanvullende Productclassificatiewaarde (Risicoklasse)**
49. **CE Certificaat nummer**
50. **CE Certificaat einddatum**
51. **CE Certificerende instantie**
52. **Duurzaam Geproduceerd**
53. **Naam Duurzaam Assortiment**
54. **Naam Duurzaamheidslabel**
55. **Omschrijving Duurzaamheid**
56. **CAS nummer**
57. **Stofnaam**
58. **Brutoformule**
59. **Claim Type Code**
60. **Element Claim Code**

---

## Verwachte Validatie Resultaten

### **Rij 1: Normale waarden**
- **Artikelnummer Alternatief Artikel**: "ALT-001" → ✅ OK (3+ chars)
- **Artikelnaam Alternatief Artikel**: "Alternatief product" → ✅ OK (dependency gevuld)
- **Barcode Alternatief Artikel**: "123456789012" → ✅ OK (dependency gevuld)
- **UNSPSC**: "12345678" → ✅ OK (8 cijfers)
- **GMDN Code**: "12345" → ✅ OK (numeriek)
- **EMDN Code**: "A12345" → ✅ OK (alphanumeriek)
- **GPCCategoryCode**: "10000001" → ✅ OK (8 cijfers)
- **Code voor Aanvullende Productclassificatie**: "76" → ✅ OK (geldig)
- **Aanvullende Productclassificatiewaarde**: "EU_CLASS_I" → ✅ OK (geldig)
- **CE Certificaat nummer**: "CE-123456" → ✅ OK (3+ chars)
- **CE Certificaat einddatum**: "2025-12-31" → ✅ OK (datum format)
- **CE Certificerende instantie**: "TÜV SÜD" → ✅ OK (dependency gevuld)
- **Duurzaam Geproduceerd**: "1" → ✅ OK (boolean)
- **Naam Duurzaam Assortiment**: "Green Line" → ✅ OK (string)
- **Naam Duurzaamheidslabel**: "FSC Certified" → ✅ OK (string)
- **Omschrijving Duurzaamheid**: "Milieuvriendelijk geproduceerd" → ✅ OK (string)
- **CAS nummer**: "50-00-0" → ✅ OK (CAS format)
- **Stofnaam**: "Formaldehyde" → ✅ OK (dependency gevuld)
- **Brutoformule**: "CH2O" → ✅ OK (dependency gevuld)
- **Claim Type Code**: "ORGANIC" → ✅ OK (geldig)
- **Element Claim Code**: "CERT01" → ✅ OK (dependency gevuld)

### **Rij 2: Format en lengte fouten**
- **Artikelnummer Alternatief Artikel**: "AB" → ⚠️ **Correction 701**: "Te kort, minimaal 3 karakters"
- **Artikelnaam Alternatief Artikel**: "" → 🏴 **Flag 761**: "Leeg terwijl Artikelnummer Alternatief Artikel is ingevuld"
- **Barcode Alternatief Artikel**: "" → 🏴 **Flag 762**: "Leeg terwijl Artikelnummer Alternatief Artikel is ingevuld"
- **UNSPSC**: "" → ❌ **Error 700**: "Niet ingevuld verplicht veld"
- **GMDN Code**: "ABC" → ⚠️ **Correction 704**: "Niet numeriek"
- **EMDN Code**: "" → ⚠️ **Correction 707**: "Leeg terwijl GMDN Code is ingevuld"
- **GPCCategoryCode**: "1234567" → ⚠️ **Correction 706**: "Moet exact 8 cijfers zijn"
- **Code voor Aanvullende Productclassificatie**: "99" → ⚠️ **Correction 707**: "Niet in referentielijst"
- **Aanvullende Productclassificatiewaarde**: "" → 🏴 **Flag 754**: "Leeg terwijl Code voor Aanvullende Productclassificatie is ingevuld"
- **CE Certificaat nummer**: "AB" → ⚠️ **Correction 701**: "Te kort, minimaal 3 karakters"
- **CE Certificaat einddatum**: "" → 🏴 **Flag 756**: "Leeg terwijl CE Certificaat nummer is ingevuld"
- **CE Certificerende instantie**: "" → 🏴 **Flag 757**: "Leeg terwijl CE Certificaat nummer is ingevuld"
- **Duurzaam Geproduceerd**: "maybe" → ⚠️ **Correction 705**: "Niet boolean (0/1, ja/nee)"
- **Naam Duurzaam Assortiment**: "" → ✅ OK (optioneel)
- **Naam Duurzaamheidslabel**: "" → ✅ OK (optioneel)
- **Omschrijving Duurzaamheid**: "" → ✅ OK (optioneel)
- **CAS nummer**: "invalid-cas" → ⚠️ **Correction 708**: "Ongeldig CAS formaat"
- **Stofnaam**: "" → 🏴 **Flag 758**: "Leeg terwijl CAS nummer is ingevuld"
- **Brutoformule**: "" → 🏴 **Flag 759**: "Leeg terwijl CAS nummer is ingevuld"
- **Claim Type Code**: "INVALID" → ⚠️ **Correction 707**: "Niet in referentielijst"
- **Element Claim Code**: "" → 🏴 **Flag 760**: "Leeg terwijl Claim Type Code is ingevuld"

### **Rij 3: Context-afhankelijke validaties**
- **Artikelnummer Alternatief Artikel**: "" → ✅ OK (optioneel)
- **Artikelnaam Alternatief Artikel**: "" → ✅ OK (geen dependency)
- **Barcode Alternatief Artikel**: "" → ✅ OK (geen dependency)
- **UNSPSC**: "12345678" → ✅ OK (geldig)
- **GMDN Code**: "" → ✅ OK (optioneel)
- **EMDN Code**: "" → ✅ OK (geen dependency)
- **GPCCategoryCode**: "" → ✅ OK (optioneel)
- **Code voor Aanvullende Productclassificatie**: "" → ✅ OK (optioneel)
- **Aanvullende Productclassificatiewaarde**: "" → ✅ OK (geen dependency)
- **CE Certificaat nummer**: "" → ✅ OK (optioneel)
- **CE Certificaat einddatum**: "" → ✅ OK (geen dependency)
- **CE Certificerende instantie**: "" → ✅ OK (geen dependency)
- **Duurzaam Geproduceerd**: "0" → ✅ OK (boolean)
- **Naam Duurzaam Assortiment**: "" → ✅ OK (optioneel)
- **Naam Duurzaamheidslabel**: "" → ✅ OK (optioneel)
- **Omschrijving Duurzaamheid**: "" → ✅ OK (optioneel)
- **CAS nummer**: "" → ✅ OK (optioneel)
- **Stofnaam**: "" → ✅ OK (geen dependency)
- **Brutoformule**: "" → ✅ OK (geen dependency)
- **Claim Type Code**: "" → ✅ OK (optioneel)
- **Element Claim Code**: "" → ✅ OK (geen dependency)

### **Rij 4: Extreme waarden en edge cases**
- **Artikelnummer Alternatief Artikel**: "A" + "b"*45 (exact 46 chars) → ✅ OK (grens)
- **Artikelnaam Alternatief Artikel**: "Test Product Name" → ✅ OK (dependency gevuld)
- **Barcode Alternatief Artikel**: "9876543210987" → ✅ OK (dependency gevuld)
- **UNSPSC**: "99999999" → ✅ OK (8 cijfers)
- **GMDN Code**: "999999" → ✅ OK (numeriek)
- **EMDN Code**: "Z99999" → ✅ OK (alphanumeriek)
- **GPCCategoryCode**: "99999999" → ✅ OK (exact 8 cijfers)
- **Code voor Aanvullende Productclassificatie**: "08" → ✅ OK (geldig)
- **Aanvullende Productclassificatiewaarde**: "EU_CLASS_III" → ✅ OK (geldig)
- **CE Certificaat nummer**: "CE-" + "1"*47 (exact 50 chars) → ✅ OK (grens)
- **CE Certificaat einddatum**: "2030-01-01" → ✅ OK (toekomst datum)
- **CE Certificerende instantie**: "Very Long Certification Body Name Inc." → ✅ OK (dependency gevuld)
- **Duurzaam Geproduceerd**: "ja" → ✅ OK (boolean variant)
- **Naam Duurzaam Assortiment**: "Ultra Sustainable Product Line" → ✅ OK (lange naam)
- **Naam Duurzaamheidslabel**: "Cradle to Cradle Certified" → ✅ OK (lange label)
- **Omschrijving Duurzaamheid**: "Zeer uitgebreide beschrijving..." → ✅ OK (lange tekst)
- **CAS nummer**: "7732-18-5" → ✅ OK (water CAS)
- **Stofnaam**: "Dihydrogen monoxide" → ✅ OK (dependency gevuld)
- **Brutoformule**: "H2O" → ✅ OK (dependency gevuld)
- **Claim Type Code**: "BIODEGRADABLE" → ✅ OK (geldig)
- **Element Claim Code**: "BIO001" → ✅ OK (dependency gevuld)

---

## Test Validatie

### **Belangrijkste Validaties die Getest Worden:**

#### ✅ **1. Dependency Validaties**
- **Alternatieve artikel velden**: Artikelnaam en Barcode zijn verplicht als Artikelnummer is ingevuld (flags 761/762)
- **GMDN/EMDN**: EMDN verplicht als GMDN is ingevuld (flag)
- **Productclassificatie**: Risicoklasse verplicht als classificatiecode is ingevuld (flag 754)
- **CE Certificering**: Einddatum en instantie verplicht als nummer is ingevuld (flags 756/757)
- **Chemische stoffen**: Stofnaam en formule verplicht als CAS nummer is ingevuld (flags 758/759)
- **Claims**: Element code verplicht als claim type is ingevuld (flag 760)

#### ✅ **2. Format Validaties**
- **UNSPSC**: Exact 8 cijfers (code 706)
- **GMDN Code**: Numeriek format (code 704)
- **GPCCategoryCode**: Exact 8 cijfers (code 706)
- **CAS nummer**: Geldig CAS format (code 708)
- **CE Certificaat einddatum**: Datum format validatie

#### ✅ **3. Referentielijst Validaties**
- **Code voor Aanvullende Productclassificatie**: Code 707 voor ongeldige codes
- **Aanvullende Productclassificatiewaarde**: Code 707 voor ongeldige risicoklassen
- **Claim Type Code**: Code 707 voor ongeldige claim types

#### ✅ **4. Length Validaties**
- **Min Length**: Code 701 voor te korte velden
- **Exact Length**: Code 706 voor velden met exacte lengte vereisten

#### ✅ **5. Boolean Validaties**
- **Duurzaam Geproduceerd**: Code 705 voor ongeldige boolean waarden

#### ✅ **6. Required Field Validaties**
- **UNSPSC**: Code 700 voor verplicht maar leeg veld

---

## Matrix Compliance Check

### **Alle Kolommen 40-60:**
- ✅ **Verplichte velden**: Error 700 voor lege mandatory fields
- ✅ **Referentielijsten**: Correction 707 voor ongeldige waarden
- ✅ **Format validaties**: Correction 704/706/708 voor format problemen
- ✅ **Lengte beperkingen**: Correction 701 voor length issues
- ✅ **Boolean formaten**: Correction 705 voor boolean format issues
- ✅ **Context dependencies**: Flags 754/756-762 voor dependency issues
- ✅ **Exact length**: Correction 706 voor velden met exacte lengte vereisten

---

## Hoe te Testen

1. Upload `TEST_KOLOM_40-60_VALIDATIES.xlsx` naar http://localhost:8504/
2. Run validatie
3. Check validatierapport tegen verwachte resultaten hierboven
4. Verifieer dat:
   - Dependency validaties correct werken (codes 754/756-762)
   - Format validaties detecteren fouten (codes 704/706/708)
   - Referentielijst validaties werken (code 707)
   - Length validaties auto-correct (code 701)
   - Boolean validaties detecteren fouten (code 705)
   - Required field validaties werken (code 700)

---

*Test aangemaakt: 2025-10-06*  
*Doel: Verificatie van kolom 40-60 matrix compliance*