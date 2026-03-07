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
st.sidebar.write(f"Enter coefficients for: $a_{n}s^{n} + \dots + a_1s + K = 0$")
for i in range(n, 0, -1):
    val = st.sidebar.number_input(f"Coefficient a{i} (s^{i})", value=1.0, key=f"a{i}")
    coeffs.append(val)

st.sidebar.divider()
st.sidebar.header("🕹️ Interactive Control")
k_user = st.sidebar.slider("Current Gain (K) for Plots:", min_value=0.1, max_value=500.0, value=1.0, step=0.1)

def convert_plt_to_bytes(figure):
    buf = io.BytesIO()
    figure.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    return buf.getvalue()

# --- ANALYSIS EXECUTION ---
if st.sidebar.button("RUN FULL ANALYSIS"):
    
    # 1. ΥΠΟΛΟΓΙΣΜΟΣ Κcr & ωcr (Συνδυασμένη Μέθοδος για ακρίβεια)
    num_unit = [1.0]
    den_free = coeffs + [0.0]
    sys_unit = ct.TransferFunction(num_unit, den_free)
    
    gm, pm, wg, wp = ct.margin(sys_unit)
    k_cr = gm if (gm is not None and not np.isinf(gm) and gm > 0) else float('inf')
    w_cr = wg if (wg is not None and wg > 0) else 0.0

    # 2. ΟΡΙΣΜΟΣ ΣΥΣΤΗΜΑΤΩΝ
    sys_open_user = ct.TransferFunction([k_user], den_free)
    sys_closed_user = ct.feedback(sys_open_user, 1)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Stability (Routh)", "Step Response", "Root Locus", "Bode Plot", "Nyquist Plot", "Nichols Chart"
    ])

    # --- TAB 1: ROUTH ---
    with tab1:
        st.header("📋 Routh-Hurwitz Stability Table")
        
        if k_cr == float('inf'):
            st.success("✅ **The system is Unconditionally Stable for all K > 0.**")
            k_display = 1.0 # default for table
        else:
            st.warning(f"⚖️ **Stability Range: 0 < K < {k_cr:.2f}**")
            st.error(f"💥 **Marginal Stability: Kcr = {k_cr:.2f} | ωcr = {w_cr:.2f} rad/s**")
            k_display = k_cr

        # Δημιουργία Πίνακα
        full_poly = coeffs + [k_display]
        rows, cols = n + 1, (n // 2) + 1
        r_mat = np.zeros((rows, cols))
        for idx, c_val in enumerate(full_poly): r_mat[idx % 2, idx // 2] = c_val
        for r in range(2, rows):
            for c in range(cols - 1):
                if r_mat[r-1, 0] == 0: r_mat[r-1, 0] = 1e-7
                r_mat[r, c] = (r_mat[r-1, 0] * r_mat[r-2, c+1] - r_mat[r-2, 0] * r_mat[r-1, c+1]) / r_mat[r-1, 0]
        
        df_routh = pd.DataFrame(r_mat, index=[f"s^{n-i}" for i in range(n+1)])
        st.table(df_routh.style.format("{:.3f}"))
        st.download_button("📥 Download Routh Table (CSV)", df_routh.to_csv().encode('utf-8'), "routh.csv")

    # --- TAB 2: STEP ---
    with tab2:
        st.header("⏱️ Step Response")
        time, response = ct.step_response(sys_closed_user)
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        ax2.plot(time, response, 'b-', label=f'K = {k_user}')
        ax2.axhline(1, color='red', linestyle='--')
        ax2.set_title(f"Closed-Loop Response (K={k_user})")
        ax2.grid(True, alpha=0.3)
        st.pyplot(fig2)
        
        info = ct.step_info(sys_closed_user)
        c1, c2, c3 = st.columns(3)
        c1.metric("Rise Time", f"{info['RiseTime']:.3f} s")
        c2.metric("Overshoot", f"{info['Overshoot']:.2f} %")
        c3.metric("Settling Time", f"{info['SettlingTime']:.3f} s")
        st.download_button("📥 Download Plot", convert_plt_to_bytes(fig2), "step.png")

    # --- TAB 3: ROOT LOCUS ---
    with tab3:
        st.header("📈 Root Locus Analysis")
        fig3, ax3 = plt.subplots(figsize=(8, 6))
        ct.root_locus(sys_unit, grid=True, ax=ax3)
        ax3.axhline(0, color='black', lw=1, alpha=0.4, ls='--')
        ax3.axvline(0, color='black', lw=1, alpha=0.4, ls='--')
        
        if k_cr != float('inf') and w_cr > 0:
            ax3.plot(0, w_cr, 'ro', markersize=8)
            ax3.plot(0, -w_cr, 'ro', markersize=8)
            ax3.annotate(f' +j{w_cr:.2f}', xy=(0, w_cr), xytext=(0.1, w_cr), color='red', fontweight='bold')
            ax3.annotate(f' -j{w_cr:.2f}', xy=(0, -w_cr), xytext=(0.1, -w_cr), color='red', fontweight='bold')
            ax3.text(0.1, 0.1, f'Kcr = {k_cr:.2f}', transform=ax3.transAxes, bbox=dict(facecolor='white', alpha=0.8))
        
        st.pyplot(fig3)
        st.download_button("📥 Download Plot", convert_plt_to_bytes(fig3), "locus.png")

    # --- TAB 4, 5, 6 ---
    with tab4:
        st.header("📊 Bode Diagram")
        fig4 = plt.figure(figsize=(8, 8))
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
        
        col1, col2 = st.columns(2)
        col1.metric("Kcr (Stability Limit)", f"{k_cr:.2f}")
        col2.metric("ωcr (Critical Freq)", f"{w_cr:.2f} rad/s")
        st.download_button("📥 Download Nichols", convert_plt_to_bytes(plt.gcf()), "nichols.png")

st.divider()
st.caption("© 2026 Dimitrios Kavalieros - Control Systems Analysis Tool")

