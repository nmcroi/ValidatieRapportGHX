# Test Kolom 21-40 Validaties - Verwachte Resultaten

## Test Bestand: TEST_KOLOM_21-40_VALIDATIES.xlsx

### Doelstelling
Test alle geïmplementeerde validaties voor kolom 21-40:
21. **GTIN Verpakkingseenheid Historie**
22. **GTIN Basiseenheid** 
23. **GTIN Basiseenheid Historie**
24. **Aanvullende Productidentificatie**
25. **Code voor Aanvullende Productidentificatie**
26. **GHX BTW Code**
27. **Staffel Vanaf**
28. **Staffel Tot** 
29. **Naam Fabrikant**
30. **Artikelnummer Fabrikant**
31. **GLN Fabrikant**
32. **GLN Leverancier**
33. **Doelmarkt Landcode**
34. **Link Artikelinformatie**
35. **Link Artikelfoto**
36. **Link IFU**
37. **Functionele Artikelnaam**
38. **Functionele Naam Taal Code** 
39. **Merknaam**
40. **Artikelnummer Alternatief Artikel**

---

## Verwachte Validatie Resultaten

### **Rij 1: Normale waarden**
- **GTIN Verpakkingseenheid Historie**: "Oude GTIN: 1234567890123" → ✅ OK (onder 200 chars)
- **GTIN Basiseenheid**: "1234567890123" → ✅ OK (13 cijfers)
- **GTIN Basiseenheid Historie**: "Oude: 9876543210987" → ✅ OK (onder 200 chars)
- **Aanvullende Productidentificatie**: "REF12345" → ✅ OK (onder 35 chars)
- **Code voor Aanvullende Productidentificatie**: "01" → ✅ OK (geldig)
- **GHX BTW Code**: "21" → ✅ OK (geldig BTW code)
- **Staffel Vanaf**: "1" → ✅ OK (numeriek)
- **Staffel Tot**: "100" → ✅ OK (numeriek)
- **Naam Fabrikant**: "ACME Medical" → ✅ OK (onder 70 chars)
- **Artikelnummer Fabrikant**: "ACM-001" → ✅ OK (3+ chars)
- **GLN Fabrikant**: "1234567890123" → ✅ OK (13 cijfers)
- **GLN Leverancier**: "9876543210987" → ✅ OK (13 cijfers)
- **Doelmarkt Landcode**: "NL" → ✅ OK (geldig land)
- **Link Artikelinformatie**: "https://example.com/info" → ✅ OK (https)
- **Link Artikelfoto**: "https://example.com/photo.jpg" → ✅ OK (https)
- **Link IFU**: "https://example.com/ifu.pdf" → ✅ OK (https)
- **Functionele Artikelnaam**: "Medische handschoen" → ✅ OK (3-150 chars)
- **Functionele Naam Taal Code**: "NL" → ✅ OK (geldig)
- **Merknaam**: "ACME" → ✅ OK (3-70 chars)
- **Artikelnummer Alternatief Artikel**: "ALT-001" → ✅ OK (3+ chars)

### **Rij 2: Format en lengte fouten**
- **GTIN Verpakkingseenheid Historie**: 250+ karakter tekst → ⚠️ **Correction 702**: "Te lang, wordt ingekort tot 200 karakters"
- **GTIN Basiseenheid**: "123456" → ❌ **Error 701**: "Te kort"
- **GTIN Basiseenheid Historie**: 250+ karakter tekst → ⚠️ **Correction 702**: "Te lang, wordt ingekort tot 200 karakters"
- **Aanvullende Productidentificatie**: 50+ karakter tekst → ⚠️ **Correction 702**: "Te lang, wordt ingekort tot 35 karakters"
- **Code voor Aanvullende Productidentificatie**: "99" → ⚠️ **Correction 707**: "Niet in referentielijst"
- **GHX BTW Code**: "" → ❌ **Error 700**: "Niet ingevuld verplicht"
- **Staffel Vanaf**: "abc" → ⚠️ **Correction 704**: "Niet numeriek"
- **Staffel Tot**: "xyz" → ⚠️ **Correction 704**: "Niet numeriek"
- **Naam Fabrikant**: 80+ karakter tekst → ⚠️ **Correction 702**: "Te lang, wordt ingekort tot 70 karakters"
- **Artikelnummer Fabrikant**: "AB" → ⚠️ **Correction 701**: "Te kort, minimaal 3 karakters"
- **GLN Fabrikant**: "12345" → ⚠️ **Correction 706**: "Moet 13 cijfers zijn"
- **GLN Leverancier**: "abcdef" → ⚠️ **Correction 706**: "Moet 13 cijfers zijn"
- **Doelmarkt Landcode**: "XX" → ⚠️ **Correction 707**: "Niet in referentielijst"
- **Link Artikelinformatie**: "http://example.com" → ⚠️ **Correction 722**: "Moet beginnen met https://"
- **Link Artikelfoto**: "ftp://example.com" → ⚠️ **Correction 722**: "Moet beginnen met https://"
- **Link IFU**: "www.example.com" → ⚠️ **Correction 722**: "Moet beginnen met https://"
- **Functionele Artikelnaam**: "AB" → ⚠️ **Correction 701**: "Te kort, minimaal 3 karakters"
- **Functionele Naam Taal Code**: "XX" → ⚠️ **Correction 707**: "Niet in referentielijst"
- **Merknaam**: "AB" → ⚠️ **Correction 701**: "Te kort, minimaal 3 karakters"
- **Artikelnummer Alternatief Artikel**: "AB" → ⚠️ **Correction 701**: "Te kort, minimaal 3 karakters"

### **Rij 3: Context-afhankelijke validaties**
- **GTIN Verpakkingseenheid Historie**: "" → ✅ OK (optioneel)
- **GTIN Basiseenheid**: "12345678901234" → ✅ OK (14 cijfers)
- **GTIN Basiseenheid Historie**: "" → ✅ OK (optioneel)
- **Aanvullende Productidentificatie**: "" → ✅ OK (optioneel)
- **Code voor Aanvullende Productidentificatie**: "08" → ✅ OK (geldig)
- **GHX BTW Code**: "0" → ✅ OK (geldig BTW code)
- **Staffel Vanaf**: "" → ✅ OK (optioneel)
- **Staffel Tot**: "" → ✅ OK (optioneel)
- **Naam Fabrikant**: "" → ✅ OK (optioneel)
- **Artikelnummer Fabrikant**: "" → ✅ OK (optioneel)
- **GLN Fabrikant**: "" → ✅ OK (optioneel)
- **GLN Leverancier**: "" → 🏴 **Flag 759**: "Leeg maar mogelijk verplicht bij context"
- **Doelmarkt Landcode**: "" → ✅ OK (optioneel)
- **Link Artikelinformatie**: "" → ✅ OK (optioneel)
- **Link Artikelfoto**: "" → ✅ OK (optioneel)
- **Link IFU**: "" → 🏴 **Flag 760**: "Leeg maar mogelijk verplicht bij risicoklasse"
- **Functionele Artikelnaam**: "Test Product" → ✅ OK (geldig)
- **Functionele Naam Taal Code**: "" → 🏴 **Flag 751**: "Leeg terwijl Functionele Artikelnaam is ingevuld"
- **Merknaam**: "TestBrand" → ✅ OK (geldig)
- **Artikelnummer Alternatief Artikel**: "" → ✅ OK (optioneel)

### **Rij 4: Extreme waarden en edge cases**
- **GTIN Verpakkingseenheid Historie**: "123456789012345678901234567890..." (exact 200 chars) → ✅ OK (grens)
- **GTIN Basiseenheid**: "123456789012345" → ❌ **Error 702**: "Te lang"
- **GTIN Basiseenheid Historie**: "A" → ✅ OK (minimaal)
- **Aanvullende Productidentificatie**: "12345678901234567890123456789012345" (exact 35 chars) → ✅ OK (grens)
- **Code voor Aanvullende Productidentificatie**: "01" → ✅ OK (valid)
- **GHX BTW Code**: "INVALID" → ⚠️ **Correction 707**: "Niet in referentielijst"
- **Staffel Vanaf**: "999999999" → ✅ OK (groot getal)
- **Staffel Tot**: "-5" → ⚠️ **Correction 704**: "Negatief getal?"
- **Naam Fabrikant**: "A" + "b"*69 (exact 70 chars) → ✅ OK (grens)
- **Artikelnummer Fabrikant**: "ABC" → ✅ OK (minimaal 3)
- **GLN Fabrikant**: "1234567890123" → ✅ OK (exact 13)
- **GLN Leverancier**: "12345678901234" → ⚠️ **Correction 706**: "Te lang, moet 13 cijfers"
- **Doelmarkt Landcode**: "BE" → ✅ OK (geldig)
- **Link Artikelinformatie**: "https://example.com/info" → 🏴 **Flag 775**: "Duplicaat URL" (zelfde als rij 1)
- **Link Artikelfoto**: "https://example.com/very-long-url..." → ✅ OK (lange URL)
- **Link IFU**: "https://example.com/ifu.pdf" → 🏴 **Flag 775**: "Duplicaat URL" (zelfde als rij 1)
- **Functionele Artikelnaam**: "A" + "b"*149 (exact 150 chars) → ✅ OK (grens)
- **Functionele Naam Taal Code**: "EN" → ✅ OK (geldig)
- **Merknaam**: "A" + "b"*69 (exact 70 chars) → ✅ OK (grens)
- **Artikelnummer Alternatief Artikel**: "A" + "b"*149 (exact 150 chars) → ✅ OK (grens)

---

## Test Validatie

### **Belangrijkste Validaties die Getest Worden:**

#### ✅ **1. GTIN Format Validaties (VERBETERD)**
- **GTIN Basiseenheid**: Exact 13 of 14 cijfers (codes 701/702)
- **GTIN Historie velden**: Max 200 karakters (code 702)

#### ✅ **2. URL Format Validaties**
- **Link velden**: Moeten beginnen met https:// (code 722)
- **Duplicate URL detection**: Flag 775 voor herhaalde URLs

#### ✅ **3. Referentielijst Validaties**
- **BTW Codes**: Code 707 voor ongeldige codes
- **Land Codes**: Code 707 voor ongeldige codes
- **Product ID Codes**: Code 707 voor ongeldige codes
- **Taal Codes**: Code 707 voor ongeldige codes

#### ✅ **4. Length Validaties**
- **Min Length**: Code 701 voor te korte velden
- **Max Length**: Code 702 voor te lange velden (auto-correction)
- **Exact Length**: Code 706 voor GLN velden (exact 13 cijfers)

#### ✅ **5. Context-Afhankelijke Validaties**
- **GLN Leverancier**: Flag 759 bij bepaalde contexten
- **Link IFU**: Flag 760 bij risicoklasse produkten
- **Taal Code**: Flag 751 bij ingevulde naam maar lege taal

#### ✅ **6. Numeric Format Validaties**
- **Staffel velden**: Code 704 voor niet-numerieke waarden
- **GLN velden**: Code 706 voor format problemen

---

## Matrix Compliance Check

### **Alle Kolommen 21-40:**
- ✅ **Verplichte velden**: Error 700 voor lege mandatory fields
- ✅ **Referentielijsten**: Error/Correction 707 voor ongeldige waarden
- ✅ **Format validaties**: Error/Correction 704/706 voor format problemen
- ✅ **Lengte beperkingen**: Correction 701/702 voor length issues
- ✅ **URL formaten**: Correction 722 voor protocol issues
- ✅ **Context dependencies**: Flags 751/759/760 voor context issues
- ✅ **Duplicate detection**: Flag 775 voor herhaalde waarden

---

## Hoe te Testen

1. Upload `TEST_KOLOM_21-40_VALIDATIES.xlsx` naar http://localhost:8504/
2. Run validatie
3. Check validatierapport tegen verwachte resultaten hierboven
4. Verifieer dat:
   - GTIN format validaties correct werken (codes 701/702)
   - URL validaties https:// vereisen (code 722)
   - Referentielijst validaties werken (code 707)
   - Length validaties auto-correct (codes 701/702)
   - Context flags verschijnen waar verwacht (codes 751/759/760)
   - Duplicate URL detection werkt (code 775)

---

*Test aangemaakt: 2025-10-06*  
*Doel: Verificatie van kolom 21-40 matrix compliance*