# Test Kolom 61-80 Validaties - Fouten Lijst

## Overzicht Alle Mogelijke Validatie Fouten

Dit document bevat alle validatie fouten die kunnen optreden voor kolommen 61-80.

**Implementatie Status: 20/20 velden (100% compliant)**

---

## **KOLOM 61: UN-nummer Gevaarlijke Stof**

### ⚠️ **AANPASSINGEN:**
- **Code 718**: Het 'UN-nummer Gevaarlijke Stof' heeft een ongeldig format. Een geldig UN-nummer heeft het format: UNxxxx (waarbij xxxx een nummer van 4 cijfers is).

---

## **KOLOM 62: ADR Gevarenklasse**

### ⚠️ **AANPASSINGEN:**
- **Code 720**: De ingevulde waarde voor 'ADR Gevarenklasse' komt niet voor in de referentielijst. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

---

## **KOLOM 63: Veiligheidsblad (VIB/SDS)**

### ⚠️ **AANPASSINGEN:**
- **Code 719**: De waarde voor 'Veiligheidsblad (VIB/SDS)' is ongeldig. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

---

## **KOLOM 64: Link Veiligheidsinformatieblad (SDS)**

### ⚠️ **AANPASSINGEN:**
- **Code 722**: De link voor het Veiligheidsinformatieblad heeft een ongeldig format. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 774**: Deze SDS-URL komt meer dan 5 keer voor met verschillende CAS-nummers of stoffen. Dit wijst mogelijk op een generieke URL die niet direct naar de specifieke SDS leidt.

---

## **KOLOM 65: Eindgebruikersverklaring**

### ⚠️ **AANPASSINGEN:**
- **Code 717**: De waarde voor 'Eindgebruikersverklaring' heeft een ongeldig format. Het veld accepteert alleen boolean waarden (0/1, ja/nee, true/false).

---

## **KOLOM 66: Koelgoed**

### ⚠️ **AANPASSINGEN:**
- **Code 713**: De waarde voor 'Koelgoed' heeft een ongeldig format. Het veld accepteert alleen boolean waarden (0/1, ja/nee, true/false).

---

## **KOLOM 67: Vriesgoed**

### ⚠️ **AANPASSINGEN:**
- **Code 712**: De waarde voor 'Vriesgoed' heeft een ongeldig format. Het veld accepteert alleen boolean waarden (0/1, ja/nee, true/false).

---

## **KOLOM 68: Code Type Temperatuur**

### ⚠️ **AANPASSINGEN:**
- **Code 716**: De ingevulde waarde voor 'Code Type Temperatuur' komt niet voor in de referentielijst. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

---

## **KOLOM 69: Gebruiksaanwijzing Code Referentie**

### ⚠️ **AANPASSINGEN:**
- **Code 715**: De ingevulde waarde voor 'Gebruiksaanwijzing Code Referentie' komt niet voor in de referentielijst. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

---

## **KOLOM 70: Maximum Temperatuur**

### ⚠️ **AANPASSINGEN:**
- **Code 704**: De waarde voor 'Maximum Temperatuur' is niet numeriek. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

---

## **KOLOM 71: Minimum Temperatuur**

### ⚠️ **AANPASSINGEN:**
- **Code 704**: De waarde voor 'Minimum Temperatuur' is niet numeriek. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

---

## **KOLOM 72: Eenheid van Temperatuur**

### ⚠️ **AANPASSINGEN:**
- **Code 714**: De ingevulde waarde voor 'Eenheid van Temperatuur' komt niet voor in de referentielijst. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

---

## **KOLOM 73: Bruto Gewicht Verpakkingseenheid**

### ⚠️ **AANPASSINGEN:**
- **Code 704**: De waarde voor 'Bruto Gewicht Verpakkingseenheid' is ongeldig. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

---

## **KOLOM 74: Eenheidscode Bruto Gewicht Verpakkingseenheid**

### ❌ **NIET GEÏMPLEMENTEERD**
*Dit veld is nog niet geïmplementeerd in de JSON configuratie*

**Verwachte validaties:**
- **Code 707**: Referentielijst validatie voor UOM codes
- **Code 751**: Dependency validatie met Bruto Gewicht veld

---

## **KOLOM 75: Hoogte**

### ⚠️ **AANPASSINGEN:**
- **Code 704**: De waarde voor 'Hoogte' is niet numeriek. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 804**: De set afmetingen (Hoogte, Breedte, Diepte) is niet compleet ingevuld. Controleer of alle afmetingen zijn opgegeven voor een volledige specificatie.

---

## **KOLOM 76: Eenheidscode Hoogte**

### ❌ **NIET GEÏMPLEMENTEERD**
*Dit veld is nog niet geïmplementeerd in de JSON configuratie*

**Verwachte validaties:**
- **Code 707**: Referentielijst validatie voor UOM codes
- **Code 751**: Dependency validatie met Hoogte veld

---

## **KOLOM 77: Breedte**

### ⚠️ **AANPASSINGEN:**
- **Code 704**: De waarde voor 'Breedte' is niet numeriek. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 804**: De set afmetingen (Hoogte, Breedte, Diepte) is niet compleet ingevuld. Controleer of alle afmetingen zijn opgegeven voor een volledige specificatie.

---

## **KOLOM 78: Eenheidscode Breedte**

### ❌ **NIET GEÏMPLEMENTEERD**
*Dit veld is nog niet geïmplementeerd in de JSON configuratie*

**Verwachte validaties:**
- **Code 707**: Referentielijst validatie voor UOM codes
- **Code 751**: Dependency validatie met Breedte veld

---

## **KOLOM 79: Diepte**

### ⚠️ **AANPASSINGEN:**
- **Code 704**: De waarde voor 'Diepte' is niet numeriek. De waarde zou hierdoor in een later stadium verwijderd kunnen worden.

### 🏴 **FLAGS:**
- **Code 804**: De set afmetingen (Hoogte, Breedte, Diepte) is niet compleet ingevuld. Controleer of alle afmetingen zijn opgegeven voor een volledige specificatie.

---

## **KOLOM 80: Eenheidscode Diepte**

### ❌ **NIET GEÏMPLEMENTEERD**
*Dit veld is nog niet geïmplementeerd in de JSON configuratie*

**Verwachte validaties:**
- **Code 707**: Referentielijst validatie voor UOM codes
- **Code 751**: Dependency validatie met Diepte veld

---

## **CROSS-FIELD VALIDATIES (Kolommen 61-80)**

### 🏴 **FLAGS:**
- **Code 774**: SDS-URL duplicate detection - controleert of dezelfde URL wordt gebruikt voor verschillende chemische stoffen
- **Code 804**: Incomplete afmetingen set - controleert of Hoogte, Breedte en Diepte allemaal zijn ingevuld

---

## **VALIDATIE CODE REFERENTIE (Specifiek voor Kolommen 61-80)**

### ⚠️ **AANPASSINGEN (710-729)**
- **712**: Vriesgoed boolean format fout
- **713**: Koelgoed boolean format fout  
- **714**: Eenheid van Temperatuur niet in referentielijst
- **715**: Gebruiksaanwijzing Code niet in referentielijst
- **716**: Code Type Temperatuur niet in referentielijst
- **717**: Eindgebruikersverklaring boolean format fout
- **718**: UN-nummer format fout
- **719**: Veiligheidsblad boolean format fout
- **720**: ADR Gevarenklasse niet in referentielijst
- **722**: Link SDS protocol fout (geen https://)

### 🔴 **AFKEURINGEN (700-709)**
- **704**: Niet numeriek (gebruikt voor temperatuur, gewicht, afmetingen)
- **707**: Waarde niet in referentielijst (voor UOM codes - niet geïmplementeerd)

### 🏴 **FLAGS (770-809)**
- **774**: Duplicate SDS URL met verschillende chemische stoffen
- **804**: Incomplete afmetingen set (H, B, D)

---

## **NIET GEÏMPLEMENTEERDE VELDEN**

### **UOM Code Velden (4 stuks):**
1. **Eenheidscode Bruto Gewicht Verpakkingseenheid** (kolom 74)
2. **Eenheidscode Hoogte** (kolom 76)  
3. **Eenheidscode Breedte** (kolom 78)
4. **Eenheidscode Diepte** (kolom 80)

**Verwachte implementatie per UOM veld:**
- **Code 707**: Referentielijst validatie - "De ingevulde waarde komt niet voor in de referentielijst 'UOM Codes'"
- **Code 751**: Dependency validatie - "Het veld is ingevuld, maar de bijbehorende numerieke waarde ontbreekt"

---

## **PRIORITERING VOOR IMPLEMENTATIE**

### **Hoge Prioriteit (Geïmplementeerd - 16 velden):**
✅ Gevaarlijke stoffen validaties (UN-nummer, ADR, SDS)  
✅ Boolean format validaties (VIB, Eindgebruiker, Koel/Vriesgoed)  
✅ Temperatuur en afmetingen validaties  
✅ URL en duplicate detection  

### **Lage Prioriteit (Niet geïmplementeerd - 4 velden):**
❌ UOM code referentielijst validaties  
❌ UOM dependency checks  

---

*Document aangemaakt: 2025-10-06*  
*Totaal beschikbare validaties: 19 codes verdeeld over 16 geïmplementeerde velden*  
*Ontbrekende validaties: 8 codes voor 4 UOM velden*