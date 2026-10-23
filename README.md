# Adaptive Exoskeleton Joint – Stability & Frequency Analysis

[![Live app](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://kavalieros-routh.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![python-control](https://img.shields.io/badge/python--control-%E2%89%A50.10-orange)

Interactive Streamlit tool for the stability analysis of a single exoskeleton joint driven by an
**Assist-as-Needed (AAN)** adaptive gain. It computes the Routh–Hurwitz stability limit, the
critical weakness level β<sub>cr</sub>, and the time- and frequency-domain behaviour of the loop.

**Live app:** https://kavalieros-routh.streamlit.app

---

## Model

Joint (gait2392 biomechanics) in series with a first-order actuator, closed by a proportional
adaptive gain:

$$
G(s) = \frac{1}{(T s + 1)(M s^2 + B s + k_s)}, \qquad
K_{ad}(\beta) = K\,\frac{e^{\alpha\beta} - 1}{e^{\alpha} - 1}
$$

Closed-loop characteristic equation:

$$
T M s^3 + (M + T B)s^2 + (B + T k_s)s + (k_s + K_{ad}) = 0
$$

Routh–Hurwitz gives the stability limit and the crossing frequency:

$$
K_{cr} = \frac{a_2 a_1}{a_3} - k_s, \qquad \omega_{cr} = \sqrt{a_1 / a_3}
$$

and the weakness level at which assistance becomes unstable:

$$
\beta_{cr} = \frac{1}{\alpha}\ln\!\left(1 + \frac{K_{cr}\,(e^{\alpha}-1)}{K}\right), \quad K_{cr} < K
$$

| Symbol | Meaning | Default |
|---|---|---|
| M | Joint inertia (kg·m²) | 0.18 |
| B | Joint damping (N·m·s/rad) | 0.50 |
| k<sub>s</sub> | Joint stiffness (N·m/rad) | 2.00 |
| T | Motor time constant (s) | 0.05 |
| β | Weakness level (0 = healthy, 1 = full weakness) | 0.20 |
| K | Base gain | 150 |
| α | Shape factor of the adaptive law | 3.0 |

## Features

| Tab | Content |
|---|---|
| **Routh** | Numerical Routh table, analytic K<sub>cr</sub> and ω<sub>cr</sub>, RHP pole count, CSV export |
| **Step response** | Closed-loop response with steady-state level, overshoot, rise/settling time, steady-state error, safety warnings |
| **Root locus** | Full locus, open-loop poles, current closed-loop poles, jω-axis crossing |
| **Bode** | Loop magnitude/phase, gain & phase margins, closed-loop bandwidth |
| **Nyquist** | Loop Nyquist plot relative to −1 |
| **β sweep** | K<sub>ad</sub>(β) against K<sub>cr</sub>, with the unstable region shaded |

Header KPIs: K<sub>ad</sub>(β), K<sub>cr</sub>, β<sub>cr</sub>, gain reserve K<sub>cr</sub>/K<sub>ad</sub>, ω<sub>cr</sub>.
All results update live when a parameter changes.

## Run locally

```bash
git clone https://github.com/jimkava/YPOLOGISMOS-ROUTH.git
cd YPOLOGISMOS-ROUTH
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Opens at `http://localhost:8501`. Alternatively, open the repository in **GitHub Codespaces**;
the included `.devcontainer` installs the dependencies and starts the app automatically.

## Embed in a website

```html
<iframe
  src="https://kavalieros-routh.streamlit.app/?embed=true&embed_options=dark_theme"
  style="width:100%; height:1150px; border:none;"
  loading="lazy"></iframe>
```

## Repository contents

| File | Description |
|---|---|
| `streamlit_app.py` | Main application (adaptive exoskeleton joint) |
| `requirements.txt` | Python dependencies |
| `Stability_Analysis.py` | Legacy generic Routh / root-locus tool for an n-th order system (n ≤ 6) |
| `main.py` | Legacy desktop (Tkinter) version |
| `.devcontainer/` | Codespaces configuration |

## Related work

Part of the computational framework for actuator selection in AAN lower-limb exoskeletons:
[jimkava/AAN-Exoskeleton-Pipeline](https://github.com/jimkava/AAN-Exoskeleton-Pipeline)

D. Kavalieros, P. Vartholomeos, *A Computational Framework for Actuator Selection in
Assist-as-Needed Lower-Limb Exoskeletons*, IEEE Transactions on Medical Robotics and Bionics (submitted).

## Author

**Dimitrios Kavalieros** – Electrical Engineer, M.Sc., M.Ed.
University of Thessaly, Dept. of Computer Science and Biomedical Informatics
