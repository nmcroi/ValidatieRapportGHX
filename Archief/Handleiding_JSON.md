# Handleiding: Werken met field_validation_v19.json

## Inhoudsopgave
1. [Inleiding](#inleiding)
2. [Basisstructuur van het bestand](#basisstructuur-van-het-bestand)
3. [Foutcodes en Beschrijvingen](#foutcodes-en-beschrijvingen)
4. [Velddefinities](#velddefinities)
5. [Validatietypen en Regels](#validatietypen-en-regels)
6. [Speciale Velden en Eigenschappen](#speciale-velden-en-eigenschappen)
7. [Voorbeelden](#voorbeelden)

## Inleiding
Deze handleiding legt uit hoe je het `field_validation_v19.json` bestand kunt bewerken en begrijpen. Dit bestand bepaalt hoe prijslijsten gevalideerd worden in de GHX Prijslijst Validatie Tool.

## Basisstructuur van het bestand

Het JSON-bestand bestaat uit vier hoofdsecties:

```json
{
    "error_code_mapping": { ... },
    "error_code_descriptions": { ... },
    "fields": { ... },
    "red_flags": [ ... ]
}
```

## 1. Foutcodes en Beschrijvingen

### error_code_mapping
Koppelt fouttypes aan numerieke codes:

```json
"error_code_mapping": {
    "required": "73",
    "min_length": "74",
    "max_length": "75",
    "unique": "76"
}
```

### error_code_descriptions
Bevat beschrijvingen voor elke foutcode:

```json
"error_code_descriptions": {
    "73": "Aantal verplichte velden die leeg zijn.",
    "74": "Aantal verplichte velden met te korte waarden."
}
```

## 2. Velddefinities

Elk veld heeft een unieke naam en eigenschappen:

```json
"Artikelnummer": {
    "GHXmandatory": true,
    "GS1mandatory": false,
    "type": "string",
    "min_length": 1,
    "max_length": 50,
    "unique": true
}
```

## 3. Validatietypen en Regels

### Tekstvelden (type: "string")
- `min_length`: Minimale lengte
- `max_length`: Maximale lengte
- `alphanumeric`: Alleen letters en cijfers toegestaan

### Numerieke velden (type: "numeric")
- `min_value`: Minimale waarde
- `max_value`: Maximale waarde
- `max_integer_digits`: Maximaal aantal cijfers voor de komma
- `max_decimal_digits`: Maximaal aantal decimalen

### Datumvelden (type: "date")
- `format`: Datumnotatie (bijv. "%Y-%m-%d")
- `min_date`: Vroegste toegestane datum
- `max_date`: Laatste toegestane datum

## 4. Speciale Velden en Eigenschappen

### Unieke velden
```json
"unique": true
```

### Voorwaardelijke velden
```json
"depends_on": {
    "field": "AnderVeld",
    "value": "SpecifiekeWaarde",
    "condition": "equals"
}
```

## 5. Voorbeelden

### Eenvoudig tekstveld
```json
"Artikelnummer": {
    "GHXmandatory": true,
    "type": "string",
    "min_length": 1,
    "max_length": 50,
    "unique": true
}
```

### Numeriek veld
```json
"Brutoprijs": {
    "GHXmandatory": true,
    "type": "numeric",
    "min_value": 0,
    "max_value": 999999.99,
    "max_decimal_digits": 2
}
```

### Keuzelijst
```json
"Landcode": {
    "type": "string",
    "allowed_values": ["NL", "BE", "DE", "FR"]
}
```

### Datumveld
```json
"Startdatum": {
    "type": "date",
    "format": "%Y-%m-%d",
    "min_date": "2000-01-01"
}
```

### Complexe validatie
```json
"GTIN": {
    "type": "string",
    "validation": {
        "type": "regex",
        "pattern": "^\\d{8}$|^\\d{12,14}$",
        "message": "Ongeldig GTIN-formaat"
    }
}
```

### Voorwaardelijk verplicht veld
```json
"CE_Datum": {
    "depends_on": {
        "field": "CE_Markering",
        "value": "Ja",
        "condition": "equals"
    },
    "type": "date"
}
```

## Belangrijke aandachtspunten

1. **JSON-syntaxis**:
   - Gebruik dubbele aanhalingstekens (`"`)
   - Scheid eigenschappen met komma's
   - Geen komma na de laatste eigenschap

2. **Foutafhandeling**:
   - Zorg voor duidelijke foutmeldingen
   - Test nieuwe validatieregels grondig

3. **Compatibiliteit**:
   - Houd rekening met bestaande data
   - Voer wijzigingen stapsgewijs door

4. **Documentatie**:
   - Houd de handleiding up-to-date
   - Documenteer complexe regels in commentaar

## Volgende stappen

1. Test nieuwe validatieregels met testbestanden
2. Controleer of bestaande data nog voldoet
3. Documenteer wijzigingen in het versiebeheer
4. Maak een backup voordat je grote wijzigingen doorvoert
