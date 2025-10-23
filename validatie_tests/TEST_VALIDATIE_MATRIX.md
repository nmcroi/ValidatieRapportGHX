# 🧪 SYSTEMATISCHE VALIDATIE TESTMATRIX

## 📋 **Test Overzicht**
Systematische test van alle 40+ validatieregels in de GHX Price Validation Tool.

| Status | Betekenis |
|--------|-----------|
| ✅ | Getest & werkt correct |
| ⚠️ | Getest - issues gevonden |
| 🔄 | Test bezig |
| ❌ | Test gefaald |
| ⏸️ | Nog niet getest |

---

## 🔍 **CORE VALIDATIES (700-749)**

### **Basic Field Validaties**
| Code | Beschrijving | Status | Test Scenario | Resultaat |
|------|-------------|--------|---------------|-----------|
| 700 | Verplichte velden leeg | ⏸️ | Template met lege mandatory fields | - |
| 701 | Waarde te kort | ⏸️ | Field met min_length > actual length | - |
| 702 | Waarde te lang | ⏸️ | Field met max_length < actual length | - |
| 703 | Duplicate waarde (GTIN) | ⏸️ | Dubbele GTIN nummers | - |
| 704 | Waarde niet numeriek | ⏸️ | Letters in numeriek veld | - |
| 705 | Verkeerde symbolen/tekens | ⏸️ | Speciale tekens in restricted field | - |
| 706 | Incorrecte exacte lengte | ⏸️ | Field met exact_length mismatch | - |
| 707 | Waarde niet in referentielijst | ⏸️ | Invalid option uit dropdown | - |

### **Specifieke Business Rules**
| Code | Beschrijving | Status | Test Scenario | Resultaat |
|------|-------------|--------|---------------|-----------|
| 708 | Ongeldige CE Certificaat datum | ⏸️ | Datum in verkeerd format | - |
| 709 | Ongeldige CE instantie | ⏸️ | Niet-erkende certificeerder | - |
| 710 | Brutoprijs max digits | ⏸️ | Prijs > max toegestane waarde | - |
| 711 | Nettoprijs ontbreekt | ⏸️ | Lege nettoprijs bij gevulde brutoprijs | - |
| 712 | Nettoprijs max digits | ⏸️ | Nettoprijs > max toegestane waarde | - |
| 713 | BestelbareEenheid ontbreekt | ⏸️ | UOM logic missing bestelbareEenheid | - |
| 714 | BestelbareEenheid ongeldig | ⏸️ | Invalid UOM code | - |
| 715 | BasisEenheid ontbreekt | ⏸️ | UOM logic missing basisEenheid | - |
| 716 | BasisEenheid ongeldig | ⏸️ | Invalid UOM code | - |
| 717 | Verpakkingseenheid ontbreekt | ⏸️ | Missing description field | - |
| 718 | Verpakkingseenheid te lang | ⏸️ | Description > max length | - |
| 719 | Boolean veld ongeldig | ⏸️ | Niet Ja/Nee waarde | - |
| 720 | Berekende waarde mismatch | ⏸️ | Manual vs calculated value verschillend | - |
| 721 | Niet alfanumeriek | ⏸️ | Special chars in alphanumeric field | - |
| 722 | Ongeldig format | ⏸️ | Malformed URL/datum/CAS | - |
| 723 | Datum logica fout | ⏸️ | Start datum > eind datum | - |
| 724 | UOM-relatie conflicten | ⏸️ | Contradictory UOM combinations | - |

---

## 🚩 **FLAGS & CORRECTIONS (750-799)**

### **Aanbevelingen (750-759)**
| Code | Beschrijving | Status | Test Scenario | Resultaat |
|------|-------------|--------|---------------|-----------|
| 750 | Optioneel veld aanbeveling | ⏸️ | Leeg description veld | - |
| 751 | Conditional mandatory field | ⏸️ | Dependent field logic | - |
| 752 | Brutoprijs < Nettoprijs | ⏸️ | Price logic error | - |
| 753 | UOM description mismatch | ⏸️ | Text vs code inconsistency | - |
| 754 | Auto-calculated omrekenfactor | ⏸️ | Automatic calculation trigger | - |
| 755 | Auto-calculated prijs/kleinste | ⏸️ | Automatic price calculation | - |
| 756 | GTIN missing hoge risicoklasse | ⏸️ | Medical device zonder GTIN | - |
| 757 | BTW percentage conversie | ⏸️ | 9% → correct BTW code | - |
| 758 | Prijsstaffel logica | ⏸️ | End value ≤ start value | - |
| 759 | GLN verplicht voor GS1 | ⏸️ | GS1 context zonder GLN | - |

### **Product-specifieke Flags (760-779)**
| Code | Beschrijving | Status | Test Scenario | Resultaat |
|------|-------------|--------|---------------|-----------|
| 760 | Link IFU aanbeveling | ⏸️ | Medical device zonder IFU link | - |
| 761 | Alt artikel naam missing | ⏸️ | Alt nummer zonder naam | - |
| 762 | Alt artikel barcode aanbeveling | ⏸️ | Alt artikel zonder barcode | - |
| 763 | UNSPSC verplicht specifieke ziekenhuizen | ⏸️ | Hospital context zonder UNSPSC | - |
| 764 | GS1 veld verplicht | ⏸️ | GS1 submission missing field | - |
| 765 | CAS nummer verwacht | ⏸️ | Chemical product zonder CAS | - |
| 766 | CAS aanbeveling bij stofnaam | ⏸️ | Chemical name zonder CAS | - |
| 767 | IFU link bij gebruiksaanwijzing | ⏸️ | Manual reference zonder link | - |
| 768 | Temperatuur logica | ⏸️ | Max temp < min temp | - |
| 769 | GMDN code verplicht | ⏸️ | Medical product zonder GMDN | - |
| 770 | EMDN code verplicht | ⏸️ | Medical product zonder EMDN | - |
| 771 | CE certificaat nummer | ⏸️ | High risk class zonder CE cert | - |
| 772 | Risicoklasse/classificatie | ⏸️ | Invalid risk class combo | - |
| 773 | GMDN/EMDN verplicht medisch | ⏸️ | Medical UNSPSC zonder codes | - |
| 774 | **SDS URL duplicate check** | ✅ | **Identical URL + different chemicals** | **GEÏMPLEMENTEERD** |
| 775 | **Generic URL duplicate check** | ✅ | **Same URL >5x for link fields** | **GEÏMPLEMENTEERD** |

---

## 🌐 **GLOBAL FLAGS (800-899)**

### **Template-brede Validaties**
| Code | Beschrijving | Status | Test Scenario | Resultaat |
|------|-------------|--------|---------------|-----------|
| 800 | Barcode missing | ⏸️ | Product zonder GTIN/Alt ID | - |
| 801 | UOM codes gelijkheid | ⏸️ | base=orderable=1 maar ≠ UOM | - |
| 802 | Verouderde template | ⏸️ | Oude template versie detectie | - |
| 803 | UOM beschrijving mismatch | ⏸️ | Description vs codes conflict | - |
| 804 | Afmetingen set incompleet | ⏸️ | Partial H/B/D dimensions | - |
| 805 | Inhoud velden gelijkheid | ⏸️ | base=orderable=1 maar ≠ content | - |

---

## 🎯 **TEST PRIORITEITEN**

### **🔥 Hoge Prioriteit (Business Critical)**
1. **700-724**: Core validaties - data integrity
2. **774-775**: Nieuwe duplicate URL checks  
3. **800-805**: Global flags - template-brede issues

### **🟡 Middel Prioriteit (Quality Improvements)**
1. **750-759**: Recommendations en auto-corrections
2. **760-773**: Product-specifieke business rules

### **🟢 Lage Prioriteit (Nice to Have)**
1. Edge cases en randgevallen
2. Performance testing bij grote datasets

---

## 🧪 **TEST METHODOLOGIE**

### **Test Templates Nodig:**
1. **Basis Test Template**: Alle mandatory fields gevuld
2. **Error Template**: Elke validation code triggeren
3. **Edge Case Template**: Boundary conditions
4. **Real Data Template**: Echte supplier data
5. **Performance Template**: 5000+ rows voor Quick Mode

### **Test Procedure per Code:**
1. **Setup**: Template met specifieke test data
2. **Execute**: Run validation via Streamlit
3. **Verify**: Check error code in rapport
4. **Document**: Result in deze matrix
5. **Edge test**: Boundary cases
6. **Cleanup**: Reset voor volgende test

### **Automatisering Mogelijkheden:**
- Python test script voor batch testing
- CSV met test scenarios per error code
- Automated rapport parsing voor result verification

---

## 📊 **VOORTGANG TRACKING**

**Totaal codes**: 44  
**Getest**: 2 (774, 775)  
**Remaining**: 42  
**Percentage compleet**: 4.5%

**Volgende test batch**: 700-710 (Core field validations)

---

*Laatst bijgewerkt: 3 oktober 2025*  
*Verantwoordelijke: Niels Croiset*