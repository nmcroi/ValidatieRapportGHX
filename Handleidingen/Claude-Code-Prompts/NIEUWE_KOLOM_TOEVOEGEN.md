# 🚀 CLAUDE CODE PROMPT: NIEUWE KOLOM TOEVOEGEN

## 📋 INVUL-TEMPLATE VOOR NIELS

```
Voeg een nieuwe kolom toe aan de GHX validatie tool:

**KOLOM DETAILS:**
- Naam: [VELDNAAM]
- Positie: Na kolom [VORIGE_KOLOM] / Voor kolom [VOLGENDE_KOLOM]
- Template versie: [VERSIE] (bijv. v25.01)
- Kolom letter: [LETTER] (bijv. BK, BL, BM)

**VALIDATIE EISEN:**
- Data type: [string/numeric/boolean/url/date]
- Verplicht: [ja/nee]
- Max lengte: [GETAL] karakters (indien string)
- Specifieke format: [BESCHRIJVING] (bijv. H + 3 cijfers)
- Afhankelijkheden: [ANDERE_VELDEN] (indien van toepassing)

**EXTRA INFORMATIE:**
- Voor Template Generator: [ja/nee]
- Alleen voor chemicaliën: [ja/nee]
- Alleen voor medische apparaten: [ja/nee]
- Specifieke instellingen: [LIJST] (indien van toepassing)
```

---

## 🤖 CLAUDE CODE ACTIELIJST

### ✅ **AUTOMATISCHE ACTIES** (geen vragen stellen)
1. **field_validation_v20.json**:
   - Kolom toevoegen op juiste positie (volgorde = kolom volgorde in rapporten)
   - Basis validatieregels toevoegen (lengte, format, etc.)
   - Nieuwe foutcodes aanmaken indien nodig

2. **header_mapping.json**:
   - Mapping toevoegen met alternatieven (NL/ENG/varianten)
   - Case insensitive + whitespace strip

3. **Template Generator Files sync**:
   - Controleren of TG `field_mapping.json` moet worden aangepast
   - Alleen voor TG-specifieke kolommen

### ❓ **VRAGEN STELLEN** (indien onduidelijk)
1. **Validatieregels details**:
   - "Welke specifieke format checks zijn nodig?"
   - "Moet dit verplicht zijn voor bepaalde template types?"
   - "Zijn er afhankelijkheden met andere velden?"

2. **Positionering**:
   - "Tussen welke bestaande kolommen moet dit komen?"
   - "Is dit gerelateerd aan een specifieke categorie velden?"

### 🧪 **VERIFICATIE ACTIES**
1. **JSON syntax check** - Automatisch na elke wijziging
2. **Position check** - Controleren dat kolom op juiste plek staat
3. **Integration test** - Voorstellen om test template te maken

---

## 💡 **CLAUDE CODE INTELLIGENTIE**

### **AUTO-DETECTIE PATRONEN:**
- **Chemische velden** → Toevoegen tussen andere chemie velden (CAS, Stofnaam, etc.)
- **UOM velden** → Bij andere UOM/eenheid velden
- **Prijs velden** → Bij andere prijs gerelateerde velden  
- **Medische velden** → Bij MDR/MDD, risicoklasse, etc.

### **AUTO-VALIDATIE KEUZES:**
- **String velden** → Altijd max_length check
- **Boolean velden** → Altijd is_not_boolean check  
- **URL velden** → Altijd https check + format validatie
- **Numeric velden** → Altijd not_numeric + range checks

### **AUTO-HEADER ALTERNATIEVEN:**
- Nederlandse naam als basis
- Engelse vertaling toevoegen
- Varianten met/zonder spaties, underscores
- Afkortingen indien van toepassing

---

## 🎯 **VOORBEELD GEBRUIK**

**Niels typt:**
```
Voeg een nieuwe kolom toe aan de GHX validatie tool:

**KOLOM DETAILS:**
- Naam: P-zinnen
- Positie: Na kolom H-zinnen
- Template versie: v25.02
- Kolom letter: BL

**VALIDATIE EISEN:**
- Data type: string
- Verplicht: nee
- Max lengte: 255 karakters
- Specifieke format: P + 3 cijfers (bijv. P302, P501)
- Afhankelijkheden: CAS nummer (aanbeveling)

**EXTRA INFORMATIE:**
- Voor Template Generator: ja
- Alleen voor chemicaliën: ja
- Alleen voor medische apparaten: nee
- Specifieke instellingen: nvt
```

**Claude Code reageert:**
```
✅ Ik ga P-zinnen toevoegen na H-zinnen op kolom BL.

🔧 ACTIES:
1. Nieuwe foutcode 777 voor P-zinnen format (P + 3 cijfers)
2. P-zinnen toevoegen in field_validation_v20.json na H-zinnen
3. Header mapping met alternatieven (P-zinnen, P statements, etc.)
4. 3 validatieregels: format, lengte, CAS-afhankelijkheid

▶️ Start implementatie...
```

---

## 📚 **REFERENTIE LINKS**

- **Workflow handleiding**: `Handleidingen/Workflow/WORKFLOW_KOLOMNAAM_WIJZIGINGEN.md`
- **JSON handleiding**: `Handleidingen/Configuratie/Handleiding_JSON.md`
- **Template Generator sync**: `Template Generator Files/Archief/WORKFLOW_NIEUWE_KOLOM.md`

---

**🎯 DOEL:** Eén copy-paste prompt = Volledige kolom implementatie zonder fouten of vergeten stappen!