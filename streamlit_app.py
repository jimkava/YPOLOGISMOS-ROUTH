import streamlit as st
import control as ct
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Control Systems Suite", layout="wide")

st.title("🚀 Advanced Control Systems Analysis")
st.subheader("DIMITRIOS KAVALIEROS\n Electrical Engineering & Informatics M.Sc. M.Ed. ")

# --- SIDEBAR: INPUT PARAMETERS ---
st.sidebar.header("⚙️ System Parameters")
n = st.sidebar.selectbox("Select System Degree (n):", [1, 2, 3, 4, 5, 6], index=2)

coeffs = []
st.sidebar.write(f"Enter coefficients for: $a_{n}s^{n} + \dots + a_1s + K = 0$")
for i in range(n, 0, -1):
    val = st.sidebar.number_input(f"Coefficient a{i} (s^{i})", value=1.0, key=f"a{i}")
    coeffs.append(val)

# --- ANALYSIS EXECUTION ---
if st.sidebar.button("RUN FULL ANALYSIS"):
    # Define Transfer Function
    num = [1.0]
    den = coeffs + [0.0]
    sys = ct.TransferFunction(num, den)

    # Tabs for different plots
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Routh Table", "Root Locus", "Bode Plot", "Nyquist Plot", "Nichols Chart"])

    with tab1:
        st.header("📋 Routh-Hurwitz Stability Table")
        
        def find_stability(n_deg, c_list):
            test_ks = np.linspace(0.01, 5000, 10000)
            for k in test_ks:
                full_poly = c_list + [k]
                rows, cols = n_deg + 1, (n_deg // 2) + 1
                r_mat = np.zeros((rows, cols))
                for idx, c_val in enumerate(full_poly): r_mat[idx % 2, idx // 2] = c_val
                for r in range(2, rows):
                    for c in range(cols - 1):
                        if r_mat[r-1, 0] == 0: r_mat[r-1, 0] = 1e-5
                        r_mat[r, c] = (r_mat[r-1, 0] * r_mat[r-2, c+1] - r_mat[r-2, 0] * r_mat[r-1, c+1]) / r_mat[r-1, 0]
                if r_mat[n_deg-1, 0] <= 0.01: return k, r_mat
            return None, None

        k_cr, final_matrix = find_stability(n, coeffs)
        if k_cr:
            st.success(f"✅ **Critical Gain ($K_{{cr}}$): {k_cr:.2f}**")
            df = pd.DataFrame(final_matrix, index=[f"s^{n-i}" for i in range(n+1)])
            st.table(df.style.format("{:.2f}"))
        else:
            st.warning("No stability limit found for K < 5000.")

    with tab2:
        st.header("📈 Root Locus")
        fig, ax = plt.subplots(figsize=(8, 5))
        ct.root_locus(sys, grid=True, ax=ax)
        st.pyplot(fig)

    with tab3:
        st.header("📊 Bode Diagram")
        fig = plt.figure(figsize=(8, 6))
        ct.bode_plot(sys, dB=True, Hz=True, grid=True)
        st.pyplot(plt.gcf())

    with tab4:
        st.header("🌀 Nyquist (Polar) Plot")
        fig, ax = plt.subplots(figsize=(7, 6))
        ct.nyquist_plot(sys, ax=ax)
        ax.set_title("Nyquist Plot")
        st.pyplot(fig)

    with tab5:
        st.header("📉 Nichols Chart")
        fig = plt.figure(figsize=(8, 6))
        ct.nichols_plot(sys, grid=True)
        st.pyplot(plt.gcf())

st.divider()
st.caption("© 2026 Dimitrios Kavalieros MSc. - Professional Control Engineering Tool")

