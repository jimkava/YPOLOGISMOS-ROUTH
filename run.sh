#!/bin/bash

echo "================================================"
echo "  ROUTH-HURWITZ CALCULATOR - MOBILE APP"
echo "================================================"
echo ""
echo "Εκκίνηση Expo Development Server..."
echo ""

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Εγκατάσταση dependencies..."
    npm install
fi

# Start expo in offline mode to avoid API issues
echo ""
echo "Server URL: http://localhost:8081"
echo ""
echo "ΕΠΙΛΟΓΕΣ:"
echo "  Πάτησε 'w' για άνοιγμα στον web browser"
echo "  Πάτησε 'a' για Android emulator"
echo "  Πάτησε 'i' για iOS simulator"
echo "  Πάτησε 'r' για reload"
echo "  Πάτησε 'q' για έξοδο"
echo ""

EXPO_OFFLINE=1 npx expo start --offline
