import streamlit as st
import control as ct
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Routh-Hurwitz & Root Locus Tool", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; background-color: #1f77b4; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎛️ Stability Analysis: Routh-Hurwitz & Root Locus")
st.subheader("Dimitrios Kavalieros\n Electrical Engineering & Informatics M.Sc. M.Ed. ")

# --- SIDEBAR: INPUT PARAMETERS ---
st.sidebar.header("⚙️ System Parameters")
n = st.sidebar.selectbox("Select System Degree (n):", [1, 2, 3, 4, 5, 6], index=2)

coeffs = []
st.sidebar.write(f"Enter coefficients for: $a_{n}s^{n} + \dots + a_1s + K = 0$")
for i in range(n, 0, -1):
    val = st.sidebar.number_input(f"Coefficient a{i} (s^{i})", value=1.0, key=f"a{i}")
    coeffs.append(val)

# --- MAIN CALCULATION LOGIC ---
if st.sidebar.button("RUN ANALYSIS"):
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.header("📋 Routh-Hurwitz Table")
        
        # Function to find Critical Gain (Kcr) via scanning
        def find_critical_k(n_deg, c_list):
            if n_deg < 2: return None, None
            # Scan K from 0.01 to 5000 to find stability limit
            test_ks = np.linspace(0.01, 5000, 10000) 
            for k in test_ks:
                full_poly = c_list + [k]
                rows, cols = n_deg + 1, (n_deg // 2) + 1
                r_mat = np.zeros((rows, cols))
                
                # Fill first two rows
                for idx, c_val in enumerate(full_poly):
                    r_mat[idx % 2, idx // 2] = c_val
                
                # Compute subsequent rows
                for r in range(2, rows):
                    for c in range(cols - 1):
                        if r_mat[r-1, 0] == 0: r_mat[r-1, 0] = 1e-5
                        r_mat[r, c] = (r_mat[r-1, 0] * r_mat[r-2, c+1] - r_mat[r-2, 0] * r_mat[r-1, c+1]) / r_mat[r-1, 0]
                
                # Check for sign change or zero in first column (Stability Limit)
                if r_mat[n_deg-1, 0] <= 0.01:
                    return k, r_mat
            return None, None

        k_cr, final_matrix = find_critical_k(n, coeffs)

        if k_cr:
            st.success(f"✅ **Critical Gain ($K_{{cr}}$): {k_cr:.2f}**")
            
            # Display Routh Table as a formatted DataFrame
            row_labels = [f"s^{n-i}" for i in range(n+1)]
            df = pd.DataFrame(final_matrix, index=row_labels)
            st.table(df.style.format("{:.2f}"))
            
            # Calculate Oscillation Frequency (w_cr) from Auxiliary Equation (s^2 row)
            try:
                # Aux Eq: A*s^2 + B = 0 -> s = sqrt(-B/A) -> w = sqrt(B/A)
                a_aux = final_matrix[n-2, 0]
                b_aux = final_matrix[n-2, 1]
                w_cr = np.sqrt(abs(b_aux / a_aux))
                st.info(f"🔊 **Oscillation Frequency ($\omega_{{cr}}$): {w_cr:.2f} rad/s**")
            except:
                st.write("Could not determine $\omega_{cr}$ automatically.")
        else:
            st.warning("⚠️ No stability limit found for $K < 5000$. Showing table for $K=1.0$")
            # Default table for K=1.0 if no limit found
            temp_k = 1.0
            full_poly = coeffs + [temp_k]
            rows, cols = n + 1, (n // 2) + 1
            r_mat = np.zeros((rows, cols))
            for idx, c_val in enumerate(full_poly): r_mat[idx % 2, idx // 2] = c_val
            for r in range(2, rows):
                for c in range(cols - 1):
                    if r_mat[r-1, 0] == 0: r_mat[r-1, 0] = 1e-5
                    r_mat[r, c] = (r_mat[r-1, 0] * r_mat[r-2, c+1] - r_mat[r-2, 0] * r_mat[r-1, c+1]) / r_mat[r-1, 0]
            st.table(pd.DataFrame(r_mat, index=[f"s^{n-i}" for i in range(n+1)]))

    with col2:
        st.header("📈 Root Locus Diagram")
        
        # Open Loop Transfer Function: G(s) = 1 / (an*s^n + ... + a1*s)
        num = [1.0]
        den = coeffs + [0.0] # K is the gain, so we add 0 for the integrator/constant term
        sys = ct.TransferFunction(num, den)
        
        fig, ax = plt.subplots(figsize=(7, 6))
        ct.root_locus(sys, grid=True, ax=ax)
        ax.set_title("Root Locus (Open Loop)", fontsize=12)
        ax.set_xlabel("Real Axis", fontsize=10)
        ax.set_ylabel("Imaginary Axis", fontsize=10)
        
        # Plot the critical points on the imaginary axis if found
        if k_cr:
            ax.plot(0, w_cr, 'ro', markersize=8, label="Critical Point")
            ax.plot(0, -w_cr, 'ro', markersize=8)
            ax.legend()

        st.pyplot(fig)

st.divider()
st.caption("© 2026 Dimitrios Kavalieros MSc. - Control Systems Analysis Tool")


