# Test Kolom 11-20 Validaties - Verwachte Resultaten

## Test Bestand: TEST_KOLOM_11-20_VALIDATIES.xlsx

### Doelstelling
Test alle geïmplementeerde validaties voor kolom 11-20:
11. **UOM Code Verpakkingseenheid**
12. **Inhoud Verpakkingseenheid**
13. **UOM Code Basiseenheid**
14. **Inhoud Basiseenheid**
15. **UOM Code Inhoud Basiseenheid**
16. **Omrekenfactor**
17. **Prijs per Kleinste eenheid**
18. **Aantal van de Volgende Lagere Verpakkingslaag**
19. **Artikel Hiërarchie Omschrijving**
20. **GTIN Verpakkingseenheid**

---

## Verwachte Validatie Resultaten

### **Rij 1: Normale waarden**
- **UOM Code Verpakkingseenheid**: "PCE" → ✅ OK (geldig)
- **Inhoud Verpakkingseenheid**: "1" → ✅ OK (numeriek)
- **UOM Code Basiseenheid**: "PCE" → ✅ OK (geldig)
- **Inhoud Basiseenheid**: "1" → ✅ OK (numeriek)
- **UOM Code Inhoud Basiseenheid**: "PCE" → ✅ OK (geldig)
- **Omrekenfactor**: "1" → ✅ OK
- **Prijs per Kleinste eenheid**: "10.50" → ✅ OK
- **Aantal van de Volgende Lagere Verpakkingslaag**: "1" → ✅ OK
- **Artikel Hiërarchie Omschrijving**: "" → ✅ OK (optioneel)
- **GTIN Verpakkingseenheid**: "1234567890123" → ✅ OK (13 cijfers)

### **Rij 2: Referentielijst & Format Fouten**
- **UOM Code Verpakkingseenheid**: "XYZ" → ❌ **Error 707**: "Niet in referentielijst UOM Codes"
- **Inhoud Verpakkingseenheid**: "abc" → ❌ **Error 704**: "Ongeldig format, alleen numeriek"
- **UOM Code Basiseenheid**: "INVALID" → ❌ **Error 707**: "Niet in referentielijst UOM Codes"
- **Inhoud Basiseenheid**: "xyz" → ❌ **Error 704**: "Ongeldig format, alleen numeriek"
- **UOM Code Inhoud Basiseenheid**: "BAD" → ❌ **Error 707**: "Niet in referentielijst UOM Codes"
- **Omrekenfactor**: "" → ❌ **Error 700**: "Niet ingevuld"
- **Prijs per Kleinste eenheid**: "" → ⚠️ **Correction 755**: "Auto-berekend"
- **Aantal van de Volgende Lagere Verpakkingslaag**: "abc" → ⚠️ **Correction 704**: "Ongeldig, alleen numeriek"
- **Artikel Hiërarchie Omschrijving**: "WRONG_CODE" → ⚠️ **Correction 707**: "Niet in referentielijst DescriptorCode"
- **GTIN Verpakkingseenheid**: "12345" → ❌ **Error 701**: "Een GTIN bestaat uit 13 of 14 cijfers" **VERBETERD!**

### **Rij 3: Normale waarden**
- **UOM Code Verpakkingseenheid**: "BOX" → ✅ OK (geldig)
- **Inhoud Verpakkingseenheid**: "10" → ✅ OK (numeriek)
- **UOM Code Basiseenheid**: "PCE" → ✅ OK (geldig)
- **Inhoud Basiseenheid**: "1" → ✅ OK (numeriek)
- **UOM Code Inhoud Basiseenheid**: "PCE" → ✅ OK (geldig)
- **Omrekenfactor**: "10" → ✅ OK
- **Prijs per Kleinste eenheid**: "1.50" → ✅ OK
- **Aantal van de Volgende Lagere Verpakkingslaag**: "" → ✅ OK (optioneel)
- **Artikel Hiërarchie Omschrijving**: "" → ✅ OK (optioneel)
- **GTIN Verpakkingseenheid**: "12345678901234" → ✅ OK (14 cijfers)

### **Rij 4: Lege verplichte velden**
- **UOM Code Verpakkingseenheid**: "" → ❌ **Error 700**: "Verplicht maar niet ingevuld"
- **Inhoud Verpakkingseenheid**: "" → ❌ **Error 700**: "Verplicht maar niet ingevuld"
- **UOM Code Basiseenheid**: "" → ❌ **Error 700**: "Verplicht maar niet ingevuld"
- **Inhoud Basiseenheid**: "" → ❌ **Error 700**: "Verplicht maar niet ingevuld"
- **UOM Code Inhoud Basiseenheid**: "" → ❌ **Error 700**: "Verplicht maar niet ingevuld"
- **Omrekenfactor**: "999" → 🏴 **Flag 720**: "Komt niet overeen met berekende waarde"
- **Prijs per Kleinste eenheid**: "999.99" → 🏴 **Flag 720**: "Komt niet overeen met berekende waarde"
- **Aantal van de Volgende Lagere Verpakkingslaag**: "5" → ✅ OK
- **Artikel Hiërarchie Omschrijving**: "VALID_CODE" → ✅ OK (geldig)
- **GTIN Verpakkingseenheid**: "123456789012345" → ❌ **Error 702**: "Een GTIN bestaat uit 13 of 14 cijfers" **VERBETERD!**

### **Rij 5: Mixed scenario's**
- **UOM Code Verpakkingseenheid**: "WRONG" → ❌ **Error 707**: "Niet in referentielijst UOM Codes"
- **Inhoud Verpakkingseenheid**: "5" → ✅ OK (numeriek)
- **UOM Code Basiseenheid**: "BOX" → ✅ OK (geldig)
- **Inhoud Basiseenheid**: "1" → ✅ OK (numeriek)
- **UOM Code Inhoud Basiseenheid**: "PCE" → ✅ OK (geldig)
- **Omrekenfactor**: "1" → ✅ OK
- **Prijs per Kleinste eenheid**: "12.50" → ✅ OK
- **Aantal van de Volgende Lagere Verpakkingslaag**: "text" → ⚠️ **Correction 704**: "Ongeldig, alleen numeriek"
- **Artikel Hiërarchie Omschrijving**: "INVALID" → ⚠️ **Correction 707**: "Niet in referentielijst DescriptorCode"
- **GTIN Verpakkingseenheid**: "1234567890123" → 🏴 **Flag 703**: "Komt meerdere malen voor" (duplicaat van rij 1)

---

## Test Validatie

### **Belangrijkste Verbeteringen die Getest Worden:**

#### ✅ **1. GTIN Format Validation (VERBETERD)**
- **Voor**: "GTIN te kort" / "GTIN te lang" (generiek)
- **Nu**: "Een GTIN bestaat uit 13 of 14 cijfers" (specifiek zoals matrix verwacht)

#### ✅ **2. UOM Code Referentielijst Validaties**
- **Alle UOM velden**: Code 707 voor ongeldige codes uit referentielijst
- **Verplichte velden**: Code 700 voor lege verplichte UOM codes

#### ✅ **3. Numerieke Format Validaties**
- **Inhoud velden**: Code 704 voor niet-numerieke waarden
- **Aantal velden**: Correction 704 voor format problemen

#### ✅ **4. Auto-Calculation Features**
- **Omrekenfactor**: Flag 720 voor berekening mismatches
- **Prijs per Kleinste eenheid**: Correction 755 voor auto-berekening + Flag 720 voor mismatches

#### ✅ **5. Duplicate Detection**
- **GTIN**: Flag 703 voor duplicate GTIN waarden

---

## Matrix Compliance Check

### **Kolom 11-15 (UOM & Inhoud velden):**
- ✅ **Verplicht maar niet ingevuld**: Error 700
- ✅ **Niet in referentielijst**: Error 707 (UOM Codes)
- ✅ **Ongeldig format**: Error 704 (alleen numeriek voor Inhoud)

### **Kolom 16-17 (Berekende velden):**
- ✅ **Auto-berekening**: Correction 754/755
- ✅ **Berekening mismatch**: Flag 720

### **Kolom 18-19 (Optionele velden):**
- ✅ **Format correcties**: Correction 704/707 zonder afkeuring

### **Kolom 20 (GTIN):**
- ✅ **Format validatie**: "13 of 14 cijfers" specifiek **VERBETERD!**
- ✅ **Duplicate check**: Flag 703
- ✅ **Medical device requirement**: Flag 756

---

## Hoe te Testen

1. Upload `TEST_KOLOM_11-20_VALIDATIES.xlsx` naar http://localhost:8504/
2. Run validatie
3. Check validatierapport tegen verwachte resultaten hierboven
4. Verifieer dat:
   - GTIN fouten "13 of 14 cijfers" message tonen **NIEUW!**
   - UOM Code referentielijst validaties werken (code 707)
   - Inhoud velden numeriek format checken (code 704)
   - Auto-calculation features correct werken (code 754/755/720)
   - Duplicate GTIN detection werkt (code 703)

---

*Test aangemaakt: 2025-10-06*  
*Doel: Verificatie van kolom 11-20 matrix compliance*