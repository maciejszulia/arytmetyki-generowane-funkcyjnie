"""Weryfikacja: aksjomaty ciała + zgodność z jawnymi wzorami z dokumentacji.

Każdy model jest izomorficzną kopią pewnego podzbioru ℝ, więc aksjomaty
muszą zachodzić do precyzji maszyny — ale tylko na tym nośniku, na którym
f jest bijekcją. Dlatego testy dzielą się na:

  * modele, które są ciałami (f: D → ℝ bijekcja),
  * modele, które są jedynie półpierścieniem lub monoidem (brak zera,
    brak elementów przeciwnych) — to nie błąd implementacji, tylko fakt
    matematyczny, który dokumentacja musi nazywać wprost.
"""

import math

import numpy as np
import pytest
from scipy.optimize import brentq
from scipy.special import lambertw

from nna import (
    CubicLogistic,
    Geometric,
    Harmonic,
    HybridCooling,
    Kepler,
    Lambert,
    Logistic,
    Power,
    Radiative,
    Relativistic,
    Softplus,
    ThermalSaturation,
)

TOL = 1e-10

# (model, punkt testowy, tolerancja) — CubicLogistic ma f'(0.5)=0, więc
# odwrotność przy 0_f jest źle uwarunkowana i wymaga luźniejszej tolerancji.
FIELDS = [
    (Geometric(), (0.3, 2.0, 7.5), TOL),
    (Relativistic(c=1.0), (0.1, 0.4, 0.7), TOL),
    (Logistic(), (0.15, 0.5, 0.85), TOL),
    (CubicLogistic(), (0.2, 0.5, 0.8), 1e-4),
    (Lambert(), (0.3, 2.0, 7.5), TOL),
    (Softplus(), (0.3, 2.0, 7.5), TOL),
    (Kepler(0.85), (-1.0, 0.4, 3.0), TOL),
    (HybridCooling(0.1), (10.0, 40.0, 90.0), TOL),
    (ThermalSaturation(20.0, 65.0), (30.0, 42.0, 55.0), TOL),
]


def w0(z):
    """Gałąź główna W Lamberta jako niezależna referencja (SciPy)."""
    return float(np.real(lambertw(z)))


def check_field(model, a, b, c, tol=TOL):
    z, o = model.zero(), model.one()

    # 1. elementy neutralne
    assert model.add(a, z) == pytest.approx(a, abs=tol)
    assert model.mul(a, o) == pytest.approx(a, abs=tol)

    # 2. element przeciwny
    assert model.add(a, model.neg(a)) == pytest.approx(z, abs=tol)

    # 3. łączność i przemienność dodawania
    assert model.add(model.add(a, b), c) == pytest.approx(
        model.add(a, model.add(b, c)), abs=tol
    )
    assert model.add(a, b) == pytest.approx(model.add(b, a), abs=tol)

    # 4. rozdzielność mnożenia względem dodawania
    assert model.mul(a, model.add(b, c)) == pytest.approx(
        model.add(model.mul(a, b), model.mul(a, c)), abs=tol
    )

    # 5. zgodność skalarów: (1+2)⊙a = 1⊙a ⊕ 2⊙a
    assert model.scale(3.0, a) == pytest.approx(
        model.add(model.scale(1.0, a), model.scale(2.0, a)), abs=tol
    )

    # 6. f⁻¹ ∘ f = id
    assert model.f_inv(model.f(a)) == pytest.approx(a, abs=1e-9)


@pytest.mark.parametrize("model, points, tol", FIELDS)
def test_field_axioms(model, points, tol):
    check_field(model, *points, tol=tol)


# --- modele, które nie są ciałami -------------------------------------------


def test_harmonic_is_a_monoid_with_partial_addition():
    m = Harmonic()
    a, b = 2.0, 3.0
    # ⊕ to opór równoległy; ⊗ to zwykłe mnożenie
    assert m.add(a, b) == pytest.approx(a * b / (a + b), rel=1e-12)
    assert m.mul(a, b) == pytest.approx(a * b, rel=1e-12)
    assert m.one() == pytest.approx(1.0, rel=1e-12)
    # brak elementu neutralnego dodawania: 0_f = f⁻¹(0) nie istnieje
    with pytest.raises(ValueError):
        m.zero()
    # ⊕ nie jest działaniem totalnym: a ⊕ (−a) wymaga dzielenia przez zero
    with pytest.raises(ValueError):
        m.add(a, -a)


def test_power_arithmetic_is_a_monoid_without_inverses():
    for m in (Power(2.0), Power(3.0), Power(4.0)):
        a, b, c = 2.0, 3.0, 5.0
        # zamkniętość, łączność, przemienność, rozdzielność — wszystko działa
        assert m.add(m.add(a, b), c) == pytest.approx(m.add(a, m.add(b, c)), rel=1e-12)
        assert m.add(a, b) == pytest.approx(m.add(b, a), rel=1e-12)
        assert m.mul(a, m.add(b, c)) == pytest.approx(
            m.add(m.mul(a, b), m.mul(a, c)), rel=1e-12
        )
        # zero istnieje (0), ale nie ma liczb przeciwnych: f nie jest surjekcją
        assert m.zero() == pytest.approx(0.0, abs=1e-12)
        assert m.add(a, m.zero()) == pytest.approx(a, rel=1e-12)
        assert m.neg(a) == pytest.approx(0.0, abs=1e-12)


def test_radiative_has_no_representable_zero():
    m, a = Radiative(), 300.0
    assert m.zero() == pytest.approx(0.0, abs=1e-12)  # 0 K, poza dziedziną T > 0
    with pytest.raises(ValueError):
        m.add(a, 0.0)


# --- zgodność z jawnymi wzorami ---------------------------------------------


def test_geometric_closed_forms():
    m, a, b = Geometric(), 1.7, 2.9
    assert m.add(a, b) == pytest.approx(a * b, rel=1e-12)  # dodawanie = mnożenie
    assert m.sub(a, b) == pytest.approx(a / b, rel=1e-12)
    assert m.scale(3, a) == pytest.approx(a**3, rel=1e-12)
    assert m.unscale(a, 3) == pytest.approx(a ** (1 / 3), rel=1e-12)
    assert m.zero() == pytest.approx(1.0, rel=1e-12)
    assert m.one() == pytest.approx(math.e, rel=1e-12)
    assert m.mul(a, b) == pytest.approx(a ** math.log(b), rel=1e-12)


def test_power_closed_forms():
    a, b = 2.0, 3.0
    for p in (2.0, 3.0, 4.0):
        m = Power(p)
        assert m.add(a, b) == pytest.approx((a**p + b**p) ** (1 / p), rel=1e-12)
        assert m.scale(5, a) == pytest.approx(a * 5 ** (1 / p), rel=1e-12)
        assert m.mul(a, b) == pytest.approx(a * b, rel=1e-12)


def test_relativistic_is_einstein_velocity_addition():
    c, v1, v2 = 1.0, 0.6, 0.7
    m = Relativistic(c)
    assert m.add(v1, v2) == pytest.approx((v1 + v2) / (1 + v1 * v2 / c**2), rel=1e-12)
    assert m.add(0.9, 0.9) < 1.0
    assert m.scale(10.0, 0.5) < 1.0
    # dla ogromnych n float nasyca się do c — to ograniczenie IEEE 754, nie teorii
    assert m.scale(1e6, 0.5) <= 1.0


def test_logistic_closed_forms():
    m, a, b = Logistic(), 0.8, 0.6
    assert m.add(a, b) == pytest.approx(
        a * b / (a * b + (1 - a) * (1 - b)), rel=1e-12
    )
    assert m.scale(2, a) == pytest.approx(a**2 / (a**2 + (1 - a) ** 2), rel=1e-12)
    assert m.zero() == pytest.approx(0.5, rel=1e-12)
    assert m.one() == pytest.approx(math.e / (math.e + 1), rel=1e-12)
    # łączenie szans: logit(a) + logit(b) = logit(a ⊕ b)
    assert math.log(a / (1 - a)) + math.log(b / (1 - b)) == pytest.approx(
        math.log(m.add(a, b) / (1 - m.add(a, b))), rel=1e-10
    )


def test_lambert_closed_forms_and_lambert_w_reference():
    m, a, b = Lambert(), 0.4, 1.5
    assert m.zero() == pytest.approx(w0(1.0), rel=1e-12)  # stała Omega
    assert m.one() == pytest.approx(1.0, rel=1e-12)
    assert m.add(a, b) == pytest.approx(w0(a * b * math.exp(a + b)), rel=1e-12)
    assert m.sub(a, b) == pytest.approx(w0(a / b * math.exp(a - b)), rel=1e-12)
    assert m.scale(2, a) == pytest.approx(w0(a**2 * math.exp(2 * a)), rel=1e-12)
    assert m.neg(a) == pytest.approx(w0(1.0 / (a * math.exp(a))), rel=1e-12)


def test_lambert_no_overflow_for_large_arguments():
    m = Lambert()
    # e^y przepełnia float64 od ~709; odwrotność liczona Newtonem tego nie dotyka
    for y in (1e3, 1e6, 1e12):
        w = m.f_inv(y)
        assert np.isfinite(w)
        assert w + math.log(w) == pytest.approx(y, rel=1e-12)
    assert np.isfinite(m.add(1000.0, 2000.0))


def test_softplus_closed_forms():
    m, a, b = Softplus(), 0.7, 1.4
    assert m.add(a, b) == pytest.approx(
        math.log((math.exp(a) - 1) * (math.exp(b) - 1) + 1), rel=1e-12
    )
    assert m.scale(3, a) == pytest.approx(
        math.log((math.exp(a) - 1) ** 3 + 1), rel=1e-12
    )
    assert m.zero() == pytest.approx(math.log(2.0), rel=1e-12)
    assert m.one() == pytest.approx(math.log(math.e + 1), rel=1e-12)


def test_kepler_inverse_matches_brentq():
    k = 0.85
    m = Kepler(k)
    for y in (-2.0, 0.0, 1.3, 4.0):
        ref = brentq(lambda x: x + k * math.sin(x) - y, y - 1.0, y + 1.0, xtol=1e-14)
        assert m.f_inv(y) == pytest.approx(ref, abs=1e-9)


def test_thermal_models():
    rad = Radiative()
    # dwa identyczne źródła 300 K dają 300·2^(1/4) K ≈ 356,7 K, nie 600 K
    assert rad.add(300.0, 300.0) == pytest.approx(300.0 * 2**0.25, rel=1e-12)

    sat = ThermalSaturation(20.0, 80.0)
    assert sat.zero() == pytest.approx(50.0, rel=1e-12)
    assert 70.0 < sat.add(70.0, 75.0) < 80.0  # saturacja nie przekracza T_max

    cool = HybridCooling(0.1)
    assert cool.f_inv(cool.f(40.0)) == pytest.approx(40.0, rel=1e-12)


def test_scalar_input_returns_scalar():
    for model, points, _ in FIELDS:
        assert np.ndim(model.add(points[0], points[0])) == 0


def test_domains_are_enforced():
    with pytest.raises(ValueError):
        Geometric().f(0.0)
    with pytest.raises(ValueError):
        Harmonic().f(0.0)
    with pytest.raises(ValueError):
        Logistic().f(1.0)
    with pytest.raises(ValueError):
        Relativistic(1.0).f(1.0)
    with pytest.raises(ValueError):
        Lambert().f(-1.0)
    with pytest.raises(ValueError):
        Kepler(1.0)
    with pytest.raises(ValueError):
        ThermalSaturation(80.0, 20.0)
