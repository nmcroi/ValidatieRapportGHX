#!/bin/bash
# export_chat.sh - Automatische chat export met metadata
# Gebruik: ./export_chat.sh "Onderwerp" "Status" ["Extra_Info"]

set -e

# Configuratie
CHAT_DIR="$(dirname "$0")/../Chats"
TEMPLATES_DIR="$(dirname "$0")/../Templates"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H%M)
MONTH_DIR="${CHAT_DIR}/$(date +%Y-%m)"

# Input parameters
ONDERWERP="$1"
STATUS="$2"
EXTRA_INFO="$3"

# Validatie
if [ -z "$ONDERWERP" ] || [ -z "$STATUS" ]; then
    echo "❌ Gebruik: $0 \"Onderwerp\" \"Status\" [\"Extra_Info\"]"
    echo ""
    echo "Status opties:"
    echo "  - Completed"
    echo "  - InProgress" 
    echo "  - Planning"
    echo "  - Debugging"
    echo "  - Research"
    echo ""
    echo "Voorbeelden:"
    echo "  $0 \"Quick_Mode_Fix\" \"Completed\""
    echo "  $0 \"Medical_Validation\" \"Planning\" \"UNSPSC_42xxx\""
    exit 1
fi

# Maak month directory als het niet bestaat
mkdir -p "$MONTH_DIR"

# Generate filename
SAFE_ONDERWERP=$(echo "$ONDERWERP" | tr ' ' '_' | tr -cd '[:alnum:]_-')
SAFE_STATUS=$(echo "$STATUS" | tr ' ' '_' | tr -cd '[:alnum:]_-')

if [ -n "$EXTRA_INFO" ]; then
    SAFE_EXTRA=$(echo "$EXTRA_INFO" | tr ' ' '_' | tr -cd '[:alnum:]_-')
    FILENAME="${DATE}_${TIME}_${SAFE_ONDERWERP}_${SAFE_STATUS}_${SAFE_EXTRA}.md"
else
    FILENAME="${DATE}_${TIME}_${SAFE_ONDERWERP}_${SAFE_STATUS}.md"
fi

FILEPATH="${MONTH_DIR}/${FILENAME}"

echo "📝 Creating chat export: $FILENAME"

# Template laden als bestaat
TEMPLATE_FILE="${TEMPLATES_DIR}/chat_template.md"
if [ -f "$TEMPLATE_FILE" ]; then
    cp "$TEMPLATE_FILE" "$FILEPATH"
    echo "✅ Template loaded"
else
    # Basis template maken
    cat > "$FILEPATH" << EOF
# Claude Code Chat - $DATE: $ONDERWERP

**Datum:** $DATE  
**Tijd:** $(date +%H:%M)  
**Sessie:** $ONDERWERP  
**Status:** $STATUS

## 🎯 Doelstellingen

- [ ] 

## 📋 Samenvatting

### Hoofdonderwerpen


### Resultaten


## 📁 Bestanden Gewijzigd

- \`\` - 

## 🚀 Git Commits

- \`\`: 

## 🧪 Verificatie & Testing


## 🔮 Volgende Stappen


## 📝 Technische Details

\`\`\`python
# Code snippets
\`\`\`

---

**Session Status:** $STATUS  
**Follow-up Required:** $([ "$STATUS" = "InProgress" ] && echo "Yes" || echo "No")
EOF
fi

# Metadata toevoegen aan begin van bestand
TEMP_FILE=$(mktemp)
cat > "$TEMP_FILE" << EOF
---
datum: $DATE
tijd: $(date +%H:%M)
onderwerp: $ONDERWERP
status: $STATUS
extra_info: ${EXTRA_INFO:-""}
tags: [$(echo $ONDERWERP | tr '[:upper:]' '[:lower:]' | tr '_' '-')]
commits: []
bestanden_gewijzigd: []
follow_up_needed: $([ "$STATUS" = "InProgress" ] && echo "true" || echo "false")
---

EOF

# Voeg originele content toe
cat "$FILEPATH" >> "$TEMP_FILE"
mv "$TEMP_FILE" "$FILEPATH"

echo "✅ Chat export created: $FILEPATH"
echo ""
echo "🔧 Volgende stappen:"
echo "1. Edit de chat: code '$FILEPATH'"
echo "2. Update index: ./update_index.sh"
echo "3. Commit: git add . && git commit -m '📝 Chat: $ONDERWERP'"
echo ""

# Open in editor als beschikbaar
if command -v code >/dev/null 2>&1; then
    read -p "📝 Open in VS Code? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        code "$FILEPATH"
    fi
fi