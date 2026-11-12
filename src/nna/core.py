"""Arytmetyki generowane funkcyjnie (rachunek nie-Newtonowski).

Jeden izomorfizm f przenosi strukturę ciała liczb rzeczywistych na dowolny
zbiór D. Wszystkie działania wynikają z czterech wzorów:

    a ⊕ b = f⁻¹(f(a) + f(b))        a ⊖ b = f⁻¹(f(a) − f(b))
    n ⊙ a = f⁻¹(n · f(a))           a ⊘ n = f⁻¹(f(a) / n)

Podklasy definiują wyłącznie parę (f, f⁻¹); reszta jest dziedziczona.
Dzięki temu nie da się „pomylić się w tabeli wzorów”: działania są zawsze
poprawne, a tabele w dokumentacji są ich jawnymi, uproszczonymi postaciami
(testowanymi w tests/test_axioms.py).
"""

from __future__ import annotations

import numpy as np

def _num(x):
    """0-d ndarray → float, aby porównania skalarne działały naturalnie."""
    x = np.asarray(x, dtype=float)
    return float(x) if x.ndim == 0 else x


__all__ = [
    "Arithmetic",
    "Classical",
    "Geometric",
    "Harmonic",
    "Power",
    "Relativistic",
    "Logistic",
    "CubicLogistic",
    "Lambert",
    "Softplus",
    "Kepler",
]


class Arithmetic:
    """Bazowa klasa: para (f, f⁻¹) plus przeniesione działania ciała."""

    name = "klasyczna"
    generator = r"f(x)=x"
    inverse = r"f^{-1}(y)=y"
    domain = "ℝ"

    # --- primitives ---------------------------------------------------
    def f(self, x):
        raise NotImplementedError

    def f_inv(self, y):
        raise NotImplementedError

    # --- transported field operations ---------------------------------
    def add(self, a, b):
        return self.f_inv(self.f(a) + self.f(b))

    def sub(self, a, b):
        return self.f_inv(self.f(a) - self.f(b))

    def scale(self, n, a):
        """n ⊙ a — mnożenie przez zwykły skalar."""
        return self.f_inv(n * self.f(a))

    def unscale(self, a, n):
        """a ⊘ n — dzielenie przez zwykły skalar."""
        return self.f_inv(self.f(a) / n)

    def mul(self, a, b):
        """a ⊗ b — pełne mnożenie w nowym ciele."""
        return self.f_inv(self.f(a) * self.f(b))

    def div(self, a, b):
        """a ⊘_f b — pełne dzielenie w nowym ciele."""
        return self.f_inv(self.f(a) / self.f(b))

    def neg(self, a):
        """⊖a — element przeciwny."""
        return self.f_inv(-self.f(a))

    def zero(self):
        """0_f = f⁻¹(0) — neutralny element dodawania."""
        return self.f_inv(0.0)

    def one(self):
        """1_f = f⁻¹(1) — neutralny element mnożenia."""
        return self.f_inv(1.0)

    def power(self, a, n):
        """a^⊗n — n-krotne mnożenie ⊗."""
        return self.f_inv(self.f(a) ** n)

    def root(self, a, n):
        """n-ty pierwiastek w sensie ⊗."""
        return self.f_inv(self.f(a) ** (1.0 / n))

    def mean(self, values):
        """Średnia Kołmogorowa M_f = f⁻¹(mean(f(x_i)))."""
        return self.f_inv(np.mean(self.f(np.asarray(values, dtype=float))))

    def distance(self, a, b):
        """Odległość d_f(a,b) = f⁻¹(|f(a) − f(b)|)."""
        return self.f_inv(np.abs(self.f(a) - self.f(b)))


class Classical(Arithmetic):
    name = "klasyczna"
    generator = r"f(x)=x"
    inverse = r"f^{-1}(y)=y"
    domain = "ℝ"

    def f(self, x):
        return np.asarray(x, dtype=float)

    def f_inv(self, y):
        return np.asarray(y, dtype=float)


class Geometric(Arithmetic):
    """Dodawanie = mnożenie. Suwak logarytmiczny, Napier 1614."""

    name = "geometryczna"
    generator = r"f(x)=\ln x"
    inverse = r"f^{-1}(y)=e^{y}"
    domain = "x > 0"

    def f(self, x):
        x = np.asarray(x, dtype=float)
        if np.any(x <= 0.0):
            raise ValueError("arytmetyka geometryczna: wymagane x > 0")
        return np.log(x)

    def f_inv(self, y):
        return np.exp(np.asarray(y, dtype=float))


class Harmonic(Arithmetic):
    """Dodawanie = opór zastępczy równoległy. f = f⁻¹ = 1/x."""

    name = "harmoniczna"
    generator = r"f(x)=1/x"
    inverse = r"f^{-1}(y)=1/y"
    domain = "x ≠ 0"

    def f(self, x):
        x = np.asarray(x, dtype=float)
        if np.any(x == 0.0):
            raise ValueError("arytmetyka harmoniczna: wymagane x ≠ 0")
        return 1.0 / x

    def f_inv(self, y):
        y = np.asarray(y, dtype=float)
        if np.any(y == 0.0):
            raise ValueError("arytmetyka harmoniczna: f⁻¹(0) nie istnieje")
        return 1.0 / y


class Power(Arithmetic):
    """Arytmetyka p-tej potęgi: dodawanie to p-norma.

    p=2 — pitagorejska (przeciwprostokątna), p=3 — sześcienna,
    p=4 — promieniowanie cieplne (Stefan–Boltzmann).
    """

    def __init__(self, p: float = 2.0):
        if p <= 0:
            raise ValueError("wykładnik p musi być dodatni")
        self.p = float(p)
        self.name = f"potęgowa p={p:g}"
        self.generator = rf"f(x)=x^{{{p:g}}}"
        self.inverse = rf"f^{{-1}}(y)=y^{{1/{p:g}}}"
        self.domain = "x ≥ 0"

    def f(self, x):
        x = np.asarray(x, dtype=float)
        if np.any(x < 0.0):
            raise ValueError("arytmetyka potęgowa: wymagane x ≥ 0")
        return x ** self.p

    def f_inv(self, y):
        y = np.asarray(y, dtype=float)
        return _num(np.maximum(y, 0.0) ** (1.0 / self.p))


class Relativistic(Arithmetic):
    """Składanie prędkości Einsteina: nic nie przekroczy c."""

    def __init__(self, c: float = 1.0):
        self.c = float(c)
        self.name = "relatywistyczna"
        self.generator = r"f(v)=\operatorname{artanh}(v/c)"
        self.inverse = r"f^{-1}(y)=c\tanh y"
        self.domain = "|v| < c"

    def f(self, x):
        v = np.asarray(x, dtype=float) / self.c
        if np.any(np.abs(v) >= 1.0):
            raise ValueError("arytmetyka relatywistyczna: wymagane |v| < c")
        return np.arctanh(v)

    def f_inv(self, y):
        return self.c * np.tanh(np.asarray(y, dtype=float))


class Logistic(Arithmetic):
    """Saturacja w (0,1): dodawanie = łączenie szans (log-odds)."""

    name = "logistyczna"
    generator = r"f(x)=\ln\frac{x}{1-x}"
    inverse = r"f^{-1}(y)=\frac{1}{1+e^{-y}}"
    domain = "0 < x < 1"

    def f(self, x):
        x = np.asarray(x, dtype=float)
        if np.any((x <= 0.0) | (x >= 1.0)):
            raise ValueError("arytmetyka logistyczna: wymagane 0 < x < 1")
        return np.log(x) - np.log1p(-x)

    def f_inv(self, y):
        y = np.asarray(y, dtype=float)
        out = np.empty_like(y)
        pos = y >= 0.0
        out[pos] = 1.0 / (1.0 + np.exp(-y[pos]))
        ey = np.exp(y[~pos])
        out[~pos] = ey / (1.0 + ey)
        return _num(out)


class CubicLogistic(Arithmetic):
    """Złożenie 2. rzędu: logit podniesiony do sześcianu (polaryzacja)."""

    name = "sześcienno-logistyczna"
    generator = r"f(x)=\left(\ln\frac{x}{1-x}\right)^{3}"
    inverse = r"f^{-1}(y)=\frac{1}{1+e^{-\sqrt[3]{y}}}"
    domain = "0 < x < 1"

    def f(self, x):
        x = np.asarray(x, dtype=float)
        if np.any((x <= 0.0) | (x >= 1.0)):
            raise ValueError("model sześcienno-logistyczny: wymagane 0 < x < 1")
        return (np.log(x) - np.log1p(-x)) ** 3

    def f_inv(self, y):
        y = np.asarray(y, dtype=float)
        return Logistic().f_inv(np.cbrt(y))


class Lambert(Arithmetic):
    """f(x) = x + ln x — płynne przejście mnożenie → dodawanie.

    Odwrotność to gałąź główna W Lamberta: f⁻¹(y) = W(e^y), liczona Newtonem
    bezpośrednio z równania w + ln w = y (brak przepełnienia e^y).
    """

    name = "Lamberta"
    generator = r"f(x)=x+\ln x"
    inverse = r"f^{-1}(y)=W(e^{y})"
    domain = "x > 0"

    def f(self, x):
        x = np.asarray(x, dtype=float)
        if np.any(x <= 0.0):
            raise ValueError("arytmetyka Lamberta: wymagane x > 0")
        return x + np.log(x)

    def f_inv(self, y):
        y = np.asarray(y, dtype=float)
        # start: dla y>0 w≈y, dla y<0 w≈e^y (underflow poniżej -745 jest nieszkodliwy)
        w = np.where(y > 0.0, y, np.exp(np.clip(y, -745.0, 700.0)))
        w = np.maximum(w, 1e-308)
        for _ in range(100):
            step = (w + np.log(w) - y) / (1.0 + 1.0 / w)
            w = w - step
            if np.all(np.abs(step) <= 1e-15 * np.maximum(1.0, np.abs(w))):
                break
        return _num(w)


class Softplus(Arithmetic):
    """f(x) = ln(e^x − 1): gładki próg; dodawanie ≈ LogSumExp."""

    name = "softplus"
    generator = r"f(x)=\ln(e^{x}-1)"
    inverse = r"f^{-1}(y)=\ln(e^{y}+1)"
    domain = "x > 0"

    def f(self, x):
        x = np.asarray(x, dtype=float)
        if np.any(x <= 0.0):
            raise ValueError("arytmetyka softplus: wymagane x > 0")
        return np.log(np.expm1(x))

    def f_inv(self, y):
        return np.logaddexp(0.0, np.asarray(y, dtype=float))


class Kepler(Arithmetic):
    """f(x) = x + k·sin x — „ziarnista” oś liczbowa, k ∈ (0,1)."""

    def __init__(self, k: float = 0.85):
        if not 0.0 < k < 1.0:
            raise ValueError("współczynnik ziarnistości k musi należeć do (0, 1)")
        self.k = float(k)
        self.name = f"Keplera k={k:g}"
        self.generator = rf"f(x)=x+{k:g}\sin x"
        self.inverse = r"f^{-1}(y)\ \text{numerycznie (Newton)}"
        self.domain = "ℝ"

    def f(self, x):
        x = np.asarray(x, dtype=float)
        return x + self.k * np.sin(x)

    def f_inv(self, y):
        y = np.asarray(y, dtype=float)
        x = y.copy()
        for _ in range(100):
            step = (x + self.k * np.sin(x) - y) / (1.0 + self.k * np.cos(x))
            x = x - step
            if np.all(np.abs(step) <= 1e-15 * np.maximum(1.0, np.abs(x))):
                break
        return _num(x)
