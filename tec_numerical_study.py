from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parents[1]
CSV_OUT = OUT / "data" / "tec_catalogo_sintetico.csv"
SUMMARY_OUT = OUT / "data" / "tec_resumo_estatistico.json"
PHASE_FIG = OUT / "figures" / "tec_diagrama_fase_Tlambda.png"
SUMMARY_FIG = OUT / "figures" / "tec_resumo_por_classe.png"
TURNAROUND_FIG = OUT / "figures" / "tec_turnaround_fit.png"
DYNAMIC_DE_FIG = OUT / "figures" / "tec_energia_escura_dinamica.png"

G = 6.67430e-11
C = 299_792_458.0
M_SUN = 1.98847e30
MPC = 3.0856775814913673e22
H0_KM = 67.4
H0 = H0_KM * 1000 / MPC
OMEGA_M0 = 0.315
OMEGA_DE0 = 0.685
LAMBDA = 3 * OMEGA_DE0 * H0**2 / C**2

RNG = np.random.default_rng(42)


@dataclass(frozen=True)
class Population:
    name: str
    n: int
    logm_mu: float
    logm_sigma: float
    logr_mu: float
    logr_sigma: float
    color: tuple[int, int, int]


POPULATIONS = [
    Population("halo_galactico", 220, 12.0, 0.35, -0.82, 0.20, (41, 118, 173)),
    Population("grupo", 180, 13.1, 0.35, 0.00, 0.18, (65, 152, 118)),
    Population("enxame", 180, 14.7, 0.32, 0.38, 0.16, (106, 81, 163)),
    Population("filamento", 180, 14.6, 0.55, 1.05, 0.22, (218, 165, 32)),
    Population("superenxame", 130, 15.8, 0.45, 1.45, 0.22, (214, 96, 46)),
    Population("vazio", 210, 14.0, 0.60, 1.45, 0.28, (145, 145, 145)),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
    ]
    for item in candidates:
        if Path(item).exists():
            return ImageFont.truetype(item, size)
    return ImageFont.load_default()


def t_lambda(mass_msun: np.ndarray, radius_mpc: np.ndarray) -> np.ndarray:
    mass = mass_msun * M_SUN
    radius = radius_mpc * MPC
    return OMEGA_DE0 * H0**2 * radius**3 / (G * mass)


def r_lambda_mpc(mass_msun: np.ndarray) -> np.ndarray:
    mass = mass_msun * M_SUN
    return (G * mass / (OMEGA_DE0 * H0**2)) ** (1 / 3) / MPC


def classify_t(value: float) -> str:
    if value < 0.1:
        return "bound"
    if value < 1:
        return "transition"
    if value < 10:
        return "boundary"
    return "expansion_dominated"


def build_catalogue() -> pd.DataFrame:
    rows = []
    for pop in POPULATIONS:
        logm = RNG.normal(pop.logm_mu, pop.logm_sigma, pop.n)
        logr = RNG.normal(pop.logr_mu, pop.logr_sigma, pop.n)
        mass = 10**logm
        radius = 10**logr
        t = t_lambda(mass, radius)
        rlim = r_lambda_mpc(mass)
        for i in range(pop.n):
            rows.append(
                {
                    "classe": pop.name,
                    "massa_msun": float(mass[i]),
                    "raio_mpc": float(radius[i]),
                    "log10_massa": float(logm[i]),
                    "log10_raio": float(logr[i]),
                    "T_lambda": float(t[i]),
                    "log10_T_lambda": float(math.log10(t[i])),
                    "R_lambda_mpc": float(rlim[i]),
                    "raio_sobre_R_lambda": float(radius[i] / rlim[i]),
                    "regime_TEC": classify_t(float(t[i])),
                }
            )
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame) -> dict:
    grouped = {}
    for name, sub in df.groupby("classe"):
        grouped[name] = {
            "n": int(len(sub)),
            "median_T_lambda": float(sub["T_lambda"].median()),
            "median_log10_T_lambda": float(sub["log10_T_lambda"].median()),
            "pct_T_menor_1": float((sub["T_lambda"] < 1).mean() * 100),
            "pct_T_maior_10": float((sub["T_lambda"] >= 10).mean() * 100),
            "median_raio_sobre_R_lambda": float(sub["raio_sobre_R_lambda"].median()),
        }

    mass = 10 ** RNG.uniform(12, 16, 600)
    r_true = r_lambda_mpc(mass)
    r_obs = r_true * 10 ** RNG.normal(0, 0.08, len(mass))
    slope, intercept = np.polyfit(np.log10(mass), np.log10(r_obs), 1)
    grouped["_turnaround_synthetic_fit"] = {
        "slope_beta": float(slope),
        "intercept_A": float(intercept),
        "expected_beta": 1 / 3,
        "scatter_dex": 0.08,
    }
    return grouped


def draw_axes(
    d: ImageDraw.ImageDraw,
    bounds: tuple[int, int, int, int],
    x_ticks: list[float],
    y_ticks: list[float],
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    xlabel: str,
    ylabel: str,
) -> tuple:
    left, top, right, bottom = bounds
    axis = (45, 45, 45)
    grid = (225, 230, 236)
    label_font = font(25, True)
    tick_font = font(20)

    def xmap(x):
        return left + (x - xlim[0]) / (xlim[1] - xlim[0]) * (right - left)

    def ymap(y):
        return bottom - (y - ylim[0]) / (ylim[1] - ylim[0]) * (bottom - top)

    d.line((left, bottom, right, bottom), fill=axis, width=3)
    d.line((left, top, left, bottom), fill=axis, width=3)
    for x in x_ticks:
        xx = xmap(x)
        d.line((xx, top, xx, bottom), fill=grid, width=1)
        d.text((xx - 25, bottom + 18), f"10^{int(x)}", fill=(60, 60, 60), font=tick_font)
    for y in y_ticks:
        yy = ymap(y)
        d.line((left, yy, right, yy), fill=grid, width=1)
        label = f"10^{int(y)}" if abs(y - round(y)) < 1e-6 else f"{10**y:.1f}"
        d.text((left - 76, yy - 12), label, fill=(60, 60, 60), font=tick_font)
    d.text(((left + right) / 2 - 130, bottom + 62), xlabel, fill=(30, 30, 30), font=label_font)
    d.text((20, (top + bottom) / 2 - 16), ylabel, fill=(30, 30, 30), font=label_font)
    return xmap, ymap


def draw_phase_diagram(df: pd.DataFrame) -> None:
    img = Image.new("RGB", (1700, 1050), "white")
    d = ImageDraw.Draw(img)
    title_font = font(44, True)
    small_font = font(20)
    d.text((130, 35), "TEC phase diagram: mass, scale and T_lambda regime", fill=(22, 42, 58), font=title_font)
    bounds = (140, 110, 1540, 885)
    xlim = (10.5, 16.7)
    ylim = (-1.3, 2.05)
    xmap, ymap = draw_axes(
        d,
        bounds,
        [11, 12, 13, 14, 15, 16],
        [-1, 0, 1, 2],
        xlim,
        ylim,
        "mass M (M_sun)",
        "radius R (Mpc)",
    )

    masses = np.logspace(xlim[0], xlim[1], 300)
    rlim = r_lambda_mpc(masses)
    line = [(xmap(math.log10(m)), ymap(math.log10(r))) for m, r in zip(masses, rlim)]
    d.line(line, fill=(20, 20, 20), width=4)
    d.text((xmap(14.55), ymap(0.97)), "T_lambda = 1", fill=(20, 20, 20), font=font(23, True))

    color_by_class = {pop.name: pop.color for pop in POPULATIONS}
    for _, row in df.sample(frac=1, random_state=1).iterrows():
        x = xmap(row["log10_massa"])
        y = ymap(row["log10_raio"])
        color = color_by_class[row["classe"]]
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=color)

    legend_x, legend_y = 1170, 140
    d.rectangle((legend_x - 20, legend_y - 18, legend_x + 300, legend_y + len(POPULATIONS) * 34 + 18), fill=(255, 255, 255), outline=(210, 215, 222), width=2)
    for i, pop in enumerate(POPULATIONS):
        y = legend_y + i * 34
        d.rectangle((legend_x, y + 4, legend_x + 20, y + 24), fill=pop.color)
        d.text((legend_x + 32, y), pop.name, fill=(40, 40, 40), font=small_font)
    d.text((140, 925), "Below the line: T_lambda < 1, local gravity dominates. Above the line: accelerated expansion dominates the analysed scale.", fill=(70, 70, 70), font=small_font)
    img.save(PHASE_FIG, quality=95)


def draw_summary_chart(summary: dict) -> None:
    img = Image.new("RGB", (1500, 980), "white")
    d = ImageDraw.Draw(img)
    title_font = font(42, True)
    label_font = font(24, True)
    tick_font = font(20)
    d.text((100, 35), "Median log10(T_lambda) by synthetic class", fill=(22, 42, 58), font=title_font)
    classes = [p.name for p in POPULATIONS]
    values = [summary[c]["median_log10_T_lambda"] for c in classes]
    colors = [p.color for p in POPULATIONS]
    xmin, xmax = -4.2, 2.7
    left, top, right, bottom = 320, 115, 1380, 805

    def xmap(x):
        return left + (x - xmin) / (xmax - xmin) * (right - left)

    d.line((xmap(0), top, xmap(0), bottom), fill=(30, 30, 30), width=4)
    for x in [-4, -3, -2, -1, 0, 1, 2]:
        xx = xmap(x)
        d.line((xx, top, xx, bottom), fill=(228, 232, 238), width=1)
        d.text((xx - 12, bottom + 20), f"{x}", fill=(70, 70, 70), font=tick_font)

    bar_h = 64
    gap = 38
    for i, (name, value, color) in enumerate(zip(classes, values, colors)):
        y = top + i * (bar_h + gap)
        d.text((95, y + 15), name, fill=(40, 40, 40), font=label_font)
        x0 = xmap(0)
        x1 = xmap(value)
        d.rectangle((min(x0, x1), y, max(x0, x1), y + bar_h), fill=color)
        d.text((max(x0, x1) + 12, y + 16), f"{value:.2f}", fill=(30, 30, 30), font=tick_font)
    d.text((left + 280, bottom + 60), "log10(T_lambda)", fill=(30, 30, 30), font=label_font)
    d.text((left - 30, 920), "Negative values indicate bound-regime structures; positive values indicate expansion-dominated scales.", fill=(70, 70, 70), font=tick_font)
    img.save(SUMMARY_FIG, quality=95)


def draw_turnaround_fit(summary: dict) -> None:
    mass = 10 ** RNG.uniform(12, 16, 600)
    r_true = r_lambda_mpc(mass)
    r_obs = r_true * 10 ** RNG.normal(0, 0.08, len(mass))
    x = np.log10(mass)
    y = np.log10(r_obs)
    slope, intercept = np.polyfit(x, y, 1)

    img = Image.new("RGB", (1600, 950), "white")
    d = ImageDraw.Draw(img)
    d.text((115, 35), "Synthetic test: recovering the R ~ M^(1/3) scaling", fill=(22, 42, 58), font=font(42, True))
    bounds = (130, 110, 1470, 790)
    xlim = (11.8, 16.2)
    ylim = (-0.1, 1.55)
    xmap, ymap = draw_axes(d, bounds, [12, 13, 14, 15, 16], [0, 1], xlim, ylim, "mass M (M_sun)", "R_turn (Mpc)")

    for xi, yi in zip(x, y):
        xx, yy = xmap(xi), ymap(yi)
        d.ellipse((xx - 3, yy - 3, xx + 3, yy + 3), fill=(80, 134, 190))

    xs = np.linspace(xlim[0], xlim[1], 100)
    ys = slope * xs + intercept
    d.line([(xmap(a), ymap(b)) for a, b in zip(xs, ys)], fill=(198, 76, 41), width=5)
    d.text((910, 150), f"fitted beta = {slope:.3f}\nexpected = 0.333", fill=(40, 40, 40), font=font(25, True))
    d.text((130, 830), "This test shows the regression that should be repeated with real or simulated halos.", fill=(70, 70, 70), font=font(21))
    img.save(TURNAROUND_FIG, quality=95)


def e_de_factor(z: np.ndarray, w0: float, wa: float) -> np.ndarray:
    return (1 + z) ** (3 * (1 + w0 + wa)) * np.exp(-3 * wa * z / (1 + z))


def w_cpl(z: np.ndarray, w0: float, wa: float) -> np.ndarray:
    return w0 + wa * z / (1 + z)


def tde_relative_to_today_lambda(z: np.ndarray, w0: float, wa: float) -> np.ndarray:
    w = w_cpl(z, w0, wa)
    repulsive_factor = -0.5 * (1 + 3 * w)
    return repulsive_factor * e_de_factor(z, w0, wa)


def draw_dynamic_de() -> None:
    img = Image.new("RGB", (1600, 950), "white")
    d = ImageDraw.Draw(img)
    d.text((115, 35), "TEC extension for dynamical dark energy", fill=(22, 42, 58), font=font(42, True))
    left, top, right, bottom = 130, 150, 1470, 810
    xlim = (0, 3)
    ylim = (0, 2.2)
    label_font = font(25, True)
    tick_font = font(20)

    def xmap(x):
        return left + (x - xlim[0]) / (xlim[1] - xlim[0]) * (right - left)

    def ymap(y):
        return bottom - (y - ylim[0]) / (ylim[1] - ylim[0]) * (bottom - top)

    d.line((left, bottom, right, bottom), fill=(45, 45, 45), width=3)
    d.line((left, top, left, bottom), fill=(45, 45, 45), width=3)
    for x_tick in [0, 0.5, 1, 1.5, 2, 2.5, 3]:
        xx = xmap(x_tick)
        d.line((xx, top, xx, bottom), fill=(228, 232, 238), width=1)
        d.text((xx - 16, bottom + 18), f"{x_tick:g}", fill=(70, 70, 70), font=tick_font)
    for y_tick in [0, 0.5, 1, 1.5, 2]:
        yy = ymap(y_tick)
        d.line((left, yy, right, yy), fill=(228, 232, 238), width=1)
        d.text((left - 55, yy - 12), f"{y_tick:g}", fill=(70, 70, 70), font=tick_font)

    z = np.linspace(0, 3, 300)
    models = [
        ("Lambda: w=-1", -1.0, 0.0, (30, 107, 165)),
        ("smooth evolving", -0.8, -0.6, (210, 93, 48)),
        ("smooth phantom", -1.1, 0.3, (92, 150, 95)),
    ]
    for label, w0, wa, color in models:
        y = tde_relative_to_today_lambda(z, w0, wa)
        points = [(xmap(float(a)), ymap(float(min(max(b, 0), ylim[1])))) for a, b in zip(z, y)]
        d.line(points, fill=color, width=5)

    lx, ly = 1060, 150
    for i, (label, _, _, color) in enumerate(models):
        y = ly + i * 42
        d.line((lx, y + 14, lx + 45, y + 14), fill=color, width=6)
        d.text((lx + 60, y), label, fill=(40, 40, 40), font=font(22, True))
    d.text((left + 570, bottom + 58), "redshift z", fill=(30, 30, 30), font=label_font)
    d.text((left, top - 38), "T_DE/T_Lambda0", fill=(30, 30, 30), font=label_font)
    d.text((130, 900), "Curves illustrate how w(z) could shift the dynamical basin boundary at low redshift.", fill=(70, 70, 70), font=font(21))
    img.save(DYNAMIC_DE_FIG, quality=95)


def main() -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
    PHASE_FIG.parent.mkdir(parents=True, exist_ok=True)
    df = build_catalogue()
    summary = summarize(df)
    df.to_csv(CSV_OUT, index=False)
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    draw_phase_diagram(df)
    draw_summary_chart(summary)
    draw_turnaround_fit(summary)
    draw_dynamic_de()
    print(CSV_OUT)
    print(SUMMARY_OUT)
    print(PHASE_FIG)
    print(SUMMARY_FIG)
    print(TURNAROUND_FIG)
    print(DYNAMIC_DE_FIG)


if __name__ == "__main__":
    main()
