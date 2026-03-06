import streamlit as st
import control as ct
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Routh & Root Locus Tool", layout="wide")

st.title("🎛️ Ανάλυση Ευστάθειας Routh & Root Locus")
st.subheader("ΔΗΜΗΤΡΙΟΣ ΚΑΒΑΛΙΕΡΟΣ MSc. ΗΛΕΚΤΡΟΛΟΓΟΣ ΜΗΧΑΝΙΚΟΣ")

# Sidebar για είσοδο δεδομένων
st.sidebar.header("Παράμετροι Συστήματος")
n = st.sidebar.number_input("Βαθμός ΧΕ (1-6)", min_value=1, max_value=6, value=3)

coeffs = []
for i in range(n, 0, -1):
    val = st.sidebar.number_input(f"Συντελεστής a{i} (S^{i})", value=1.0)
    coeffs.append(val)

# Υπολογισμοί
if st.sidebar.button("ΕΚΤΕΛΕΣΗ"):
    col1, col2 = st.columns(2)

    with col1:
        st.write("### Πίνακας Routh & Ανάλυση")
        # Εδώ μπαίνει η λογική σου για τον πίνακα (print -> st.write)
        # Παράδειγμα για n=3
        if n == 3:
            a3, a2, a1 = coeffs[0], coeffs[1], coeffs[2]
            kkr = (a1 * a2) / a3
            st.code(f"S^3 | {a3:.2f}  {a1:.2f}\nS^2 | {a2:.2f}  K\nS^1 | {a1 - (a3 / a2):.2f}K")
            if kkr > 0:
                st.success(f"Ευσταθές για K < {kkr:.2f}")

    with col2:
        st.write("### Γεωμετρικός Τόπος Ριζών")
        den = coeffs + [0.0]  # Προσθήκη K
        sys = ct.TransferFunction([1], den)
        fig, ax = plt.subplots()
        ct.root_locus(sys, grid=True, ax=ax)
        st.pyplot(fig)