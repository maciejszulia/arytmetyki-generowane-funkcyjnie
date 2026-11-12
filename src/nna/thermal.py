"""Modele termiczne: promieniowanie, chłodzenie hybrydowe, saturacja."""

from __future__ import annotations

import numpy as np

from .core import Arithmetic, Lambert, Logistic, _num

__all__ = ["Radiative", "HybridCooling", "ThermalSaturation"]


class Radiative(Arithmetic):
    """Prawo Stefana–Boltzmanna: strumienie rosną jak T⁴, więc temperatury
    wypadkowe dodają się w arytmetyce czwartej potęgi."""

    name = "radiacyjna (T⁴)"
    generator = r"f(T)=T^{4}"
    inverse = r"f^{-1}(y)=\sqrt[4]{y}"
    domain = "T > 0 K"

    def f(self, x):
        x = np.asarray(x, dtype=float)
        if np.any(x <= 0.0):
            raise ValueError("model radiacyjny: temperatura w kelwinach, T > 0")
        return x ** 4

    def f_inv(self, y):
        return _num(np.maximum(np.asarray(y, dtype=float), 0.0) ** 0.25)


class HybridCooling(Arithmetic):
    """Chłodzenie konwekcją (liniowo) i promieniowaniem (logarytmicznie):
    f(ΔT) = α·ΔT + ln(ΔT). Odwrotność: α·w + ln w = y."""

    def __init__(self, alpha: float = 0.1):
        if alpha <= 0:
            raise ValueError("współczynnik α musi być dodatni")
        self.alpha = float(alpha)
        self.name = f"chłodzenie hybrydowe α={alpha:g}"
        self.generator = rf"f(\Delta T)={alpha:g}\Delta T+\ln\Delta T"
        self.inverse = r"f^{-1}(y)=W(\alpha e^{y})/\alpha"
        self.domain = "ΔT > 0"

    def f(self, x):
        x = np.asarray(x, dtype=float)
        if np.any(x <= 0.0):
            raise ValueError("model chłodzenia: wymagane ΔT > 0")
        return self.alpha * x + np.log(x)

    def f_inv(self, y):
        # α·w + ln w = y  ⇔  u + ln u = y + ln α, gdzie u = α·w
        u = Lambert().f_inv(np.asarray(y, dtype=float) + np.log(self.alpha))
        return _num(u / self.alpha)


class ThermalSaturation(Arithmetic):
    """Saturacja między T_min i T_max (pompy ciepła, materiały PCM)."""

    def __init__(self, t_min: float = 20.0, t_max: float = 65.0):
        if t_min >= t_max:
            raise ValueError("wymagane t_min < t_max")
        self.t_min = float(t_min)
        self.t_max = float(t_max)
        self.name = f"saturacja cieplna ({t_min:g}–{t_max:g} °C)"
        self.generator = r"f(T)=\ln\frac{T-T_{\min}}{T_{\max}-T}"
        self.inverse = r"f^{-1}(y)=T_{\min}+(T_{\max}-T_{\min})\sigma(y)"
        self.domain = f"{t_min:g} < T < {t_max:g}"

    def f(self, x):
        x = np.asarray(x, dtype=float)
        if np.any((x <= self.t_min) | (x >= self.t_max)):
            raise ValueError(f"model saturacji: wymagane {self.t_min} < T < {self.t_max}")
        return np.log(x - self.t_min) - np.log(self.t_max - x)

    def f_inv(self, y):
        return _num(self.t_min + (self.t_max - self.t_min) * Logistic().f_inv(y))
