#!/bin/bash
# Start AI DJ for Traktor
# Make sure Traktor is running with your playlist loaded first!

cd "/Users/dantaylor/Claude/Last Night an AI Saved My Life/traktor-automation"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              STARTING TRAKTOR AI DJ CONTROLLER               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Before starting, make sure:"
echo "  ✓ Traktor is running"
echo "  ✓ Best of Deep Dub Tech House playlist is loaded"
echo "  ✓ First track is highlighted in browser"
echo ""
read -p "Ready to start? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo ""
    echo "Starting AI DJ..."
    echo "Press Ctrl+C to stop"
    echo ""
    python3 traktor_ai_dj.py
else
    echo "Cancelled."
fi
