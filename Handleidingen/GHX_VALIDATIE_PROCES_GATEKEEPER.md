# 🏛️ GHX Template Validatie Proces & Gatekeeper Functie

*Complete documentatie van het GHX prijstemplate validatie proces en de rol van de gatekeeper database functie*

---

## 📋 Proces Overzicht

Het GHX template validatie proces bestaat uit twee hoofdcomponenten die **parallel** maar **onafhankelijk** werken:

1. **Ons Validatierapport** - Voorspellende kwaliteitscheck
2. **Gatekeeper Database Functie** - Definitieve validatie met beslissingsmacht

---

## 🔄 Complete Proces Flow

### Stap 1: Template Upload Door Leverancier

Leverancier heeft **twee opties** bij het uploaden van een Excel template:

#### Optie A: Test Upload
- **Doel:** Alleen validatierapport krijgen voor kwaliteitscheck
- **Proces:** Template → Validatierapport → Leverancier
- **Gatekeeper:** NIET actief
- **Resultaat:** Informatierapport, geen database acties

#### Optie B: Definitieve Upload  
- **Doel:** Template officieel indienen voor verwerking
- **Proces:** Template → Validatierapport → Leverancier + Template → Gatekeeper
- **Gatekeeper:** WEL actif  
- **Resultaat:** Informatierapport + gatekeeper verwerking

### Stap 2: Ons Validatierapport

**Wat het WEL doet:**
- Analyseert template kwaliteit tegen validatiematrix
- Genereert error codes (700-805) 
- Voorspelt wat gatekeeper waarschijnlijk gaat doen
- Waarschuwt leverancier vooraf

**Wat het NIET doet:**
- Templates afkeuren of goedkeuren
- Data aanpassen in database
- Contact hebben met database
- Definitieve beslissingen nemen

**Voorbeeld Rapport Berichten:**
```
❌ "Artikelnummer is leeg - gatekeeper zal dit waarschijnlijk AFKEUREN"
⚠️ "Artikelnaam te lang - gatekeeper zal dit waarschijnlijk INKORTEN tot 90 karakters"  
🏴 "Brutoprijs lager dan nettoprijs (onmogelijk scenario)"
```

### Stap 3: Gatekeeper Database Functie

**Wat het WEL doet:**
- Automatische validatie van templates (eigen implementatie)
- Templates **afkeuren** en weigeren database opslag
- Template data **aanpassen** voordat opslag
- Templates **doorlaten** met waarschuwingsvlaggen
- Directe database interactie

**Wat het NIET doet:**
- Ons validatierapport lezen of gebruiken
- Handmatige review (volledig geautomatiseerd)
- Feedback geven aan leveranciers

---

## 📊 Validatiematrix: Gemeenschappelijke Basis

### Structuur Matrix (GHX Prijstemplate Validatiematrix v10TG.xlsx)

- **Regel 31:** Afkeuringen - Validaties die templates doen afwijzen
- **Regel 32:** Aanpassingen - Validaties waar gatekeeper data kan corrigeren  
- **Regel 33:** Flags - Waarschuwingen/verdachte situaties

### Gebruik Van Matrix

**Door Ons Validatierapport:**
- Basis voor alle error codes (700-805)
- Voorspelt gatekeeper gedrag
- Waarschuwt leveranciers vooraf

**Door IT/Gatekeeper:**
- Basis voor gatekeeper implementatie
- IT bepaalt uiteindelijke implementatie details
- Kan afwijken van onze interpretatie

---

## ⚠️ Kritieke Uitdagingen

### 1. Twee Onafhankelijke Systemen
- **Probleem:** Ons rapport en gatekeeper zijn los ontwikkeld
- **Risico:** Verschillende interpretaties van validatiematrix
- **Gevolg:** Ons rapport voorspelt verkeerde gatekeeper acties

### 2. Synchronisatie
- **Probleem:** Gatekeeper kan wijzigen zonder onze kennis
- **Oplossing:** Regelmatige communicatie met IT vereist
- **Monitoring:** Vergelijken gatekeeper resultaten met onze voorspellingen

### 3. Matrix Updates
- **Scenario:** Nieuwe validaties toegevoegd/weggehaald
- **Actie:** Beide systemen moeten synchroon updaten
- **Eigenaar:** GHX (ons) stuurt validatiematrix naar IT

---

## 🎯 Onze Verantwoordelijkheid

### Kwaliteit Validatierapport
1. **Dekking:** Alle gatekeeper validaties moeten in ons rapport
2. **Accuraatheid:** Voorspellingen moeten kloppen met gatekeeper gedrag  
3. **Duidelijkheid:** Leveranciers moeten begrijpen wat gatekeeper gaat doen

### Monitoring & Communicatie
1. **Test vergelijking:** Periodiek testen of onze voorspellingen kloppen
2. **IT Contact:** Regelmatig afstemmen over matrix wijzigingen
3. **Update Proces:** Beide systemen gelijktijdig updaten bij wijzigingen

---

## 📈 Succes Criteria

**Perfect Scenario:**
- Leverancier krijgt ons validatierapport  
- Past template aan op basis van onze waarschuwingen
- Uploadt definitief → Gatekeeper vindt geen fouten meer
- Template wordt perfect verwerkt

**Faal Scenario:**  
- Ons rapport zegt "gatekeeper accepteert dit"
- Gatekeeper wijst template toch af
- Leverancier vertrouwt ons systeem niet meer

---

## 🔧 Technische Details

### Ons Systeem
- **Tech Stack:** Python/Streamlit validatie tool
- **Config:** field_validation_v20.json
- **Output:** Validatierapport met error codes 700-805

### Gatekeeper Systeem  
- **Eigenaar:** IT Department
- **Implementatie:** Database functie (details onbekend)
- **Input:** Template + mogelijk eigen validatiematrix copy
- **Output:** Database acties (accept/reject/modify)

---

## 📚 Gerelateerde Documentatie

- `VALIDATIE_CROSS_REFERENCE.md` - Matrix vs implementatie mapping
- `TEST_VALIDATIE_MATRIX.md` - Systematische test resultaten  
- `field_validation_v20.json` - Onze validatie configuratie
- `GHX Prijstemplate Validatiematrix v10TG.xlsx` - Basis validatiematrix

---

*Laatste update: 2025-10-05*  
*Status: In ontwikkeling - Gatekeeper nog niet live*