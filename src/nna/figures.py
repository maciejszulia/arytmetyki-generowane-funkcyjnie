"""Wizualizacje modeli: matplotlib + seaborn.

Uruchomienie:  python -m nna.figures   (albo: nna-figures)
Wynik:         docs/figures/*.png (200 dpi, gotowe do paper.tex i README)
"""

from __future__ import annotations

import math
import os

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from .core import (
    Classical,
    Geometric,
    Kepler,
    Lambert,
    Logistic,
    Power,
    Relativistic,
    Softplus,
)
from .thermal import HybridCooling, Radiative, ThermalSaturation

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "docs", "figures")

PALETTE = {
    "classical": "#4c4c4c",
    "geometric": "#1f77b4",
    "power": "#ff7f0e",
    "lambert": "#2ca02c",
    "softplus": "#9467bd",
    "kepler": "#8c564b",
    "logistic": "#d62728",
}


def _style():
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams.update(
        {
            "figure.dpi": 110,
            "savefig.dpi": 200,
            "savefig.bbox": "tight",
            "axes.titleweight": "semibold",
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "legend.fontsize": 9,
            "legend.frameon": True,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def _save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    fig.savefig(path)
    plt.close(fig)
    print(f"  {name}")


# --- 1. generator i gęstość osi ---------------------------------------------


def fig_generators():
    x = np.linspace(0.2, 4.0, 400)
    models = [
        (Classical(), "klasyczna: $f(x)=x$", PALETTE["classical"], "--"),
        (Geometric(), "geometryczna: $\\ln x$", PALETTE["geometric"], "-"),
        (Lambert(), "Lamberta: $x+\\ln x$", PALETTE["lambert"], "-"),
        (Softplus(), "softplus: $\\ln(e^x-1)$", PALETTE["softplus"], "-"),
        (Kepler(0.85), "Keplera: $x+0{,}85\\sin x$", PALETTE["kepler"], "-"),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.7), constrained_layout=True)
    for m, label, color, ls in models:
        axes[0].plot(x, m.f(x), label=label, color=color, lw=2.4, ls=ls)
        axes[1].plot(x, 1.0 / np.gradient(m.f(x), x), label=label, color=color, lw=2.4, ls=ls)

    axes[0].set(title="Generator $f$ przenosi liczby do świata liniowego",
                xlabel="x", ylabel="$f(x)$", ylim=(-3.0, 5.0))
    axes[0].legend(loc="upper left")
    axes[1].set(title="Gęstość osi: $1/f'(x)$ — gdzie liczby się ściskają",
                xlabel="x", ylabel="jednostki $x$ na jednostkę $f$",
                ylim=(0, 6.5))
    axes[1].legend(loc="upper right")
    _save(fig, "fig01_generators.png")


# --- 2. nowe dodawanie -------------------------------------------------------


def fig_addition():
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.7), constrained_layout=True)

    x = np.linspace(0.1, 4.0, 400)
    curves = [
        (Classical(), "klasyczna: $0{,}8+x$", PALETTE["classical"], "--"),
        (Geometric(), "geometryczna: $0{,}8x$", PALETTE["geometric"], "-"),
        (Lambert(), "Lamberta: $W(0{,}8x\\,e^{0{,}8+x})$", PALETTE["lambert"], "-"),
        (Softplus(), "softplus", PALETTE["softplus"], "-"),
        (Power(2.0), "pitagorejska: $\\sqrt{0{,}64+x^2}$", PALETTE["power"], "-"),
        (Kepler(0.85), "Keplera", PALETTE["kepler"], "-"),
    ]
    for m, label, color, ls in curves:
        axes[0].plot(x, m.add(0.8, x), label=label, color=color, lw=2.4, ls=ls)
    axes[0].set(title="Dodawanie stałej $a=0{,}8$ w różnych światach",
                xlabel="x", ylabel="$0{,}8 \\oplus x$", ylim=(0, 6.0))
    axes[0].legend(loc="upper left")

    xl = np.linspace(0.02, 0.98, 400)
    lg = Logistic()
    axes[1].plot(xl, lg.add(0.8, xl), color=PALETTE["logistic"], lw=2.8,
                 label="logistyczna: $0{,}8 \\oplus x$")
    axes[1].plot(xl, xl, color=PALETTE["classical"], ls="--", lw=1.4, label="$y=x$")
    axes[1].axhline(1.0, color="#999999", ls=":", lw=1.2)
    axes[1].axhline(0.0, color="#999999", ls=":", lw=1.2)
    axes[1].axvline(0.5, color=PALETTE["logistic"], ls=":", lw=1.2, alpha=0.7)
    axes[1].scatter([0.5], [0.8], s=70, color=PALETTE["logistic"], zorder=5)
    axes[1].annotate("nowe zero $0_f=0{,}5$\n(neutralne dla $\\oplus$)",
                     xy=(0.5, 0.8), xytext=(0.56, 0.42), fontsize=9,
                     arrowprops=dict(arrowstyle="->", color=PALETTE["logistic"]))
    axes[1].set(title="Model ograniczony: wynik zostaje w $(0,1)$",
                xlabel="x", ylabel="$0{,}8 \\oplus x$", ylim=(-0.02, 1.02))
    axes[1].legend(loc="lower right")
    _save(fig, "fig02_addition.png")


# --- 3. mapy cieplne ---------------------------------------------------------


def fig_heatmaps():
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 10.0), constrained_layout=True)
    specs = [
        (Classical(), np.linspace(0, 3, 220), "klasyczna: $x+y$", "rocket"),
        (Geometric(), np.linspace(0.15, 3, 220), "geometryczna: $xy$", "mako"),
        (Logistic(), np.linspace(0.01, 0.99, 220), "logistyczna: łączenie szans", "icefire"),
        (Relativistic(1.0), np.linspace(-0.95, 0.95, 220), "relatywistyczna: $\\frac{x+y}{1+xy}$", "viridis"),
    ]
    for ax, (m, grid, title, cmap) in zip(axes.ravel(), specs):
        X, Y = np.meshgrid(grid, grid)
        Z = m.add(X, Y)
        sns.heatmap(Z, ax=ax, cmap=cmap, xticklabels=False, yticklabels=False,
                    cbar_kws={"label": "$x \\oplus y$", "shrink": 0.85})
        ax.set(title=title, xlabel="x", ylabel="y")
        ax.set_aspect("equal")
    _save(fig, "fig03_heatmaps.png")


# --- 4. przejście fazowe Lamberta -------------------------------------------


def fig_phase_transition():
    m = Lambert()
    a = 0.8
    x = np.logspace(-3, 3, 500)

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.7), constrained_layout=True)
    axes[0].plot(x, m.add(a, x), color=PALETTE["lambert"], lw=2.8, label="$0{,}8 \\oplus x$")
    axes[0].plot(x, a * x, color=PALETTE["geometric"], ls="--", lw=1.6, label="$0{,}8\\cdot x$ (mnożenie)")
    axes[0].plot(x, a + x, color=PALETTE["classical"], ls=":", lw=1.8, label="$0{,}8+x$ (dodawanie)")
    axes[0].set(xscale="log", yscale="log", xlabel="x", ylabel="wynik",
                title="Jedno działanie, dwa reżimy")
    axes[0].legend(loc="upper left")

    # asymptotyki: dla małych x wynik ≈ (a·e^a)·x, dla dużych ≈ a + x
    ratio_mul = np.abs(m.add(a, x) - a * math.exp(a) * x) / np.abs(m.add(a, x))
    ratio_add = np.abs(m.add(a, x) - (a + x)) / np.abs(m.add(a, x))
    axes[1].plot(x, ratio_mul, color=PALETTE["geometric"], lw=2.4,
                 label="błąd względny vs $(a e^a)\,x$")
    axes[1].plot(x, ratio_add, color=PALETTE["classical"], lw=2.4, ls="--",
                 label="błąd względny vs $a+x$")
    axes[1].axvline(1.0, color="#999999", ls=":", lw=1.2)
    axes[1].text(1.15, 0.55, "$x \\approx 1$: zmiana reżimu", fontsize=9, color="#555555")
    axes[1].set(xscale="log", yscale="log", xlabel="x", ylabel="błąd względny",
                title="Przejście fazowe: od mnożenia do dodawania", ylim=(1e-4, 3))
    axes[1].legend(loc="lower left")
    _save(fig, "fig04_phase_transition.png")


# --- 5. Kepler ---------------------------------------------------------------


def fig_kepler():
    t = np.linspace(0, 12, 600)
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.7), constrained_layout=True)

    for k, color, ls in [(0.5, PALETTE["kepler"], "--"), (0.85, PALETTE["kepler"], "-")]:
        m = Kepler(k)
        pos = m.scale(t, 1.0)
        axes[0].plot(t, pos, color=color, lw=2.4, ls=ls, label=f"$t \\odot 1$, k={k}")
        vel = np.gradient(pos, t)
        axes[1].plot(t, vel, color=color, lw=2.4, ls=ls, label=f"k={k}")
    axes[0].plot(t, t, color=PALETTE["classical"], ls=":", lw=1.6, label="ruch klasyczny $x=t$")
    axes[0].set(xlabel="czas t", ylabel="położenie", title="Ruch jednostajny w ziarnistej osi")
    axes[0].legend(loc="upper left")

    axes[1].axhline(1.0, color=PALETTE["classical"], ls=":", lw=1.2, label="prędkość klasyczna")
    axes[1].set(xlabel="czas t", ylabel="$dx/dt$", title="Prędkość: spowolnienia w węzłach sieci")
    axes[1].legend(loc="upper right")
    _save(fig, "fig05_kepler.png")


# --- 6-8. termika ------------------------------------------------------------


def fig_thermal_radiation():
    m = Radiative()
    T2 = np.linspace(100, 1000, 400)
    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    ax.plot(T2, m.add(300.0, T2), color="#d62728", lw=2.8,
            label="$300\\,\\mathrm{K} \\oplus T_2$ (strumienie się dodają)")
    ax.plot(T2, 300.0 + T2, color=PALETTE["classical"], ls="--", lw=1.6,
            label="naiwne $300 + T_2$")
    ax.plot(T2, T2, color="#999999", ls=":", lw=1.2, label="$T_2$")
    ax.scatter([300], [m.add(300.0, 300.0)], color="#d62728", zorder=5)
    ax.annotate("$300 \\oplus 300 = 300\\sqrt[4]{2} \\approx 356{,}7\\,\\mathrm{K}$",
                xy=(300, m.add(300.0, 300.0)), xytext=(430, 180), fontsize=9,
                arrowprops=dict(arrowstyle="->", color="#d62728"))
    ax.set(xlabel="$T_2$ [K]", ylabel="temperatura wypadkowa [K]",
           title="Promieniowanie cieplne: arytmetyka $T^4$ (Stefan–Boltzmann)")
    ax.legend(loc="upper left")
    _save(fig, "fig06_thermal_radiation.png")


def fig_thermal_cooling():
    alpha, k_rate, dT0 = 0.05, 0.08, 80.0
    m = HybridCooling(alpha)
    t = np.linspace(0, 60, 400)

    # w tej arytmetyce stygnięcie jest liniowe w zmiennej f: f(ΔT) = f(ΔT0) − k·t
    f0 = m.f(dT0)
    hybrid = np.array([m.f_inv(f0 - k_rate * tt) for tt in t])
    newton = dT0 * np.exp(-k_rate * t)
    linear = dT0 - k_rate * dT0 * t / 10.0

    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    ax.plot(t, newton, color=PALETTE["classical"], ls="--", lw=1.8, label="Newton: $e^{-kt}$")
    ax.plot(t, hybrid, color=PALETTE["lambert"], lw=2.8,
            label="hybrydowe: liniowe w $\\alpha\\Delta T+\\ln\\Delta T$")
    ax.plot(t, np.maximum(linear, 0), color=PALETTE["geometric"], ls=":", lw=1.6, label="liniowe w $\\Delta T$")
    ax.set(xlabel="czas [min]", ylabel="$\\Delta T$ [K]",
           title="Stygnięcie: konwekcja + promieniowanie w jednym równaniu liniowym")
    ax.legend(loc="upper right")
    _save(fig, "fig07_thermal_cooling.png")


def fig_thermal_saturation():
    m = ThermalSaturation(20.0, 65.0)
    n = np.linspace(0, 12, 400)
    T0, T_first = 35.0, 40.0

    # jedna „dawka" = tyle samo log-szans, ile daje pierwsze +5 °C
    dose = m.f_inv(m.f(T_first) - m.f(T0))
    sat = np.array([m.add(T0, m.scale(nn, dose)) for nn in n])
    classical = T0 + (T_first - T0) * n

    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    ax.plot(n, sat, color="#2ca02c", lw=2.8,
            label="saturacja: $35\\,^\\circ\\mathrm{C} \\oplus (n\\odot\\mathrm{dawka})$")
    ax.plot(n, classical, color=PALETTE["classical"], ls="--", lw=1.6,
            label="sterowanie klasyczne: $35+5n$")
    ax.axhline(65.0, color="#d62728", ls=":", lw=1.4, label="limit $T_{\\max}=65\\,^\\circ\\mathrm{C}$")
    ax.axhline(20.0, color="#999999", ls=":", lw=1.0)
    ax.fill_between(n, 65.0, classical, where=classical > 65.0, color="#d62728", alpha=0.12)
    ax.annotate("przegrzanie w modelu klasycznym", xy=(7.0, 65.0), xytext=(6.0, 82),
                fontsize=9, color="#d62728",
                arrowprops=dict(arrowstyle="->", color="#d62728"))
    ax.set(xlabel="skumulowana liczba dawek ciepła n", ylabel="temperatura [$^\\circ$C]",
           title="Sterowanie pompą ciepła: arytmetyka saturacji nie przekracza limitu",
           ylim=(15, 95))
    ax.legend(loc="lower right")
    _save(fig, "fig08_thermal_saturation.png")


def main():
    _style()
    print(f"Zapisuję wykresy do {OUT}")
    fig_generators()
    fig_addition()
    fig_heatmaps()
    fig_phase_transition()
    fig_kepler()
    fig_thermal_radiation()
    fig_thermal_cooling()
    fig_thermal_saturation()
    print("Gotowe.")


if __name__ == "__main__":
    main()
