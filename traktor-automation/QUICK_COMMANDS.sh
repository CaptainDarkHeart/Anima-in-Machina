#!/bin/bash
# TRAKTOR AI DJ - Quick Command Reference

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         TRAKTOR AI DJ - QUICK COMMANDS                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Change to traktor-automation directory
cd "/Users/dantaylor/Claude/Last Night an AI Saved My Life/traktor-automation"

echo "Available commands:"
echo ""
echo "  1. Test MIDI connection"
echo "     python3 test_midi_connection.py"
echo ""
echo "  2. Run AI DJ (full automation)"
echo "     python3 traktor_ai_dj.py"
echo ""
echo "  3. Open setup guide"
echo "     open SETUP_INSTRUCTIONS.md"
echo ""
echo "  4. Open MIDI mapping guide"
echo "     open TRAKTOR_MIDI_MAPPING_GUIDE.md"
echo ""
echo "  5. Open README"
echo "     open README.md"
echo ""
echo "  6. View playlist"
echo "     cat ../track-selection-engine/best-of-deep-dub-tech-house-ai-ordered.json | jq '.tracks[] | {artist, title, bpm, energy_level}'"
echo ""
echo "  7. Check MIDI ports"
echo "     python3 -c 'import mido; print(\"\\nMIDI Ports:\"); [print(f\"  - {p}\") for p in mido.get_output_names()]'"
echo ""
echo "  8. Open Audio MIDI Setup"
echo "     open -a \"Audio MIDI Setup\""
echo ""
echo "  9. Open Traktor"
echo "     open -a \"/Applications/Native Instruments/Traktor Pro 3/Traktor.app\""
echo ""

read -p "Enter command number (1-9) or 'q' to quit: " choice

case $choice in
    1) python3 test_midi_connection.py ;;
    2) python3 traktor_ai_dj.py ;;
    3) open SETUP_INSTRUCTIONS.md ;;
    4) open TRAKTOR_MIDI_MAPPING_GUIDE.md ;;
    5) open README.md ;;
    6) cat ../track-selection-engine/best-of-deep-dub-tech-house-ai-ordered.json | python3 -m json.tool | head -100 ;;
    7) python3 -c 'import mido; print("\nMIDI Ports:"); [print(f"  - {p}") for p in mido.get_output_names()]' ;;
    8) open -a "Audio MIDI Setup" ;;
    9) open -a "/Applications/Native Instruments/Traktor Pro 3/Traktor.app" ;;
    q|Q) echo "Goodbye!" ;;
    *) echo "Invalid choice" ;;
esac
