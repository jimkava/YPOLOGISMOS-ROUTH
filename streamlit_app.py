import streamlit as st
import control as ct
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
import io

st.set_page_config(page_title="Control Systems Suite", layout="wide")

st.title("🚀 Advanced Control Systems Analysis")
st.subheader("DIMITRIOS KAVALIEROS\nElectrical Engineering & Informatics M.Sc. M.Ed.")

# --- SIDEBAR ---
st.sidebar.header("⚙️ System Parameters")
n = st.sidebar.selectbox("Select System Degree (n):", [1, 2, 3, 4, 5, 6], index=2)

coeffs = []
st.sidebar.write(f"Enter coefficients for: $a_{n}s^{n} + \dots + a_1s + K = 0$")
for i in range(n, 0, -1):
    val = st.sidebar.number_input(f"Coefficient a{i}", value=1.0, key=f"a{i}")
    coeffs.append(val)

st.sidebar.divider()
k_user = st.sidebar.slider("Current Gain (K):", 0.1, 500.0, 1.0, 0.1)

def convert_plt_to_bytes(figure):
    buf = io.BytesIO()
    figure.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    return buf.getvalue()

if st.sidebar.button("RUN FULL ANALYSIS"):
    # 1. Υπολογισμός Πίνακα Routh για το τρέχον K
    full_poly = coeffs + [k_user]
    rows, cols = n + 1, (n // 2) + 1
    r_mat = np.zeros((rows, cols))
    for idx, c_val in enumerate(full_poly): r_mat[idx % 2, idx // 2] = c_val
    for r in range(2, rows):
        for c in range(cols - 1):
            if r_mat[r-1, 0] == 0: r_mat[r-1, 0] = 1e-7
            r_mat[r, c] = (r_mat[r-1, 0] * r_mat[r-2, c+1] - r_mat[r-2, 0] * r_mat[r-1, c+1]) / r_mat[r-1, 0]

    # Έλεγχος Ευστάθειας (Πρώτη Στήλη)
    is_stable = np.all(r_mat[:, 0] > 0)
    
    # 2. Υπολογισμός Margins
    sys_unit = ct.TransferFunction([1.0], coeffs + [0.0])
    gm, pm, wg, wp = ct.margin(sys_unit)
    k_cr = gm if (gm is not None and not np.isinf(gm) and gm > 0) else float('inf')

    sys_open_user = ct.TransferFunction([k_user], coeffs + [0.0])
    sys_closed_user = ct.feedback(sys_open_user, 1)

    tab1, tab2, tab3 = st.tabs(["Stability (Routh)", "Step Response", "Root Locus"])

    with tab1:
        st.header("📋 Routh-Hurwitz Table")
        if is_stable:
            st.success(f"✅ System is STABLE for K={k_user}")
        else:
            st.error(f"❌ System is UNSTABLE for K={k_user} (Sign change in 1st column)")
        
        df_routh = pd.DataFrame(r_mat, index=[f"s^{n-i}" for i in range(n+1)])
        st.table(df_routh.style.format("{:.3f}"))

    with tab2:
        st.header("⏱️ Step Response")
        try:
            time, response = ct.step_response(sys_closed_user)
            fig2, ax2 = plt.subplots()
            ax2.plot(time, response)
            ax2.axhline(1, color='r', ls='--')
            ax2.grid(True)
            st.pyplot(fig2)
            
            if is_stable:
                info = ct.step_info(sys_closed_user)
                c1, c2 = st.columns(2)
                c1.metric("Rise Time", f"{info['RiseTime']:.3f} s")
                c2.metric("Overshoot", f"{info['Overshoot']:.2f} %")
            else:
                st.warning("Metrics cannot be calculated for unstable systems.")
        except Exception as e:
            st.error("Step response diverged (Unstable System).")

    with tab3:
        st.header("📈 Root Locus")
        fig3, ax3 = plt.subplots()
        ct.root_locus(sys_unit, grid=True, ax=ax3)
        # Προσθήκη labels για ωcr αν υπάρχει
        if wg and wg > 0 and k_cr != float('inf'):
            ax3.plot(0, wg, 'ro')
            ax3.annotate(f"j{wg:.2f}", (0, wg))
        st.pyplot(fig3)

st.divider()
st.caption("© 2026 Dimitrios Kavalieros")
