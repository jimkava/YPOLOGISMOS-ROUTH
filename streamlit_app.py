import streamlit as st
import control as ct
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
import io

# Page Configuration
st.set_page_config(page_title="Adaptive Exoskeleton Control", layout="wide")

st.title("🚀 Adaptive Control Systems Analysis")
st.subheader("DIMITRIOS KAVALIEROS\nElectrical Engineering & Informatics M.Sc. M.Ed.")

# --- SIDEBAR: ΠΑΡΑΜΕΤΡΙΚΟ ΜΟΝΤΕΛΟ ---
st.sidebar.header("🧬 Biomechanical Parameters")
M = st.sidebar.number_input("Inertia / Mass (M)", value=1.0, min_value=0.1)
B = st.sidebar.number_input("Damping coefficient (B)", value=0.5, min_value=0.01)
ks = st.sidebar.number_input("Natural Stiffness (ks)", value=2.0, min_value=0.0)

st.sidebar.divider()
st.sidebar.header("🕹️ Adaptive Supervisor")
beta = st.sidebar.slider("Weakness Level (β): 0=Healthy, 1=Weak", 0.0, 1.0, 0.5)
k_user = st.sidebar.slider("Assistance Gain (K):", 0.1, 500.0, 50.0)

# --- ΥΠΟΛΟΓΙΣΜΟΣ ΧΑΡΑΚΤΗΡΙΣΤΙΚΗΣ ΕΞΙΣΩΣΗΣ ---
# Εδώ ορίζουμε το μοντέλο μας (π.χ. 3ου βαθμού για να συμπεριλάβουμε καθυστέρηση ενεργοποιητή)
# Χαρακτηριστική: a2*s^2 + a1*s + a0 = 0 -> Εμπλουτισμένη με β και K
a2 = M
a1 = B
a0 = ks + (beta * k_user) # Η ενεργός ακαμψία αυξάνεται με την υποβοήθηση

# Σχηματισμός λίστας συντελεστών για τον κώδικα (σταθερά a_n...a_1)
coeffs = [a2, a1] # Το σταθερό όρος a0 θα μπει ως 'K' στους υπολογισμούς

def convert_plt_to_bytes(figure):
    buf = io.BytesIO()
    figure.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    return buf.getvalue()

# --- ANALYSIS EXECUTION ---
if st.sidebar.button("RUN ADAPTIVE ANALYSIS"):
    
    # 1. ΣΥΣΤΗΜΑΤΑ
    # Ανοιχτός βρόχος: G(s) = 1 / (Ms^2 + Bs + ks)
    # Κλείνουμε βρόχο με το (beta * k_user)
    num_unit = [1.0]
    den_free = [M, B, ks] 
    sys_unit = ct.TransferFunction(num_unit, den_free)
    
    # Υπολογισμός Margins
    gm, pm, wg, wp = ct.margin(sys_unit * k_user)
    k_cr = gm * k_user if (gm is not None and not np.isinf(gm)) else float('inf')
    w_cr = wg if (wg is not None and wg > 0) else 0.0

    # Κλειστό σύστημα με το Adaptive Gain
    sys_closed_user = ct.feedback(k_user * beta * sys_unit, 1)

    tab1, tab2, tab3, tab4 = st.tabs([
        "Stability (Routh)", "Step Response", "Root Locus", "Frequency Analysis"
    ])

    # --- TAB 1: ROUTH ---
    with tab1:
        st.header("📋 Routh-Hurwitz Stability Table")
        # Εδώ χρησιμοποιούμε τους τελικούς συντελεστές του κλειστού βρόχου
        # Χαρακτηριστική: M*s^2 + B*s + (ks + beta*K) = 0
        final_coeffs = [M, B, ks + (beta * k_user)]
        n_deg = len(final_coeffs) - 1
        
        # Κατασκευή πίνακα Routh
        rows, cols = n_deg + 1, (n_deg // 2) + 1
        r_mat = np.zeros((rows, cols))
        for idx, c_val in enumerate(final_coeffs): r_mat[idx % 2, idx // 2] = c_val
        for r in range(2, rows):
            for c in range(cols - 1):
                if r_mat[r-1, 0] == 0: r_mat[r-1, 0] = 1e-7
                r_mat[r, c] = (r_mat[r-1, 0] * r_mat[r-2, c+1] - r_mat[r-2, 0] * r_mat[r-1, c+1]) / r_mat[r-1, 0]
        
        st.table(pd.DataFrame(r_mat, index=[f"s^{n_deg-i}" for i in range(n_deg+1)]).style.format("{:.3f}"))
        
        if np.all(r_mat[:, 0] > 0):
            st.success(f"✅ System is STABLE for β={beta}")
        else:
            st.error("❌ System is UNSTABLE")

    # --- TAB 2: STEP RESPONSE (SAFETY) ---
    with tab2:
        st.header("⏱️ Performance & Safety Indices")
        time, response = ct.step_response(sys_closed_user)
        fig2, ax2 = plt.subplots()
        ax2.plot(time, response, lw=2)
        ax2.axhline(1, color='r', ls='--')
        st.pyplot(fig2)
        
        info = ct.step_info(sys_closed_user)
        zeta = -np.log(info['Overshoot']/100) / np.sqrt(np.pi**2 + np.log(info['Overshoot']/100)**2) if info['Overshoot']>0 else 1.0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Damping Ratio (ζ)", f"{zeta:.3f}")
        c2.metric("Overshoot (%)", f"{info['Overshoot']:.2f}%")
        c3.metric("Settling Time", f"{info['SettlingTime']:.3f}s")

        if info['Overshoot'] > 15:
            st.error("⚠️ SAFETY ALERT: Excessive vibration for the human limb!")

    # --- TAB 3: ROOT LOCUS ---
    with tab3:
        st.header("📈 Adaptive Root Locus")
        fig3, ax3 = plt.subplots()
        ct.root_locus(sys_unit, grid=True, ax=ax3)
        st.pyplot(fig3)

st.divider()
st.caption("© 2026 Dimitrios Kavalieros - Adaptive Supervisor Logic")
