# GHX Prijslijst Validatie App

Een Streamlit applicatie voor het valideren van prijslijsten volgens GHX-standaarden.

## Functies

- Upload Excel prijslijsten voor validatie
- Automatische herkenning van kolommen via header mapping
- Validatie op basis van configurable rules
- Genereert uitgebreide Excel-rapporten met validatieresultaten
- Identificeert ontbrekende of onjuiste gegevens

## Projectstructuur

- `prijslijst_validatie_app.py` - Hoofdbestand voor de Streamlit app
- `validator/` - Bevat validatielogica
  - `price_tool.py` - Core validatie engine
  - `rapport_utils.py` - Excel rapport generatie
- `field_validation_v18.json` - Configuratie voor veldvalidatie
- `header_mapping.json` - Mapping van Excel headers naar GHX-standaard velden

## Git Workflow

### Wijzigingen bijhouden op GitHub

Volg deze stappen om wijzigingen naar GitHub te pushen:

1. **Open Terminal** (via Spotlight: cmd+spatie, typ 'Terminal')

2. **Navigeer naar de projectmap**:
   ```bash
   cd "/Users/ghxnielscroiset/Library/CloudStorage/OneDrive-GlobalHealthcareExchange/Documenten/Windsurf/Project PrijsValGem_WS app"
   ```

3. **Controleer welke bestanden gewijzigd zijn**:
   ```bash
   git status
   ```

4. **Voeg gewijzigde bestanden toe aan staging**:
   ```bash
   git add .
   ```
   (of specifieke bestanden: `git add validator/price_tool.py validator/rapport_utils.py`)

5. **Commit met beschrijvende boodschap**:
   ```bash
   git commit -m "Duidelijke beschrijving van wijzigingen"
   ```

6. **Push wijzigingen naar GitHub**:
   ```bash
   git push origin main
   ```

### Opmerkingen

- Geef duidelijke commit messages die beschrijven WAT er is gewijzigd en WAAROM
- Voeg de versie toe in de commit message voor belangrijke releases, bijv.: `"Fix: rapportgeneratie verbeterd (versie6525-15.46)"`
- Test altijd wijzigingen voordat je ze commit

## Bekende Versies

- **versie6525(13:35)**: Rapport generatie en donut charts structuur gefixt
- **versie6525(15:46)**: Foutcode 76 exclusief voor Artikelnummer duplicaten gemaakt en template-check geïmplementeerd
