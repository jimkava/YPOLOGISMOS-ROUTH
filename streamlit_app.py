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
k_user = st.sidebar.slider("Adjust Gain (K) for Analysis:", min_value=0.1, max_value=200.0, value=1.0, step=0.1)

# Helper function for plot download
def convert_plt_to_bytes(figure):
    buf = io.BytesIO()
    figure.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    return buf.getvalue()

# --- ANALYSIS EXECUTION ---
if st.sidebar.button("RUN FULL ANALYSIS"):
    
    # 1. ΣΤΑΘΕΡΟΣ ΥΠΟΛΟΓΙΣΜΟΣ Κcr & ωcr
    def get_stability_data(n_deg, c_list):
        test_ks = np.linspace(0.001, 15000, 30000)
        k_found = float('inf')
        w_found = 0.0
        
        for k in test_ks:
            full_poly = c_list + [k]
            rows, cols = n_deg + 1, (n_deg // 2) + 1
            r_mat = np.zeros((rows, cols))
            for idx, c_val in enumerate(full_poly): r_mat[idx % 2, idx // 2] = c_val
            
            for r in range(2, rows):
                for c in range(cols - 1):
                    if r_mat[r-1, 0] == 0: r_mat[r-1, 0] = 1e-7
                    r_mat[r, c] = (r_mat[r-1, 0] * r_mat[r-2, c+1] - r_mat[r-2, 0] * r_mat[r-1, c+1]) / r_mat[r-1, 0]
            
            # Έλεγχος αλλαγής προσήμου στην πρώτη στήλη
            if np.any(r_mat[:, 0] <= 0.001):
                k_found = k
                # Υπολογισμός ωcr από τη σειρά s^2 (A*s^2 + B = 0)
                try:
                    A, B = r_mat[n_deg-2, 0], r_mat[n_deg-2, 1]
                    if A != 0: w_found = math.sqrt(abs(B/A))
                except: w_found = 0.0
                break
        return k_found, w_found

    k_cr, w_cr = get_stability_data(n, coeffs)
    sys_open_unit = ct.TransferFunction([1.0], coeffs + [0.0])
    sys_open_user = ct.TransferFunction([k_user], coeffs + [0.0])
    sys_closed = ct.feedback(sys_open_user, 1)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Stability (Routh)", "Step Response", "Root Locus", "Bode Plot", "Nyquist Plot", "Nichols Chart"
    ])

    # --- TAB 1: ROUTH ---
    with tab1:
        st.header("📋 Routh-Hurwitz Stability Table")
        if k_cr == float('inf'):
            st.success("✅ **System is Unconditionally Stable for all K > 0**")
            k_val_for_table = 1.0
        else:
            st.warning(f"⚠️ **Stability Range: 0 < K < {k_cr:.2f}**")
            st.error(f"💀 **Marginal Stability at Kcr = {k_cr:.2f} with ωcr = {w_cr:.2f} rad/s**")
            k_val_for_table = k_cr

        # Κατασκευή τελικού πίνακα για εμφάνιση
        full_poly = coeffs + [k_val_for_table]
        rows, cols = n + 1, (n // 2) + 1
        display_mat = np.zeros((rows, cols))
        for idx, c_val in enumerate(full_poly): display_mat[idx % 2, idx // 2] = c_val
        for r in range(2, rows):
            for c in range(cols - 1):
                if display_mat[r-1, 0] == 0: display_mat[r-1, 0] = 1e-7
                display_mat[r, c] = (display_mat[r-1, 0] * display_mat[r-2, c+1] - display_mat[r-2, 0] * display_mat[r-1, c+1]) / display_mat[r-1, 0]
        
        df_routh = pd.DataFrame(display_mat, index=[f"s^{n-i}" for i in range(n+1)])
        st.table(df_routh.style.format("{:.2f}"))
        st.download_button("📥 Download Routh Table (CSV)", df_routh.to_csv().encode('utf-8'), "routh.csv")

    # --- TAB 3: ROOT LOCUS (ΒΕΛΤΙΩΜΕΝΟ) ---
    with tab3:
        st.header("📈 Root Locus with Critical Limits")
        fig3, ax3 = plt.subplots(figsize=(8, 6))
        ct.root_locus(sys_open_unit, grid=True, ax=ax3)
        ax3.axhline(0, color='black', lw=1, alpha=0.3, ls='--')
        ax3.axvline(0, color='black', lw=1, alpha=0.3, ls='--')
        
        if k_cr != float('inf') and w_cr > 0:
            ax3.plot(0, w_cr, 'ro', markersize=8)
            ax3.plot(0, -w_cr, 'ro', markersize=8)
            ax3.annotate(f' +j{w_cr:.2f}', xy=(0, w_cr), xytext=(0.1, w_cr), color='red', fontweight='bold')
            ax3.annotate(f' -j{w_cr:.2f}', xy=(0, -w_cr), xytext=(0.1, -w_cr), color='red', fontweight='bold')
            st.info(f"Points of intersection with the Imaginary Axis at ω = ±{w_cr:.2f}")
        
        st.pyplot(fig3)
        st.download_button("📥 Download Plot", convert_plt_to_bytes(fig3), "locus.png")

    # --- TAB 2, 4, 5, 6 (Step, Bode, Nyquist, Nichols) ---
    # Κρατάμε την ίδια δομή με τις προηγούμενες διορθώσεις για τα downloads και metrics
    with tab2:
        st.header("⏱️ Step Response")
        time, response = ct.step_response(sys_closed)
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        ax2.plot(time, response, 'b-')
        ax2.axhline(1, color='r', ls='--')
        ax2.set_title(f"Step Response (Closed-loop) at K={k_user}")
        st.pyplot(fig2)
        st.download_button("📥 Download Step Response", convert_plt_to_bytes(fig2), "step.png")

    with tab4:
        st.header("📊 Bode Diagram")
        plt.figure(figsize=(8, 8))
        ct.bode_plot(sys_open_user, dB=True, Hz=False, grid=True, margins=True)
        st.pyplot(plt.gcf())
        st.download_button("📥 Download Bode", convert_plt_to_bytes(plt.gcf()), "bode.png")

    with tab5:
        st.header("🌀 Nyquist Plot")
        fig5, ax5 = plt.subplots(figsize=(7, 6))
        ct.nyquist_plot(sys_open_user, ax=ax5)
        st.pyplot(fig5)
        st.download_button("📥 Download Nyquist", convert_plt_to_bytes(fig5), "nyquist.png")

    with tab6:
        st.header("📉 Nichols Chart")
        plt.figure(figsize=(8, 7))
        ct.nichols_plot(sys_open_user, grid=True)
        st.pyplot(plt.gcf())
        st.download_button("📥 Download Nichols", convert_plt_to_bytes(plt.gcf()), "nichols.png")

st.divider()
st.caption("© 2026 Dimitrios Kavalieros - Control Systems Analysis Tool")
