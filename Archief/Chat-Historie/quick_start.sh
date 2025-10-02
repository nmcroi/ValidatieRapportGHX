#!/bin/bash
# quick_start.sh - Quick setup en demo van Chat Historie systeem
# Run: ./quick_start.sh

set -e

CHAT_DIR="$(dirname "$0")"
echo "🚀 Chat Historie Management System - Quick Start"
echo "==============================================="

# 1. Load aliases
echo "📝 Loading chat aliases..."
source "$CHAT_DIR/Scripts/setup_aliases.sh"

# 2. Show current structure
echo ""
echo "📁 Current structure:"
tree "$CHAT_DIR" 2>/dev/null || find "$CHAT_DIR" -type d | sed 's|[^/]*/|  |g'

# 3. Show existing chats
echo ""
echo "💬 Existing chats:"
find "$CHAT_DIR/Chats" -name "*.md" -not -name "index.md" | sort

# 4. Show quick commands
echo ""
echo "🔧 Quick commands now available:"
echo "  chathelp     - Show all commands"
echo "  chatdir      - Go to chat directory"
echo "  chatstats    - Show statistics"
echo "  chatrecent   - List recent chats"
echo ""

# 5. Demo: Create a sample chat
echo "📝 Demo: Creating a sample chat..."
read -p "Create demo chat? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    "$CHAT_DIR/Scripts/export_chat.sh" "Chat_System_Setup" "Completed" "Demo"
    echo "✅ Demo chat created!"
fi

# 6. Update index
echo ""
echo "📑 Updating chat index..."
"$CHAT_DIR/Scripts/update_index.sh"

# 7. Show final status
echo ""
echo "✅ Chat Historie System Ready!"
echo ""
echo "📖 Next Steps:"
echo "1. Add this to your ~/.bashrc for permanent aliases:"
echo "   echo 'source \"$CHAT_DIR/Scripts/setup_aliases.sh\"' >> ~/.bashrc"
echo ""
echo "2. Start using commands:"
echo "   chathelp                                    # See all commands"
echo "   chatnew 'My_Topic' 'Planning'              # Create new chat"
echo "   chatopen 'Quick_Mode'                      # Open existing chat"
echo ""
echo "3. View the chat index:"
echo "   cat '$CHAT_DIR/Chats/index.md'"