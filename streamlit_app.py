"""
Gait2392 Control Suite – Adaptive AAN exoskeleton joint loop
Plant:  (T s + 1)(M s^2 + B s + ks)   |   Controller: K_ad(β) (proportional)
Dimitrios Kavalieros
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import control as ct
import streamlit as st

st.set_page_config(page_title="Gait2392 Control Suite", layout="wide")
st.title("Adaptive Exoskeleton Joint – Stability & Frequency Analysis")
st.caption("Dimitrios Kavalieros · Assist-as-Needed lower-limb exoskeleton framework")

# ---------------------------------------------------------------- SIDEBAR
sb = st.sidebar
sb.header("🦴 Joint biomechanics")
M = sb.number_input("Inertia M (kg·m²)", 0.001, 10.0, 0.18, format="%.3f")
B = sb.number_input("Damping B (N·m·s/rad)", 0.0, 50.0, 0.50, format="%.2f")
ks = sb.number_input("Stiffness ks (N·m/rad)", 0.0, 500.0, 2.00, format="%.2f")

sb.header("⚙️ Actuator")
T = sb.slider("Motor time constant T (s)", 0.005, 0.50, 0.05, 0.005, format="%.3f")

sb.header("🕹️ Adaptive supervisor")
beta = sb.slider("Weakness level β", 0.0, 1.0, 0.2, 0.01)
K_base = sb.slider("Base gain K", 1.0, 500.0, 150.0, 1.0)
alpha = sb.slider("Shape factor α", 0.5, 6.0, 3.0, 0.1)


# ---------------------------------------------------------------- MODEL
def k_adaptive(b, Kb=K_base, a=alpha):
    return Kb * (np.exp(a * b) - 1.0) / (np.exp(a) - 1.0)


K_ad = float(k_adaptive(beta))
a3, a2, a1 = T * M, M + T * B, B + T * ks
den_ol = np.array([a3, a2, a1, ks])           # plant denominator
char = den_ol + np.array([0, 0, 0, K_ad])      # closed-loop characteristic

# Analytic Routh limit for a 3rd-order loop: a2·a1 > a3·(ks + K)
K_cr = a1 * a2 / a3 - ks
w_cr = np.sqrt(a1 / a3)
stable = (K_ad < K_cr) and np.all(char > 0)

# β at which K_ad reaches K_cr
ratio = 1 + K_cr * (np.exp(alpha) - 1) / K_base
beta_cr = np.log(ratio) / alpha if K_cr < K_base else np.inf

G_unit = ct.tf([1.0], den_ol.tolist())
G = ct.tf([K_ad], den_ol.tolist())
CL = ct.feedback(G, 1)

# ---------------------------------------------------------------- KPIs
c = st.columns(5)
c[0].metric("K_ad(β)", f"{K_ad:.2f}")
c[1].metric("K_cr (Routh)", f"{K_cr:.2f}")
c[2].metric("β_cr", "—" if np.isinf(beta_cr) else f"{beta_cr:.3f}")
c[3].metric("Gain reserve K_cr/K_ad", "∞" if K_ad == 0 else f"{K_cr / K_ad:.2f}×")
c[4].metric("ω_cr", f"{w_cr:.1f} rad/s")

if K_ad == 0:
    st.info("β = 0 → no assistance (K_ad = 0). Open-loop joint only.")
elif stable:
    st.success(f"✅ Stable — K_ad = {K_ad:.2f} < K_cr = {K_cr:.2f}")
else:
    st.error(f"❌ Unstable — K_ad = {K_ad:.2f} ≥ K_cr = {K_cr:.2f}")

tabs = st.tabs(["Routh", "Step response", "Root locus", "Bode", "Nyquist", "β sweep"])


def show(fig):
    st.pyplot(fig)
    plt.close(fig)  # prevent memory growth on Streamlit Cloud


# ---------------------------------------------------------------- ROUTH
with tabs[0]:
    s1 = (a2 * a1 - a3 * (ks + K_ad)) / a2
    df = pd.DataFrame(
        [[a3, a1], [a2, ks + K_ad], [s1, 0.0], [ks + K_ad, 0.0]],
        index=["s³", "s²", "s¹", "s⁰"], columns=["col 1", "col 2"],
    )
    st.table(df.style.format("{:.4f}"))
    st.latex(r"T M s^3 + (M+TB)s^2 + (B+T k_s)s + (k_s + K_{ad}) = 0")
    st.latex(rf"K_{{cr}} = \frac{{a_2 a_1}}{{a_3}} - k_s = {K_cr:.3f},\quad "
             rf"\omega_{{cr}} = \sqrt{{a_1/a_3}} = {w_cr:.3f}\ \text{{rad/s}}")
    sign_changes = int(np.sum(np.diff(np.sign(df["col 1"].values)) != 0))
    st.write(f"Sign changes in first column: **{sign_changes}** "
             f"→ {sign_changes} RHP pole(s).")
    st.download_button("📥 Routh table (CSV)", df.to_csv().encode(), "routh.csv")

# ---------------------------------------------------------------- STEP
with tabs[1]:
    if K_ad == 0:
        st.info("No closed loop at β = 0.")
    elif not stable:
        st.warning("Unstable loop — step response diverges; metrics not computed.")
    else:
        t_end = min(max(10 * 4 / max(abs(np.real(CL.poles())).min(), 1e-3), 0.5), 60)
        t, y = ct.step_response(CL, T=np.linspace(0, t_end, 2000))
        y_ss = K_ad / (ks + K_ad)
        info = ct.step_info(CL)
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(t, y, lw=2, label="θ(t) / θ_ref")
        ax.axhline(1, color="grey", ls=":", label="reference")
        ax.axhline(y_ss, color="r", ls="--", label=f"steady state = {y_ss:.3f}")
        ax.set_xlabel("Time (s)"); ax.set_ylabel("Normalised angle")
        ax.grid(alpha=0.3); ax.legend()
        show(fig)
        m = st.columns(4)
        m[0].metric("Overshoot", f"{info['Overshoot']:.2f} %")
        m[1].metric("Rise time", f"{info['RiseTime']:.3f} s")
        m[2].metric("Settling time (2%)", f"{info['SettlingTime']:.3f} s")
        m[3].metric("Steady-state error", f"{(1 - y_ss) * 100:.1f} %")
        if info["Overshoot"] > 15:
            st.error("⚠️ Overshoot > 15 %: motion may be too aggressive for the joint.")
        elif info["Overshoot"] > 5:
            st.warning("Overshoot 5–15 %: check user comfort.")

# ---------------------------------------------------------------- ROOT LOCUS
with tabs[2]:
    k_max = max(2 * K_cr, 2 * K_ad, 1.0)
    ks_grid = np.concatenate([np.linspace(0, k_max, 600), [K_cr]])
    locus = np.array([np.sort_complex(np.roots(den_ol + [0, 0, 0, k])) for k in ks_grid])
    fig, ax = plt.subplots(figsize=(8, 6))
    for i in range(3):
        ax.plot(locus[:, i].real, locus[:, i].imag, "b.", ms=1.5)
    ol = np.roots(den_ol)
    ax.plot(ol.real, ol.imag, "kx", ms=10, mew=2, label="open-loop poles")
    if K_ad > 0:
        cp = np.roots(char)
        ax.plot(cp.real, cp.imag, "o", color="orange", ms=9, label=f"poles @ K_ad={K_ad:.1f}")
    ax.plot([0, 0], [w_cr, -w_cr], "ro", ms=8, label=f"jω crossing @ K_cr={K_cr:.1f}")
    ax.axvline(0, color="k", lw=0.8)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xlabel("Re(s)"); ax.set_ylabel("Im(s)"); ax.grid(alpha=0.3); ax.legend()
    show(fig)

# ---------------------------------------------------------------- BODE
w = np.logspace(-1, 4, 2000)
if K_ad > 0:
    gm, pm, _, wpc, wgc, _ = ct.stability_margins(G)
    Gjw = K_ad / np.polyval(den_ol, 1j * w)
    bw = ct.bandwidth(CL) if stable else np.nan
with tabs[3]:
    if K_ad == 0:
        st.info("No loop gain at β = 0.")
    else:
        fig, (axm, axp) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
        axm.semilogx(w, 20 * np.log10(np.abs(Gjw)))
        axm.axhline(0, color="k", lw=0.8); axm.set_ylabel("|L(jω)| (dB)"); axm.grid(which="both", alpha=0.3)
        axp.semilogx(w, np.unwrap(np.angle(Gjw)) * 180 / np.pi)
        axp.axhline(-180, color="k", lw=0.8); axp.set_ylabel("Phase (deg)")
        axp.set_xlabel("ω (rad/s)"); axp.grid(which="both", alpha=0.3)
        if np.isfinite(wgc):
            axm.axvline(wgc, color="g", ls="--"); axp.axvline(wgc, color="g", ls="--")
        if np.isfinite(wpc):
            axm.axvline(wpc, color="r", ls="--"); axp.axvline(wpc, color="r", ls="--")
        show(fig)
        m = st.columns(3)
        m[0].metric("Gain margin", "∞" if not np.isfinite(gm) else f"{20 * np.log10(gm):.2f} dB")
        m[1].metric("Phase margin", "∞" if not np.isfinite(pm) else f"{pm:.2f}°")
        m[2].metric("Closed-loop bandwidth", "—" if np.isnan(bw) else f"{bw / (2 * np.pi):.2f} Hz")

# ---------------------------------------------------------------- NYQUIST
with tabs[4]:
    if K_ad == 0:
        st.info("No loop gain at β = 0.")
    else:
        fig, ax = plt.subplots(figsize=(7, 6))
        ax.plot(Gjw.real, Gjw.imag, "b", label="ω > 0")
        ax.plot(Gjw.real, -Gjw.imag, "b--", alpha=0.5, label="ω < 0")
        ax.plot(-1, 0, "r+", ms=14, mew=2, label="−1")
        ax.axhline(0, color="k", lw=0.6); ax.axvline(0, color="k", lw=0.6)
        ax.set_aspect("equal", "datalim"); ax.grid(alpha=0.3); ax.legend()
        ax.set_xlabel("Re L(jω)"); ax.set_ylabel("Im L(jω)")
        show(fig)

# ---------------------------------------------------------------- β SWEEP
with tabs[5]:
    b = np.linspace(0, 1, 201)
    kb = k_adaptive(b)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(b, kb, lw=2, label="K_ad(β)")
    ax.axhline(K_cr, color="r", ls="--", label=f"K_cr = {K_cr:.1f}")
    ax.fill_between(b, kb, K_cr, where=kb >= K_cr, color="r", alpha=0.15, label="unstable region")
    ax.axvline(beta, color="orange", ls=":", label=f"current β = {beta:.2f}")
    if np.isfinite(beta_cr):
        ax.axvline(beta_cr, color="r", lw=0.8)
    ax.set_xlabel("Weakness level β"); ax.set_ylabel("Gain"); ax.grid(alpha=0.3); ax.legend()
    show(fig)
    st.write(
        "The whole β range is stable for these parameters."
        if np.isinf(beta_cr)
        else f"Assistance becomes unstable for **β > {beta_cr:.3f}** "
             f"with K = {K_base:.0f}, α = {alpha:.1f}, T = {T:.3f} s."
    )

st.divider()
st.caption("© 2026 Dimitrios Kavalieros – Adaptive Biomechanical Control Suite")
