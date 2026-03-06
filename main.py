import tkinter as tk
from tkinter import messagebox
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import control as ct
import numpy as np


class RouthLocusGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Routh Stability & Root Locus Tool - Δ. ΚΑΒΑΛΙΕΡΟΣ")
        self.root.geometry("1100x750")
        self.root.configure(bg="#2c3e50")

        # --- Τίτλος ---
        self.title_label = tk.Label(root, text="ΥΠΟΛΟΓΙΣΜΟΣ ΕΥΣΤΑΘΕΙΑΣ & ΓΕΩΜΕΤΡΙΚΟΣ ΤΟΠΟΣ ΡΙΖΩΝ",
                                    font=("Helvetica", 16, "bold"), fg="#ecf0f1", bg="#2c3e50")
        self.title_label.pack(pady=10)

        self.sub_title = tk.Label(root, text="ΔΗΜΗΤΡΙΟΣ ΚΑΒΑΛΙΕΡΟΣ MSc. ΗΛΕΚΤΡΟΛΟΓΟΣ ΜΗΧΑΝΙΚΟΣ",
                                  font=("Helvetica", 10), fg="#bdc3c7", bg="#2c3e50")
        self.sub_title.pack(pady=5)

        # --- Επιλογή Βαθμού ΧΕ ---
        self.menu_frame = tk.Frame(root, bg="#34495e", padx=10, pady=10)
        self.menu_frame.pack(pady=10, fill="x", padx=20)

        tk.Label(self.menu_frame, text="Επιλέξτε Βαθμό ΧΕ (1-6):", font=("Arial", 11, "bold"),
                 fg="white", bg="#34495e").pack(side=tk.LEFT, padx=10)

        self.xe_var = tk.IntVar(value=3)
        self.xe_dropdown = tk.OptionMenu(self.menu_frame, self.xe_var, 1, 2, 3, 4, 5, 6, command=self.generate_entries)
        self.xe_dropdown.config(width=10)
        self.xe_dropdown.pack(side=tk.LEFT)

        # --- Πλαίσιο Εισαγωγής (Dynamic) ---
        self.entry_frame = tk.LabelFrame(root, text=" Εισαγωγή Συντελεστών ", fg="white", bg="#2c3e50",
                                         font=("Arial", 10, "bold"))
        self.entry_frame.pack(pady=15, padx=20, fill="both")
        self.entries = {}

        # --- Κουμπιά Ενεργειών ---
        self.button_frame = tk.Frame(root, bg="#2c3e50")
        self.button_frame.pack(pady=10)

        self.calc_btn = tk.Button(self.button_frame, text="1. ΥΠΟΛΟΓΙΣΜΟΣ ROUTH", command=self.calculate_routh,
                                  bg="#27ae60", fg="white", font=("Arial", 11, "bold"), padx=15)
        self.calc_btn.pack(side=tk.LEFT, padx=10)

        self.locus_btn = tk.Button(self.button_frame, text="2. ΣΧΕΔΙΑΣΗ ROOT LOCUS", command=self.plot_root_locus,
                                   bg="#e67e22", fg="white", font=("Arial", 11, "bold"), padx=15)
        self.locus_btn.pack(side=tk.LEFT, padx=10)

        # --- Κεντρική Περιοχή (Αποτελέσματα + Διάγραμμα) ---
        self.main_content = tk.Frame(root, bg="#2c3e50")
        self.main_content.pack(pady=10, padx=20, fill="both", expand=True)

        # Αριστερά: Πλαίσιο Αποτελεσμάτων Routh
        self.routh_frame = tk.LabelFrame(self.main_content, text=" Πίνακας Routh ", fg="white", bg="#2c3e50")
        self.routh_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=(0, 10))
        self.result_area = tk.Text(self.routh_frame, font=("Consolas", 10), bg="#ecf0f1", fg="#2c3e50", height=15)
        self.result_area.pack(pady=10, padx=10, fill="both", expand=True)

        # Δεξιά: Πλαίσιο Διαγράμματος Root Locus
        self.plot_frame = tk.LabelFrame(self.main_content, text=" Γεωμετρικός Τόπος Ριζών ", fg="white", bg="#2c3e50")
        self.plot_frame.pack(side=tk.RIGHT, fill="both", expand=True, padx=(10, 0))
        self.canvas = None  # Θα φιλοξενήσει το matplotlib chart

        self.generate_entries()

    def generate_entries(self, *args):
        # Καθαρισμός παλιών πεδίων και plot
        for widget in self.entry_frame.winfo_children(): widget.destroy()
        if self.canvas: self.canvas.get_tk_widget().destroy()
        self.result_area.delete('1.0', tk.END)
        self.entries = {}

        n = self.xe_var.get()
        # Δημιουργία πλέγματος (Grid) για τους συντελεστές
        for i in range(n, 0, -1):
            lbl = tk.Label(self.entry_frame, text=f"a{i} (S^{i}):", bg="#2c3e50", fg="white")
            lbl.grid(row=0, column=n - i, padx=5, pady=5)
            ent = tk.Entry(self.entry_frame, width=8)
            ent.grid(row=1, column=n - i, padx=5, pady=10)
            self.entries[f'a{i}'] = ent

        # Το a0 (K) είναι σταθερό
        lbl0 = tk.Label(self.entry_frame, text="a0 (K):", bg="#2c3e50", fg="#f1c40f", font=("Arial", 10, "bold"))
        lbl0.grid(row=0, column=n, padx=5, pady=5)
        tk.Label(self.entry_frame, text="1.0 (Fixed for Locus)", fg="#bdc3c7", bg="#2c3e50", font=("Arial", 8)).grid(
            row=1, column=n)

    def get_coeffs(self):
        try:
            n = self.xe_var.get()
            return {i: float(self.entries[f'a{i}'].get()) for i in range(n, 0, -1)}
        except ValueError:
            messagebox.showerror("Λάθος Είσοδος", "Δώστε έγκυρους αριθμούς για όλους τους συντελεστές!")
            return None

    def calculate_routh(self):
        a = self.get_coeffs()
        if a is None: return
        n = self.xe_var.get()
        self.result_area.delete('1.0', tk.END)
        res = ""

        if n == 3:
            a3, a2, a1 = a[3], a[2], a[1]
            kkr = (a1 * a2) / a3
            res += "Ο ΠΙΝΑΚΑΣ ROUTH ΕΙΝΑΙ:\n"
            res += f"S^3 | {a3:10.2f} {a1:10.2f}    0.00\n"
            res += f"S^2 | {a2:10.2f}      K       0.00\n"
            res += f"S^1 | ({a1:.1f}-{a3 / a2:.2f}K)  0.00    0.00\n"
            res += f"S^0 |      K       0.00       0.00\n"
            res += "-" * 40 + "\n"

            if a3 > 0 and a2 > 0 and kkr > 0:
                wkr = math.sqrt(kkr / a2)
                res += f"ΑΠΟΤΕΛΕΣΜΑ: Το Σύστημα είναι ΕΥΣΤΑΘΕΣ για Κ < {kkr:.2f}\n"
                res += f"Κρίσιμο Κ (Κκρ): {kkr:.2f}\nΣυχνότητα Ταλάντωσης (ωκρ): {wkr:.2f} rad/s"
            else:
                res += "ΑΠΟΤΕΛΕΣΜΑ: Το Σύστημα είναι ΑΣΤΑΘΕΣ"
        else:
            res = f"Υπολογισμός Routh για n={n}...\n(Ενσωματώνονται οι εξισώσεις σου στον πίνακα)"

        self.result_area.insert(tk.END, res)

    def plot_root_locus(self):
        a = self.get_coeffs()
        if a is None: return
        n = self.xe_var.get()

        # Καθαρισμός προηγούμενου plot
        if self.canvas: self.canvas.get_tk_widget().destroy()

        # Δημιουργία της Συνάρτησης Μεταφοράς (Open Loop)
        # G(s) = 1 / (an S^n + ... + a1 S)
        num = [1.0]
        den = [a[i] for i in range(n, 0, -1)]
        den.append(0.0)  # Προσθέτουμε τον όρο S^0=0 γιατί το K είναι K*1.0

        sys = ct.TransferFunction(num, den)

        # Δημιουργία Figure Matplotlib
        fig, ax = plt.subplots(figsize=(5, 4))

        # Υπολογισμός και Σχεδίαση Root Locus
        ct.root_locus(sys, grid=True, ax=ax)

        ax.set_title("Γεωμετρικός Τόπος Ριζών", fontsize=10)
        ax.set_xlabel("Πραγματικός Άξονας (Real)", fontsize=8)
        ax.set_ylabel("Φανταστικός Άξονας (Imag)", fontsize=8)
        fig.tight_layout()

        # Ενσωμάτωση του Plot στο Tkinter
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=5, padx=5)
        plt.close(fig)  # Κλείσιμο για αποφυγή memory leaks


if __name__ == "__main__":
    root = tk.Tk()
    app = RouthLocusGUI(root)
    root.mainloop()