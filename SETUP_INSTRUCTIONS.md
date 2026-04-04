# Οδηγίες Εγκατάστασης και Εκτέλεσης

## Προαπαιτούμενα

Πριν ξεκινήσετε, βεβαιωθείτε ότι έχετε εγκατεστημένα:

1. **Node.js** (έκδοση 14 ή νεότερη)
   - Λήψη από: https://nodejs.org/
   - Επαλήθευση: `node --version`

2. **npm** (συνήθως εγκαθίσταται με το Node.js)
   - Επαλήθευση: `npm --version`

3. **Expo Go app** στο κινητό σας
   - iOS: https://apps.apple.com/app/expo-go/id982107779
   - Android: https://play.google.com/store/apps/details?id=host.exp.exponent

## Βήμα 1: Εγκατάσταση Dependencies

Ανοίξτε το terminal στο directory του project και εκτελέστε:

```bash
npm install
```

Αυτό θα εγκαταστήσει όλες τις απαραίτητες βιβλιοθήκες.

## Βήμα 2: Εκκίνηση του Development Server

```bash
npm start
```

ή

```bash
npx expo start
```

Θα εμφανιστεί ένα QR code στο terminal.

## Βήμα 3: Άνοιγμα της Εφαρμογής

### Σε πραγματική συσκευή:

1. Ανοίξτε την εφαρμογή **Expo Go** στο κινητό σας
2. Σαρώστε το QR code που εμφανίστηκε στο terminal
   - iOS: Χρησιμοποιήστε την κάμερα
   - Android: Χρησιμοποιήστε το Expo Go app

### Σε Emulator/Simulator:

- **Android**: Πατήστε `a` στο terminal
- **iOS**: Πατήστε `i` στο terminal
- **Web Browser**: Πατήστε `w` στο terminal

## Λύση Προβλημάτων

### Πρόβλημα: "Metro bundler error"

```bash
# Καθαρισμός cache
npx expo start -c
```

### Πρόβλημα: "Dependencies mismatch"

```bash
# Διαγραφή node_modules και reinstall
rm -rf node_modules
npm install
```

### Πρόβλημα: Το QR code δεν σαρώνεται

- Βεβαιωθείτε ότι το κινητό και ο υπολογιστής είναι στο ίδιο WiFi network
- Δοκιμάστε να πατήσετε "Tunnel" αντί για "LAN" στο Expo Dev Tools

## Δοκιμή της Εφαρμογής

1. Στην αρχική οθόνη, επιλέξτε τον βαθμό της χαρακτηριστικής εξίσωσης (π.χ. "ΧΕ 3ου ΒΑΘΜΟΥ")
2. Εισάγετε τους συντελεστές (π.χ. a3=1, a2=2, a1=3)
3. Εισάγετε την τιμή K (π.χ. K=5)
4. Πατήστε "ΥΠΟΛΟΓΙΣΜΟΣ"
5. Δείτε τα αποτελέσματα με τον πίνακα Routh και την ανάλυση σταθερότητας

## Παράδειγμα Δοκιμής - ΧΕ 3ου Βαθμού

```
a3 = 1
a2 = 2
a1 = 3
K = 5
```

Η εφαρμογή θα υπολογίσει:
- Τον πίνακα Routh
- Την κρίσιμη τιμή Κκρ
- Την κρίσιμη συχνότητα ωκρ
- Αν το σύστημα είναι ευσταθές

## Build για Production

### Android APK:

```bash
npx eas build --platform android --profile preview
```

### iOS (απαιτεί Apple Developer Account):

```bash
npx eas build --platform ios --profile preview
```

Για περισσότερες πληροφορίες: https://docs.expo.dev/build/setup/

## Επιπλέον Πόροι

- Expo Documentation: https://docs.expo.dev/
- React Native Documentation: https://reactnative.dev/
- React Navigation: https://reactnavigation.org/

## Υποστήριξη

Για ερωτήσεις ή προβλήματα, ανοίξτε ένα issue στο GitHub repository.
