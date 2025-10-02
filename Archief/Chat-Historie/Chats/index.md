# 📑 Chat Index - GHX Validatie Tool

**Laatste update:** 2025-10-02 12:25  
**Totaal sessies:**        5

## 📊 Overzicht per Maand

### 📅 2025-10 (       1 sessies)

- 📝 **[Quick](./../Chats/2025-10/2025-10-02_1430_Quick_Mode_Fix_Completed.md)** - `Mode` - 2025-10-02

## 🔍 Zoeken in Chats

### Per Status
```bash
# Incomplete sessies
grep -l "InProgress" Chats/*/*.md

# Voltooide sessies  
grep -l "Completed" Chats/*/*.md

# Planning sessies
grep -l "Planning" Chats/*/*.md
```

### Per Onderwerp
```bash
# Validation gerelateerd
grep -r "validation" Chats/ --include="*.md"

# Quick Mode gerelateerd
grep -r "Quick Mode" Chats/ --include="*.md"

# Medical gerelateerd
grep -r "medical\|UNSPSC" Chats/ --include="*.md"
```

### Recente Chats
```bash
# Laatste week
find Chats/ -mtime -7 -name "*.md" | sort

# Laatste maand
find Chats/ -mtime -30 -name "*.md" | sort
```

## 📈 Statistieken

- **Totaal sessies:**        5
- **Voltooid:**        1  
- **In progress:**        1
- **Completion rate:** 20%

## 🎯 Meest Actieve Onderwerpen


---
*Index automatisch gegenereerd - do  2 okt. 2025 12:25:10 CEST*
