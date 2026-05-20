from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parents[1]
CSV_OUT = OUT / "data" / "tec_literature_validation.csv"
SUMMARY_OUT = OUT / "data" / "tec_literature_validation_summary.json"
FIG_OUT = OUT / "figures" / "tec_literature_validation.png"

G = 6.67430e-11
M_SUN = 1.98847e30
MPC = 3.0856775814913673e22
H0_KM = 67.4
H0 = H0_KM * 1000 / MPC
H = H0_KM / 100.0
OMEGA_L = 0.685


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
    ]
    for item in candidates:
        if Path(item).exists():
            return ImageFont.truetype(item, size)
    return ImageFont.load_default()


def convert_h_inv(value: float) -> float:
    return value / H


def t_lambda(mass_msun: float, radius_mpc: float) -> float:
    return OMEGA_L * H0**2 * (radius_mpc * MPC) ** 3 / (G * mass_msun * M_SUN)


def r_lambda_mpc(mass_msun: float) -> float:
    return (G * mass_msun * M_SUN / (OMEGA_L * H0**2)) ** (1 / 3) / MPC


def add_row(rows, name, kind, mass, radius, source, mass_low=None, mass_high=None, radius_low=None, radius_high=None, notes=""):
    mass_low = mass if mass_low is None else mass_low
    mass_high = mass if mass_high is None else mass_high
    radius_low = radius if radius_low is None else radius_low
    radius_high = radius if radius_high is None else radius_high
    t = t_lambda(mass, radius)
    t_low = t_lambda(mass_high, radius_low)
    t_high = t_lambda(mass_low, radius_high)
    rlim = r_lambda_mpc(mass)
    rows.append(
        {
            "estrutura": name,
            "tipo_medida": kind,
            "massa_msun": mass,
            "massa_low_msun": mass_low,
            "massa_high_msun": mass_high,
            "raio_mpc": radius,
            "raio_low_mpc": radius_low,
            "raio_high_mpc": radius_high,
            "R_lambda_mpc": rlim,
            "R_sobre_R_lambda": radius / rlim,
            "T_lambda": t,
            "T_lambda_low": t_low,
            "T_lambda_high": t_high,
            "cumpre_limite_T_menor_1": t <= 1,
            "pode_violar_com_incerteza": t_high > 1,
            "fonte": source,
            "notas": notes,
        }
    )


def build_dataset() -> pd.DataFrame:
    rows = []

    add_row(
        rows,
        "Milky Way / Leo I",
        "satélite ligado, não turnaround",
        mass=1.7e12,
        mass_low=1.0e12,
        mass_high=2.4e12,
        radius=0.254,
        radius_low=0.238,
        radius_high=0.270,
        source="Pavlidou & Tomaras 2014; Bellazzini et al. 2004; Boylan-Kolchin et al. 2013",
        notes="Teste interno: deve estar muito abaixo da fronteira TEC-2.",
    )
    add_row(
        rows,
        "Local Group",
        "zero-velocity / turnaround local",
        mass=4.17e12,
        mass_low=3.24e12,
        mass_high=5.62e12,
        radius=0.96,
        radius_low=0.93,
        radius_high=0.99,
        source="Karachentsev & Kashibadze 2006; Gonzalez et al. 2013; Pavlidou & Tomaras 2014",
        notes="Massa independente e raio de zero-velocity local.",
    )
    add_row(
        rows,
        "M81/M82 Group",
        "zero-velocity / turnaround local",
        mass=1.6e12,
        mass_low=1.2e12,
        mass_high=2.0e12,
        radius=0.89,
        radius_low=0.84,
        radius_high=0.94,
        source="Karachentsev et al. 2002; Karachentsev & Kashibadze 2006; Pavlidou & Tomaras 2014",
        notes="Grupo local próximo usado como teste de turnaround.",
    )
    add_row(
        rows,
        "Fornax-Eridanus Complex",
        "zero-velocity / turnaround aproximado",
        mass=1.92e14,
        mass_low=1.30e14,
        mass_high=3.93e14,
        radius=4.60,
        radius_low=3.88,
        radius_high=5.60,
        source="Nasonova et al. 2011; Tanoglidis et al. 2014",
        notes="Massa de grupos virializados e intervalo de superfície de velocidade zero.",
    )
    add_row(
        rows,
        "Virgo Cluster",
        "zero-velocity / turnaround local",
        mass=1.10e15,
        mass_low=0.98e15,
        mass_high=1.22e15,
        radius=8.60,
        radius_low=7.80,
        radius_high=9.40,
        source="Karachentsev & Nasonova 2010; Tanoglidis et al. 2014",
        notes="Estimativa via modelo Tolman-Bondi/local flow.",
    )
    add_row(
        rows,
        "Virgo Cluster X-ray core",
        "raio interno, não turnaround",
        mass=1.4e14,
        radius=1.20,
        source="Urban et al. 2011; Pavlidou & Tomaras 2014",
        notes="Ponto interno não informativo para fronteira, mas deve cumprir TΛ << 1.",
    )
    add_row(
        rows,
        "Coma Cluster",
        "turnaround/infall bound; ambiente filamentar",
        mass=1.90e15,
        mass_low=1.05e15,
        mass_high=2.74e15,
        radius=6.66,
        radius_low=6.66,
        radius_high=11.82,
        source="Benisty et al. 2025 preprint; Gavazzi et al. 2009; Pavlidou & Tomaras 2014",
        notes="Raio de turnaround inferior e possível limite superior; Coma não é isolado.",
    )
    add_row(
        rows,
        "A2142 supercluster core",
        "turnaround/collapsing core",
        mass=convert_h_inv(2.3e15),
        radius=convert_h_inv(8.0),
        source="Einasto et al. 2018/2021",
        notes="Massa e raio publicados em unidades h^-1.",
    )
    add_row(
        rows,
        "Sloan Great Wall core",
        "turnaround/collapsing core",
        mass=convert_h_inv(1.8e15),
        radius=convert_h_inv(7.5),
        source="Einasto et al. 2016/2021",
        notes="Core colapsante comparado em estudos de superenxames.",
    )
    add_row(
        rows,
        "Shapley supercluster core",
        "turnaround/collapsing core",
        mass=convert_h_inv(1.3e16),
        radius=convert_h_inv(12.4),
        source="Reisenegger et al.; Einasto et al. 2021",
        notes="Core massivo em turnaround/collapse.",
    )
    add_row(
        rows,
        "Corona Borealis core",
        "turnaround/candidate bound supercluster",
        mass=convert_h_inv(3.0e16),
        radius=convert_h_inv(12.5),
        source="Pearson et al. 2014; Einasto et al. 2021",
        notes="Estimativa clássica de estrutura grande ligada; incertezas sistemáticas altas.",
    )
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame) -> dict:
    informative = df[~df["tipo_medida"].str.contains("não turnaround", case=False, regex=False)]
    return {
        "n_total": int(len(df)),
        "n_informative_turnaround_like": int(len(informative)),
        "n_central_T_less_equal_1": int((informative["T_lambda"] <= 1).sum()),
        "n_possible_uncertainty_violation": int(informative["pode_violar_com_incerteza"].sum()),
        "median_T_informative": float(informative["T_lambda"].median()),
        "max_T_central_informative": float(informative["T_lambda"].max()),
        "objects_possible_uncertainty_violation": informative.loc[informative["pode_violar_com_incerteza"], "estrutura"].tolist(),
    }


def draw_validation_plot(df: pd.DataFrame) -> None:
    img = Image.new("RGB", (1800, 1250), "white")
    d = ImageDraw.Draw(img)
    title_font = font(46, True)
    label_font = font(27, True)
    tick_font = font(21)
    small_font = font(18)
    d.text((120, 38), "Validação piloto TEC-2 com estruturas publicadas", fill=(22, 42, 58), font=title_font)
    left, top, right, bottom = 150, 150, 1610, 900
    xlim = (11.3, 17.0)
    ylim = (-0.9, 1.65)

    def xmap(x):
        return left + (x - xlim[0]) / (xlim[1] - xlim[0]) * (right - left)

    def ymap(y):
        return bottom - (y - ylim[0]) / (ylim[1] - ylim[0]) * (bottom - top)

    d.line((left, bottom, right, bottom), fill=(45, 45, 45), width=3)
    d.line((left, top, left, bottom), fill=(45, 45, 45), width=3)
    for x in [12, 13, 14, 15, 16, 17]:
        xx = xmap(x)
        d.line((xx, top, xx, bottom), fill=(227, 232, 238), width=1)
        d.text((xx - 25, bottom + 20), f"10^{x}", fill=(70, 70, 70), font=tick_font)
    for y, label in [(-0.5, "0.3"), (0, "1"), (0.5, "3"), (1, "10"), (1.5, "30")]:
        yy = ymap(y)
        d.line((left, yy, right, yy), fill=(227, 232, 238), width=1)
        d.text((left - 74, yy - 12), label, fill=(70, 70, 70), font=tick_font)

    masses = [10 ** (xlim[0] + i * (xlim[1] - xlim[0]) / 300) for i in range(301)]
    line = [(xmap(math.log10(m)), ymap(math.log10(r_lambda_mpc(m)))) for m in masses]
    d.line(line, fill=(20, 20, 20), width=5)
    d.text((xmap(15.1), ymap(0.95)), "T_lambda = 1 / R_lambda", fill=(20, 20, 20), font=font(22, True))

    label_offsets = {
        "Milky Way / Leo I": (12, 10),
        "Local Group": (12, -12),
        "M81/M82 Group": (12, -10),
        "Fornax-Eridanus Complex": (12, -10),
        "Virgo Cluster": (12, -4),
        "Virgo Cluster X-ray core": (12, -4),
        "Coma Cluster": (12, -8),
        "A2142 supercluster core": (12, -28),
        "Sloan Great Wall core": (12, 6),
        "Shapley supercluster core": (-210, -26),
        "Corona Borealis core": (-5, 12),
    }
    label_names = {
        "Local Group": "Local Group",
        "M81/M82 Group": "M81/M82",
        "Virgo Cluster X-ray core": "Virgo X-ray core",
        "A2142 supercluster core": "A2142 core",
        "Sloan Great Wall core": "Sloan GW core",
        "Shapley supercluster core": "Shapley core",
        "Corona Borealis core": "Corona Borealis core",
    }
    for _, row in df.iterrows():
        x = xmap(math.log10(row["massa_msun"]))
        y = ymap(math.log10(row["raio_mpc"]))
        color = (37, 120, 175)
        if row["tipo_medida"].lower().find("não turnaround") >= 0:
            color = (150, 150, 150)
        elif row["T_lambda"] > 0.5:
            color = (210, 93, 48)
        elif row["T_lambda"] > 0.2:
            color = (219, 169, 45)
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=color, outline=(35, 35, 35))
        label = label_names.get(row["estrutura"], row["estrutura"].replace(" Cluster", "").replace(" Group", ""))
        dx, dy = label_offsets.get(row["estrutura"], (12, -9))
        d.text((x + dx, y + dy), label, fill=(45, 45, 45), font=small_font)

    d.text((left + 540, bottom + 70), "massa M (M_sun)", fill=(30, 30, 30), font=label_font)
    d.text((left, top - 46), "raio R (Mpc)", fill=(30, 30, 30), font=label_font)
    d.text((150, 1030), "Todos os pontos centrais informativos ficam abaixo do limite T_lambda = 1; Coma pode aproximar-se do limite sob escolhas extremas de incerteza.", fill=(70, 70, 70), font=font(22))
    d.text((150, 1070), "Isto é evidência piloto de consistência com a fronteira TEC-2, não prova final de universalidade.", fill=(110, 70, 35), font=font(22, True))
    img.save(FIG_OUT, quality=95)


def main() -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_OUT.parent.mkdir(parents=True, exist_ok=True)
    FIG_OUT.parent.mkdir(parents=True, exist_ok=True)

    df = build_dataset()
    summary = summarize(df)

    df.to_csv(CSV_OUT, index=False)
    SUMMARY_OUT.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    draw_validation_plot(df)

    print(CSV_OUT)
    print(SUMMARY_OUT)
    print(FIG_OUT)
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
