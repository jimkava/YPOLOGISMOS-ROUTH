# 🚀 QUICK START - Routh-Hurwitz Calculator

## ✅ Ο Server Τρέχει Τώρα!

```
✓ Metro Bundler: RUNNING
✓ Server URL: http://localhost:8081
```

---

## 📱 Τρόποι να Δοκιμάσεις την Εφαρμογή

### **Επιλογή 1: Web Browser (Συνιστάται για πρώτη δοκιμή)**

Σε νέο terminal:
```bash
cd /home/user/YPOLOGISMOS-ROUTH
npx expo start --web --offline
```

Ή άνοιξε: http://localhost:19006

---

### **Επιλογή 2: Expo Go App (Πραγματικό Κινητό)**

1. **Κατέβασε το Expo Go:**
   - 📱 iOS: https://apps.apple.com/app/expo-go/id982107779
   - 🤖 Android: https://play.google.com/store/apps/details?id=host.exp.exponent

2. **Σάρωσε το QR code** που εμφανίζεται στο terminal

3. **Βεβαιώσου** ότι το κινητό και ο υπολογιστής είναι στο ίδιο WiFi

---

### **Επιλογή 3: Android Emulator**

```bash
# Στο terminal που τρέχει ο Expo server
# Πάτησε: a
```

---

### **Επιλογή 4: iOS Simulator (Mac only)**

```bash
# Στο terminal που τρέχει ο Expo server
# Πάτησε: i
```

---

## 🧪 Δοκιμαστικά Παραδείγματα

### Παράδειγμα 1: ΧΕ 3ου Βαθμού (ΕΥΣΤΑΘΕΣ)
```
a3 = 1
a2 = 2
a1 = 3
K = 5
```
**Αναμενόμενο:** Σύστημα ΕΥΣΤΑΘΕΣ με Κκρ = 6.00

---

### Παράδειγμα 2: ΧΕ 2ου Βαθμού (ΕΥΣΤΑΘΕΣ)
```
a2 = 1
a1 = 2
K = 3
```
**Αναμενόμενο:** Σύστημα ΕΥΣΤΑΘΕΣ

---

### Παράδειγμα 3: ΧΕ 4ου Βαθμού
```
a4 = 1
a3 = 3
a2 = 3
a1 = 2
K = 1
```

---

## 🎯 Πώς να Χρησιμοποιήσεις την Εφαρμογή

1. **Επίλεξε τον βαθμό** της χαρακτηριστικής εξίσωσης (1-6)
2. **Εισάγαγε τους συντελεστές** (a1, a2, κλπ.)
3. **Δες την εξίσωση** σε real-time
4. **Εισάγαγε την τιμή K**
5. **Πάτησε ΥΠΟΛΟΓΙΣΜΟΣ**
6. **Δες τα αποτελέσματα:**
   - ✅ Πίνακας Routh
   - ✅ Κατάσταση Σταθερότητας
   - ✅ Κρίσιμες Τιμές (Κκρ, ωκρ)

---

## 🛠️ Χρήσιμες Εντολές

### Επανεκκίνηση Server:
```bash
./run.sh
```

### Καθαρισμός Cache:
```bash
npx expo start -c --offline
```

### Έλεγχος Status:
```bash
curl http://localhost:8081/status
```

---

## 🐛 Αντιμετώπιση Προβλημάτων

### "Cannot connect to Metro Bundler"
```bash
# Σταμάτησε και ξανάρχισε τον server
pkill -f expo
./run.sh
```

### "Module not found"
```bash
# Reinstall dependencies
rm -rf node_modules
npm install
```

### "Port 8081 already in use"
```bash
# Kill process on port 8081
lsof -ti:8081 | xargs kill -9
./run.sh
```

---

## 📚 Περισσότερα

- **README.md** - Πλήρης τεκμηρίωση
- **SETUP_INSTRUCTIONS.md** - Λεπτομερείς οδηγίες setup
- **main.py** - Original Python implementation

---

## ✨ Features

✅ Cross-platform (iOS & Android)
✅ Ελληνική γλώσσα
✅ Real-time equation preview
✅ Πλήρης πίνακας Routh
✅ Κρίσιμες τιμές (Κκρ, ωκρ)
✅ Όμορφο UI με χρωματική διαφοροποίηση
✅ Validation όλων των inputs

---

**Καλή επιτυχία με τους υπολογισμούς σου! 🎉**
