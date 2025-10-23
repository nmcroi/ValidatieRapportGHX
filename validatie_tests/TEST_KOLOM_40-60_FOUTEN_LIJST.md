# Test Kolom 40-60 Validaties - Fouten Lijst

## Overzicht Alle Mogelijke Validatie Fouten

Dit document bevat alle validatie fouten die kunnen optreden voor kolommen 40-60.

---

## **KOLOM 40: Artikelnummer Alternatief Artikel**

### ⚠️ **AANPASSINGEN:**
- **Code 701**: Artikelnummer Alternatief Artikel is te kort, minimaal 3 karakters vereist
- **Code 702**: Artikelnummer Alternatief Artikel is te lang, wordt ingekort tot 46 karakters

---

## **KOLOM 41: Artikelnaam Alternatief Artikel**

### 🏴 **FLAGS:**
- **Code 761**: Het veld 'Artikelnaam Alternatief Artikel' is niet ingevuld, terwijl u wel een 'Artikelnummer Alternatief Artikel' heeft opgegeven. Deze combinatie is verplicht.

---

## **KOLOM 42: Barcode Alternatief Artikel**

### 🏴 **FLAGS:**
- **Code 762**: Het veld 'Barcode Alternatief Artikel' is niet ingevuld. Het wordt aanbevolen dit veld in te vullen als er een alternatief artikel is opgegeven.

---

## **KOLOM 43: UNSPSC**

### 🔴 **AFKEURINGEN:**
- **Code 700**: De 'UNSPSC' is niet ingevuld. De regel zou hierdoor in een later stadium afgekeurd kunnen worden.

### ⚠️ **AANPASSINGEN:**
- **Code 706**: De 'UNSPSC' heeft een ongeldig format. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 763**: Het veld 'UNSPSC' is niet ingevuld. Voor aanlevering aan bepaalde ziekenhuizen is dit een verplicht veld.

---

## **KOLOM 44: GMDN Code**

### ⚠️ **AANPASSINGEN:**
- **Code 704**: De 'GMDN Code' is niet numeriek. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.
- **Code 701**: De 'GMDN Code' is te kort. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 753**: Er is geen 'GMDN Code' of 'EMDN Code' ingevuld. Voor medische hulpmiddelen is het invullen van één van deze codes verplicht.

---

## **KOLOM 45: EMDN Code**

### ⚠️ **AANPASSINGEN:**
- **Code 701**: De 'EMDN Code' is te kort. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.
- **Code 702**: De 'EMDN Code' is te lang. De waarde zou hierdoor in een later stadium ingekort kunnen worden.

### 🏴 **FLAGS:**
- **Code 754**: Het veld 'EMDN Code' is niet ingevuld, terwijl u wel een 'GMDN Code' heeft opgegeven. Voor een complete classificatie is beide codes aanbevolen.

---

## **KOLOM 46: GPCCategoryCode**

### ⚠️ **AANPASSINGEN:**
- **Code 706**: De 'GPCCategoryCode' heeft een ongeldig format. Het moet uit exact 8 cijfers bestaan.
- **Code 704**: De 'GPCCategoryCode' is niet numeriek. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

---

## **KOLOM 47: Code voor Aanvullende Productclassificatie**

### ⚠️ **AANPASSINGEN:**
- **Code 707**: De ingevulde waarde voor 'Code voor Aanvullende Productclassificatie' komt niet voor in de referentielijst. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 755**: Het veld 'Code voor Aanvullende Productclassificatie' is niet ingevuld, terwijl u wel een 'Aanvullende Productclassificatiewaarde' heeft opgegeven. Deze combinatie is verplicht.

---

## **KOLOM 48: Aanvullende Productclassificatiewaarde (Risicoklasse)**

### ⚠️ **AANPASSINGEN:**
- **Code 707**: De ingevulde waarde voor 'Aanvullende Productclassificatiewaarde' komt niet voor in de referentielijst. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 754**: Het veld 'Aanvullende Productclassificatiewaarde' is niet ingevuld, terwijl u wel een 'Code voor Aanvullende Productclassificatie' heeft opgegeven. Deze combinatie is verplicht.
- **Code 748**: De combinatie van AU-code en risicoklasse is ongeldig volgens de EU MDR/IVDR regelgeving.

---

## **KOLOM 49: CE Certificaat nummer**

### ⚠️ **AANPASSINGEN:**
- **Code 701**: Het 'CE Certificaat nummer' is te kort. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.
- **Code 702**: Het 'CE Certificaat nummer' is te lang. De waarde zou hierdoor in een later stadium ingekort kunnen worden.

---

## **KOLOM 50: CE Certificaat einddatum**

### ⚠️ **AANPASSINGEN:**
- **Code 703**: De 'CE Certificaat einddatum' heeft een ongeldig datumformat. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 756**: Het veld 'CE Certificaat einddatum' is niet ingevuld, terwijl u wel een 'CE Certificaat nummer' heeft opgegeven. Deze combinatie is verplicht.
- **Code 747**: De 'CE Certificaat einddatum' ligt in het verleden. Controleer of het certificaat nog geldig is.

---

## **KOLOM 51: CE Certificerende instantie**

### ⚠️ **AANPASSINGEN:**
- **Code 701**: De 'CE Certificerende instantie' is te kort. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 757**: Het veld 'CE Certificerende instantie' is niet ingevuld, terwijl u wel een 'CE Certificaat nummer' heeft opgegeven. Deze combinatie is verplicht.

---

## **KOLOM 52: Duurzaam Geproduceerd**

### ⚠️ **AANPASSINGEN:**
- **Code 705**: De waarde voor 'Duurzaam Geproduceerd' heeft een ongeldig format. Het veld accepteert alleen boolean waarden (0/1, ja/nee, true/false).

---

## **KOLOM 53: Naam Duurzaam Assortiment**

### ⚠️ **AANPASSINGEN:**
- **Code 702**: De 'Naam Duurzaam Assortiment' is te lang. De waarde zou hierdoor in een later stadium ingekort kunnen worden.

---

## **KOLOM 54: Naam Duurzaamheidslabel**

### ⚠️ **AANPASSINGEN:**
- **Code 702**: De 'Naam Duurzaamheidslabel' is te lang. De waarde zou hierdoor in een later stadium ingekort kunnen worden.

---

## **KOLOM 55: Omschrijving Duurzaamheid**

### ⚠️ **AANPASSINGEN:**
- **Code 702**: De 'Omschrijving Duurzaamheid' is te lang. De waarde zou hierdoor in een later stadium ingekort kunnen worden.

---

## **KOLOM 56: CAS nummer**

### ⚠️ **AANPASSINGEN:**
- **Code 708**: Het 'CAS nummer' heeft een ongeldig format. Een geldig CAS nummer heeft het format: xxxxxx-xx-x.
- **Code 701**: Het 'CAS nummer' is te kort. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

---

## **KOLOM 57: Stofnaam**

### ⚠️ **AANPASSINGEN:**
- **Code 701**: De 'Stofnaam' is te kort. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 758**: Het veld 'Stofnaam' is niet ingevuld, terwijl u wel een 'CAS nummer' heeft opgegeven. Voor chemische stoffen is deze combinatie verplicht.

---

## **KOLOM 58: Brutoformule**

### ⚠️ **AANPASSINGEN:**
- **Code 701**: De 'Brutoformule' is te kort. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 759**: Het veld 'Brutoformule' is niet ingevuld, terwijl u wel een 'CAS nummer' heeft opgegeven. Voor chemische stoffen is deze combinatie verplicht.

---

## **KOLOM 59: Claim Type Code**

### ⚠️ **AANPASSINGEN:**
- **Code 707**: De ingevulde waarde voor 'Claim Type Code' komt niet voor in de referentielijst. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 761**: Het veld 'Claim Type Code' is niet ingevuld, terwijl u wel een 'Element Claim Code' heeft opgegeven. Deze combinatie is verplicht.

---

## **KOLOM 60: Element Claim Code**

### ⚠️ **AANPASSINGEN:**
- **Code 707**: De ingevulde waarde voor 'Element Claim Code' komt niet voor in de referentielijst. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 760**: Het veld 'Element Claim Code' is niet ingevuld, terwijl u wel een 'Claim Type Code' heeft opgegeven. Deze combinatie is verplicht.

---

## **CROSS-FIELD VALIDATIES (Kolommen 40-60)**

### 🏴 **FLAGS:**
- **Code 753**: Er is geen 'GMDN Code' of 'EMDN Code' ingevuld. Voor medische hulpmiddelen is het invullen van één van deze codes verplicht.
- **Code 748**: De combinatie van AU-code (kolom 47) en risicoklasse (kolom 48) is ongeldig volgens de EU MDR/IVDR regelgeving.
- **Code 747**: De 'CE Certificaat einddatum' ligt in het verleden. Controleer of het certificaat nog geldig is.

---

## **VALIDATIE CODE REFERENTIE**

### 🔴 **AFKEURINGEN (700-799)**
- **700**: Verplicht veld niet ingevuld
- **701**: Waarde te kort
- **702**: Waarde te lang
- **703**: Ongeldig datumformat
- **704**: Niet numeriek
- **705**: Ongeldig boolean format
- **706**: Ongeldig exact length format
- **707**: Waarde niet in referentielijst
- **708**: Ongeldig CAS format

### 🏴 **FLAGS (750-799)**
- **747**: Datum ligt in verleden
- **748**: Ongeldige AU-code/risicoklasse combinatie
- **753**: Geen GMDN of EMDN code ingevuld
- **754**: Dependency veld leeg terwijl parent gevuld
- **755**: Parent veld leeg terwijl dependency gevuld
- **756**: CE einddatum leeg terwijl nummer gevuld
- **757**: CE instantie leeg terwijl nummer gevuld
- **758**: Stofnaam leeg terwijl CAS nummer gevuld
- **759**: Brutoformule leeg terwijl CAS nummer gevuld
- **760**: Element claim leeg terwijl claim type gevuld
- **761**: Claim type leeg terwijl element claim gevuld
- **762**: Barcode alternatief leeg terwijl artikelnummer gevuld
- **763**: UNSPSC leeg voor specifieke ziekenhuizen

---

*Document aangemaakt: 2025-10-06*  
*Totaal validaties: 42 verdeeld over 21 velden (kolommen 40-60)*