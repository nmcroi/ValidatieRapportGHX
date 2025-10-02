#!/bin/bash
# setup_aliases.sh - Setup bash aliases voor chat management
# Run: source ./setup_aliases.sh

CHAT_HISTORIE_DIR="/Users/ncroiset/Vibe Coding Projecten/Cursor Projecten/Project GHX Prijstemplate Validatie Tool/Archief/Chat-Historie"

echo "📝 Setting up Chat Historie aliases..."

# Core navigation aliases
alias chatdir="cd '$CHAT_HISTORIE_DIR'"
alias chatcd="cd '$CHAT_HISTORIE_DIR'"

# Listing aliases  
alias chatls="ls -la '$CHAT_HISTORIE_DIR/Chats/\$(date +%Y-%m)/'"
alias chatall="find '$CHAT_HISTORIE_DIR/Chats' -name '*.md' -not -name 'index.md' | sort"
alias chatrecent="find '$CHAT_HISTORIE_DIR/Chats' -mtime -7 -name '*.md' | sort"
alias chattoday="find '$CHAT_HISTORIE_DIR/Chats' -mtime -1 -name '*.md' | sort"

# Search aliases
alias chatfind="grep -r \"\$1\" '$CHAT_HISTORIE_DIR/Chats/' --include='*.md'"
alias chatgrep="grep -r \"\$1\" '$CHAT_HISTORIE_DIR/Chats/' --include='*.md'"
alias chatsearch="grep -r \"\$1\" '$CHAT_HISTORIE_DIR/Chats/' --include='*.md' -l"

# Status based searches
alias chatcompleted="find '$CHAT_HISTORIE_DIR/Chats' -name '*.md' -exec grep -l 'Completed' {} \;"
alias chatprogress="find '$CHAT_HISTORIE_DIR/Chats' -name '*.md' -exec grep -l 'InProgress' {} \;"
alias chatplanning="find '$CHAT_HISTORIE_DIR/Chats' -name '*.md' -exec grep -l 'Planning' {} \;"

# Management aliases  
alias chatnew="'$CHAT_HISTORIE_DIR/Scripts/export_chat.sh'"
alias chatindex="'$CHAT_HISTORIE_DIR/Scripts/update_index.sh'"
alias chatview="cat '$CHAT_HISTORIE_DIR/Chats/index.md'"

# Quick access functions
chatopen() {
    if [ -z "\$1" ]; then
        echo "Usage: chatopen [search_term]"
        echo "Example: chatopen 'Quick_Mode'"
        return 1
    fi
    
    local matches=\$(find '$CHAT_HISTORIE_DIR/Chats' -name "*\$1*" -type f)
    local count=\$(echo "\$matches" | wc -l)
    
    if [ \$count -eq 1 ]; then
        echo "Opening: \$matches"
        code "\$matches" 2>/dev/null || nano "\$matches"
    elif [ \$count -gt 1 ]; then
        echo "Multiple matches found:"
        echo "\$matches" | nl
        read -p "Select number (or 0 to cancel): " selection
        if [ "\$selection" -gt 0 ] && [ "\$selection" -le \$count ]; then
            local selected=\$(echo "\$matches" | sed -n "\${selection}p")
            echo "Opening: \$selected"
            code "\$selected" 2>/dev/null || nano "\$selected"
        fi
    else
        echo "No matches found for: \$1"
    fi
}

chatstats() {
    echo "📊 Chat Historie Statistics"
    echo "=========================="
    
    local total=\$(find '$CHAT_HISTORIE_DIR/Chats' -name '*.md' -not -name 'index.md' | wc -l)
    local completed=\$(find '$CHAT_HISTORIE_DIR/Chats' -name '*.md' -exec grep -l 'Completed' {} \; | wc -l)
    local inprogress=\$(find '$CHAT_HISTORIE_DIR/Chats' -name '*.md' -exec grep -l 'InProgress' {} \; | wc -l)
    local thismonth=\$(find '$CHAT_HISTORIE_DIR/Chats/\$(date +%Y-%m)' -name '*.md' 2>/dev/null | wc -l)
    
    echo "Total chats: \$total"
    echo "Completed: \$completed"  
    echo "In Progress: \$inprogress"
    echo "This month: \$thismonth"
    
    if [ \$total -gt 0 ]; then
        local completion_rate=\$((completed * 100 / total))
        echo "Completion rate: \${completion_rate}%"
    fi
}

chathelp() {
    echo "🔧 Chat Historie Management Commands"
    echo "===================================="
    echo ""
    echo "📁 Navigation:"
    echo "  chatdir     - Go to chat historie directory"
    echo "  chatls      - List current month's chats"
    echo "  chatall     - List all chats"
    echo "  chatrecent  - List recent chats (last 7 days)"
    echo "  chattoday   - List today's chats"
    echo ""
    echo "🔍 Search:"
    echo "  chatfind 'term'    - Search in chat content"
    echo "  chatsearch 'term'  - Find chats containing term"
    echo "  chatcompleted      - List completed chats"
    echo "  chatprogress       - List in-progress chats"
    echo "  chatplanning       - List planning chats"
    echo ""
    echo "🛠️ Management:"
    echo "  chatnew 'Topic' 'Status'  - Create new chat export"
    echo "  chatindex                 - Update chat index"
    echo "  chatview                  - View chat index"
    echo "  chatopen 'term'           - Open chat by search term"
    echo "  chatstats                 - Show statistics"
    echo ""
    echo "📝 Examples:"
    echo "  chatnew 'Medical_Validation' 'Planning'"
    echo "  chatopen 'Quick_Mode'"
    echo "  chatfind 'validation'"
}

echo "✅ Chat aliases loaded!"
echo "📖 Type 'chathelp' to see all available commands"