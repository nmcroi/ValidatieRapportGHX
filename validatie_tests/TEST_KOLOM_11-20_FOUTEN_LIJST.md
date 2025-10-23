# 📋 Test Fouten Lijst voor Kolom 11-20

## **Maak je eigen test template met deze fouten:**

### **KOLOM 11: UOM CODE VERPAKKINGSEENHEID**
1. **Leeg laten** → Error 700: "Verplicht maar niet ingevuld"
2. **Ongeldige code**: "XYZ" → Error 707: "Niet in referentielijst UOM Codes"
3. **Normaal OK**: "PCE" → ✅ Geen fout

### **KOLOM 12: INHOUD VERPAKKINGSEENHEID**  
1. **Leeg laten** → Error 700: "Verplicht maar niet ingevuld"
2. **Niet numeriek**: "abc" → Error 704: "Ongeldig format, alleen numeriek"
3. **Normaal OK**: "1" → ✅ Geen fout

### **KOLOM 13: UOM CODE BASISEENHEID**
1. **Leeg laten** → Error 700: "Verplicht maar niet ingevuld" 
2. **Ongeldige code**: "WRONG" → Error 707: "Niet in referentielijst UOM Codes"
3. **Normaal OK**: "PCE" → ✅ Geen fout

### **KOLOM 14: INHOUD BASISEENHEID**
1. **Leeg laten** → Error 700: "Verplicht maar niet ingevuld"
2. **Niet numeriek**: "xyz" → Error 704: "Ongeldig format, alleen numeriek"  
3. **Normaal OK**: "1" → ✅ Geen fout

### **KOLOM 15: UOM CODE INHOUD BASISEENHEID**
1. **Leeg laten** → Error 700: "Verplicht maar niet ingevuld"
2. **Ongeldige code**: "BAD" → Error 707: "Niet in referentielijst UOM Codes"
3. **Normaal OK**: "PCE" → ✅ Geen fout

### **KOLOM 16: OMREKENFACTOR**
1. **Leeg laten** → Error 700: "Niet ingevuld"
2. **Berekening mismatch**: "999" → Flag 720: "Komt niet overeen met berekende waarde"
3. **Normaal OK**: "1" → ✅ Mogelijk correction 754 (auto-calculated)

### **KOLOM 17: PRIJS PER KLEINSTE EENHEID**  
1. **Berekening mismatch**: "999" → Flag 720: "Komt niet overeen met berekende waarde"
2. **Normaal**: Leeg laten → Correction 755: "Auto-berekend"

### **KOLOM 18: AANTAL VAN DE VOLGENDE LAGERE VERPAKKINGSLAAG**
1. **Niet numeriek**: "abc" → Correction 704: "Ongeldig, alleen numeriek"
2. **Normaal OK**: "1" → ✅ Geen fout

### **KOLOM 19: ARTIKEL HIËRARCHIE OMSCHRIJVING**
1. **Ongeldige waarde**: "WRONG" → Correction 707: "Niet in referentielijst DescriptorCode"
2. **Normaal OK**: Geldige waarde → ✅ Geen fout

### **KOLOM 20: GTIN VERPAKKINGSEENHEID**
1. **Te kort**: "123456" → Error 701: "Een GTIN bestaat uit 13 of 14 cijfers" **VERBETERD!**
2. **Te lang**: "123456789012345" → Error 702: "Een GTIN bestaat uit 13 of 14 cijfers" **VERBETERD!**  
3. **Duplicaat**: Zelfde GTIN 2x → Flag 703: "Komt meerdere malen voor"
4. **Normaal OK**: "1234567890123" → ✅ Geen fout

## 🎯 **Belangrijkste Tests:**

### **Error 707 Test (UOM Codes)**
- Alle UOM velden met ongeldige codes → Moet referentielijst errors geven

### **Error 704 Test (Numerieke Velden)**  
- Inhoud velden met tekst → Moet numeriek format errors geven

### **GTIN Format Test (VERBETERD)**
- GTIN < 13 of > 14 digits → Moet "13 of 14 cijfers" message geven **NIEUW!**

### **Auto-Calculation Tests**
- Omrekenfactor & Prijs per Kleinste eenheid → Correction/Flag berichten

**Kolom 11-20 zijn zeer stabiel - minimale fouten verwacht! ✅**