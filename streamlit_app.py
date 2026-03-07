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
    sys_open_unit = ct.TransferFunction(num_base, den_base) # System with K=1
    sys_open_user = ct.TransferFunction([k_user], den_base) # System with K_user
    sys_closed = ct.feedback(sys_open_user, 1)

    # Calculate Margins (Kcr and wcr via Frequency Domain)
    gm, pm, wg, wp = ct.margin(sys_open_unit)
    k_cr_freq = gm  # Critical Gain is the Gain Margin when K=1
    w_cr_freq = wg  # Phase crossover frequency is the critical frequency

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Stability (Routh)", "Step Response", "Root Locus", "Bode Plot", "Nyquist Plot", "Nichols Chart"
    ])

    # --- TAB 1: ROUTH ---
    with tab1:
        st.header("📋 Routh-Hurwitz Stability Table")
        # (Χρησιμοποιούμε τη λογική σάρωσης που είχαμε για επιβεβαίωση)
        st.success(f"📈 **Theoretical Critical Gain ($K_{{cr}}$): {k_cr_freq:.2f}**")
        st.info(f"🔊 **Theoretical Critical Frequency ($\omega_{{cr}}$): {w_cr_freq:.2f} rad/s**")
        
        # Κατασκευή πίνακα για το Kcr
        full_poly = coeffs + [k_cr_freq]
        rows, cols = n + 1, (n // 2) + 1
        r_mat = np.zeros((rows, cols))
        for idx, c_val in enumerate(full_poly): r_mat[idx % 2, idx // 2] = c_val
        for r in range(2, rows):
            for c in range(cols - 1):
                if r_mat[r-1, 0] == 0: r_mat[r-1, 0] = 1e-5
                r_mat[r, c] = (r_mat[r-1, 0] * r_mat[r-2, c+1] - r_mat[r-2, 0] * r_mat[r-1, c+1]) / r_mat[r-1, 0]
        
        df_routh = pd.DataFrame(r_mat, index=[f"s^{n-i}" for i in range(n+1)])
        st.table(df_routh.style.format("{:.2f}"))

    # --- TAB 2: STEP ---
    with tab2:
        st.header("⏱️ Step Response")
        time, response = ct.step_response(sys_closed)
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        ax2.plot(time, response, 'b-', label=f'K={k_user}')
        ax2.axhline(1, color='r', linestyle='--')
        ax2.set_title(f"Step Response at K={k_user}")
        ax2.grid(True)
        st.pyplot(fig2)
        st.download_button("📥 Download Step Response", convert_plt_to_bytes(fig2), "step.png")

    # --- TAB 3: ROOT LOCUS ---
    with tab3:
        st.header("📈 Root Locus Analysis")
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        ct.root_locus(sys_open_unit, grid=True, ax=ax3)
        if not np.isinf(k_cr_freq):
            ax3.plot(0, w_cr_freq, 'ro', label=f'Crit. Point (K={k_cr_freq:.1f})')
            ax3.plot(0, -w_cr_freq, 'ro')
        ax3.legend()
        st.pyplot(fig3)
        st.write(f"**Interpretation:** The branches cross the imaginary axis at $\omega = \pm{w_cr_freq:.2f}j$ when $K = {k_cr_freq:.2f}$.")
        st.download_button("📥 Download Root Locus", convert_plt_to_bytes(fig3), "locus.png")

    # --- TAB 4: BODE ---
    with tab4:
        st.header("📊 Bode Diagram (Stability Margins)")
        fig4 = plt.figure(figsize=(8, 8))
        ct.bode_plot(sys_open_user, dB=True, Hz=False, grid=True, margins=True)
        st.pyplot(plt.gcf())
        st.info(f"**Gain Margin:** {gm/k_user:.2f} (at current K) | **Critical Gain Kcr:** {k_cr_freq:.2f}")
        st.download_button("📥 Download Bode Plot", convert_plt_to_bytes(plt.gcf()), "bode.png")

    # --- TAB 5: NYQUIST ---
    with tab5:
        st.header("🌀 Nyquist Plot")
        fig5, ax5 = plt.subplots(figsize=(7, 6))
        ct.nyquist_plot(sys_open_user, ax=ax5)
        ax5.set_title(f"Nyquist Plot for K={k_user}")
        st.pyplot(fig5)
        st.write(f"The system is stable if the plot does not encircle the -1 point.")
        st.download_button("📥 Download Nyquist", convert_plt_to_bytes(fig5), "nyquist.png")

    # --- TAB 6: NICHOLS ---
    with tab6:
        st.header("📉 Nichols Chart")
        fig6 = plt.figure(figsize=(8, 6))
        ct.nichols_plot(sys_open_user, grid=True)
        st.pyplot(plt.gcf())
        st.download_button("📥 Download Nichols", convert_plt_to_bytes(plt.gcf()), "nichols.png")

st.divider()
st.caption("© 2026 Dimitrios Kavalieros - Control Systems Analysis Tool")
