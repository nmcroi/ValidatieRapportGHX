# 💬 Chat Historie Management Systeem

**Doel:** Gestructureerde opslag en management van Claude Code chat sessies

## 📁 Mappenstructuur

```
Chat-Historie/
├── README.md                    # Dit bestand
├── Chats/                      # Alle chat exports
│   ├── 2025-10/               # Per maand georganiseerd
│   ├── templates/             # Chat export templates
│   └── index.md              # Chat index met links
├── Scripts/                   # Automation scripts
└── Templates/                # Chat export templates
```

## 🏷️ Naamgeving Conventie

### Chat Bestanden
```
YYYY-MM-DD_[Tijdstip]_[Hoofdonderwerp]_[Status].md

Voorbeelden:
- 2025-10-02_1430_Quick_Mode_Fix_Completed.md
- 2025-10-02_1600_UI_Improvements_InProgress.md
- 2025-10-03_0900_Medical_Validation_Planning.md
```

### Status Codes
- `Completed` - Sessie volledig afgerond
- `InProgress` - Sessie onderbroken, voortzetting nodig
- `Planning` - Brainstorm/planning sessie
- `Debugging` - Bug fixing sessie
- `Research` - Onderzoek en analyse

## 📊 Chat Index Systeem

### Automatische Indexering
Elke chat krijgt metadata:
```yaml
---
datum: 2025-10-02
tijd: 14:30-17:00
onderwerp: Quick Mode Validatie Fix
status: Completed
bestanden_gewijzigd:
  - validator/rapport_utils.py
  - validator/price_tool.py
commits:
  - "🔧 Quick Mode Validatie Fix + Archief Reorganisatie"
  - "🧹 Complete archief cleanup"
tags: [quick-mode, validation, fix, ui-improvement]
---
```

## 🔍 Zoek Strategieën

### 1. Per Onderwerp
```bash
# Zoek alle validation gerelateerde chats
grep -r "validation" Chats/ --include="*.md"

# Zoek specifieke fixes
grep -r "Quick Mode" Chats/ --include="*.md"
```

### 2. Per Datum Range
```bash
# Chats van deze week
find Chats/ -name "2025-10-*" -type f

# Recente chats (laatste 7 dagen)
find Chats/ -mtime -7 -name "*.md"
```

### 3. Per Status
```bash
# Incomplete sessies
grep -l "InProgress" Chats/*.md

# Completed sessies
grep -l "Completed" Chats/*.md
```

## 🤖 Automation Scripts

### Chat Export Script
```bash
#!/bin/bash
# export_chat.sh - Automatische chat export met metadata

DATUM=$(date +%Y-%m-%d)
TIJD=$(date +%H%M)
ONDERWERP="$1"
STATUS="$2"

FILENAME="Chats/${DATUM}_${TIJD}_${ONDERWERP}_${STATUS}.md"

echo "Exporting chat to: $FILENAME"
# Chat export logic hier
```

### Chat Index Update
```bash
#!/bin/bash
# update_index.sh - Update chat index automatisch

echo "# 📑 Chat Index - Updated $(date)" > Chats/index.md
echo "" >> Chats/index.md

for chat in Chats/2025-*/*.md; do
    echo "Processing: $chat"
    # Extract metadata en voeg toe aan index
done
```

## 📋 Gebruik Workflow

### 1. Start Nieuwe Chat Sessie
```bash
# Ga naar chat historie folder
cd "Archief/Chat-Historie"

# Check vorige sessies
ls -la Chats/$(date +%Y-%m)/

# Maak notitie van geplande onderwerpen
echo "$(date): Starting work on [ONDERWERP]" >> session_log.txt
```

### 2. Tijdens Chat Sessie
- Gebruik duidelijke commit messages
- Noteer belangrijke beslissingen
- Tag relevante bestanden

### 3. Chat Beëindigen
```bash
# Export chat met metadata
./Scripts/export_chat.sh "Medical_Validation" "Completed"

# Update index
./Scripts/update_index.sh

# Commit naar git
git add Archief/Chat-Historie/
git commit -m "📝 Chat archived: [ONDERWERP]"
```

## 🔗 Integratie met Git

### Chat Branches
Voor grote features:
```bash
# Maak feature branch voor complexe chats
git checkout -b feature/medical-validation-chat

# Commit chat exports per sessie
git add Archief/Chat-Historie/Chats/2025-10-03_Medical_Validation_*.md
git commit -m "💬 Chat session: Medical validation planning"
```

### Linking Chats to Commits
In commit messages:
```
🔧 Implement medical validation rules

Chat-Reference: Archief/Chat-Historie/Chats/2025-10-03_0900_Medical_Validation_Completed.md
Related-Chat-Sessions: 2025-10-02_Quick_Mode_Fix, 2025-10-03_Medical_Validation
```

## 📊 Chat Analytics

### Productivity Metrics
```bash
# Chats per maand
ls Chats/2025-10/ | wc -l

# Gemiddelde sessie lengte (gebaseerd op timestamps)
# Meest actieve onderwerpen
grep -h "tags:" Chats/*.md | sort | uniq -c | sort -nr
```

### Follow-up Tracking
```yaml
# In chat metadata
follow_up_needed: true
follow_up_date: 2025-10-05
follow_up_topics:
  - "Implement GTIN validation for medical products"
  - "Test new percentage calculations"
```

## 🎯 Quick Access Commands

### Bash Aliases (voeg toe aan ~/.bashrc)
```bash
alias chatdir='cd "/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project GHX Prijstemplate Validatie Tool/Archief/Chat-Historie"'
alias chatls='ls -la Chats/$(date +%Y-%m)/'
alias chatfind='grep -r "$1" Chats/ --include="*.md"'
alias chatrecent='find Chats/ -mtime -7 -name "*.md" | sort'
```

### VS Code Integration
```json
// .vscode/settings.json
{
  "files.associations": {
    "Archief/Chat-Historie/Chats/*.md": "markdown"
  },
  "search.exclude": {
    "**/Archief/Chat-Historie/Chats/archive/**": true
  }
}
```

---

## 🚀 Implementatie Stappen

1. **✅ Basis structuur** - README en folder setup
2. **⏳ Scripts maken** - export_chat.sh en update_index.sh  
3. **⏳ Templates** - Chat export templates
4. **⏳ Automation** - Git hooks voor auto-archiving
5. **⏳ Integration** - VS Code snippets en aliases

**Volgende stap:** Wil je dat ik de automation scripts maak?