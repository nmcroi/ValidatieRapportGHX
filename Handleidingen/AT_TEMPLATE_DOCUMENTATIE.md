# AT Template Documentatie

## Wat zijn AT Templates?

**AT = Alternatieve Template**

AT templates zijn prijslijst bestanden die **afwijken van de standaard GHX template structuur** maar toch voldoende compatibel zijn om gevalideerd te kunnen worden door ons systeem.

## Template Types Overzicht

| Template Type | Volledige Naam | Beschrijving |
|---------------|----------------|--------------|
| **TG** | Template Generator | Moderne templates met metadata stamp - optimaal formaat |
| **DT** | Default Template | Standaard GHX templates zonder stamp - goed formaat |
| **AT** | Alternatieve Template | Afwijkende structuur - suboptimaal formaat |

## AT Template Karakteristieken

### Herkenning
AT templates worden automatisch gedetecteerd wanneer:
- Het Excel bestand **niet** de standaard GHX kolom configuratie heeft
- Header mapping wel mogelijk is (bestand is nog wel bruikbaar)
- Bestand valt terug op "alternatieve template" classificatie

### Validatie Proces
1. **Header Mapping**: AT templates doorlopen dezelfde header mapping als andere templates
2. **Mandatory Fields**: Moeten alle 17 standaard GHX mandatory fields bevatten (na mapping)
3. **Validatie Rules**: Gebruiken dezelfde validatie regels als TG/DT templates
4. **Special Detection**: Automatische detectie van chemical fields waar aanwezig

## Score Impact: -25 Punt Penalty

### Waarom de Penalty?
AT templates krijgen een **-25 punt aftrek** op de eindscore omdat:

1. **Suboptimale Structuur**: Wijken af van GHX standaarden
2. **Risico Factor**: Hogere kans op mapping/validatie problemen  
3. **Maintenance Overhead**: Vereisen meer handmatige configuratie
4. **Kwaliteit Incentive**: Motivatie om over te stappen naar standaard templates

### Score Berekening
```
Final Score = Core Score + UOM Penalties + Template Penalty
            = (M% × 0.6) + (J% × 0.4) + UOM_penalties + (-25)
```

**Template Penalty per Type:**
- TG templates: `0` punten (geen penalty)
- DT templates: `0` punten (geen penalty)  
- AT templates: `-25` punten (penalty)

### Praktijk Voorbeeld
Een AT template met:
- M% = 85% (volledigheid)
- J% = 90% (juistheid)  
- UOM penalties = -3

**Berekening:**
- Core Score: (85 × 0.6) + (90 × 0.4) = 51 + 36 = 87
- Total Score: 87 + (-3) + (-25) = **59 punten**

**Vergelijking met DT template:**
Dezelfde data in DT template = 87 + (-3) + 0 = **84 punten**

## Aanbevelingen

### Voor Leveranciers
1. **Migratie**: Overweeg migratie naar standaard GHX TG/DT templates
2. **Template Request**: Vraag actuele GHX template aan bij account manager
3. **Kwaliteitsverbetering**: Focus extra op data kwaliteit om penalty te compenseren

### Voor Account Managers  
1. **Communicatie**: Leg penalty uit als kwaliteit incentive
2. **Template Support**: Help leveranciers bij migratie naar standaard format
3. **Verwachtingsmanagement**: Penalty is configureerbaar maar standaard -25 punten

## Configuratie

De AT template penalty is instelbaar via `uom_penalty_config.json`:

```json
{
  "template_penalties": {
    "TG": 0,
    "DT": 0,
    "AT": -25
  }
}
```

**Overwegingen voor aanpassing:**
- **Hogere penalty** = sterkere incentive voor migratie
- **Lagere penalty** = minder impact op leveranciers scores
- **Penalty = 0** = geen onderscheid tussen template types

## Vragen & Ondersteuning

Voor vragen over AT templates:
1. Check eerst header mapping configuratie
2. Valideer mandatory fields mapping  
3. Test met verschillende penalty instellingen
4. Documenteer specifieke use cases

---
*Laatst bijgewerkt: Oktober 2024*
*Voor: IT Deployment & Account Management Team*