# Test Kolom 1-5 Validaties - Verwachte Resultaten

## Test Bestand: TEST_KOLOM_1-5_VALIDATIES.xlsx

### Doelstelling
Test alle geïmplementeerde validaties voor de eerste 5 kolommen:
1. Artikelnummer
2. Artikelnaam  
3. Artikelomschrijving
4. Artikelomschrijving Taal Code
5. **Brutoprijs (ONTBREEKT OPZETTELIJK)**

---

## Verwachte Validatie Resultaten

### **Rij 1: Normale waarden**
- **Artikelnummer**: "TEST001" → ✅ OK
- **Artikelnaam**: "Test Product" → ✅ OK  
- **Artikelomschrijving**: "Dit is een korte omschrijving" → ✅ OK
- **Artikelomschrijving Taal Code**: "NL" → ✅ OK
- **Brutoprijs**: MISSING → ❌ **Error 780**: "Kolom 'Brutoprijs' niet gevonden in template"

### **Rij 2: Te korte waarden**
- **Artikelnummer**: "AB" → ❌ **Error 701**: "Artikelnummer is te kort"
- **Artikelnaam**: "AB" → ❌ **Error 701**: "Artikelnaam is te kort"
- **Artikelomschrijving**: 2005 A's → ⚠️ **Correction 702**: "Artikelomschrijving is te lang, wordt ingekort tot 2000 karakters"
- **Artikelomschrijving Taal Code**: "XX" → ❌ **Error 707**: "Niet in referentielijst"
- **Brutoprijs**: MISSING → ❌ **Error 780**: "Kolom 'Brutoprijs' niet gevonden"

### **Rij 3: Te lange waarden**
- **Artikelnummer**: 50 A's → ❌ **Error 702**: "Artikelnummer is te lang"
- **Artikelnaam**: 95 A's → ⚠️ **Correction 702**: "Artikelnaam is te lang, wordt ingekort tot 90 karakters"
- **Artikelomschrijving**: "Normale omschrijving" → ✅ OK
- **Artikelomschrijving Taal Code**: "EN" → ✅ OK
- **Brutoprijs**: MISSING → ❌ **Error 780**: "Kolom 'Brutoprijs' niet gevonden"

### **Rij 4: Lege waarden**
- **Artikelnummer**: "" → ❌ **Error 700**: "Artikelnummer is niet ingevuld"
- **Artikelnaam**: "" → ❌ **Error 700**: "Artikelnaam is niet ingevuld"
- **Artikelomschrijving**: "" → 🏴 **Flag 750**: "Artikelomschrijving aanbevolen in te vullen"
- **Artikelomschrijving Taal Code**: "" → 🏴 **Flag 751**: "Taal code verplicht als omschrijving gevuld"
- **Brutoprijs**: MISSING → ❌ **Error 780**: "Kolom 'Brutoprijs' niet gevonden"

### **Rij 5: Duplicaat + normale waarden**
- **Artikelnummer**: "TEST001" → 🏴 **Flag 703**: "Duplicaat toegestaan maar controleren"
- **Artikelnaam**: "Normaal Product Naam" → ✅ OK
- **Artikelomschrijving**: "Nog een normale omschrijving" → ✅ OK
- **Artikelomschrijving Taal Code**: "DE" → ✅ OK
- **Brutoprijs**: MISSING → ❌ **Error 780**: "Kolom 'Brutoprijs' niet gevonden"

---

## Test Validatie

### **Belangrijkste Verbeteringen die Getest Worden:**

#### ✅ **1. Message Specificiteit**
- **Voor**: "Artikelnaam is te lang"
- **Nu**: "Artikelnaam is te lang. De waarde zou hierdoor in een later stadium ingekort kunnen worden tot 90 karakters"

- **Voor**: "Artikelomschrijving is te lang"  
- **Nu**: "Artikelomschrijving is te lang. De waarde zou hierdoor in een later stadium ingekort kunnen worden tot 2000 karakters"

#### ✅ **2. Missing Column Validation**
- **Voor**: Missing Brutoprijs kolom wordt niet gedetecteerd
- **Nu**: **Error 780** per rij: "Kolom 'Brutoprijs' niet gevonden in template. De regel zou hierdoor in een later stadium afgekeurd kunnen worden."

---

## Hoe te Testen

1. Upload `TEST_KOLOM_1-5_VALIDATIES.xlsx` naar http://localhost:8504/
2. Run validatie
3. Check validatierapport tegen verwachte resultaten hierboven
4. Verifieer dat:
   - Specifieke karakterlimieten in berichten staan
   - Elke rij een Error 780 heeft voor missing Brutoprijs
   - Alle andere validaties correct werken

---

*Test aangemaakt: 2025-10-06*  
*Doel: Verificatie van kolom 1-5 verbeteringen*