# 📊 Alle Matrix Validaties Per Kolom

*Complete extractie van validaties uit GHX Prijstemplate Validatiematrix v10TG.xlsx*

---

## 📍 KOLOM 1: Artikelnummer
**🔴 AFKEURINGEN:**
- Artikelnummer is niet ingevuld terwijl dit een verplicht veld is. De regel is daarom afgekeurd.
- Artikelnummer is te lang. De regel is daarom afgekeurd.
- Artikelnummer is te kort. De regel is daarom afgekeurd.

**🏴 FLAGS:**
- Artikelnummer komt meerdere malen voor in uw lijst. Dit is toegestaan, maar controleer of dit correct is en of de bijbehorende verpakkingseenheden verschillen.

---

## 📍 KOLOM 2: Artikelnaam
**🔴 AFKEURINGEN:**
- Artikelnaam is niet ingevuld terwijl dit een verplicht veld is. De regel is daarom afgekeurd.
- Artikelnaam is te kort. De regel is daarom afgekeurd.

**🔧 AANPASSINGEN:**
- Artikelnaam is te lang en is ingekort tot 90 karakters.

---

## 📍 KOLOM 3: Artikelomschrijving
**🔧 AANPASSINGEN:**
- Artikelomschrijving is te lang en is ingekort tot 2000 karakters.

---

## 📍 KOLOM 4: Artikelomschrijving Taal Code
**🔧 AANPASSINGEN:**
- Artikelomschrijving Taal Code is leeg of komt niet voor in de Referentielijst 'Language Code'. Het veld is daarom leeg gelaten, terwijl deze verplicht is voor GS1.

---

## 📍 KOLOM 5: Brutoprijs
**🔴 AFKEURINGEN:**
- Brutoprijs kolom is niet gevonden. De regel is daarom afgekeurd.
- Brutoprijs is niet gevuld. De regel is daarom afgekeurd.
- Brutoprijs is niet numeriek. De regel is daarom afgekeurd.

**🔧 AANPASSINGEN:**
- In het veld Brutoprijs stonden valutatekens en duizendtallenscheidingstekens in het veld, die hebben wij verwijderd.

**🏴 FLAGS:**
- Brutoprijs is een lagere waarde dan de Nettoprijs. Dat is niet mogelijk.

---

## 📍 KOLOM 6: Nettoprijs
**🔴 AFKEURINGEN:**
- Nettoprijs kolom is niet gevonden. De regel is daarom afgekeurd.
- Nettoprijs is niet gevuld. De regel is daarom afgekeurd.
- Nettoprijs is niet numeriek. De regel is daarom afgekeurd.

**🔧 AANPASSINGEN:**
- In het veld Nettoprijs stonden valutatekens en duizendtallenscheidingstekens in het veld, die hebben wij verwijderd.

**🏴 FLAGS:**
- Meer dan 25% van de velden heeft de waarde '0'.

---

## 📍 KOLOM 7: Is BestelbareEenheid
**🔴 AFKEURINGEN:**
- Is BestelbareEenheid is niet ingevuld. De regel is daarom afgekeurd.
- De ingevulde waarde voor 'Is BestelbareEenheid' is ongeldig. Het veld accepteert alleen '1' (JA) of '0' (NEE). De regel is daarom afgekeurd.

**🔧 AANPASSINGEN:**
- BestelbareEenheid moet 0 of 1 zijn. We hebben de velden aangepast.

---

## 📍 KOLOM 8: Is BasisEenheid  
**🔴 AFKEURINGEN:**
- Is BasisEenheid is niet ingevuld. De regel is daarom afgekeurd.
- De ingevulde waarde voor 'Is BasisEenheid' is ongeldig. Het veld accepteert alleen '1' (JA) of '0' (NEE). De regel is daarom afgekeurd.

**🔧 AANPASSINGEN:**
- BasisEenheid moet 0 of 1 zijn. We hebben de velden aangepast.

---

## 📍 KOLOM 9: Omschrijving Verpakkingseenheid
**🔴 AFKEURINGEN:**
- Omschrijving Verpakkingseenheid is niet ingevuld. De regel is daarom afgekeurd.

**🔧 AANPASSINGEN:**
- Omschrijving Verpakkingseenheid is te lang en is ingekort tot 25 karakters.

**🏴 FLAGS:**
- De 'Omschrijving Verpakkingseenheid' komt mogelijk niet overeen met de specificaties in de UOM-velden die erop volgen. Controleer of de omschrijving en de UOM-codes en -inhoud met elkaar corresponderen.

---

## 📍 KOLOM 10: UOM Code Verpakkingseenheid
**🔴 AFKEURINGEN:**
- Het veld 'UOM Code Verpakkingseenheid' is verplicht, maar niet ingevuld. De regel is daarom afgekeurd.
- De ingevulde waarde voor 'UOM Code Verpakkingseenheid' komt niet voor in de referentielijst 'UOM Codes'. Het veld is daarom leeg gelaten.

---

## 📍 KOLOM 11: Inhoud Verpakkingseenheid
**🔴 AFKEURINGEN:**
- Het veld 'Inhoud Verpakkingseenheid' is verplicht, maar niet ingevuld. De regel is daarom afgekeurd.
- De waarde voor 'Inhoud Verpakkingseenheid' heeft een ongeldig format. Het veld accepteert alleen een numerieke waarde. De regel is daarom afgekeurd.

---

## 📍 KOLOM 12: UOM Code Basiseenheid
**🔴 AFKEURINGEN:**
- Het veld 'UOM Code Basiseenheid' is verplicht, maar niet ingevuld. De regel is daarom afgekeurd.
- De ingevulde waarde voor 'UOM Code Basiseenheid' komt niet voor in de referentielijst 'UOM Codes'. Het veld is daarom leeg gelaten.

---

## 📍 KOLOM 13: Inhoud Basiseenheid
**🔴 AFKEURINGEN:**
- Het veld 'Inhoud Basiseenheid' is verplicht, maar niet ingevuld. De regel is daarom afgekeurd.
- De waarde voor 'Inhoud Basiseenheid' heeft een ongeldig format. Het veld accepteert alleen een numerieke waarde. De regel is daarom afgekeurd.

---

## 📍 KOLOM 14: UOM Code Inhoud Basiseenheid
**🔴 AFKEURINGEN:**
- Het veld 'UOM Code Inhoud Basiseenheid' is verplicht, maar niet ingevuld. De regel is daarom afgekeurd.
- De ingevulde waarde voor 'UOM Code Inhoud Basiseenheid' komt niet voor in de referentielijst 'UOM Codes'. Het veld is daarom leeg gelaten.

---

## 📍 KOLOM 15: Omrekenfactor
**🔴 AFKEURINGEN:**
- Omrekenfactor is leeg.
- Omrekenfactor is niet numeriek.

**🔧 AANPASSINGEN:**
- De 'Omrekenfactor' is niet ingevuld. De waarde is voor u berekend op basis van 'Inhoud Verpakkingseenheid' en 'Inhoud Basiseenheid'.
- De 'Omrekenfactor' is ongeldig. De waarde is voor u berekend op basis van 'Inhoud Verpakkingseenheid' en 'Inhoud Basiseenheid'.

**🏴 FLAGS:**
- De door u ingevulde 'Omrekenfactor' komt niet overeen met de berekende waarde (Inhoud Verpakkingseenheid x Inhoud Basiseenheid). Controleer of deze waarden correct zijn.

---

## 📍 KOLOM 16: Prijs per Kleinste eenheid
**🔧 AANPASSINGEN:**
- De 'Prijs per Kleinste eenheid' is ongeldig. De waarde is voor u berekend op basis van de 'Nettoprijs' en de 'Omrekenfactor'.
- De 'Prijs per Kleinste eenheid' is niet ingevuld. De waarde is voor u berekend op basis van de 'Nettoprijs' en de 'Omrekenfactor'.

**🏴 FLAGS:**
- De door u ingevulde 'Prijs per Kleinste eenheid' komt niet overeen met de berekende waarde (Nettoprijs / Omrekenfactor). Controleer of deze waarden correct zijn.

---

## 📍 KOLOM 17: Aantal van de Volgende Lagere Verpakkingslaag
**🔧 AANPASSINGEN:**
- De waarde voor 'Aantal van de Volgende Lagere Verpakkingslaag' is ongeldig. Het veld accepteert alleen een numerieke waarde en is daarom leeg gelaten.

---

## 📍 KOLOM 18: Artikel Hiërarchie Omschrijving
**🔧 AANPASSINGEN:**
- De ingevulde waarde voor 'Artikel Hiërarchie Omschrijving' komt niet voor in de referentielijst 'DescriptorCode'. Het veld is daarom leeg gelaten.

---

## 📍 KOLOM 19: GTIN Verpakkingseenheid
**🔴 AFKEURINGEN:**
- De 'GTIN Verpakkingseenheid' heeft een ongeldig format. Een GTIN bestaat uit 13 of 14 cijfers. De regel is daarom afgekeurd.
- Een GTIN is verplicht voor medische hulpmiddelen met een risicoklasse, maar het veld 'GTIN Verpakkingseenheid' is niet ingevuld.

**🏴 FLAGS:**
- De 'GTIN Verpakkingseenheid' komt meerdere malen voor in deze lijst. Hoewel dit soms correct kan zijn, is een GTIN doorgaans uniek per productregel. Controleer of dit de bedoeling is.
- Er is geen GTIN ingevuld en geen 'Aanvullende Productidentificatie'. Het invullen van 1 van deze velden is verplicht bij alle medische producten.
- GTIN is verplicht bij ingevulde risicoklasse.
- Een GTIN is verplicht voor medische hulpmiddelen met een risicoklasse, maar het veld 'GTIN Verpakkingseenheid' is niet ingevuld.

---

## 📍 KOLOM 20: GTIN Verpakkingseenheid Historie
**🔧 AANPASSINGEN:**
- Het veld 'GTIN Verpakkingseenheid Historie' is te lang en is ingekort tot 200 karakters.

---

*Geëxtraheerd: 2025-10-05*  
*Status: Eerste 20 kolommen compleet*