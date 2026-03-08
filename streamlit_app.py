import streamlit as st
import control as ct
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io

st.set_page_config(page_title="Full Control Suite | gait2392", layout="wide")

st.title("🚀 Cloud Digital Twin: Full Control & Actuator Suite")
st.subheader("DIMITRIOS KAVALLIEROS - Adaptive Framework Analysis")

# --- SIDEBAR ---
st.sidebar.header("🦴 gait2392 Biomechanics")
M = st.sidebar.number_input("Inertia M (kg·m²)", value=0.18, format="%.3f")
B = st.sidebar.number_input("Damping B (Nms/rad)", value=0.50, format="%.2f")
ks = st.sidebar.number_input("Stiffness ks (Nm/rad)", value=2.00, format="%.2f")

st.sidebar.divider()
st.sidebar.header("⚙️ Actuator (Motor) Delay")
T_motor = st.sidebar.slider("Motor Time Constant (T):", 0.01, 0.50, 0.05)

st.sidebar.divider()
st.sidebar.header("🕹️ Adaptive Supervisor")
beta = st.sidebar.slider("Weakness Level (β):", 0.0, 1.0, 0.2)
K_base = st.sidebar.slider("Base Gain (K):", 1.0, 500.0, 150.0)

# --- ADAPTIVE LOGIC ---
alpha_val = 3.0 
K_ad = K_base * (np.exp(alpha_val * beta) - 1) / (np.exp(alpha_val) - 1)

# Coefficients for (T*M)s^3 + (M+T*B)s^2 + (B+T*ks)s + (ks+Kad) = 0
a3, a2, a1, a0 = T_motor*M, M+T_motor*B, B+T_motor*ks, ks+K_ad

if st.sidebar.button("RUN FULL ANALYSIS"):
    # Systems Definition
    num_open = [1]
    den_open = [a3, a2, a1, ks] # Open loop for frequency analysis
    sys_open = K_ad * ct.TransferFunction(num_open, den_open)
    sys_closed = ct.feedback(sys_open, 1)

    tabs = st.tabs(["Stability", "Step Response", "Root Locus", "Bode Plot", "Nyquist & Nichols"])

    with tabs[0]:
        st.header("📋 Routh-Hurwitz")
        r_mat = np.zeros((4, 2))
        r_mat[0,0], r_mat[0,1] = a3, a1
        r_mat[1,0], r_mat[1,1] = a2, a0
        r_mat[2,0] = (r_mat[1,0]*r_mat[0,1] - r_mat[0,0]*r_mat[1,1])/r_mat[1,0]
        r_mat[3,0] = a0
        st.table(pd.DataFrame(r_mat, index=["s^3","s^2","s^1","s^0"]))
        if np.all(r_mat[:,0] > 0): st.success("✅ Stable System")
        else: st.error("❌ Unstable System")

    with tabs[1]:
        st.header("⏱️ Step Response")
        t, y = ct.step_response(sys_closed)
        fig, ax = plt.subplots()
        ax.plot(t, y)
        ax.axhline(1, color='r', ls='--')
        st.pyplot(fig)

    with tabs[2]:
        st.header("📈 Root Locus")
        fig_rl, ax_rl = plt.subplots()
        ct.root_locus(sys_open/K_ad, grid=True, ax=ax_rl)
        st.pyplot(fig_rl)

    with tabs[3]:
        st.header("📊 Bode Diagram")
        fig_bode = plt.figure(figsize=(10, 8))
        ct.bode_plot(sys_open, dB=True, Hz=False, grid=True, margins=True)
        st.pyplot(fig_bode)

    with tabs[4]:
        col1, col2 = st.columns(2)
        with col1:
            st.header("🌀 Nyquist Plot")
            fig_ny, ax_ny = plt.subplots()
            ct.nyquist_plot(sys_open, ax=ax_ny)
            st.pyplot(fig_ny)
        with col2:
            st.header("📉 Nichols Chart")
            fig_nic = plt.figure()
            ct.nichols_plot(sys_open, grid=True)
            st.pyplot(fig_nic)
