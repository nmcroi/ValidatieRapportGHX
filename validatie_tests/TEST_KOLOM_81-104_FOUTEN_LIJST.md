# Test Kolom 81-104 Validaties - Fouten Lijst

## Overzicht Alle Mogelijke Validatie Fouten

Dit document bevat alle validatie fouten die kunnen optreden voor kolommen 81-104 (laatste kolommen).

**Implementatie Status: 23/24 velden (96% compliant)**

---

## **KOLOM 81: Bruto Gewicht Basiseenheid**

### ⚠️ **AANPASSINGEN:**
- **Code 704**: De waarde voor 'Bruto Gewicht Basiseenheid' is niet numeriek. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 751**: Het veld 'Bruto Gewicht Basiseenheid' is ingevuld, maar de bijbehorende 'Eenheidscode Gewicht Basiseenheid' ontbreekt.

---

## **KOLOM 82: Eenheidscode Gewicht Basiseenheid (UOM)**

### ⚠️ **AANPASSINGEN:**
- **Code 707**: De ingevulde waarde voor 'Eenheidscode Gewicht Basiseenheid (UOM)' komt niet voor in de referentielijst. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 751**: Het veld 'Eenheidscode Gewicht Basiseenheid (UOM)' is ingevuld, maar de bijbehorende 'Bruto Gewicht Basiseenheid' ontbreekt.

---

## **KOLOM 83: Herbruikbaar**

### ⚠️ **AANPASSINGEN:**
- **Code 705**: De waarde voor 'Herbruikbaar' heeft een ongeldig format. Het veld accepteert alleen boolean waarden (0/1, ja/nee, true/false).

---

## **KOLOM 84: Herbruikbaarheids Code**

### ⚠️ **AANPASSINGEN:**
- **Code 707**: De ingevulde waarde voor 'Herbruikbaarheids Code' komt niet voor in de referentielijst. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 751**: Het veld 'Herbruikbaarheids Code' is ingevuld, maar de bijbehorende 'Herbruikbaar' ontbreekt of is negatief.

---

## **KOLOM 85: Indicatie Implanteerbaar**

### ⚠️ **AANPASSINGEN:**
- **Code 705**: De waarde voor 'Indicatie Implanteerbaar' heeft een ongeldig format. Het veld accepteert alleen boolean waarden (0/1, ja/nee, true/false).

---

## **KOLOM 86: Bevat het Artikel Menselijk Weefsel**

### ⚠️ **AANPASSINGEN:**
- **Code 705**: De waarde voor 'Bevat het Artikel Menselijk Weefsel' heeft een ongeldig format. Het veld accepteert alleen boolean waarden (0/1, ja/nee, true/false).

---

## **KOLOM 87: Serienummer**

### ⚠️ **AANPASSINGEN:**
- **Code 705**: De waarde voor 'Serienummer' heeft een ongeldig format. Het veld accepteert alleen boolean waarden (0/1, ja/nee, true/false).

---

## **KOLOM 88: Locatie Serienummer op de Verpakking**

### ⚠️ **AANPASSINGEN:**
- **Code 707**: De ingevulde waarde voor 'Locatie Serienummer op de Verpakking' komt niet voor in de referentielijst. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

---

## **KOLOM 89: Batch Nummer**

### ⚠️ **AANPASSINGEN:**
- **Code 705**: De waarde voor 'Batch Nummer' heeft een ongeldig format. Het veld accepteert alleen boolean waarden (0/1, ja/nee, true/false).

---

## **KOLOM 90: Steriel**

### ⚠️ **AANPASSINGEN:**
- **Code 705**: De waarde voor 'Steriel' heeft een ongeldig format. Het veld accepteert alleen boolean waarden (0/1, ja/nee, true/false).

---

## **KOLOM 91: Type Sterilisatie Gebruikt door Fabrikant**

### ❌ **NIET GEÏMPLEMENTEERD**
*Dit veld is nog niet geïmplementeerd in de JSON configuratie*

**Verwachte validaties:**
- **Code 707**: Referentielijst validatie voor sterilisatie types
- **Code 751**: Dependency validatie - verplicht als 'Steriel' = 1

---

## **KOLOM 92: Latex**

### ⚠️ **AANPASSINGEN:**
- **Code 705**: De waarde voor 'Latex' heeft een ongeldig format. Het veld accepteert alleen boolean waarden (0/1, ja/nee, true/false).

---

## **KOLOM 93: MRI Compatibility**

### ⚠️ **AANPASSINGEN:**
- **Code 705**: De waarde voor 'MRI Compatibility' heeft een ongeldig format. Het veld accepteert alleen boolean waarden (0/1, ja/nee, true/false).

---

## **KOLOM 94: Is ConsumentenEenheid**

### ⚠️ **AANPASSINGEN:**
- **Code 705**: De waarde voor 'Is ConsumentenEenheid' heeft een ongeldig format. Het veld accepteert alleen boolean waarden (0/1, ja/nee, true/false).

### 🏴 **FLAGS:**
- **Code 802**: Zowel 'Is ConsumentenEenheid' als 'Is VerzendEenheid' zijn ingevuld als 1. Dit is een conflicterende combinatie.

---

## **KOLOM 95: Is VerzendEenheid**

### ⚠️ **AANPASSINGEN:**
- **Code 705**: De waarde voor 'Is VerzendEenheid' heeft een ongeldig format. Het veld accepteert alleen boolean waarden (0/1, ja/nee, true/false).

### 🏴 **FLAGS:**
- **Code 802**: Zowel 'Is ConsumentenEenheid' als 'Is VerzendEenheid' zijn ingevuld als 1. Dit is een conflicterende combinatie.

---

## **KOLOM 96: Levertijd**

### ⚠️ **AANPASSINGEN:**
- **Code 704**: De waarde voor 'Levertijd' is niet numeriek. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

---

## **KOLOM 97: Code Type Datum op Verpakking**

### ⚠️ **AANPASSINGEN:**
- **Code 707**: De ingevulde waarde voor 'Code Type Datum op Verpakking' komt niet voor in de referentielijst. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

---

## **KOLOM 98: Startdatum Beschikbaarheid**

### ⚠️ **AANPASSINGEN:**
- **Code 703**: De 'Startdatum Beschikbaarheid' heeft een ongeldig datumformat. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 780**: De 'Startdatum Beschikbaarheid' ligt na de 'Einddatum Beschikbaarheid'. Controleer of de datums correct zijn.

---

## **KOLOM 99: Einddatum Beschikbaarheid**

### ⚠️ **AANPASSINGEN:**
- **Code 703**: De 'Einddatum Beschikbaarheid' heeft een ongeldig datumformat. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 780**: De 'Einddatum Beschikbaarheid' ligt vóór de 'Startdatum Beschikbaarheid'. Controleer of de datums correct zijn.

---

## **KOLOM 100: Startdatum Prijs Artikel**

### ⚠️ **AANPASSINGEN:**
- **Code 703**: De 'Startdatum Prijs Artikel' heeft een ongeldig datumformat. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 780**: De 'Startdatum Prijs Artikel' ligt na de 'Einddatum Prijs Artikel'. Controleer of de datums correct zijn.

---

## **KOLOM 101: Einddatum Prijs Artikel**

### ⚠️ **AANPASSINGEN:**
- **Code 703**: De 'Einddatum Prijs Artikel' heeft een ongeldig datumformat. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 780**: De 'Einddatum Prijs Artikel' ligt vóór de 'Startdatum Prijs Artikel'. Controleer of de datums correct zijn.
- **Code 781**: De 'Einddatum Prijs Artikel' ligt in het verleden. Controleer of de prijsgegevens nog actueel zijn.

---

## **KOLOM 102: Contract aanwezig**

### ⚠️ **AANPASSINGEN:**
- **Code 705**: De waarde voor 'Contract aanwezig' heeft een ongeldig format. Het veld accepteert alleen boolean waarden (0/1, ja/nee, true/false).

---

## **KOLOM 103: Contractnummer Provider**

### ⚠️ **AANPASSINGEN:**
- **Code 701**: Het 'Contractnummer Provider' is te kort. Minimaal 5 karakters vereist.

---

## **KOLOM 104: Zoeksleutels**

### ⚠️ **AANPASSINGEN:**
- **Code 702**: De 'Zoeksleutels' zijn te lang. De waarde zou hierdoor in een later stadium ingekort kunnen worden.

---

## **CROSS-FIELD VALIDATIES (Kolommen 81-104)**

### 🏴 **FLAGS:**
- **Code 751**: Dependency validaties - UOM codes zonder bijbehorende numerieke waarden
- **Code 780**: Datum logica - einddata die vóór startdata liggen
- **Code 781**: Verouderde data - einddata in het verleden
- **Code 802**: Conflicterende unit types - Consumer en Dispatch beide 1

---

## **VALIDATIE CODE REFERENTIE (Specifiek voor Kolommen 81-104)**

### ⚠️ **AANPASSINGEN (700-709)**
- **701**: Te kort (contractnummer)
- **702**: Te lang (zoeksleutels)
- **703**: Ongeldig datumformat (alle datum velden)
- **704**: Niet numeriek (gewicht, levertijd)
- **705**: Ongeldig boolean format (alle boolean velden)
- **707**: Waarde niet in referentielijst (UOM codes, locatie codes, etc.)

### 🏴 **FLAGS (750-809)**
- **751**: Dependency validatie - gekoppelde velden ontbreken
- **780**: Datum logica fout - eind vóór start
- **781**: Verouderde data - datum in verleden
- **802**: Conflicterende unit combinatie

---

## **MEDICAL DEVICE SPECIFIEKE VALIDATIES**

### **Implanteerbaar Product Context:**
- **Serienummer**: Verplicht voor implantaten
- **Batch Nummer**: Verplicht voor medische apparaten
- **Steriel**: Vaak verplicht voor implantaten
- **MRI Compatibility**: Belangrijk voor implantaten
- **Latex**: Belangrijk voor allergenen

### **Contract en Beschikbaarheid:**
- **Contract aanwezig**: Voor gereguleerde producten
- **Contractnummer**: Tracering van agreements
- **Beschikbaarheid datums**: Planning en voorraad
- **Prijs datums**: Commerciële planning

---

## **NIET GEÏMPLEMENTEERDE VELDEN**

### **Type Sterilisatie Gebruikt door Fabrikant (kolom 91):**
**Verwachte implementatie:**
- **Code 707**: Referentielijst validatie - "De ingevulde waarde komt niet voor in de referentielijst 'Sterilization Types'"
- **Code 751**: Dependency validatie - "Het veld 'Type Sterilisatie' is niet ingevuld, terwijl is aangegeven dat het product 'Steriel' is"

---

## **PRIORITERING VOOR TESTEN**

### **Hoge Prioriteit:**
✅ Boolean format validaties (veel velden)  
✅ Medical device context validaties  
✅ Datum logica validaties  

### **Gemiddelde Prioriteit:**
✅ Referentielijst validaties  
✅ Dependency checks  

### **Lage Prioriteit:**
✅ Optionele velden (Zoeksleutels, Contract details)  
❌ Niet geïmplementeerde validaties (1 veld)  

---

*Document aangemaakt: 2025-10-06*  
*Totaal beschikbare validaties: 15 codes verdeeld over 23 geïmplementeerde velden*  
*Ontbrekende validaties: 2 codes voor 1 veld (Type Sterilisatie)*