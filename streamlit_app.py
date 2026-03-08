import streamlit as st
import control as ct
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io

# Page Configuration
st.set_page_config(page_title="Adaptive Exoskeleton Analysis", layout="wide")

st.title("🚀 Cloud Digital Twin: Adaptive Actuator Analysis")
st.subheader("DIMITRIOS KAVALIEROS - gait2392 Adaptive Framework")

# --- SIDEBAR: ΠΑΡΑΜΕΤΡΟΙ ΜΟΝΤΕΛΟΥ & ΕΝΕΡΓΟΠΟΙΗΤΗ ---
st.sidebar.header("🦴 Biomechanical Properties (gait2392)")
M = st.sidebar.number_input("Inertia M (kg·m²)", value=0.18, format="%.3f")
B = st.sidebar.number_input("Damping B (Nms/rad)", value=0.50, format="%.2f")
ks = st.sidebar.number_input("Stiffness ks (Nm/rad)", value=2.00, format="%.2f")

st.sidebar.divider()
st.sidebar.header("⚙️ Actuator Selection (Digital Twin)")
T_motor = st.sidebar.slider("Motor Time Constant (T) [s]:", 0.01, 0.50, 0.10)

st.sidebar.divider()
st.sidebar.header("🕹️ Adaptive Supervisor")
beta = st.sidebar.slider("Weakness Level (β):", 0.0, 1.0, 0.5)
K_base = st.sidebar.slider("Base Gain (K):", 1.0, 500.0, 100.0)

# --- ΥΠΟΛΟΓΙΣΜΟΣ ADAPTIVE GAIN (Βάσει του Paper) ---
# Εκθετική αύξηση της υποβοήθησης J(β)
alpha = 3.0 
K_ad = K_base * (np.exp(alpha * beta) - 1) / (np.exp(alpha) - 1)

# --- ΣΥΝΤΕΛΕΣΤΕΣ ΧΑΡΑΚΤΗΡΙΣΤΙΚΗΣ ΕΞΙΣΩΣΗΣ ---
# (T*M)s^3 + (M + T*B)s^2 + (B + T*ks)s + (ks + Kad) = 0
a3 = T_motor * M
a2 = M + (T_motor * B)
a1 = B + (T_motor * ks)
a0 = ks + K_ad

characteristic_coeffs = [a3, a2, a1, a0]

def convert_plt_to_bytes(figure):
    buf = io.BytesIO()
    figure.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    return buf.getvalue()

if st.sidebar.button("RUN ADAPTIVE ANALYSIS"):
    
    # Ορισμός Συστημάτων
    sys_open = ct.TransferFunction([1], characteristic_coeffs[:-1] + [0])
    sys_closed = ct.feedback(K_ad * ct.TransferFunction([1], [T_motor*M, M+T_motor*B, B+T_motor*ks, ks]), 1)

    tab1, tab2, tab3 = st.tabs(["Stability (Routh)", "Step Response", "Root Locus"])

    # --- TAB 1: ROUTH ---
    with tab1:
        st.header("📋 Routh-Hurwitz Stability Table")
        rows, cols = 4, 2
        r_mat = np.zeros((rows, cols))
        r_mat[0, 0], r_mat[0, 1] = a3, a1
        r_mat[1, 0], r_mat[1, 1] = a2, a0
        
        # Υπολογισμός σειράς s^1
        r_mat[2, 0] = (r_mat[1, 0] * r_mat[0, 1] - r_mat[0, 0] * r_mat[1, 1]) / r_mat[1, 0]
        # Υπολογισμός σειράς s^0
        r_mat[3, 0] = (r_mat[2, 0] * r_mat[1, 1]) / r_mat[2, 0] if r_mat[2, 0] != 0 else 0
        
        df_routh = pd.DataFrame(r_mat, index=["s^3", "s^2", "s^1", "s^0"])
        st.table(df_routh.style.format("{:.3f}"))
        
        if np.all(r_mat[:, 0] > 0):
            st.success(f"✅ Σύστημα Ευσταθές για β={beta}")
        else:
            st.error("❌ Σύστημα Ασταθές! Η καθυστέρηση του μοτέρ ή το υψηλό Gain προκαλούν απόκλιση.")

    # --- TAB 2: STEP ---
    with tab2:
        st.header("⏱️ Step Response & Safety Analysis")
        time, response = ct.step_response(sys_closed)
        fig2, ax2 = plt.subplots()
        ax2.plot(time, response, lw=2, label="Adaptive Response")
        ax2.axhline(1, color='r', ls='--')
        ax2.grid(True)
        st.pyplot(fig2)
        
        info = ct.step_info(sys_closed)
        c1, c2, c3 = st.columns(3)
        c1.metric("Overshoot", f"{info['Overshoot']:.2f} %")
        c2.metric("Settling Time", f"{info['SettlingTime']:.3f} s")
        c3.metric("K_adaptive", f"{K_ad:.2f} Nm/rad")

    # --- TAB 3: ROOT LOCUS ---
    with tab3:
        st.header("📈 Root Locus (Actuator-Plant Interaction)")
        fig3, ax3 = plt.subplots()
        ct.root_locus(ct.TransferFunction([1], [T_motor*M, M+T_motor*B, B+T_motor*ks, ks]), grid=True, ax=ax3)
        st.pyplot(fig3)

st.divider()
st.caption("© 2026 Dimitrios Kavalieros - Digital Twin Actuator Selection Suite")
