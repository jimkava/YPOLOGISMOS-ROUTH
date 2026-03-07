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
k_user = st.sidebar.slider("Adjust Gain (K) for Analysis:", min_value=0.1, max_value=100.0, value=1.0, step=0.1)

# Helper function to convert plot to bytes
def convert_plt_to_bytes(figure):
    buf = io.BytesIO()
    figure.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    return buf.getvalue()

# --- ANALYSIS EXECUTION ---
if st.sidebar.button("RUN FULL ANALYSIS"):
    # Define Systems
    num_base = [1.0]
    den_base = coeffs + [0.0]
    sys_open_unit = ct.TransferFunction(num_base, den_base)
    sys_open_user = ct.TransferFunction([k_user], den_base)
    sys_closed = ct.feedback(sys_open_user, 1)

    # Calculate Margins
    gm, pm, wg, wp = ct.margin(sys_open_unit)
    k_cr_freq = gm
    w_cr_freq = wg
    
    # User Specific Margins (for current K)
    gm_u, pm_u, wg_u, wp_u = ct.margin(sys_open_user)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Stability (Routh)", "Step Response", "Root Locus", "Bode Plot", "Nyquist Plot", "Nichols Chart"
    ])

    # --- TAB 1: ROUTH ---
    with tab1:
        st.header("📋 Routh-Hurwitz Stability Table")
        st.success(f"📈 **Critical Gain ($K_{{cr}}$): {k_cr_freq:.2f}**")
        st.info(f"🔊 **Critical Frequency ($\omega_{{cr}}$): {w_cr_freq:.2f} rad/s**")
        
        full_poly = coeffs + [k_cr_freq if not np.isinf(k_cr_freq) else 1.0]
        rows, cols = n + 1, (n // 2) + 1
        r_mat = np.zeros((rows, cols))
        for idx, c_val in enumerate(full_poly): r_mat[idx % 2, idx // 2] = c_val
        for r in range(2, rows):
            for c in range(cols - 1):
                if r_mat[r-1, 0] == 0: r_mat[r-1, 0] = 1e-5
                r_mat[r, c] = (r_mat[r-1, 0] * r_mat[r-2, c+1] - r_mat[r-2, 0] * r_mat[r-1, c+1]) / r_mat[r-1, 0]
        
        df_routh = pd.DataFrame(r_mat, index=[f"s^{n-i}" for i in range(n+1)])
        st.table(df_routh.style.format("{:.2f}"))
        
        # ΕΠΑΝΑΦΟΡΑ DOWNLOAD REPORT
        csv_routh = df_routh.to_csv().encode('utf-8')
        st.download_button("📥 Download Routh Table (CSV)", csv_routh, "routh_table.csv", "text/csv")

    # --- TAB 2: STEP ---
    with tab2:
        st.header("⏱️ Step Response")
        time, response = ct.step_response(sys_closed)
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        ax2.plot(time, response, 'b-')
        ax2.axhline(1, color='r', linestyle='--')
        ax2.grid(True)
        st.pyplot(fig2)
        st.download_button("📥 Download Step Response (PNG)", convert_plt_to_bytes(fig2), "step.png")

    # --- TAB 3: ROOT LOCUS ---
    with tab3:
        st.header("📈 Root Locus")
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        ct.root_locus(sys_open_unit, grid=True, ax=ax3)
        if not np.isinf(k_cr_freq) and k_cr_freq is not None:
            ax3.plot(0, w_cr_freq, 'ro', label='Crit. Point')
            ax3.plot(0, -w_cr_freq, 'ro')
        st.pyplot(fig3)
        st.download_button("📥 Download Root Locus (PNG)", convert_plt_to_bytes(fig3), "locus.png")

    # --- TAB 4: BODE ---
    with tab4:
        st.header("📊 Bode Diagram")
        plt.figure(figsize=(8, 8))
        ct.bode_plot(sys_open_user, dB=True, Hz=False, grid=True, margins=True)
        fig4 = plt.gcf()
        st.pyplot(fig4)
        st.info(f"**Gain Margin:** {gm_u:.2f} | **Phase Margin:** {pm_u:.2f}°")
        st.download_button("📥 Download Bode Plot (PNG)", convert_plt_to_bytes(fig4), "bode.png")

    # --- TAB 5: NYQUIST ---
    with tab5:
        st.header("🌀 Nyquist Plot")
        fig5, ax5 = plt.subplots(figsize=(7, 6))
        ct.nyquist_plot(sys_open_user, ax=ax5)
        st.pyplot(fig5)
        st.download_button("📥 Download Nyquist (PNG)", convert_plt_to_bytes(fig5), "nyquist.png")

    # --- TAB 6: NICHOLS ---
    with tab6:
        st.header("📉 Nichols Chart Analysis")
        plt.figure(figsize=(8, 7))
        ct.nichols_plot(sys_open_user, grid=True)
        
        # ΠΡΟΣΘΗΚΗ ΥΠΟΛΟΓΙΣΜΩΝ ΣΤΟ NICHOLS
        st.pyplot(plt.gcf())
        col1, col2 = st.columns(2)
        col1.metric("Critical Gain Kcr", f"{k_cr_freq:.2f}")
        col1.metric("Critical Freq ωcr", f"{w_cr_freq:.2f} rad/s")
        col2.metric("Gain Margin (Current K)", f"{gm_u:.2f}")
        col2.metric("Phase Margin (Current K)", f"{pm_u:.2f}°")
        
        st.info(f"At gain K={k_user}, the Nichols plot must avoid the (0dB, -180°) point for stability.")
        st.download_button("📥 Download Nichols Chart (PNG)", convert_plt_to_bytes(plt.gcf()), "nichols.png")

st.divider()
st.caption("© 2026 Dimitrios Kavalieros - Control Systems Analysis Tool")
