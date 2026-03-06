import streamlit as st
import control as ct
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Ρυθμίσεις Σελίδας
st.set_page_config(page_title="Routh & Root Locus Tool", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; background-color: #27ae60; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎛️ Ανάλυση Ευστάθειας & Γεωμετρικός Τόπος Ριζών")
st.subheader("ΔΗΜΗΤΡΙΟΣ ΚΑΒΑΛΙΕΡΟΣ MSc. ΗΛΕΚΤΡΟΛΟΓΟΣ ΜΗΧΑΝΙΚΟΣ")

# --- SIDEBAR: ΕΙΣΑΓΩΓΗ ΔΕΔΟΜΕΝΩΝ ---
st.sidebar.header("⚙️ Παράμετροι Συστήματος")
n = st.sidebar.selectbox("Επιλέξτε Βαθμό ΧΕ (n):", [1, 2, 3, 4, 5, 6], index=2)

coeffs = []
st.sidebar.write("Εισάγετε τους συντελεστές $a_n, a_{n-1}, \dots, a_1$:")
for i in range(n, 0, -1):
    val = st.sidebar.number_input(f"Συντελεστής a{i} (s^{i})", value=1.0, key=f"a{i}")
    coeffs.append(val)

# --- ΚΥΡΙΟΣ ΥΠΟΛΟΓΙΣΜΟΣ ---
if st.sidebar.button("ΕΚΤΕΛΕΣΗ ΑΝΑΛΥΣΗΣ"):
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.header("📋 Πίνακας Routh")
        
        # 1. Εύρεση Κρίσιμου Κ (Kkp) με σάρωση
        # Ψάχνουμε την τιμή του K που κάνει το πρώτο στοιχείο της s^1 σειράς μηδέν
        def find_critical_k(n, coeffs_list):
            if n < 2: return None
            test_ks = np.linspace(0.01, 2000, 5000) # Ψάχνει K από 0 έως 2000
            for k in test_ks:
                # Κατασκευή πίνακα Routh για το συγκεκριμένο k
                full_c = coeffs_list + [k]
                rows, cols = n + 1, (n // 2) + 1
                r_mat = np.zeros((rows, cols))
                for idx, c_val in enumerate(full_c):
                    r_mat[idx % 2, idx // 2] = c_val
                
                for r in range(2, rows):
                    for c in range(cols - 1):
                        if r_mat[r-1, 0] == 0: r_mat[r-1, 0] = 1e-5
                        r_mat[r, c] = (r_mat[r-1, 0] * r_mat[r-2, c+1] - r_mat[r-2, 0] * r_mat[r-1, c+1]) / r_mat[r-1, 0]
                
                # Αν το s^1 (προτελευταία σειρά) μηδενιστεί, βρήκαμε το K_kp
                if r_mat[n-1, 0] <= 0.05:
                    return k, r_mat
            return None, None

        kkp, final_matrix = find_critical_k(n, coeffs)

        if kkp:
            st.success(f"✅ **Κρίσιμο Κ (Kκρ): {kkp:.2f}**")
            
            # Εμφάνιση Πίνακα Routh (ως DataFrame)
            row_names = [f"s^{n-i}" for i in range(n+1)]
            df = pd.DataFrame(final_matrix, index=row_names)
            st.table(df.style.format("{:.2f}"))
            
            # Υπολογισμός ωκρ από τη βοηθητική εξίσωση (σειρά s^2)
            # A(s) = a*s^2 + b = 0 -> w = sqrt(b/a)
            try:
                a_aux = final_matrix[n-2, 0]
                b_aux = final_matrix[n-2, 1]
                wkp = np.sqrt(abs(b_aux / a_aux))
                st.info(f"🔊 **Συχνότητα Ταλάντωσης (ωκρ): {wkp:.2f} rad/s**")
            except:
                st.write("Δεν ήταν δυνατός ο υπολογισμός του ωκρ.")
        else:
            st.warning("⚠️ Δεν βρέθηκε σημείο οριακής ευστάθειας για K < 2000.")
            # Δείξε τον πίνακα για K=1
            full_c = coeffs + [1.0]
            rows, cols = n + 1, (n // 2) + 1
            r_mat = np.zeros((rows, cols))
            for idx, c_val in enumerate(full_c): r_mat[idx % 2, idx // 2] = c_val
            for r in range(2, rows):
                for c in range(cols - 1):
                    if r_mat[r-1, 0] == 0: r_mat[r-1, 0] = 1e-5
                    r_mat[r, c] = (r_mat[r-1, 0] * r_mat[r-2, c+1] - r_mat[r-2, 0] * r_mat[r-1, c+1]) / r_mat[r-1, 0]
            st.table(pd.DataFrame(r_mat, index=[f"s^{n-i}" for i in range(n+1)]))

    with col2:
        st.header("📈 Γεωμετρικός Τόπος Ριζών")
        
        # G(s) = 1 / (an*s^n + ... + a1*s)
        num = [1.0]
        den = coeffs + [0.0]
        sys = ct.TransferFunction(num, den)
        
        fig, ax = plt.subplots(figsize=(7, 6))
        ct.root_locus(sys, grid=True, ax=ax)
        ax.set_title("Root Locus Plot", fontsize=12)
        
        # Αν έχουμε Kkp, σημείωσε το πάνω στον άξονα
        if kkp:
            ax.plot(0, wkp, 'ro', markersize=8, label="Οριακή Ευστάθεια")
            ax.plot(0, -wkp, 'ro', markersize=8)
            ax.legend()

        st.pyplot(fig)

st.divider()
st.caption("© 2026 Δημήτριος Καβαλιέρος - Συστήματα Αυτομάτου Ελέγχου")
