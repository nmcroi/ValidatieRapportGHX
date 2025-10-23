# 📊 VALIDATIEMATRIX vs IMPLEMENTATIE CROSS-REFERENCE

## 🎯 Overzicht
Cross-reference tussen de GHX Prijstemplate Validatiematrix v10TG.xlsx en onze field_validation_v20.json implementatie.

**Legenda:**
- ✅ **Geïmplementeerd** - Validatie bestaat in beide systemen
- ❌ **Missing** - Validatie staat in matrix maar niet in implementatie  
- ⚠️ **Discrepancy** - Validatie bestaat maar met verschillen
- 🆕 **Extra** - Validatie in implementatie maar niet in matrix

---

## 📋 VELD-VOOR-VELD ANALYSE

### 1. **Artikelnummer** (Kolom 1)
**Matrix Validaties:**
- 🔴 **Afkeuring:** "Artikelnummer is niet ingevuld terwijl dit een verplicht veld is"
- 🏴 **Flag:** "Artikelnummer komt meerdere malen voor in uw lijst"

**Implementatie Status:**
- ✅ **Code 700:** Verplichte velden check 
- ✅ **Code 703:** Duplicate check voor unieke velden
- ❌ **Missing:** Specifieke "artikelnummer leeg" check

---

### 2. **Artikelnaam** (Kolom 2)  
**Matrix Validaties:**
- 🔴 **Afkeuring:** "Artikelnaam is niet ingevuld terwijl dit een verplicht veld is"
- 🔧 **Aanpassing:** "Artikelnaam is te lang en is ingekort tot 90 karakters"

**Implementatie Status:**
- ✅ **Code 700:** Verplichte velden check
- ✅ **Code 702:** Te lange waarde check
- ⚠️ **Discrepancy:** Specifieke 90 karakter limiet onduidelijk

---

### 3. **Artikelomschrijving** (Kolom 3)
**Matrix Validaties:**
- 🔧 **Aanpassing:** "Artikelomschrijving is te lang en is ingekort tot 2000 karakters"

**Implementatie Status:**
- ✅ **Code 702:** Te lange waarde check
- ⚠️ **Discrepancy:** Specifieke 2000 karakter limiet onduidelijk

---

### 4. **Artikelomschrijving Taal Code** (Kolom 4)
**Matrix Validaties:**
- 🔧 **Aanpassing:** "Code is leeg of komt niet voor in de Referentielijst"

**Implementatie Status:**
- ✅ **Code 707:** Referentielijst validatie
- ✅ **Code 700:** Lege velden check

---

### 5. **Brutoprijs** (Kolom 5)
**Matrix Validaties:**
- 🔴 **Afkeuring:** "Brutoprijs kolom is niet gevonden"
- 🔧 **Aanpassing:** "Valutatekens en duizendtallenscheidingstekens ingekort"
- 🏴 **Flag:** "Brutoprijs is lager dan Nettoprijs"

**Implementatie Status:**
- ✅ **Code 710:** Brutoprijs max digits overschrijding
- ✅ **Code 705:** Verkeerde symbolen/tekens
- ✅ **Code 752:** FLAG - Brutoprijs lager dan Nettoprijs
- ❌ **Missing:** Kolom niet gevonden check

---

### 6. **Nettoprijs** (Kolom 6)
**Matrix Validaties:**
- 🔴 **Afkeuring:** "Nettoprijs kolom is niet gevonden" 
- 🔧 **Aanpassing:** "Valutatekens en duizendtallenscheidingstekens ingekort"
- 🏴 **Flag:** "Meer dan 25% van de velden heeft waarde '0'"

**Implementatie Status:**
- ✅ **Code 711:** Nettoprijs-veld ontbreekt
- ✅ **Code 712:** Nettoprijs max digits overschrijding
- ✅ **Code 705:** Verkeerde symbolen/tekens
- ❌ **Missing:** "25% velden heeft waarde 0" check

---

### 7. **Is BestelbareEenheid** (Kolom 7)
**Matrix Validaties:**
- 🔴 **Afkeuring:** "Is BestelbareEenheid is niet ingevuld"
- 🔧 **Aanpassing:** "BestelbareEenheid moet 0 of 1 zijn"

**Implementatie Status:**
- ✅ **Code 713:** Is BestelbareEenheid-veld ontbreekt
- ✅ **Code 714:** Is BestelbareEenheid-veld ongeldige waarde

---

### 8. **Is BasisEenheid** (Kolom 8) 
**Matrix Validaties:**
- 🔴 **Afkeuring:** "Is BasisEenheid is niet ingevuld"
- 🔧 **Aanpassing:** "BasisEenheid moet 0 of 1 zijn"

**Implementatie Status:**
- ✅ **Code 715:** Is BasisEenheid-veld ontbreekt  
- ✅ **Code 716:** Is BasisEenheid-veld ongeldige waarde

---

### 9. **Omschrijving Verpakkingseenheid** (Kolom 9)
**Matrix Validaties:**
- 🔴 **Afkeuring:** "Omschrijving Verpakkingseenheid is niet ingevuld"
- 🔧 **Aanpassing:** "Is te lang en is ingekort tot 25 karakters"
- 🏴 **Flag:** "Komt mogelijk niet overeen met de specificaties"

**Implementatie Status:**
- ✅ **Code 717:** Omschrijving Verpakkingseenheid-veld ontbreekt
- ✅ **Code 718:** Omschrijving Verpakkingseenheid te lang
- ✅ **Code 753:** FLAG - Komt niet overeen met UOM-velden

---

### 10-14. **UOM en Inhoud Velden** (Kolommen 10-14)
**Matrix Validaties:**
- 🔴 **Afkeuring:** "Veld is verplicht, maar niet ingevuld" (voor alle 5 velden)

**Implementatie Status:**
- ✅ **Code 700:** Verplichte velden check
- ✅ **Code 724:** UOM-relatie fouten
- ✅ **Code 801:** GLOBAL FLAG - UOM codes moeten gelijk zijn
- ✅ **Code 805:** GLOBAL FLAG - Inhoud velden moeten gelijk zijn

---

### 15. **Omrekenfactor** (Kolom 15)
**Matrix Validaties:**
- 🔴 **Afkeuring:** "Omrekenfactor is leeg" + "niet numeriek"
- 🔧 **Aanpassing:** "Waarde is berekend op basis van andere velden"
- 🏴 **Flag:** "Ingevulde waarde komt niet overeen met berekende waarde"

**Implementatie Status:**
- ✅ **Code 704:** Waarde is niet numeriek
- ✅ **Code 754:** CORRECTION - Omrekenfactor automatisch berekend
- ✅ **Code 720:** Ingevulde ≠ berekende waarde (mismatch)

---

### 16. **Prijs per Kleinste eenheid** (Kolom 16)
**Matrix Validaties:**
- 🔧 **Aanpassing:** "Waarde is ongeldig, is berekend op basis van andere velden"
- 🏴 **Flag:** "Ingevulde waarde komt niet overeen met berekende waarde"

**Implementatie Status:**
- ✅ **Code 755:** CORRECTION - Prijs per Kleinste eenheid automatisch berekend
- ✅ **Code 720:** Ingevulde ≠ berekende waarde (mismatch)

---

### 19. **GTIN Verpakkingseenheid** (Kolom 19)
**Matrix Validaties:**
- 🔴 **Afkeuring:** "GTIN heeft ongeldig format (13 of 14 digits)"
- 🏴 **Flag:** "GTIN komt meerdere malen voor in lijst"

**Implementatie Status:**
- ✅ **Code 706:** Waarde heeft niet correcte, exacte lengte
- ✅ **Code 703:** Duplicaat check voor unieke velden
- ✅ **Code 722:** Ongeldig format (datum, URL, GTIN, CAS)

---

### 25. **GHX BTW Code** (Kolom 25)  
**Matrix Validaties:**
- 🔴 **Afkeuring:** "Veld is verplicht, maar niet ingevuld"
- 🔧 **Aanpassing:** "Ingevulde waarde is ongeldig"

**Implementatie Status:**
- ✅ **Code 700:** Verplichte velden check
- ✅ **Code 707:** Waarde komt niet voor in referentielijst
- ✅ **Code 757:** CORRECTION - BTW-percentage omgezet naar juiste code

---

## 🔍 AANVULLENDE IMPLEMENTATIE CODES

### Codes die NIET direct in matrix staan:
- **Code 708-709:** CE Certificaat validaties
- **Code 719:** Boolean-veld validatie  
- **Code 721:** Alfanumeriek validatie
- **Code 723:** Datum logica validatie
- **Code 750-773:** Diverse FLAG codes voor medische producten
- **Code 774-775:** URL validaties (recent toegevoegd)
- **Code 800-805:** GLOBAL FLAGS

---

## 📈 SAMENVATTING

### ✅ **Goed Geïmplementeerd (Voorbeelden):**
- Basis validaties (verplicht, te lang, niet numeriek)
- UOM en Inhoud validatie logica 
- GTIN format en duplicate checks
- Brutoprijs/Nettoprijs logica
- Boolean field validaties (0/1)

### ❌ **Missing/Incomplete:**
- Specifieke karakterlimiet enforcement (90, 2000, 25 chars)
- "Kolom niet gevonden" validaties
- "25% velden heeft waarde 0" check
- Specifieke matrix teksten in error messages

### 🆕 **Extra Features:**
- Uitgebreide medische product validaties (750-773)
- URL validaties (774-775) 
- Global template validaties (800-805)
- CE Certificaat validaties

### 🎯 **Actie Items:**
1. **Test alle codes 700-720** tegen matrix verwachtingen
2. **Implementeer missing specific checks** 
3. **Verify character limits** enforcement
4. **Add missing error messages** voor matrix compatibiliteit
5. **Test medical product validations** (750-773)

---

*Laatste update: 2025-10-05*