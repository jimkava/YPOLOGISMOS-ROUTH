import streamlit as st
import control as ct
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math

st.set_page_config(page_title="Routh-Hurwitz Stability Analysis", layout="wide")

st.title("🎛️ Ανάλυση Ευστάθειας: $K_{kp}$ & $\omega_{kp}$")
st.subheader("ΔΗΜΗΤΡΙΟΣ ΚΑΒΑΛΙΕΡΟΣ MSc. ΗΛΕΚΤΡΟΛΟΓΟΣ ΜΗΧΑΝΙΚΟΣ")

# --- Sidebar ---
st.sidebar.header("Συντελεστές ΧΕ")
n = st.sidebar.number_input("Βαθμός n", min_value=1, max_value=6, value=3)

coeffs_input = []
for i in range(n, 0, -1):
    val = st.sidebar.number_input(f"a{i} (s^{i})", value=1.0)
    coeffs_input.append(val)

if st.sidebar.button("ΥΠΟΛΟΓΙΣΜΟΣ"):
    col1, col2 = st.columns([1, 1])

    with col1:
        st.write("### 📋 Πίνακας Routh (για οριακή ευστάθεια)")
        
        # Συνάρτηση που χτίζει τον πίνακα Routh για ένα συγκεκριμένο K
        def get_routh_matrix(n, coeffs, K):
            all_c = coeffs + [K]
            num_rows = n + 1
            num_cols = (n // 2) + 1
            res = np.zeros((num_rows, num_cols))
            for i, val in enumerate(all_c):
                res[i % 2, i // 2] = val
            for i in range(2, num_rows):
                for j in range(num_cols - 1):
                    if res[i-1, 0] == 0: res[i-1, 0] = 1e-9
                    res[i, j] = (res[i-1, 0] * res[i-2, j+1] - res[i-2, 0] * res[i-1, j+1]) / res[i-1, 0]
            return res

        # Εύρεση K_kp με σάρωση (Root Finding)
        # Ψάχνουμε την τιμή του K που μηδενίζει το στοιχείο s^1, στήλη 1
        def find_kkr(n, coeffs):
            if n < 2: return None
            ks = np.linspace(0, 1000, 10000) # Σάρωση από 0 έως 1000
            for k in ks:
                m = get_routh_matrix(n, coeffs, k)
                if m[n-1, 0] <= 0: return k
            return None

        kkr = find_kkr(n, coeffs_input)
        
        # Εμφάνιση πίνακα για το K_kp (ή για K=1 αν δεν βρέθηκε)
        disp_k = kkr if kkr else 1.0
        final_m = get_routh_matrix(n, coeffs_input, disp_k)
        df = pd.DataFrame(final_m, index=[f"s^{n-i}" for i in range(n+1)])
        st.table(df.style.format("{:.2f}"))

        if kkr:
            st.success(f"✅ **Κρίσιμο Κ (Kκρ): {kkr:.2f}**")
            # Υπολογισμός ω_kp από τη βοηθητική εξίσωση (γραμμή s^2)
            # A(s) = m[n-2, 0]*s^2 + m[n-2, 1] = 0 => w = sqrt(m2/m1)
            row_aux = n - 2
            if final_m[row_aux, 0] != 0:
                wkr = math.sqrt(abs(final_m[row_aux, 1] / final_m[row_aux, 0]))
                st.info(f"🔊 **Συχνότητα Ταλάντωσης (ωκρ): {wkr:.2f} rad/s**")
                st.latex(f"\\omega_{{kp}} = \\sqrt{{\\frac{{{final_m[row_aux, 1]:.2f}}}{{{final_m[row_aux, 0]:.2f}}}}} = {wkr:.2f}")
        else:
            st.warning("Το σύστημα δεν παρουσιάζει οριακή ευστάθεια για K > 0 ή το Kκρ είναι πολύ μεγάλο.")

    with col2:
        st.write("### 📈 Γεωμετρικός Τόπος Ριζών")
        sys = ct.TransferFunction([1], coeffs_input + [0])
        fig, ax = plt.subplots()
        ct.root_locus(sys, grid=True, ax=ax)
        if kkr:
            ax.plot(0, wkr, 'ro', label='Οριακή Ευστάθεια')
            ax.plot(0, -wkr, 'ro')
        st.pyplot(fig)
