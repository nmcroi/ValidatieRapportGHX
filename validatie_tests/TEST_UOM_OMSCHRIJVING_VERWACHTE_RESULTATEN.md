# Test UOM Omschrijving Validatie - Verwachte Resultaten

## Test Bestand: TEST_UOM_OMSCHRIJVING_VALIDATIE.xlsx

### Doelstelling
Test de nieuwe **code 753** implementatie voor `uom_description_mismatch` validatie.

---

## Test Data & Verwachte Resultaten

### **Rij 1: TEST001 - Perfect scenario** ✅
- **Omschrijving**: "BX 72 BO 150 ML"
- **UOM Code Verpakkingseenheid**: "BX" 
- **Verwacht resultaat**: ✅ **GEEN** code 753 fout
- **Reden**: Begint met BX, bevat alleen geldige UOM codes

### **Rij 2: TEST002 - Slecht scenario** ❌
- **Omschrijving**: "Doos met medicijnen"
- **UOM Code Verpakkingseenheid**: "BX"
- **Verwacht resultaat**: ❌ **WEL** code 753 fout
- **Reden**: Begint NIET met BX, bevat geen UOM codes

### **Rij 3: TEST003 - Goed scenario** ✅  
- **Omschrijving**: "BX 24 PCE"
- **UOM Code Verpakkingseenheid**: "BX"
- **Verwacht resultaat**: ✅ **GEEN** code 753 fout
- **Reden**: Begint met BX, bevat geldige UOM codes

### **Rij 4: TEST004 - Mixed scenario** ⚠️
- **Omschrijving**: "BOX 12 XYZ"  
- **UOM Code Verpakkingseenheid**: "BX"
- **Verwacht resultaat**: ❌ **WEL** code 753 fout
- **Reden**: Begint met BOX (niet BX), of XYZ is geen geldige UOM

---

## Implementatie Details

### **FASE 1 Checks (Geïmplementeerd):**
1. **Check 1**: Begint omschrijving met UOM Code uit kolom K?
2. **Check 2**: Zijn alle hoofdletterwoorden geldige UOM codes?

### **Code Details:**
- **Error Code**: 753
- **Type**: Flag
- **Condition**: `uom_description_mismatch`
- **Message**: "De 'Omschrijving Verpakkingseenheid' komt mogelijk niet overeen met de specificaties in de UOM-velden die erop volgen. Controleer of de omschrijving en de UOM-codes en -inhoud met elkaar corresponderen."

---

## Hoe te Testen

1. Upload `TEST_UOM_OMSCHRIJVING_VALIDATIE.xlsx` naar http://localhost:8504/
2. Run validatie
3. Check validatierapport voor code 753 meldingen
4. Verifieer dat:
   - **TEST001**: Geen code 753 ✅
   - **TEST002**: WEL code 753 ❌ 
   - **TEST003**: Geen code 753 ✅
   - **TEST004**: WEL code 753 ❌

---

*Test aangemaakt: 2025-10-06*  
*Doel: Verificatie van nieuwe UOM-omschrijving validatie implementatie*