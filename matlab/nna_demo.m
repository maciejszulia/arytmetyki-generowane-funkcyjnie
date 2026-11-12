%% Arytmetyki generowane funkcyjnie — demo MATLAB / Octave
%  Uruchomienie:  matlab -batch "nna_demo"      albo:  octave nna_demo.m
%  Odpowiednik Pythona: src/nna/core.py + src/nna/figures.py
%
%  Każdy model to para (f, f^-1); działania wynikają z czterech wzorów:
%     a (+) b = f^-1(f(a) + f(b))     a (-) b = f^-1(f(a) - f(b))
%     n (*) a = f^-1(n * f(a))        a (/) n = f^-1(f(a) / n)

clear; clc; close all;

%% 1. Definicje modeli ----------------------------------------------------
% Lamberta: f(x) = x + ln x,  f^-1(y) = W(e^y), liczona Newtonem na w + ln w = y
lam.f    = @(x) x + log(x);
lam.finv = @(y) arrayfun(@lambert_inv, y);
lam.name = 'Lamberta: x + ln x';

% Geometryczna: f(x) = ln x
geo.f    = @(x) log(x);
geo.finv = @(y) exp(y);
geo.name = 'geometryczna: ln x';

% Relatywistyczna: f(v) = artanh(v/c)
rel.c    = 1.0;
rel.f    = @(v) atanh(v / rel.c);
rel.finv = @(y) rel.c * tanh(y);
rel.name = 'relatywistyczna';

% Radiacyjna: f(T) = T^4
rad.f    = @(T) T.^4;
rad.finv = @(y) y.^(1/4);
rad.name = 'radiacyjna: T^4';

% Saturacja cieplna: f(T) = ln((T-Tmin)/(Tmax-T))
sat.tmin = 20; sat.tmax = 65;
sat.f    = @(T) log((T - sat.tmin) ./ (sat.tmax - T));
sat.finv = @(y) sat.tmin + (sat.tmax - sat.tmin) ./ (1 + exp(-y));
sat.name = 'saturacja cieplna';

%% 2. Operacje przeniesione ----------------------------------------------
add    = @(m, a, b) m.finv(m.f(a) + m.f(b));
sub    = @(m, a, b) m.finv(m.f(a) - m.f(b));
scale  = @(m, n, a) m.finv(n .* m.f(a));
mul    = @(m, a, b) m.finv(m.f(a) .* m.f(b));

fprintf('--- stale kardynalne ---\n');
fprintf('Lambert: 0_f = %.6f, 1_f = %.6f\n', lam.finv(0), lam.finv(1));
fprintf('Saturacja 20-65 C: 0_f = %.2f C\n', sat.finv(0));

%% 3. Test aksjomatow (rozdzielnosc mnozenia wzgledem dodawania) ----------
a = 0.4; b = 1.5; c = 3.2;
lhs = mul(lam, a, add(lam, b, c));
rhs = add(lam, mul(lam, a, b), mul(lam, a, c));
fprintf('Blad rozdzielnosci (Lambert): %.3e\n', abs(lhs - rhs));

%% 4. Wykresy -------------------------------------------------------------
figure('Name', 'Arytmetyki generowane funkcyjnie', 'Position', [100 100 1100 780]);

% (a) nowe dodawanie: 0.8 (+) x
subplot(2, 2, 1);
x = linspace(0.05, 4, 300);
plot(x, add(lam, 0.8, x), 'g-', 'LineWidth', 2); hold on;
plot(x, add(geo, 0.8, x), 'b-', 'LineWidth', 2);
plot(x, 0.8 + x, 'k--', 'LineWidth', 1.2);
grid on; xlabel('x'); ylabel('0.8 (+) x');
title('Nowe dodawanie'); legend('Lambert', 'geometryczna', 'klasyczne', 'Location', 'northwest');

% (b) skladanie predkosci: nic nie przekroczy c
subplot(2, 2, 2);
v2 = linspace(-0.99, 0.99, 300);
plot(v2, add(rel, 0.6, v2), 'r-', 'LineWidth', 2); hold on;
plot(v2, 0.6 + v2, 'k--', 'LineWidth', 1.2);
plot([-1 1], [1 1], 'k:', [-1 1], [-1 -1], 'k:');
grid on; axis([-1 1 -1 1]); xlabel('v_2 / c'); ylabel('v_{wyp} / c');
title('Skladanie predkosci (Einstein)'); legend('0.6c (+) v_2', '0.6c + v_2', 'Location', 'northwest');

% (c) promieniowanie: 300 K (+) T2
subplot(2, 2, 3);
T2 = linspace(100, 1000, 300);
plot(T2, add(rad, 300, T2), 'r-', 'LineWidth', 2); hold on;
plot(T2, 300 + T2, 'k--', 'LineWidth', 1.2);
grid on; xlabel('T_2 [K]'); ylabel('T_{wyp} [K]');
title('Promieniowanie cieplne'); legend('300 K (+) T_2', '300 K + T_2', 'Location', 'northwest');

% (d) saturacja: regulator nie przekracza Tmax
subplot(2, 2, 4);
n = linspace(0, 12, 300);
dose = sat.finv(sat.f(40) - sat.f(35));   % jedna dawka = pierwsze +5 C
T = arrayfun(@(nn) add(sat, 35, scale(sat, nn, dose)), n);
plot(n, T, 'g-', 'LineWidth', 2); hold on;
plot(n, 35 + 5 * n, 'k--', 'LineWidth', 1.2);
plot([0 12], [sat.tmax sat.tmax], 'r:');
grid on; xlabel('liczba dawek n'); ylabel('temperatura [C]');
title('Saturacja cieplna'); legend('saturacja', 'klasycznie', 'T_{max}', 'Location', 'southeast');

fprintf('Wykresy gotowe.\n');

%% 5. Funkcje pomocnicze --------------------------------------------------
function w = lambert_inv(y)
    % rozwiazuje w + ln w = y (rownowaznie w = W(e^y)) metoda Newtona
    if y > 0
        w = y;
    else
        w = exp(y);
    end
    w = max(w, 1e-300);
    for k = 1:100
        step = (w + log(w) - y) / (1 + 1/w);
        w = w - step;
        if abs(step) <= 1e-15 * max(1, abs(w))
            break;
        end
    end
end
