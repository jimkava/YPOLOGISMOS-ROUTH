import streamlit as st
import control as ct
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.set_page_config(page_title="Routh & Root Locus Tool", layout="wide")

st.title("🎛️ Ανάλυση Ευστάθειας Routh & Root Locus")
st.subheader("ΔΗΜΗΤΡΙΟΣ ΚΑΒΑΛΙΕΡΟΣ MSc. ΗΛΕΚΤΡΟΛΟΓΟΣ ΜΗΧΑΝΙΚΟΣ")

# --- Sidebar Εισαγωγής ---
st.sidebar.header("Παράμετροι Συστήματος")
n = st.sidebar.number_input("Βαθμός Χαρακτηριστικής Εξίσωσης (n)", min_value=1, max_value=6, value=3)

st.sidebar.write(f"Εισάγετε τους συντελεστές για το πολυώνυμο:")
st.sidebar.latex(f"a_{n}s^{n} + a_{{n-1}}s^{{n-1}} + \dots + a_1s + K = 0")

coeffs_input = []
for i in range(n, 0, -1):
    val = st.sidebar.number_input(f"Συντελεστής a{i}", value=1.0, key=f"a{i}")
    coeffs_input.append(val)

# --- Κύριο Μέρος Υπολογισμών ---
if st.sidebar.button("ΕΚΤΕΛΕΣΗ ΑΝΑΛΥΣΗΣ"):
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.write("### 📋 Πίνακας Routh")
        
        # Προετοιμασία πίνακα Routh
        num_rows = n + 1
        num_cols = (n // 2) + 1
        matrix = np.zeros((num_rows, num_cols))
        
        # Γέμισμα πρώτων δύο γραμμών
        # Η πρώτη γραμμή παίρνει a_n, a_n-2...
        # Η δεύτερη γραμμή παίρνει a_n-1, a_n-3... (και το K στο τέλος)
        
        all_coeffs = coeffs_input + [1.0] # Το 1.0 αντιπροσωπεύει το 'K' για τους υπολογισμούς
        
        for i, val in enumerate(all_coeffs):
            row = i % 2
            col = i // 2
            if col < num_cols:
                matrix[row, col] = val

        # Υπολογισμός υπόλοιπων γραμμών (Routh Algorithm)
        stable_flag = True
        for i in range(2, num_rows):
            for j in range(num_cols - 1):
                # Ορίζουσα: (m21*m12 - m11*m22) / m21
                m11, m12 = matrix[i-2, 0], matrix[i-2, j+1]
                m21, m22 = matrix[i-1, 0], matrix[i-1, j+1]
                
                if m21 == 0:
                    matrix[i, j] = 0.0001 # Μικρή τιμή αντί για μηδέν για αποφυγή σφάλματος
                else:
                    matrix[i, j] = (m21 * m12 - m11 * m22) / m21

        # Μετατροπή σε DataFrame για όμορφη εμφάνιση
        row_labels = [f"s^{n-i}" for i in range(num_rows)]
        df = pd.DataFrame(matrix, index=row_labels)
        
        # Εμφάνιση του πίνακα με format 2 δεκαδικών
        st.table(df.style.format("{:.2f}"))

        # Έλεγχος Ευστάθειας (1η στήλη)
        first_col = matrix[:, 0]
        if np.all(first_col > 0) or np.all(first_col < 0):
            st.success("✅ Το σύστημα είναι ΕΥΣΤΑΘΕΣ (Δεν υπάρχουν αλλαγές προσήμου στην 1η στήλη).")
        else:
            changes = np.count_nonzero(np.diff(np.sign(first_col)))
            st.error(f"❌ Το σύστημα είναι ΑΣΤΑΘΕΣ. Βρέθηκαν {changes} αλλαγές προσήμου.")

    with col2:
        st.write("### 📈 Γεωμετρικός Τόπος Ριζών (Root Locus)")
        
        # Συνάρτηση Μεταφοράς: G(s) = 1 / (an*s^n + ... + a1*s)
        # Ο παρονομαστής έχει ένα 0 στο τέλος γιατί το σταθερό K είναι στον αριθμητή
        den = coeffs_input + [0.0]
        sys = ct.TransferFunction([1], den)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ct.root_locus(sys, grid=True, ax=ax)
        ax.set_title("Root Locus Diagram")
        st.pyplot(fig)
        
        st.info("Σημείωση: Ο ΓΤΡ δείχνει πώς μετακινούνται οι πόλοι καθώς το K αυξάνεται από 0 έως άπειρο.")
