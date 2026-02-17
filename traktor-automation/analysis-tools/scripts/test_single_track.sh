#!/bin/bash
#
# Test Hybrid Analyzer on a Single Track
# =======================================
#
# Quick test script to run hybrid analysis on one track from the
# "Best of Deep Dub Tech House" collection.
#
# Usage:
#   ./test_single_track.sh "track_name.m4a" "stripes_hash"
#
# Example:
#   ./test_single_track.sh "Dreams.m4a" "A2ODYSAZ0WSBEBBVFNHUBQ5QHMCD"

set -e

# Configuration
MUSIC_DIR="/Volumes/TRAKTOR/Traktor/Music/2026/Best of Deep Dub Tech House"
STRIPES_BASE="/Users/dantaylor/Documents/Native Instruments/Traktor 3.11.1/Stripes"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <track_name> <stripes_hash>"
    echo ""
    echo "Example:"
    echo "  $0 \"Dreams.m4a\" \"A2ODYSAZ0WSBEBBVFNHUBQ5QHMCD\""
    echo ""
    echo "Available tracks:"
    ls -1 "$MUSIC_DIR" | grep -E '\.(m4a|mp3)$' | head -10
    echo "  ..."
    echo ""
    echo "To find stripes hash:"
    echo "  1. Open Traktor"
    echo "  2. Analyze the track"
    echo "  3. Check ~/Documents/Native Instruments/Traktor 3.11.1/Stripes/"
    echo "  4. Look for recently modified files"
    exit 1
fi

TRACK_NAME="$1"
STRIPES_HASH="$2"

# Build paths
AUDIO_FILE="$MUSIC_DIR/$TRACK_NAME"
STRIPES_FILE=""

# Find stripes file in subdirectories
for subdir in "$STRIPES_BASE"/{000,001,002,003,004,005,006,007,008,009}; do
    if [ -f "$subdir/$STRIPES_HASH" ]; then
        STRIPES_FILE="$subdir/$STRIPES_HASH"
        break
    fi
done

# Validate files exist
if [ ! -f "$AUDIO_FILE" ]; then
    echo "Error: Audio file not found: $AUDIO_FILE"
    exit 1
fi

if [ ! -f "$STRIPES_FILE" ]; then
    echo "Error: Stripes file not found: $STRIPES_HASH"
    echo "Searched in: $STRIPES_BASE/{000..009}/"
    exit 1
fi

echo "=================================================="
echo "TEST: Hybrid Analysis on Single Track"
echo "=================================================="
echo "Audio file: $AUDIO_FILE"
echo "Stripes file: $STRIPES_FILE"
echo "=================================================="
echo ""

# Run hybrid analyzer
python3 "$SCRIPT_DIR/hybrid_analyzer.py" "$AUDIO_FILE" "$STRIPES_FILE"

echo ""
echo "=================================================="
echo "Test complete!"
echo "=================================================="
