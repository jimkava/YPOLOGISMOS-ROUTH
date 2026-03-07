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
st.sidebar.write(f"Enter coefficients for: $a_{n}s^{n} + \dots + a_1s + K_{{user}} = 0$")
for i in range(n, 0, -1):
    val = st.sidebar.number_input(f"Coefficient a{i} (s^{i})", value=1.0, key=f"a{i}")
    coeffs.append(val)

st.sidebar.divider()
st.sidebar.header("🕹️ Interactive Control")
k_user = st.sidebar.slider("Adjust Gain (K) for Step Response:", min_value=0.1, max_value=100.0, value=1.0, step=0.1)

# --- ANALYSIS EXECUTION ---
if st.sidebar.button("RUN FULL ANALYSIS"):
    # Open Loop: G(s) = K / (an*s^n + ... + a1*s)
    num = [k_user]
    den = coeffs + [0.0]
    sys_open = ct.TransferFunction(num, den)
    
    # Closed Loop: T(s) = G(s) / (1 + G(s))
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
            except:
                st.warning("Could not calculate $\omega_{cr}$ automatically.")
            
            df = pd.DataFrame(final_matrix, index=[f"s^{n-i}" for i in range(n+1)])
            st.table(df.style.format("{:.2f}"))
        else:
            st.warning("No stability limit found for K < 5000.")

    with tab2:
        st.header("⏱️ Step Response (Time Domain)")
        st.write(f"Closed-loop response for **K = {k_user}**")
        
        time, response = ct.step_response(sys_closed)
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(time, response, 'b-', linewidth=2, label=f'Response (K={k_user})')
        ax.axhline(1, color='red', linestyle='--', label='Target')
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)
        
        info = ct.step_info(sys_closed)
        c1, c2, c3 = st.columns(3)
        c1.metric("Rise Time", f"{info['RiseTime']:.2f} s")
        c2.metric("Overshoot", f"{info['Overshoot']:.2f} %")
        c3.metric("Settling Time", f"{info['SettlingTime']:.2f} s")

    with tab3:
        st.header("📈 Root Locus")
        # For Root Locus we use the open loop without the k_user multiplier 
        # to show the full potential path of poles.
        sys_locus = ct.TransferFunction([1], den)
        fig, ax = plt.subplots(figsize=(8, 5))
        ct.root_locus(sys_locus, grid=True, ax=ax)
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
