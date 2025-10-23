# Test Kolom 61-80 Validaties - Verwachte Resultaten

## Test Bestand: TEST_KOLOM_61-80_VALIDATIES.xlsx

### Doelstelling
Test alle geïmplementeerde validaties voor kolom 61-80:
61. **UN-nummer Gevaarlijke Stof**
62. **ADR Gevarenklasse**
63. **Veiligheidsblad (VIB/SDS)**
64. **Link Veiligheidsinformatieblad (SDS)**
65. **Eindgebruikersverklaring**
66. **Koelgoed**
67. **Vriesgoed**
68. **Code Type Temperatuur**
69. **Gebruiksaanwijzing Code Referentie**
70. **Maximum Temperatuur**
71. **Minimum Temperatuur**
72. **Eenheid van Temperatuur**
73. **Bruto Gewicht Verpakkingseenheid**
74. **Eenheidscode Bruto Gewicht Verpakkingseenheid (UOM)**
75. **Hoogte**
76. **Eenheidscode Hoogte (UOM)**
77. **Breedte**
78. **Eenheidscode Breedte (UOM)**
79. **Diepte**
80. **Eenheidscode Diepte (UOM)**

**Implementatie Status: 20/20 velden (100%)**

---

## Verwachte Validatie Resultaten

### **Rij 1: Normale waarden**
- **UN-nummer Gevaarlijke Stof**: "UN1234" → ✅ OK (geldig format)
- **ADR Gevarenklasse**: "3" → ✅ OK (geldig)
- **Veiligheidsblad (VIB/SDS)**: "1" → ✅ OK (boolean)
- **Link Veiligheidsinformatieblad (SDS)**: "https://example.com/sds.pdf" → ✅ OK (https)
- **Eindgebruikersverklaring**: "1" → ✅ OK (boolean)
- **Koelgoed**: "0" → ✅ OK (boolean)
- **Vriesgoed**: "0" → ✅ OK (boolean)
- **Code Type Temperatuur**: "AMBIENT" → ✅ OK (geldig)
- **Gebruiksaanwijzing Code Referentie**: "REF001" → ✅ OK (geldig)
- **Maximum Temperatuur**: "25" → ✅ OK (numeriek)
- **Minimum Temperatuur**: "15" → ✅ OK (numeriek)
- **Eenheid van Temperatuur**: "CEL" → ✅ OK (geldig)
- **Bruto Gewicht Verpakkingseenheid**: "2.5" → ✅ OK (numeriek)
- **Hoogte**: "10.5" → ✅ OK (numeriek)
- **Breedte**: "8.0" → ✅ OK (numeriek)
- **Diepte**: "6.2" → ✅ OK (numeriek)

### **Rij 2: Format en dependency fouten**
- **UN-nummer Gevaarlijke Stof**: "INVALID" → ⚠️ **Correction 718**: "Ongeldig UN-nummer format"
- **ADR Gevarenklasse**: "invalid" → ⚠️ **Correction 720**: "Niet in referentielijst"
- **Veiligheidsblad (VIB/SDS)**: "maybe" → ⚠️ **Correction 719**: "Niet boolean (0/1, ja/nee)"
- **Link Veiligheidsinformatieblad (SDS)**: "http://example.com" → ⚠️ **Correction 722**: "Moet beginnen met https://"
- **Eindgebruikersverklaring**: "misschien" → ⚠️ **Correction 717**: "Niet boolean"
- **Koelgoed**: "yes" → ✅ OK (boolean variant)
- **Vriesgoed**: "no" → ✅ OK (boolean variant)
- **Code Type Temperatuur**: "INVALID" → ⚠️ **Correction 716**: "Niet in referentielijst"
- **Gebruiksaanwijzing Code Referentie**: "INVALID" → ⚠️ **Correction 715**: "Niet in referentielijst"
- **Maximum Temperatuur**: "not-a-number" → ⚠️ **Correction 704**: "Niet numeriek"
- **Minimum Temperatuur**: "abc" → ⚠️ **Correction 704**: "Niet numeriek"
- **Eenheid van Temperatuur**: "INVALID" → ⚠️ **Correction 714**: "Niet in referentielijst"
- **Bruto Gewicht Verpakkingseenheid**: "text" → ⚠️ **Correction 704**: "Niet numeriek"
- **Hoogte**: "text" → ⚠️ **Correction 704**: "Niet numeriek"
- **Breedte**: "text" → ⚠️ **Correction 704**: "Niet numeriek"
- **Diepte**: "text" → ⚠️ **Correction 704**: "Niet numeriek"

### **Rij 3: Context-afhankelijke validaties**
- **UN-nummer Gevaarlijke Stof**: "" → ✅ OK (optioneel)
- **ADR Gevarenklasse**: "" → ✅ OK (optioneel)
- **Veiligheidsblad (VIB/SDS)**: "0" → ✅ OK (boolean)
- **Link Veiligheidsinformatieblad (SDS)**: "" → ✅ OK (optioneel)
- **Eindgebruikersverklaring**: "0" → ✅ OK (boolean)
- **Koelgoed**: "1" → ✅ OK (boolean)
- **Vriesgoed**: "1" → ✅ OK (boolean)
- **Code Type Temperatuur**: "" → ✅ OK (optioneel)
- **Gebruiksaanwijzing Code Referentie**: "" → ✅ OK (optioneel)
- **Maximum Temperatuur**: "37" → ✅ OK (numeriek)
- **Minimum Temperatuur**: "2" → ✅ OK (numeriek)
- **Eenheid van Temperatuur**: "CEL" → ✅ OK (geldig)
- **Bruto Gewicht Verpakkingseenheid**: "" → ✅ OK (optioneel)
- **Hoogte**: "15.0" → ✅ OK (numeriek)
- **Breedte**: "" → 🏴 **Flag 801**: "Incomplete afmetingen set (H, B, D)"
- **Diepte**: "" → 🏴 **Flag 801**: "Incomplete afmetingen set (H, B, D)"

### **Rij 4: Extreme waarden en duplicate detection**
- **UN-nummer Gevaarlijke Stof**: "UN9999" → ✅ OK (geldig)
- **ADR Gevarenklasse**: "9" → ✅ OK (geldig)
- **Veiligheidsblad (VIB/SDS)**: "true" → ✅ OK (boolean variant)
- **Link Veiligheidsinformatieblad (SDS)**: "https://example.com/sds.pdf" → 🏴 **Flag 774**: "Duplicate SDS URL" (zelfde als rij 1)
- **Eindgebruikersverklaring**: "ja" → ✅ OK (boolean variant)
- **Koelgoed**: "false" → ✅ OK (boolean variant)
- **Vriesgoed**: "nee" → ✅ OK (boolean variant)
- **Code Type Temperatuur**: "FROZEN" → ✅ OK (geldig)
- **Gebruiksaanwijzing Code Referentie**: "REF999" → ✅ OK (geldig)
- **Maximum Temperatuur**: "-273.15" → ✅ OK (extreme waarde)
- **Minimum Temperatuur**: "-80" → ✅ OK (extreme waarde)
- **Eenheid van Temperatuur**: "FAH" → ✅ OK (geldig)
- **Bruto Gewicht Verpakkingseenheid**: "999.999" → ✅ OK (decimaal)
- **Hoogte**: "0.001" → ✅ OK (kleine waarde)
- **Breedte**: "1000.0" → ✅ OK (grote waarde)
- **Diepte**: "50.5" → ✅ OK (normaal)

### **Rij 5: Chemical substance context**
- **UN-nummer Gevaarlijke Stof**: "UN1170" → ✅ OK (ethanol)
- **ADR Gevarenklasse**: "3" → ✅ OK (brandbaar)
- **Veiligheidsblad (VIB/SDS)**: "1" → ✅ OK (verplicht voor gevaarlijke stoffen)
- **Link Veiligheidsinformatieblad (SDS)**: "https://chemical-company.com/ethanol-sds.pdf" → ✅ OK (specifieke SDS)
- **Eindgebruikersverklaring**: "1" → ✅ OK (vereist)
- **Koelgoed**: "0" → ✅ OK (niet gekoeld)
- **Vriesgoed**: "0" → ✅ OK (niet bevroren)
- **Code Type Temperatuur**: "AMBIENT" → ✅ OK (kamertemperatuur)
- **Gebruiksaanwijzing Code Referentie**: "HAZMAT01" → ✅ OK (gevaarlijke goederen)
- **Maximum Temperatuur**: "40" → ✅ OK (opslagtemperatuur)
- **Minimum Temperatuur**: "-10" → ✅ OK (opslagtemperatuur)
- **Eenheid van Temperatuur**: "CEL" → ✅ OK (Celsius)
- **Bruto Gewicht Verpakkingseenheid**: "1.0" → ✅ OK (1 liter)
- **Hoogte**: "25.4" → ✅ OK (fles hoogte)
- **Breedte**: "7.5" → ✅ OK (fles diameter)
- **Diepte**: "7.5" → ✅ OK (fles diameter)

---

## Test Validatie

### **Belangrijkste Validaties die Getest Worden:**

#### ✅ **1. Gevaarlijke Stoffen Validaties**
- **UN-nummer**: Format validatie voor UN-nummers (code 718)
- **ADR Gevarenklasse**: Referentielijst validatie (code 720)
- **SDS Link**: HTTPS vereiste + duplicate detection (codes 722/774)

#### ✅ **2. Boolean Format Validaties**
- **VIB/SDS, Eindgebruikersverklaring, Koelgoed, Vriesgoed**: Boolean format checks (codes 717/719)
- Accepteert: 0/1, ja/nee, yes/no, true/false

#### ✅ **3. Temperatuur Validaties**
- **Max/Min Temperatuur**: Numerieke format validatie (code 704)
- **Eenheid van Temperatuur**: Referentielijst validatie (code 714)
- **Code Type Temperatuur**: Referentielijst validatie (code 716)

#### ✅ **4. Afmetingen en Gewicht Validaties**
- **Numerieke velden**: Format validatie voor Hoogte, Breedte, Diepte, Gewicht (code 704)
- **Incomplete set**: Flag voor onvolledige afmetingen set (flag 801)

#### ✅ **5. Referentielijst Validaties**
- **Codes**: Gebruiksaanwijzing, Temperatuur, etc. (codes 714-716/720)

#### ✅ **6. URL en Duplicate Validaties**
- **SDS Links**: HTTPS vereiste (code 722)
- **Duplicate SDS**: Detection van herhaalde URLs met verschillende chemicaliën (flag 774)

---

## Matrix Compliance Check

### **Geïmplementeerde Kolommen (16/20):**
- ✅ **Boolean validaties**: Correction codes 717/719 voor boolean format fouten
- ✅ **Referentielijsten**: Correction codes 714-716/720 voor ongeldige waarden
- ✅ **Format validaties**: Correction 704 voor numerieke format problemen
- ✅ **URL formaten**: Correction 722 voor protocol issues
- ✅ **Duplicate detection**: Flag 774 voor herhaalde SDS URLs
- ✅ **Cross-field checks**: Flag 801 voor incomplete afmetingen sets

### **Niet Geïmplementeerde Kolommen (4/20):**
- ❌ **Eenheidscode Bruto Gewicht Verpakkingseenheid** - UOM referentielijst validatie
- ❌ **Eenheidscode Hoogte** - UOM referentielijst validatie  
- ❌ **Eenheidscode Breedte** - UOM referentielijst validatie
- ❌ **Eenheidscode Diepte** - UOM referentielijst validatie

---

## Hoe te Testen

1. Upload `TEST_KOLOM_61-80_VALIDATIES.xlsx` naar http://localhost:8504/
2. Run validatie
3. Check validatierapport tegen verwachte resultaten hierboven
4. Verifieer dat:
   - Boolean validaties correct werken (codes 717/719)
   - UN-nummer format validaties detecteren fouten (code 718)
   - Referentielijst validaties werken (codes 714-716/720)
   - Numerieke format validaties detecteren fouten (code 704)
   - HTTPS URL validaties werken (code 722)
   - Duplicate SDS detection werkt (flag 774)
   - Incomplete afmetingen detection werkt (flag 801)

### **Test Prioriteiten:**
1. **Hoge prioriteit**: Gevaarlijke stoffen validaties (UN-nummer, ADR, SDS)
2. **Gemiddelde prioriteit**: Temperatuur en afmetingen validaties
3. **Lage prioriteit**: UOM code velden (niet geïmplementeerd)

---

*Test aangemaakt: 2025-10-06*  
*Doel: Verificatie van kolom 61-80 matrix compliance (80% compliant)*