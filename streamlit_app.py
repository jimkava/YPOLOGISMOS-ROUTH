import streamlit as st
import control as ct
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io

# --- ΡΥΘΜΙΣΗ ΣΕΛΙΔΑΣ ---
st.set_page_config(page_title="Gait2392 Control Suite", layout="wide")
st.title("🚀 Cloud Digital Twin: Full Stability & Frequency Analysis")
st.subheader("DIMITRIOS KAVALLIEROS - Adaptive Exoskeleton Framework")

# --- SIDEBAR: ΠΑΡΑΜΕΤΡΟΙ ---
st.sidebar.header("🦴 gait2392 Biomechanics")
M = st.sidebar.number_input("Inertia M (kg·m²)", value=0.18, format="%.3f")
B = st.sidebar.number_input("Damping B (Nms/rad)", value=0.50, format="%.2f")
ks = st.sidebar.number_input("Stiffness ks (Nm/rad)", value=2.00, format="%.2f")

st.sidebar.divider()
st.sidebar.header("⚙️ Actuator Selection")
T_motor = st.sidebar.slider("Motor Time Constant (T) [s]:", 0.01, 0.50, 0.05)

st.sidebar.divider()
st.sidebar.header("🕹️ Adaptive Supervisor")
beta = st.sidebar.slider("Weakness Level (β):", 0.0, 1.0, 0.2)
K_base = st.sidebar.slider("Base Gain (K):", 1.0, 500.0, 150.0)

# --- ΕΚΘΕΤΙΚΟΣ ADAPTIVE GAIN (Paper Formula) ---
alpha_val = 3.0 
K_ad = K_base * (np.exp(alpha_val * beta) - 1) / (np.exp(alpha_val) - 1)

# Συντελεστές Χαρακτηριστικής: a3*s^3 + a2*s^2 + a1*s + a0 = 0
a3, a2, a1, a0 = T_motor*M, M + T_motor*B, B + T_motor*ks, ks + K_ad

if st.sidebar.button("RUN FULL ANALYSIS"):
    # Ορισμός Συστημάτων
    num_open = [1]
    den_open = [a3, a2, a1, ks]
    sys_open = K_ad * ct.TransferFunction(num_open, den_open)
    sys_closed = ct.feedback(sys_open, 1)

    tabs = st.tabs(["Stability (Routh)", "Step Response", "Root Locus", "Bode Plot", "Nyquist & Nichols"])

    # 1. ROUTH
    with tabs[0]:
        st.header("📋 Routh-Hurwitz Stability Table")
        r_mat = np.zeros((4, 2))
        r_mat[0,0], r_mat[0,1] = a3, a1
        r_mat[1,0], r_mat[1,1] = a2, a0
        r_mat[2,0] = (r_mat[1,0]*r_mat[0,1] - r_mat[0,0]*r_mat[1,1])/r_mat[1,0]
        r_mat[3,0] = a0
        st.table(pd.DataFrame(r_mat, index=["s^3","s^2","s^1","s^0"]))
        if np.all(r_mat[:,0] > 0): st.success("✅ Stable System")
        else: st.error("❌ Unstable System")

    # 2. STEP
    with tabs[1]:
        st.header("⏱️ Time Domain Response")
        t, y = ct.step_response(sys_closed)
        fig_step, ax_step = plt.subplots(figsize=(8, 4))
        ax_step.plot(t, y, lw=2)
        ax_step.axhline(1, color='r', ls='--')
        ax_step.grid(True, alpha=0.3)
        st.pyplot(fig_step)
        
        info = ct.step_info(sys_closed)
        st.metric("Overshoot", f"{info['Overshoot']:.2f} %")

    # 3. ROOT LOCUS
    with tabs[2]:
        st.header("📈 Root Locus")
        fig_rl, ax_rl = plt.subplots(figsize=(8, 5))
        ct.root_locus(sys_open/K_ad, grid=True, ax=ax_rl)
        st.pyplot(fig_rl)

    # 4. BODE & BANDWIDTH
    with tabs[3]:
        st.header("📊 Bode Diagram & Frequency Metrics")
        fig_bode = plt.figure(figsize=(10, 8))
        gm, pm, wg, wp = ct.margin(sys_open)
        ct.bode_plot(sys_open, dB=True, Hz=True, grid=True, margins=True)
        st.pyplot(fig_bode)
        
        # Υπολογισμός Bandwidth (εκεί που το Gain πέφτει -3dB από το DC)
        bw = ct.bandwidth(sys_closed)
        c1, c2 = st.columns(2)
        c1.metric("Bandwidth (Hz)", f"{bw/(2*np.pi):.2f} Hz")
        c2.metric("Phase Margin", f"{pm:.2f} deg")
        st.info(f"Το Bandwidth δείχνει πόσο γρήγορα μπορεί ο εξωσκελετός να αντιδράσει στις αλλαγές της βάδισης.")

    # 5. NYQUIST & NICHOLS
    with tabs[4]:
        col1, col2 = st.columns(2)
        with col1:
            st.header("🌀 Nyquist Plot")
            fig_ny, ax_ny = plt.subplots()
            ct.nyquist_plot(sys_open, ax=ax_ny)
            st.pyplot(fig_ny)
        with col2:
            st.header("📉 Nichols Chart")
            fig_nic, ax_nic = plt.subplots()
            ct.nichols_plot(sys_open, grid=True, ax=ax_nic)
            st.pyplot(fig_nic)

st.divider()
st.caption("© 2026 Dimitrios Kavallieros - Adaptive Biomechanical Control Suite")
