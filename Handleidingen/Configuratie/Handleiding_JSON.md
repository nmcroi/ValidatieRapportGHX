# 📋 Handleiding: field_validation_v20.json

## 🎯 Inhoudsopgave
1. [Wat doet dit bestand?](#wat-doet-dit-bestand)
2. [Basisstructuur v20](#basisstructuur-v20)
3. [Foutcodes: Het foutmeldingen systeem](#foutcodes-het-foutmeldingen-systeem)
4. [Velden: Hoe validatie werkt](#velden-hoe-validatie-werkt)
5. [Validatie Types: Wat kun je controleren](#validatie-types-wat-kun-je-controleren)
6. [Geavanceerde V20 Features](#geavanceerde-v20-features)
7. [Complexe Validaties: Cross-row checks](#complexe-validaties-cross-row-checks)
8. [Praktische Voorbeelden](#praktische-voorbeelden)
9. [Een nieuwe validatie toevoegen](#een-nieuwe-validatie-toevoegen)
10. [Recente Wijzigingen](#recente-wijzigingen)

## 📖 Wat doet dit bestand?

Het `field_validation_v20.json` bestand is het **brein** van de GHX validatie tool. Het bepaalt:
- 🚨 **Welke fouten** worden gedetecteerd  
- 📝 **Welke foutmeldingen** gebruikers zien
- ✅ **Welke velden** hoe gevalideerd worden
- 🔧 **Hoe complex** validaties werken (bijv. CAS-nummer checks)

**In simpele woorden:** Dit bestand zegt tegen het systeem "Check dit, rapporteer dat, en als X gebeurt, dan doe Y"

## 🏗️ Basisstructuur v20

```json
{
    "version": "2.0",
    "global_settings": {
        "null_values": ["nvt", "N/A", "-", ...],
        "error_code_descriptions": { "700": "Foutmelding...", ... }
    },
    "field_validations": {
        "Artikelnummer": { ... },
        "CAS nummer": { ... },
        "Link Veiligheidsinformatieblad (SDS)": { ... }
    }
}
```

**Verschil met v19:** V20 is **veel simpeler** - geen aparte secties voor mapping, alles staat bij het veld zelf.

## 🚨 Foutcodes: Het foutmeldingen systeem

Foutcodes zijn de **ID-nummers** voor verschillende soorten problemen. Denk aan het als een catalogus van "wat kan er fout gaan":

```json
"error_code_descriptions": {
    "700": "Aantal verplichte velden die leeg zijn.",
    "701": "Een waarde is te kort.",
    "702": "Een waarde is te lang.",
    "703": "Een waarde die uniek moet zijn, is een duplicaat (bijv. GTIN).",
    "774": "Veiligheidsblad URL mogelijk generiek - URL komt meer dan 5x voor met verschillende CAS-nummers/stoffen."
}
```

### 📊 Foutcode Categorieën:
- **700-729:** Basis validatie fouten (leeg, te kort, te lang, etc.)
- **750-779:** Flags & correcties (aanbevelingen, automatische fixes)  
- **800-805:** Global flags (hele dataset problemen)

**Praktisch:** Als je een nieuwe fout wilt toevoegen, pak het volgende beschikbare nummer en voeg beschrijving toe.

## ✅ Velden: Hoe validatie werkt

Elk veld (zoals "Artikelnummer" of "CAS nummer") heeft zijn eigen **validatie recept**. Dit bestaat uit:

### 🏗️ Basis structuur van een veld:

```json
"Artikelnummer": {
    "data_format": "string",
    "rules": [
        {
            "type": "error",
            "code": "700",
            "condition": "is_empty",
            "message": "Artikelnummer is verplicht en mag niet leeg zijn."
        },
        {
            "type": "error", 
            "code": "702",
            "condition": "exceeds_max_length",
            "params": 50,
            "message": "Artikelnummer is te lang (max 50 karakters)."
        }
    ]
}
```

### 🧩 Onderdelen uitgelegd:

**`data_format`:** Het type data (string, numeric, boolean, url, date)  
**`rules`:** Een lijst van checks die uitgevoerd worden  
**`type`:** Soort melding - "error" (fout) of "flag" (waarschuwing)  
**`code`:** Welke foutcode (zie foutcode lijst)  
**`condition`:** Wat wordt gecontroleerd (is_empty, too_long, etc.)  
**`params`:** Extra informatie voor de check (bijv. max lengte = 50)  
**`message`:** De tekst die de gebruiker ziet

## 🔧 Validatie Types: Wat kun je controleren

### 📝 String velden (tekst)
```json
"condition": "is_empty"           → Is het veld leeg?
"condition": "exceeds_max_length" → Is de tekst te lang?
"condition": "below_min_length"   → Is de tekst te kort?
"condition": "not_alphanumeric"   → Bevat het rare tekens?
```

### 🔢 Numeric velden (cijfers)  
```json
"condition": "exceeds_max_value"  → Is het getal te groot?
"condition": "below_min_value"    → Is het getal te klein?
"condition": "not_numeric"        → Is het geen geldig getal?
"condition": "too_many_decimals"  → Teveel cijfers achter komma?
```

### 🌐 URL velden (links)
```json
"condition": "not_starts_with"    → Begint niet met https?
"condition": "invalid_url_format" → Is het geen geldige URL?
```

### 📅 Boolean velden (ja/nee)
```json
"condition": "is_not_boolean"     → Is het niet Ja/Nee/1/0?
```

## 🧠 Geavanceerde V20 Features

### **Context Triggers: Medical Device Validaties**
V20 ondersteunt slimme context-detectie voor medische apparaten:

```json
"context_triggers": {
    "is_medical_device": {
        "description": "Bepaalt of het product een medisch apparaat is.",
        "trigger_logic": "OR",
        "triggers": [
            { "if_field": "UNSPSC Code", "starts_with": "42" },
            { "if_field": "Steriel", "equals": 1 },
            { "if_field": "Indicatie Implanteerbaar", "equals": 1 }
        ]
    }
}
```

**Hoe werkt dit:**
- Systeem checkt automatisch of product medisch apparaat is
- Op basis hiervan worden extra validaties getriggerd
- Zorgt voor context-gevoelige business rules

### **Template Type Support**
V20 detecteert automatisch template types (TG/DT/AT):
- **TG (Template Generator)**: Dynamische templates met stamp-detectie
- **DT (Default Template)**: Standaard GHX templates  
- **AT (Alternative Template)**: Afwijkende leverancier templates

### **Cross-field Dependencies**
Geavanceerde veld-afhankelijkheden:
```json
"rules": [
    {
        "type": "flag",
        "code": "751",
        "condition": "conditional_required",
        "params": {
            "if_field": "Bruto Gewicht Basiseenheid", 
            "is": "filled",
            "then_required": "Eenheidscode Gewicht Basiseenheid (UOM)"
        }
    }
]
```

## 🎯 Complexe Validaties: Cross-row checks

Sommige validaties kijken naar **meerdere rijen tegelijk**. Dit is handig voor complexe business rules:

### 🧪 Voorbeeld: SDS URL Duplicaat Check

**Probleem:** Leveranciers gebruiken soms één generieke URL voor verschillende chemicaliën  
**Oplossing:** Check of dezelfde URL bij verschillende stoffen wordt gebruikt

```json
"Link Veiligheidsinformatieblad (SDS)": {
    "data_format": "url",
    "rules": [
        {
            "type": "flag",
            "code": "774", 
            "condition": "duplicate_url_with_varying_chemicals",
            "params": {
                "threshold": 5,
                "check_fields": ["CAS nummer", "Stofnaam", "Brutoformule"]
            },
            "message": "Deze SDS-URL komt meer dan 5 keer voor met verschillende CAS-nummers of stoffen."
        }
    ]
}
```

**Hoe werkt dit:**
1. Systeem groepeert alle rijen op URL  
2. Voor URLs die ≥5x voorkomen
3. Check of CAS-nummer/Stofnaam/Brutoformule verschillen
4. Als ja → waarschuwing dat URL generiek is

## 📚 Praktische Voorbeelden

### 🔤 Eenvoudig tekstveld (Artikelnummer)
```json
"Artikelnummer": {
    "data_format": "string",
    "rules": [
        {
            "type": "error",
            "code": "700", 
            "condition": "is_empty",
            "message": "Artikelnummer is verplicht."
        },
        {
            "type": "error",
            "code": "702",
            "condition": "exceeds_max_length", 
            "params": 50,
            "message": "Artikelnummer mag max 50 karakters zijn."
        }
    ]
}
```

### 💰 Numeriek veld (Brutoprijs)
```json
"Brutoprijs": {
    "data_format": "numeric",
    "rules": [
        {
            "type": "error",
            "code": "704",
            "condition": "not_numeric",
            "message": "Brutoprijs moet een geldig getal zijn."
        },
        {
            "type": "error", 
            "code": "710",
            "condition": "exceeds_max_digits",
            "params": {"integer_digits": 6, "decimal_digits": 2},
            "message": "Brutoprijs mag max 6 cijfers voor komma en 2 na komma hebben."
        }
    ]
}
```

### 🔗 URL veld (Veiligheidsblad)
```json
"Link Veiligheidsinformatieblad (SDS)": {
    "data_format": "url", 
    "rules": [
        {
            "type": "correction",
            "code": "722",
            "condition": "not_starts_with",
            "params": "https",
            "message": "SDS link moet beginnen met https://"
        }
    ]
}
```

### ✅ Boolean veld (Geregistreerd geneesmiddel)
```json
"Geregistreerd geneesmiddel": {
    "data_format": "boolean",
    "rules": [
        {
            "type": "correction", 
            "code": "719",
            "condition": "is_not_boolean",
            "message": "Moet Ja/Nee/1/0 zijn."
        }
    ]
}
```

## 🛠️ Een nieuwe validatie toevoegen

**Scenario:** Je wilt een nieuwe check toevoegen voor een veld

### Stap 1: Kies een foutcode
```json
// Voeg toe aan "error_code_descriptions" 
"775": "Jouw nieuwe foutmelding hier."
```

### Stap 2: Zoek het veld op
```json
// Zoek het veld in de "fields" sectie
"Jouw Veld Naam": {
    "data_format": "string",
    "rules": [
        // Bestaande rules...
    ]
}
```

### Stap 3: Voeg de regel toe
```json
// Voeg nieuwe rule toe aan de rules array
{
    "type": "error",        // of "flag" voor waarschuwing
    "code": "775", 
    "condition": "jouw_condition_naam",
    "params": "extra_info_indien_nodig",
    "message": "Wat de gebruiker ziet bij deze fout."
}
```

### Stap 4: Test het
1. Upload een Excel bestand met je test case
2. Check of de fout correct wordt gedetecteerd  
3. Verificeer dat de foutmelding duidelijk is

## 🔄 Recente Wijzigingen

### **UNSPSC Veldnaam Update**
**Let op:** Het veld `"UNSPSC"` is hernoemd naar `"UNSPSC Code"` voor consistentie met GHX templates.

```json
// Oud (werkt niet meer):
"UNSPSC": { ... }

// Nieuw (correct):
"UNSPSC Code": { ... }
```

### **Error Code 775 Bewoording**
Foutcode 775 is aangepast voor algemene beschrijving in Sheet 1:
```json
"775": "FLAG: Een URL komt meer dan 5 keer voor en wijst mogelijk op een generieke link die niet specifiek is voor een product."
```

## 💡 Tips & Tricks

### ✅ Do's:
- **Duidelijke foutmeldingen** - Leg uit wat er fout is EN hoe het op te lossen
- **Logische foutcodes** - Gebruik de juiste categorie (700-729 voor basis fouten)
- **Test eerst** - Maak altijd een backup en test met kleine bestanden

### ❌ Don'ts:  
- **Geen onduidelijke messages** - "Er is een fout" helpt niemand
- **Geen dubbele foutcodes** - Elke code mag maar 1x gebruikt worden
- **Geen complexe params zonder documentatie** - Documenteer ingewikkelde conditions

## 🔍 Debuggen

**Fout wordt niet gedetecteerd?**
1. Check of de veldnaam exact klopt (hoofdletters, spaties)
2. Check of de condition bestaat in de Python code
3. Test met een simpel voorbeeld eerst

**Verkeerde foutmelding?**  
1. Check de foutcode mapping
2. Verificeer dat je de juiste "type" gebruikt (error vs flag)

**JSON syntax fout?**
1. Gebruik een JSON validator online
2. Check of alle haakjes/komma's kloppen
3. Let op: laatste rule in array heeft GEEN komma

---

**🎓 Je bent nu klaar om de field_validation_v20.json te begrijpen en aan te passen!**
