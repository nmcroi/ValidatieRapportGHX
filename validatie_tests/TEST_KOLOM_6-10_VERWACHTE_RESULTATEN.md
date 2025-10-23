# Test Kolom 6-10 Validaties - Verwachte Resultaten

## Test Bestand: TEST_KOLOM_6-10_VALIDATIES.xlsx

### Doelstelling
Test alle geïmplementeerde validaties voor kolom 6-10:
6. **Brutoprijs** (al getest in eerste 5)
7. **Nettoprijs** 
8. **Is BestelbareEenheid**
9. **Is BasisEenheid**
10. **Omschrijving Verpakkingseenheid**

---

## Verwachte Validatie Resultaten

### **Rij 1: Normale waarden**
- **Brutoprijs**: "10.50" → ✅ OK
- **Nettoprijs**: "9.50" → ✅ OK
- **Is BestelbareEenheid**: "1" → ✅ OK (geldig)
- **Is BasisEenheid**: "0" → ✅ OK (geldig)
- **Omschrijving Verpakkingseenheid**: "Stuk" → ✅ OK

### **Rij 2: Correctie scenario's**
- **Brutoprijs**: "€ 25,99" → ⚠️ **Correction 705**: "Valutatekens verwijderd"
- **Nettoprijs**: "€ 23,99" → ⚠️ **Correction 705**: "Valutatekens en duizendtallenscheidingstekens verwijderd" **NIEUW!**
- **Is BestelbareEenheid**: "0" → ✅ OK (geldig)
- **Is BasisEenheid**: "1" → ✅ OK (geldig)
- **Omschrijving Verpakkingseenheid**: 30 A's → ⚠️ **Correction 702**: "Te lang, wordt ingekort tot 25 karakters" **VERBETERD!**

### **Rij 3: Rejection scenario's**
- **Brutoprijs**: "15.00" → ✅ OK
- **Nettoprijs**: "abc" → ❌ **Error 704**: "Niet numeriek"
- **Is BestelbareEenheid**: "Ja" → ❌ **Error 719**: "Ongeldig, alleen 1 of 0"
- **Is BasisEenheid**: "Nee" → ❌ **Error 719**: "Ongeldig, alleen 1 of 0"
- **Omschrijving Verpakkingseenheid**: "Doos" → ✅ OK

### **Rij 4: Empty field scenario's**
- **Brutoprijs**: "0" → ✅ OK (nul is geldig)
- **Nettoprijs**: "" → ❌ **Error 700**: "Niet ingevuld verplicht"
- **Is BestelbareEenheid**: "" → ❌ **Error 700**: "Niet ingevuld verplicht"
- **Is BasisEenheid**: "" → ❌ **Error 700**: "Niet ingevuld verplicht"
- **Omschrijving Verpakkingseenheid**: "" → ❌ **Error 700**: "Niet ingevuld verplicht"

### **Rij 5: Invalid value scenario's**
- **Brutoprijs**: "" → ❌ **Error 700**: "Niet ingevuld verplicht"
- **Nettoprijs**: "12,50" → ✅ OK (decimal comma toegestaan) **GEFIXED!**
- **Is BestelbareEenheid**: "2" → ❌ **Error 719**: "Ongeldig, alleen 1 of 0"
- **Is BasisEenheid**: "True" → ❌ **Error 719**: "Ongeldig, alleen 1 of 0"
- **Omschrijving Verpakkingseenheid**: "Fles" → ✅ OK

---

## Test Validatie

### **Belangrijkste Verbeteringen die Getest Worden:**

#### ✅ **1. Nettoprijs Currency Symbol Validation (NIEUW)**
- **Voor**: Geen code 705 voor Nettoprijs
- **Nu**: **Code 705**: "In het veld 'Nettoprijs' stonden valutatekens en duizendtallenscheidingstekens in het veld, die hebben wij verwijderd."

#### ✅ **2. Omschrijving Verpakkingseenheid Message Specificiteit (VERBETERD)**
- **Voor**: "Omschrijving Verpakkingseenheid is te lang"
- **Nu**: "Omschrijving Verpakkingseenheid is te lang. De waarde zou hierdoor in een later stadium ingekort kunnen worden tot 25 karakters."

#### ✅ **3. Boolean Field Validation**
- **Is BestelbareEenheid & Is BasisEenheid**: Correcte validatie voor alleen 0/1 waarden
- **Error 719**: Voor ongeldige boolean waarden
- **Error 700**: Voor lege verplichte velden

---

## Matrix Compliance Check

### **Kolom 7 (Nettoprijs):**
- ✅ **Kolom niet gevonden**: Error 780 (via missing mandatory fields)
- ✅ **Niet gevuld**: Error 700
- ✅ **Niet numeriek**: Error 704  
- ✅ **Valutatekens verwijderen**: Error 705 **NIEUW!**

### **Kolom 8 & 9 (Boolean Fields):**
- ✅ **Niet ingevuld**: Error 700
- ✅ **Ongeldige waarde**: Error 719 (correction type)

### **Kolom 10 (Omschrijving Verpakkingseenheid):**
- ✅ **Niet ingevuld**: Error 700
- ✅ **Te lang**: Error 702 met "25 karakters" specificatie **VERBETERD!**
- ✅ **UOM mismatch**: Flag 753

---

## Hoe te Testen

1. Upload `TEST_KOLOM_6-10_VALIDATIES.xlsx` naar http://localhost:8504/
2. Run validatie
3. Check validatierapport tegen verwachte resultaten hierboven
4. Verifieer dat:
   - Nettoprijs currency symbols worden gedetecteerd (code 705)
   - Omschrijving Verpakkingseenheid "25 karakters" in bericht staat
   - Boolean fields correct valideren (alleen 0/1)
   - Alle missing mandatory column errors (780) verschijnen

---

*Test aangemaakt: 2025-10-06*  
*Doel: Verificatie van kolom 6-10 verbeteringen*