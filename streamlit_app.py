import streamlit as st
import control as ct
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
import io

# Page Configuration
st.set_page_config(page_title="Control Systems Suite", layout="wide")

st.title("🚀 Advanced Control Systems Analysis")
st.subheader("DIMITRIOS KAVALIEROS\nElectrical Engineering & Informatics M.Sc. M.Ed.")

# --- SIDEBAR: INPUT PARAMETERS ---
st.sidebar.header("⚙️ System Parameters")
n = st.sidebar.selectbox("Select System Degree (n):", [1, 2, 3, 4, 5, 6], index=2)

coeffs = []
st.sidebar.write(f"Enter coefficients for: $a_{n}s^{n} + \dots + a_1s + K_{{user}} = 0$")
for i in range(n, 0, -1):
    val = st.sidebar.number_input(f"Coefficient a{i} (s^{i})", value=1.0, key=f"a{i}")
    coeffs.append(val)

st.sidebar.divider()
st.sidebar.header("🕹️ Interactive Control")
k_user = st.sidebar.slider("Adjust Gain (K) for Step Response:", min_value=0.1, max_value=100.0, value=1.0, step=0.1)

# Helper function to convert plot to bytes for download
def convert_plt_to_bytes(figure):
    buf = io.BytesIO()
    figure.savefig(buf, format="png", dpi=300)
    return buf.getvalue()

# --- ANALYSIS EXECUTION ---
if st.sidebar.button("RUN FULL ANALYSIS"):
    num = [k_user]
    den = coeffs + [0.0]
    sys_open = ct.TransferFunction(num, den)
    sys_closed = ct.feedback(sys_open, 1)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Stability (Routh)", "Step Response", "Root Locus", "Bode Plot", "Nyquist Plot", "Nichols Chart"
    ])

    with tab1:
        st.header("📋 Routh-Hurwitz Stability Table")
        def get_full_analysis(n_deg, c_list):
            test_ks = np.linspace(0.01, 5000, 10000)
            for k in test_ks:
                full_poly = c_list + [k]
                rows, cols = n_deg + 1, (n_deg // 2) + 1
                r_mat = np.zeros((rows, cols))
                for idx, c_val in enumerate(full_poly):
                    r_mat[idx % 2, idx // 2] = c_val
                for r in range(2, rows):
                    for c in range(cols - 1):
                        if r_mat[r-1, 0] == 0: r_mat[r-1, 0] = 1e-5
                        r_mat[r, c] = (r_mat[r-1, 0] * r_mat[r-2, c+1] - r_mat[r-2, 0] * r_mat[r-1, c+1]) / r_mat[r-1, 0]
                if r_mat[n_deg-1, 0] <= 0.01: return k, r_mat
            return None, None

        k_cr, final_matrix = get_full_analysis(n, coeffs)
        if k_cr:
            st.success(f"✅ **Critical Gain ($K_{{cr}}$): {k_cr:.2f}**")
            df_routh = pd.DataFrame(final_matrix, index=[f"s^{n-i}" for i in range(n+1)])
            st.table(df_routh.style.format("{:.2f}"))
            st.download_button("📥 Download Table (CSV)", df_routh.to_csv().encode('utf-8'), "routh_table.csv", "text/csv")

    with tab2:
        st.header("⏱️ Step Response")
        time, response = ct.step_response(sys_closed)
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        ax2.plot(time, response, 'b-', linewidth=2)
        ax2.axhline(1, color='red', linestyle='--')
        ax2.set_title("Step Response")
        ax2.grid(True)
        st.pyplot(fig2)
        # Download Button for Step Response
        st.download_button("📥 Download Step Response (PNG)", convert_plt_to_bytes(fig2), "step_response.png", "image/png")

    with tab3:
        st.header("📈 Root Locus")
        sys_locus = ct.TransferFunction([1], den)
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        ct.root_locus(sys_locus, grid=True, ax=ax3)
        st.pyplot(fig3)
        st.download_button("📥 Download Root Locus (PNG)", convert_plt_to_bytes(fig3), "root_locus.png", "image/png")

    with tab4:
        st.header("📊 Bode Diagram")
        fig4, ax4 = plt.subplots(2, 1, figsize=(8, 8))
        ct.bode_plot(sys_open, dB=True, Hz=False, grid=True)
        # Bode plot generates its own figure in control lib, we grab the current one
        fig4 = plt.gcf()
        st.pyplot(fig4)
        st.download_button("📥 Download Bode Plot (PNG)", convert_plt_to_bytes(fig4), "bode_plot.png", "image/png")

    with tab5:
        st.header("🌀 Nyquist Plot")
        fig5, ax5 = plt.subplots(figsize=(7, 6))
        ct.nyquist_plot(sys_open, ax=ax5)
        st.pyplot(fig5)
        st.download_button("📥 Download Nyquist (PNG)", convert_plt_to_bytes(fig5), "nyquist.png", "image/png")

    with tab6:
        st.header("📉 Nichols Chart")
        fig6 = plt.figure(figsize=(8, 6))
        ct.nichols_plot(sys_open, grid=True)
        fig6 = plt.gcf()
        st.pyplot(fig6)
        st.download_button("📥 Download Nichols (PNG)", convert_plt_to_bytes(fig6), "nichols.png", "image/png")

st.divider()
st.caption("© 2026 Dimitrios Kavalieros - Control Systems Analysis Tool")
