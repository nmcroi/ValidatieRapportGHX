#!/bin/bash
# update_index.sh - Update chat index automatisch
# Genereert een overzicht van alle chat sessies

set -e

CHAT_DIR="$(dirname "$0")/../Chats"
INDEX_FILE="${CHAT_DIR}/index.md"
DATE=$(date +"%Y-%m-%d %H:%M")

echo "📑 Updating chat index..."

# Backup existing index
if [ -f "$INDEX_FILE" ]; then
    cp "$INDEX_FILE" "${INDEX_FILE}.backup"
fi

# Create new index
cat > "$INDEX_FILE" << EOF
# 📑 Chat Index - GHX Validatie Tool

**Laatste update:** $DATE  
**Totaal sessies:** $(find "$CHAT_DIR" -name "*.md" -not -name "index.md" | wc -l)

## 📊 Overzicht per Maand

EOF

# Process per month directory
for month_dir in "$CHAT_DIR"/20*/; do
    if [ -d "$month_dir" ]; then
        month=$(basename "$month_dir")
        echo "Processing month: $month"
        
        chat_count=$(find "$month_dir" -name "*.md" | wc -l)
        echo "### 📅 $month ($chat_count sessies)" >> "$INDEX_FILE"
        echo "" >> "$INDEX_FILE"
        
        # Sort chats by date
        find "$month_dir" -name "*.md" | sort | while read -r chat_file; do
            if [ -f "$chat_file" ]; then
                filename=$(basename "$chat_file" .md)
                
                # Extract metadata if available
                onderwerp=""
                status=""
                datum=""
                
                if head -20 "$chat_file" | grep -q "^onderwerp:"; then
                    onderwerp=$(grep "^onderwerp:" "$chat_file" | head -1 | cut -d: -f2- | xargs)
                    status=$(grep "^status:" "$chat_file" | head -1 | cut -d: -f2- | xargs)
                    datum=$(grep "^datum:" "$chat_file" | head -1 | cut -d: -f2- | xargs)
                fi
                
                # Fallback to filename parsing
                if [ -z "$onderwerp" ]; then
                    IFS='_' read -ra PARTS <<< "$filename"
                    if [ ${#PARTS[@]} -ge 4 ]; then
                        datum="${PARTS[0]}"
                        tijd="${PARTS[1]}"
                        onderwerp="${PARTS[2]}"
                        status="${PARTS[3]}"
                    fi
                fi
                
                # Status emoji
                case "$status" in
                    "Completed") status_emoji="✅" ;;
                    "InProgress") status_emoji="🔄" ;;
                    "Planning") status_emoji="📋" ;;
                    "Debugging") status_emoji="🐛" ;;
                    "Research") status_emoji="🔍" ;;
                    *) status_emoji="📝" ;;
                esac
                
                echo "- $status_emoji **[$onderwerp]($chat_file)** - \`$status\` - $datum" >> "$INDEX_FILE"
            fi
        done
        
        echo "" >> "$INDEX_FILE"
    fi
done

# Add search section
cat >> "$INDEX_FILE" << EOF
## 🔍 Zoeken in Chats

### Per Status
\`\`\`bash
# Incomplete sessies
grep -l "InProgress" Chats/*/*.md

# Voltooide sessies  
grep -l "Completed" Chats/*/*.md

# Planning sessies
grep -l "Planning" Chats/*/*.md
\`\`\`

### Per Onderwerp
\`\`\`bash
# Validation gerelateerd
grep -r "validation" Chats/ --include="*.md"

# Quick Mode gerelateerd
grep -r "Quick Mode" Chats/ --include="*.md"

# Medical gerelateerd
grep -r "medical\\|UNSPSC" Chats/ --include="*.md"
\`\`\`

### Recente Chats
\`\`\`bash
# Laatste week
find Chats/ -mtime -7 -name "*.md" | sort

# Laatste maand
find Chats/ -mtime -30 -name "*.md" | sort
\`\`\`

## 📈 Statistieken

EOF

# Add statistics
completed_count=$(find "$CHAT_DIR" -name "*.md" -exec grep -l "Completed" {} \; | wc -l)
inprogress_count=$(find "$CHAT_DIR" -name "*.md" -exec grep -l "InProgress" {} \; | wc -l)
total_count=$(find "$CHAT_DIR" -name "*.md" -not -name "index.md" | wc -l)

cat >> "$INDEX_FILE" << EOF
- **Totaal sessies:** $total_count
- **Voltooid:** $completed_count  
- **In progress:** $inprogress_count
- **Completion rate:** $(( completed_count * 100 / (total_count > 0 ? total_count : 1) ))%

## 🎯 Meest Actieve Onderwerpen

EOF

# Top topics
if find "$CHAT_DIR" -name "*.md" -exec grep -h "^onderwerp:" {} \; 2>/dev/null | head -1 >/dev/null 2>&1; then
    find "$CHAT_DIR" -name "*.md" -exec grep -h "^onderwerp:" {} \; 2>/dev/null | \
    cut -d: -f2- | tr '[:upper:]' '[:lower:]' | sort | uniq -c | sort -nr | head -5 | \
    while read count topic; do
        echo "- **$topic:** $count sessies" >> "$INDEX_FILE"
    done
fi

echo "" >> "$INDEX_FILE"
echo "---" >> "$INDEX_FILE"
echo "*Index automatisch gegenereerd - $(date)*" >> "$INDEX_FILE"

echo "✅ Chat index updated: $INDEX_FILE"
echo "📊 Statistics:"
echo "   - Total chats: $total_count"
echo "   - Completed: $completed_count"
echo "   - In Progress: $inprogress_count"