#!/bin/bash
# Monitor the AI DJ Controller

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              TRAKTOR AI DJ - LIVE MONITOR                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if AI DJ is running
if ps aux | grep -q "[t]raktor_ai_dj.py"; then
    PID=$(ps aux | grep "[t]raktor_ai_dj.py" | awk '{print $2}')
    echo "✅ AI DJ is running (PID: $PID)"
    echo ""
    echo "Press Ctrl+C to stop monitoring (AI DJ will keep running)"
    echo "To stop AI DJ: pkill -f traktor_ai_dj.py"
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo ""

    # Monitor log output (if we had logging to a file)
    # For now, just show it's running
    echo "AI DJ is actively controlling Traktor..."
    echo ""
    echo "Watch Traktor to see:"
    echo "  • Track 1 loading to Deck A"
    echo "  • Playback starting"
    echo "  • Automatic transitions every ~6 minutes"
    echo "  • 75-second crossfades"
    echo ""

    # Keep monitoring
    while ps -p $PID > /dev/null; do
        sleep 5
        echo "$(date '+%H:%M:%S') - AI DJ still running..."
    done

    echo ""
    echo "AI DJ has stopped."
else
    echo "❌ AI DJ is not running"
    echo ""
    echo "To start: ./START_AI_DJ.sh"
fi
