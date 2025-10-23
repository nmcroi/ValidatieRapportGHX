# 🚀 CLAUDE CODE PROMPT LIBRARY

## 🎯 **DOEL**

**Eén copy-paste prompt = Volledige implementatie**

In plaats van elke keer uitzoeken wat er moet gebeuren, gewoon de juiste prompt invullen en Claude Code doet automatisch alle benodigde stappen correct.

---

## 📋 **BESCHIKBARE PROMPTS**

### 🆕 **[NIEUWE_KOLOM_TOEVOEGEN.md](NIEUWE_KOLOM_TOEVOEGEN.md)**
Voor het toevoegen van nieuwe kolommen aan templates
- **Gebruik:** Nieuwe template versies, extra velden
- **Automatisch:** field_validation_v20.json, header_mapping.json, TG sync
- **Vraagt:** Validatieregels, positionering, afhankelijkheden

### 🔧 **[VALIDATIEREGEL_AANPASSEN.md](VALIDATIEREGEL_AANPASSEN.md)**
Voor het wijzigen van bestaande validatieregels
- **Gebruik:** Strengere/soepelere validatie, nieuwe checks
- **Automatisch:** Regel update, foutcode beheer, impact analyse
- **Vraagt:** Specificaties nieuwe regel, backward compatibility

### 🔍 **[FOUT_DEBUGGEN.md](VALIDATIEREGEL_AANPASSEN.md#-claude-code-prompt-fout-debuggen)**
Voor het oplossen van validatie problemen
- **Gebruik:** Onverwacht gedrag, foutmeldingen, configuratie issues
- **Automatisch:** Config check, mapping conflicts, template type analyse
- **Vraagt:** Reproductie stappen, verwacht vs actueel gedrag

### ⚙️ **[FOUTCODE_BEHEER.md](VALIDATIEREGEL_AANPASSEN.md#️-claude-code-prompt-foutcode-beheer)**
Voor het beheren van foutcodes en beschrijvingen
- **Gebruik:** Nieuwe foutcodes, tekst wijzigingen, reorganisatie
- **Automatisch:** Code toewijzing, categorisatie, consistentie check
- **Vraagt:** Type fout (error/correction/flag), scope

---

## 🎮 **HOE TE GEBRUIKEN**

### **Stap 1: Kies juiste prompt**
```
- Nieuwe kolom toevoegen? → NIEUWE_KOLOM_TOEVOEGEN.md
- Validatie aanpassen? → VALIDATIEREGEL_AANPASSEN.md  
- Probleem oplossen? → FOUT_DEBUGGEN.md
- Foutcode wijzigen? → FOUTCODE_BEHEER.md
```

### **Stap 2: Vul template in**
```
Open de .md file → Copy het invul-template → Vul jouw gegevens in
```

### **Stap 3: Paste in Claude Code**
```
Plak de ingevulde prompt → Claude Code doet automatisch alle stappen
```

### **Stap 4: Verificatie** 
```
Claude Code test automatisch en rapporteert resultaat
```

---

## 💡 **VOORBEELD WORKFLOW**

**Scenario:** H-zinnen kolom toevoegen

**Voorheen:** 
```
Niels: "Kun je H-zinnen toevoegen?"
Claude: "Waar moet het komen? Welke validaties?"
Niels: "Na ADR, H + 3 cijfers format"
Claude: "Ik update field_validation... oh wacht ook header_mapping..."
Niels: "En de Template Generator Files?"
Claude: "Oh ja, en de fallback lijsten? En..."
→ 45 minuten, veel heen-en-weer
```

**Nu:**
```
Niels: [copy-paste NIEUWE_KOLOM_TOEVOEGEN.md template met H-zinnen details]
Claude: "✅ H-zinnen toegevoegd op kolom BK met 3 validatieregels. JSON syntax correct. Template Generator sync niet nodig."
→ 5 minuten, geen vergeten stappen
```

---

## 🔮 **TOEKOMSTIGE UITBREIDINGEN**

Potentiële nieuwe prompts:
- **TEMPLATE_VERSIE_UPGRADE** - Voor complete template upgrades
- **BATCH_KOLOMMEN_TOEVOEGEN** - Voor meerdere kolommen tegelijk  
- **VALIDATIE_RAPPORT_ANALYSE** - Voor rapport problemen
- **PERFORMANCE_OPTIMALISATIE** - Voor speed improvements
- **BACKUP_RESTORE** - Voor configuratie herstel

---

## 📚 **REFERENTIES**

**Onderliggende handleidingen:**
- `../Workflow/WORKFLOW_KOLOMNAAM_WIJZIGINGEN.md` - Complete technische workflow
- `../Configuratie/Handleiding_JSON.md` - JSON configuratie details
- `../../Template Generator Files/Archief/WORKFLOW_NIEUWE_KOLOM.md` - TG specifieke stappen

**Verschil:**
- **Handleidingen** = Complete technische documentatie voor begrip
- **Prompts** = Ready-to-use templates voor snelle executie

---

**🎯 Het doel: Over een jaar weet Claude Code nog steeds precies wat te doen, zonder dat jij de details hoeft te onthouden!**