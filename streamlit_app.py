import streamlit as st
import control as ct
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math

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

# --- ANALYSIS EXECUTION ---
if st.sidebar.button("RUN FULL ANALYSIS"):
    # Define Open Loop Transfer Function: G(s) = 1 / (an*s^n + ... + a1*s)
    num = [1.0]
    den = coeffs + [0.0]
    sys_open = ct.TransferFunction(num, den)
    
    # Define Closed Loop Transfer Function (Unity Feedback): T(s) = G(s) / (1 + G(s))
    # For a simple K=1 gain for the step response
    sys_closed = ct.feedback(sys_open, 1)

    # Tabs for different plots
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
                if r_mat[n_deg-1, 0] <= 0.01:
                    return k, r_mat
            return None, None

        k_cr, final_matrix = get_full_analysis(n, coeffs)
        
        if k_cr:
            st.success(f"✅ **Critical Gain ($K_{{cr}}$): {k_cr:.2f}**")
            try:
                a_aux = final_matrix[n-2, 0]
                b_aux = final_matrix[n-2, 1]
                if a_aux != 0:
                    w_cr = math.sqrt(abs(b_aux / a_aux))
                    st.info(f"🔊 **Critical Frequency ($\omega_{{cr}}$): {w_cr:.2f} rad/s**")
                    st.latex(f"\\omega_{{cr}} = {w_cr:.2f} \\text{{ rad/s}}")
            except:
                st.warning("Could not calculate $\omega_{cr}$ automatically.")
            
            df = pd.DataFrame(final_matrix, index=[f"s^{n-i}" for i in range(n+1)])
            st.table(df.style.format("{:.2f}"))
        else:
            st.warning("No stability limit found for K < 5000.")

    with tab2:
        st.header("⏱️ Step Response (Time Domain)")
        st.write("Response of the closed-loop system to a unit step input (for K=1).")
        
        time, response = ct.step_response(sys_closed)
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(time, response, b='-')
        ax.axhline(1, color='red', linestyle='--', label='Target Value')
        ax.set_title("Closed-Loop Step Response")
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Amplitude")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)
        
        # Calculate key metrics
        info = ct.step_info(sys_closed)
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Rise Time", f"{info['RiseTime']:.2f} s")
        col_m2.metric("Overshoot", f"{info['Overshoot']:.2f} %")
        col_m3.metric("Settling Time", f"{info['SettlingTime']:.2f} s")

    with tab3:
        st.header("📈 Root Locus")
        fig, ax = plt.subplots(figsize=(8, 5))
        ct.root_locus(sys_open, grid=True, ax=ax)
        st.pyplot(fig)

    with tab4:
        st.header("📊 Bode Diagram")
        fig, ax = plt.subplots(2, 1, figsize=(8, 8))
        ct.bode_plot(sys_open, dB=True, Hz=False, grid=True, ax=ax)
        st.pyplot(fig)

    with tab5:
        st.header("🌀 Nyquist (Polar) Plot")
        fig, ax = plt.subplots(figsize=(7, 6))
        ct.nyquist_plot(sys_open, ax=ax)
        st.pyplot(fig)

    with tab6:
        st.header("📉 Nichols Chart")
        fig = plt.figure(figsize=(8, 6))
        ct.nichols_plot(sys_open, grid=True)
        st.pyplot(plt.gcf())

st.divider()
st.caption("© 2026 Dimitrios Kavalieros - Control Systems Analysis Tool")
