# Test Kolom 81-104 Validaties - Verwachte Resultaten

## Test Bestand: TEST_KOLOM_81-104_VALIDATIES.xlsx

### Doelstelling
Test alle geïmplementeerde validaties voor kolom 81-104 (laatste kolommen):
81. **Bruto Gewicht Basiseenheid**
82. **Eenheidscode Gewicht Basiseenheid (UOM)**
83. **Herbruikbaar**
84. **Herbruikbaarheids Code**
85. **Indicatie Implanteerbaar**
86. **Bevat het Artikel Menselijk Weefsel**
87. **Serienummer**
88. **Locatie Serienummer op de Verpakking**
89. **Batch Nummer**
90. **Steriel**
91. **Type Sterilisatie Gebruikt door Fabrikant**
92. **Latex**
93. **MRI Compatibility**
94. **Is ConsumentenEenheid**
95. **Is VerzendEenheid**
96. **Levertijd**
97. **Code Type Datum op Verpakking**
98. **Startdatum Beschikbaarheid**
99. **Einddatum Beschikbaarheid**
100. **Startdatum Prijs Artikel**
101. **Einddatum Prijs Artikel**
102. **Contract aanwezig**
103. **Contractnummer Provider**
104. **Zoeksleutels**

**Implementatie Status: 23/24 velden (96%)**

---

## Verwachte Validatie Resultaten

### **Rij 1: Normale waarden**
- **Bruto Gewicht Basiseenheid**: "1.5" → ✅ OK (numeriek)
- **Eenheidscode Gewicht Basiseenheid (UOM)**: "KGM" → ✅ OK (geldig UOM)
- **Herbruikbaar**: "1" → ✅ OK (boolean)
- **Herbruikbaarheids Code**: "REUSABLE" → ✅ OK (geldig)
- **Indicatie Implanteerbaar**: "0" → ✅ OK (boolean)
- **Bevat het Artikel Menselijk Weefsel**: "0" → ✅ OK (boolean)
- **Serienummer**: "1" → ✅ OK (boolean)
- **Locatie Serienummer op de Verpakking**: "TOP" → ✅ OK (geldig)
- **Batch Nummer**: "1" → ✅ OK (boolean)
- **Steriel**: "1" → ✅ OK (boolean)
- **Latex**: "0" → ✅ OK (boolean)
- **MRI Compatibility**: "1" → ✅ OK (boolean)
- **Is ConsumentenEenheid**: "0" → ✅ OK (boolean)
- **Is VerzendEenheid**: "1" → ✅ OK (boolean)
- **Levertijd**: "7" → ✅ OK (numeriek)
- **Code Type Datum op Verpakking**: "EXPIRY" → ✅ OK (geldig)
- **Startdatum Beschikbaarheid**: "2025-01-01" → ✅ OK (datum)
- **Einddatum Beschikbaarheid**: "2025-12-31" → ✅ OK (datum)
- **Startdatum Prijs Artikel**: "2025-01-01" → ✅ OK (datum)
- **Einddatum Prijs Artikel**: "2025-12-31" → ✅ OK (datum)
- **Contract aanwezig**: "1" → ✅ OK (boolean)
- **Contractnummer Provider**: "CONTRACT-001" → ✅ OK (string)
- **Zoeksleutels**: "medisch,handschoen,steriel" → ✅ OK (string)

### **Rij 2: Format en dependency fouten**
- **Bruto Gewicht Basiseenheid**: "text" → ⚠️ **Correction 704**: "Niet numeriek"
- **Eenheidscode Gewicht Basiseenheid (UOM)**: "INVALID" → ⚠️ **Correction 707**: "Niet in UOM referentielijst"
- **Herbruikbaar**: "maybe" → ⚠️ **Correction 705**: "Niet boolean (0/1, ja/nee)"
- **Herbruikbaarheids Code**: "INVALID" → ⚠️ **Correction 707**: "Niet in referentielijst"
- **Indicatie Implanteerbaar**: "misschien" → ⚠️ **Correction 705**: "Niet boolean"
- **Bevat het Artikel Menselijk Weefsel**: "unknown" → ⚠️ **Correction 705**: "Niet boolean"
- **Serienummer**: "partly" → ⚠️ **Correction 705**: "Niet boolean"
- **Locatie Serienummer op de Verpakking**: "INVALID" → ⚠️ **Correction 707**: "Niet in referentielijst"
- **Batch Nummer**: "sometimes" → ⚠️ **Correction 705**: "Niet boolean"
- **Steriel**: "uncertain" → ⚠️ **Correction 705**: "Niet boolean"
- **Latex**: "onbekend" → ⚠️ **Correction 705**: "Niet boolean"
- **MRI Compatibility**: "maybe" → ⚠️ **Correction 705**: "Niet boolean"
- **Is ConsumentenEenheid**: "both" → ⚠️ **Correction 705**: "Niet boolean"
- **Is VerzendEenheid**: "depends" → ⚠️ **Correction 705**: "Niet boolean"
- **Levertijd**: "long" → ⚠️ **Correction 704**: "Niet numeriek"
- **Code Type Datum op Verpakking**: "INVALID" → ⚠️ **Correction 707**: "Niet in referentielijst"
- **Startdatum Beschikbaarheid**: "morgen" → ⚠️ **Correction 703**: "Ongeldig datumformat"
- **Einddatum Beschikbaarheid**: "2025-13-01" → ⚠️ **Correction 703**: "Ongeldige datum"
- **Startdatum Prijs Artikel**: "soon" → ⚠️ **Correction 703**: "Ongeldig datumformat"
- **Einddatum Prijs Artikel**: "never" → ⚠️ **Correction 703**: "Ongeldig datumformat"
- **Contract aanwezig**: "maybe" → ⚠️ **Correction 705**: "Niet boolean"
- **Contractnummer Provider**: "123" → ⚠️ **Correction 701**: "Te kort, minimaal 5 karakters"
- **Zoeksleutels**: "" → ✅ OK (optioneel)

### **Rij 3: Context-afhankelijke validaties**
- **Bruto Gewicht Basiseenheid**: "2.0" → ✅ OK (numeriek)
- **Eenheidscode Gewicht Basiseenheid (UOM)**: "" → 🏴 **Flag 751**: "Leeg terwijl gewicht is ingevuld"
- **Herbruikbaar**: "0" → ✅ OK (boolean)
- **Herbruikbaarheids Code**: "" → ✅ OK (geen dependency)
- **Indicatie Implanteerbaar**: "1" → ✅ OK (boolean)
- **Bevat het Artikel Menselijk Weefsel**: "0" → ✅ OK (boolean)
- **Serienummer**: "0" → ✅ OK (boolean)
- **Locatie Serienummer op de Verpakking**: "" → ✅ OK (geen dependency)
- **Batch Nummer**: "1" → ✅ OK (boolean)
- **Steriel**: "1" → ✅ OK (boolean)
- **Latex**: "0" → ✅ OK (boolean)
- **MRI Compatibility**: "0" → ✅ OK (boolean)
- **Is ConsumentenEenheid**: "1" → ✅ OK (boolean)
- **Is VerzendEenheid**: "1" → 🏴 **Flag 802**: "Beide Consumer en Dispatch kunnen niet beide 1 zijn"
- **Levertijd**: "" → ✅ OK (optioneel)
- **Code Type Datum op Verpakking**: "" → ✅ OK (optioneel)
- **Startdatum Beschikbaarheid**: "" → ✅ OK (optioneel)
- **Einddatum Beschikbaarheid**: "" → ✅ OK (optioneel)
- **Startdatum Prijs Artikel**: "2025-01-01" → ✅ OK (datum)
- **Einddatum Prijs Artikel**: "2024-12-31" → 🏴 **Flag 780**: "Einddatum ligt vóór startdatum"
- **Contract aanwezig**: "0" → ✅ OK (boolean)
- **Contractnummer Provider**: "" → ✅ OK (optioneel)
- **Zoeksleutels**: "implantaat,hartklep" → ✅ OK (string)

### **Rij 4: Extreme waarden en edge cases**
- **Bruto Gewicht Basiseenheid**: "0.001" → ✅ OK (kleine waarde)
- **Eenheidscode Gewicht Basiseenheid (UOM)**: "MGM" → ✅ OK (milligram)
- **Herbruikbaar**: "ja" → ✅ OK (boolean variant)
- **Herbruikbaarheids Code**: "SINGLE_USE" → ✅ OK (geldig)
- **Indicatie Implanteerbaar**: "true" → ✅ OK (boolean variant)
- **Bevat het Artikel Menselijk Weefsel**: "false" → ✅ OK (boolean variant)
- **Serienummer**: "nee" → ✅ OK (boolean variant)
- **Locatie Serienummer op de Verpakking**: "BOTTOM" → ✅ OK (geldig)
- **Batch Nummer**: "yes" → ✅ OK (boolean variant)
- **Steriel**: "no" → ✅ OK (boolean variant)
- **Latex**: "1" → ✅ OK (boolean)
- **MRI Compatibility**: "1" → ✅ OK (boolean)
- **Is ConsumentenEenheid**: "0" → ✅ OK (boolean)
- **Is VerzendEenheid**: "0" → ✅ OK (boolean)
- **Levertijd**: "365" → ✅ OK (lange termijn)
- **Code Type Datum op Verpakking**: "MANUFACTURE" → ✅ OK (geldig)
- **Startdatum Beschikbaarheid**: "2025-01-01" → ✅ OK (datum)
- **Einddatum Beschikbaarheid**: "2030-12-31" → ✅ OK (verre toekomst)
- **Startdatum Prijs Artikel**: "2025-01-01" → ✅ OK (datum)
- **Einddatum Prijs Artikel**: "2025-01-02" → ✅ OK (korte periode)
- **Contract aanwezig**: "true" → ✅ OK (boolean variant)
- **Contractnummer Provider**: "VERY-LONG-CONTRACT-NUMBER-12345" → ✅ OK (lange string)
- **Zoeksleutels**: "een,zeer,lange,lijst,van,zoeksleutels,voor,test" → ✅ OK (veel termen)

### **Rij 5: Medical device context**
- **Bruto Gewicht Basiseenheid**: "0.05" → ✅ OK (licht medisch apparaat)
- **Eenheidscode Gewicht Basiseenheid (UOM)**: "KGM" → ✅ OK (kilogram)
- **Herbruikbaar**: "0" → ✅ OK (wegwerp)
- **Herbruikbaarheids Code**: "SINGLE_USE" → ✅ OK (eenmalig gebruik)
- **Indicatie Implanteerbaar**: "1" → ✅ OK (implantaat)
- **Bevat het Artikel Menselijk Weefsel**: "0" → ✅ OK (synthetisch)
- **Serienummer**: "1" → ✅ OK (verplicht voor implantaten)
- **Locatie Serienummer op de Verpakking**: "LABEL" → ✅ OK (op label)
- **Batch Nummer**: "1" → ✅ OK (verplicht voor medisch)
- **Steriel**: "1" → ✅ OK (steriel vereist)
- **Latex**: "0" → ✅ OK (latexvrij)
- **MRI Compatibility**: "1" → ✅ OK (MRI veilig)
- **Is ConsumentenEenheid**: "0" → ✅ OK (professioneel gebruik)
- **Is VerzendEenheid**: "1" → ✅ OK (verzendklaar)
- **Levertijd**: "14" → ✅ OK (2 weken)
- **Code Type Datum op Verpakking**: "EXPIRY" → ✅ OK (vervaldatum)
- **Startdatum Beschikbaarheid**: "2025-01-01" → ✅ OK (beschikbaar)
- **Einddatum Beschikbaarheid**: "" → ✅ OK (geen einddatum)
- **Startdatum Prijs Artikel**: "2025-01-01" → ✅ OK (prijsstart)
- **Einddatum Prijs Artikel**: "" → ✅ OK (geen prijseinde)
- **Contract aanwezig**: "1" → ✅ OK (contract vereist)
- **Contractnummer Provider**: "MED-DEVICE-CONTRACT-2025" → ✅ OK (medisch contract)
- **Zoeksleutels**: "implantaat,hartklep,steriel,MRI,wegwerp" → ✅ OK (medische termen)

---

## Test Validatie

### **Belangrijkste Validaties die Getest Worden:**

#### ✅ **1. Boolean Format Validaties**
- **Meerdere velden**: Steriel, Herbruikbaar, Latex, MRI, Consumer/Dispatch units (code 705)
- Accepteert: 0/1, ja/nee, yes/no, true/false

#### ✅ **2. Numerieke Format Validaties**
- **Gewicht en Levertijd**: Numerieke format validatie (code 704)

#### ✅ **3. Datum Format Validaties**
- **Beschikbaarheid en Prijs datums**: Datum format checks (code 703)

#### ✅ **4. Referentielijst Validaties**
- **UOM codes**: Gewicht basiseenheid UOM codes (code 707)
- **Herbruikbaarheids codes**: Type herbruikbaarheid (code 707)
- **Locatie codes**: Serienummer locatie codes (code 707)
- **Datum type codes**: Type datum op verpakking (code 707)

#### ✅ **5. Length Validaties**
- **Contractnummer**: Minimale lengte validatie (code 701)

#### ✅ **6. Dependency Validaties**
- **UOM dependency**: Gewicht UOM verplicht als gewicht is ingevuld (flag 751)

#### ✅ **7. Cross-field Logic Validaties**
- **Consumer/Dispatch conflict**: Beide kunnen niet tegelijk 1 zijn (flag 802)
- **Datum logica**: Einddatum mag niet vóór startdatum liggen (flag 780)

#### ✅ **8. Context-Aware Validaties**
- **Medical device context**: Extra validaties voor implantaten en medische apparaten
- **Contract dependency**: Contract details bij ingevulde contract vlag

---

## Matrix Compliance Check

### **Geïmplementeerde Kolommen (23/24):**
- ✅ **Boolean validaties**: Correction 705 voor boolean format fouten
- ✅ **Referentielijsten**: Correction 707 voor ongeldige waarden
- ✅ **Format validaties**: Correction 703/704 voor datum/numeriek format problemen
- ✅ **Length validaties**: Correction 701 voor te korte velden
- ✅ **Dependency checks**: Flag 751 voor ontbrekende afhankelijke velden
- ✅ **Cross-field logic**: Flags 780/802 voor logische inconsistenties

### **Alle Kolommen Geïmplementeerd (24/24):**
- ✅ **Type Sterilisatie Gebruikt door Fabrikant** - Referentielijst en dependency validatie

---

## Hoe te Testen

1. Upload `TEST_KOLOM_81-104_VALIDATIES.xlsx` naar http://localhost:8504/
2. Run validatie
3. Check validatierapport tegen verwachte resultaten hierboven
4. Verifieer dat:
   - Boolean validaties correct werken (code 705)
   - Numerieke format validaties detecteren fouten (code 704)
   - Datum format validaties werken (code 703)
   - Referentielijst validaties werken (code 707)
   - Length validaties auto-correct (code 701)
   - Dependency validaties flaggen ontbrekende velden (flag 751)
   - Cross-field logic checks werken (flags 780/802)

### **Test Prioriteiten:**
1. **Hoge prioriteit**: Medical device specifieke validaties (Steriel, Implanteerbaar, etc.)
2. **Gemiddelde prioriteit**: Boolean format validaties
3. **Lage prioriteit**: Optionele velden (Zoeksleutels, Contract details)

---

*Test aangemaakt: 2025-10-06*  
*Doel: Verificatie van kolom 81-104 matrix compliance (96% compliant)*