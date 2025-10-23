# 🔧 CLAUDE CODE PROMPT: VALIDATIEREGEL AANPASSEN

## 📋 INVUL-TEMPLATE VOOR NIELS

```
Pas een validatieregel aan voor kolom [KOLOMNAAM]:

**HUIDIGE SITUATIE:**
- Kolom: [KOLOMNAAM]
- Probleem: [BESCHRIJVING_PROBLEEM]
- Huidige regel: [HUIDIGE_REGEL] (indien bekend)

**GEWENSTE WIJZIGING:**
- Nieuwe regel: [NIEUWE_REGEL]
- Type: [error/correction/flag]
- Strengheid: [strenger/soepeler/anders]
- Specifieke check: [BESCHRIJVING]

**VOORBEELDEN:**
- Geldig: [VOORBEELDEN_GELDIG]
- Ongeldig: [VOORBEELDEN_ONGELDIG]
```

## 🤖 CLAUDE CODE ACTIELIJST

### ✅ **AUTOMATISCHE ACTIES**
1. **Zoek huidige regel** in field_validation_v20.json
2. **Analyseer impact** - welke andere velden kunnen beïnvloed worden
3. **Update regel** of voeg nieuwe toe
4. **Test JSON syntax**
5. **Controleer foutcode beschrijving**

### ❓ **VRAGEN STELLEN**
- "Moet de oude regel vervangen of nieuwe regel toegevoegd?"
- "Welke foutcode voorkeur? (correction/flag/error)"
- "Backward compatibility belangrijk voor bestaande data?"

---

# 🔍 CLAUDE CODE PROMPT: FOUT DEBUGGEN

## 📋 INVUL-TEMPLATE VOOR NIELS

```
Debug een probleem in de validatie tool:

**PROBLEEM:**
- Beschrijving: [PROBLEEM_BESCHRIJVING]
- Template type: [TG/DT/AT]
- Specifieke kolom: [KOLOMNAAM] (indien van toepassing)
- Foutmelding: [FOUTMELDING]

**REPRODUCTIE:**
- Bestand: [BESTANDSNAAM] (indien beschikbaar)
- Waarde: [SPECIFIEKE_WAARDE]
- Verwacht: [VERWACHT_RESULTAAT]
- Actueel: [WERKELIJK_RESULTAAT]

**CONTEXT:**
- Recent gewijzigd: [ja/nee] - [WAT_GEWIJZIGD]
- Werkte eerder: [ja/nee]
- Alleen bij bepaalde templates: [ja/nee]
```

## 🤖 CLAUDE CODE ACTIELIJST

### ✅ **AUTOMATISCHE ACTIES**
1. **Check recente wijzigingen** - git log/file dates
2. **Zoek gerelateerde config** - JSON files, Python validation logic
3. **Analyseer template type impact** - TG vs DT vs AT verschillen
4. **Test JSON syntax** - alle config bestanden
5. **Check mapping conflicts** - header_mapping.json

---

# ⚙️ CLAUDE CODE PROMPT: FOUTCODE BEHEER

## 📋 INVUL-TEMPLATE VOOR NIELS

```
Beheer foutcodes in de validatie tool:

**ACTIE:**
- [nieuwe_foutcode_toevoegen/bestaande_wijzigen/foutcode_hernoemen]

**NIEUWE FOUTCODE** (indien van toepassing):
- Categorie: [700-729 basis / 750-779 flags / 800-805 global]
- Type: [error/correction/flag]
- Beschrijving: [KORTE_BESCHRIJVING]
- Voor welke velden: [VELDNAMEN]

**BESTAANDE FOUTCODE** (indien van toepassing):
- Code: [NUMMER]
- Probleem: [BESCHRIJVING_PROBLEEM]
- Nieuwe tekst: [NIEUWE_BESCHRIJVING]
```

## 🤖 CLAUDE CODE ACTIELIJST

### ✅ **AUTOMATISCHE ACTIES**
1. **Zoek volgende beschikbare code** in juiste categorie
2. **Update error_code_descriptions**
3. **Zoek alle referenties** naar bestaande codes
4. **Consistentie check** - geen duplicate codes
5. **Update documentatie** indien nodig