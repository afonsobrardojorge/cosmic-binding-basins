from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
PDF_OUT = ROOT / "paper" / "Cosmic_Binding_Basins_preprint_v0.2.pdf"
CSV = ROOT / "data" / "tec_literature_validation.csv"
SUMMARY_JSON = ROOT / "data" / "tec_literature_validation_summary.json"
FIG_PHASE = ROOT / "figures" / "tec_diagrama_fase_Tlambda.png"
FIG_SUMMARY = ROOT / "figures" / "tec_resumo_por_classe.png"
FIG_VALIDATION = ROOT / "figures" / "tec_literature_validation.png"
FIG_TURNAROUND = ROOT / "figures" / "tec_turnaround_fit.png"
FIG_DYNAMIC_DE = ROOT / "figures" / "tec_energia_escura_dinamica.png"


def register_fonts() -> tuple[str, str]:
    regular = Path(r"C:\Windows\Fonts\arial.ttf")
    bold = Path(r"C:\Windows\Fonts\arialbd.ttf")
    if regular.exists():
        pdfmetrics.registerFont(TTFont("Arial", str(regular)))
        if bold.exists():
            pdfmetrics.registerFont(TTFont("Arial-Bold", str(bold)))
        return "Arial", "Arial-Bold" if bold.exists() else "Arial"
    return "Helvetica", "Helvetica-Bold"


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text.replace("&", "&amp;"), style)


def equation(text: str, style: ParagraphStyle) -> KeepTogether:
    return KeepTogether([Spacer(1, 4), p(text, style), Spacer(1, 4)])


def make_styles() -> dict[str, ParagraphStyle]:
    regular, bold = register_fonts()
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            parent=base["Title"],
            fontName=bold,
            fontSize=20,
            leading=24,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1F3E58"),
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            parent=base["BodyText"],
            fontName=regular,
            fontSize=11,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#333333"),
            spaceAfter=14,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontName=bold,
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1F3E58"),
            spaceBefore=10,
            spaceAfter=5,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName=bold,
            fontSize=10.5,
            leading=13,
            textColor=colors.HexColor("#36556E"),
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["BodyText"],
            fontName=regular,
            fontSize=9.2,
            leading=12,
            spaceAfter=5,
        ),
        "equation": ParagraphStyle(
            "equation",
            parent=base["BodyText"],
            fontName=regular,
            fontSize=10,
            leading=13,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#222222"),
        ),
        "caption": ParagraphStyle(
            "caption",
            parent=base["Italic"],
            fontName=regular,
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#555555"),
            spaceAfter=8,
        ),
        "table": ParagraphStyle(
            "table",
            parent=base["BodyText"],
            fontName=regular,
            fontSize=6.4,
            leading=7.6,
        ),
        "table_header": ParagraphStyle(
            "table_header",
            parent=base["BodyText"],
            fontName=bold,
            fontSize=6.4,
            leading=7.6,
            textColor=colors.white,
        ),
    }


def radius_type_label(value: str) -> str:
    mapping = {
        "satélite ligado, não turnaround": "bound satellite (not turnaround)",
        "zero-velocity / turnaround local": "zero-velocity / local turnaround",
        "zero-velocity / turnaround aproximado": "zero-velocity / approximate turnaround",
        "raio interno, não turnaround": "internal core radius (not turnaround)",
        "turnaround/infall bound; ambiente filamentar": "turnaround/infall bound; filamentary environment",
        "turnaround/collapsing core": "turnaround/collapsing core",
        "turnaround/candidate bound supercluster": "turnaround/candidate bound supercluster",
    }
    return mapping.get(value, value)


def object_table(df: pd.DataFrame, styles: dict[str, ParagraphStyle]) -> Table:
    headers = ["Object", "Radius type", "M [M_sun]", "R [Mpc]", "TΛ", "Flag", "Primary source"]
    rows = [[p(h, styles["table_header"]) for h in headers]]
    for _, row in df.iterrows():
        rows.append(
            [
                p(str(row["estrutura"]), styles["table"]),
                p(radius_type_label(str(row["tipo_medida"])), styles["table"]),
                p(f"{row['massa_msun']:.2e}", styles["table"]),
                p(f"{row['raio_mpc']:.2f}", styles["table"]),
                p(f"{row['T_lambda']:.3f}", styles["table"]),
                p("possible" if row["pode_violar_com_incerteza"] else "no", styles["table"]),
                p(str(row["fonte"]).split(";")[0], styles["table"]),
            ]
        )
    table = Table(rows, colWidths=[3.0 * cm, 3.5 * cm, 2.2 * cm, 1.6 * cm, 1.3 * cm, 1.5 * cm, 3.7 * cm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D5DBE3")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F7FA")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def build_pdf() -> None:
    PDF_OUT.parent.mkdir(parents=True, exist_ok=True)
    styles = make_styles()
    df = pd.read_csv(CSV)
    summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))

    doc = SimpleDocTemplate(
        str(PDF_OUT),
        pagesize=A4,
        rightMargin=1.65 * cm,
        leftMargin=1.65 * cm,
        topMargin=1.55 * cm,
        bottomMargin=1.55 * cm,
        title="Cosmic Binding Basins",
        author="Afonso Brardo Buinheira Sal Jorge",
    )
    story = []
    story.append(p("Cosmic Binding Basins", styles["title"]))
    story.append(p("A Dimensionless Boundary Index for Gravitational Membership in ΛCDM", styles["subtitle"]))
    story.append(p("Short exploratory preprint draft v0.2 | 20 May 2026 | Afonso Brardo Buinheira Sal Jorge", styles["subtitle"]))

    story.append(p("Abstract", styles["h1"]))
    story.append(
        p(
            "We propose Cosmic Binding Basins (TEC-2), a phenomenological ΛCDM-compatible framework in which dark energy is treated as a large-scale boundary-setting term for gravitational membership, rather than as an internal dynamical disruption mechanism within already bound systems.",
            styles["body"],
        )
    )
    story.append(equation("TΛ(R,M) = ΩΛ H0² R³ / (GM)", styles["equation"]))
    story.append(
        p(
            "This work is not claimed as a new physical law, but as a compact diagnostic derived from the ΛCDM turnaround scale.",
            styles["body"],
        )
    )
    story.append(
        p(
            f"In a pilot literature sample of {summary['n_total']} structures, all {summary['n_informative_turnaround_like']} central turnaround-like or zero-velocity estimates satisfy TΛ ≤ 1, with median TΛ = {summary['median_T_informative']:.3f}. This is preliminary independent consistency, not proof of universality.",
            styles["body"],
        )
    )

    sections = [
        (
            "1. Physical Idea",
            [
                "TEC-2 does not introduce a new force. It reorganizes a known ΛCDM boundary scale into an operational index. The proposed publication-level statement is: dark energy is treated here as a large-scale boundary-setting term for gravitational membership, rather than as an internal dynamical disruption mechanism within already bound systems.",
                "The testable question is whether observed boundaries such as zero-velocity or turnaround surfaces lie at or below TΛ ≈ 1.",
            ],
        ),
        (
            "2. Formal Derivation",
            [
                "For a mass M enclosed within physical radius R, the characteristic inward gravitational acceleration is ag = GM/R². In the low-redshift ΛCDM limit, the outward acceleration scale associated with dark energy is aΛ ≈ ΩΛH0²R. Their ratio defines TΛ.",
            ],
        ),
        (
            "3. Relation To Existing ΛCDM Boundaries",
            [
                "For a cosmological constant, TΛ = 1 is equivalent to the maximum turnaround-radius scale in Schwarzschild-de Sitter/Kottler and spherical-collapse arguments.",
            ],
        ),
    ]
    for heading, paragraphs in sections:
        story.append(p(heading, styles["h1"]))
        for paragraph in paragraphs:
            story.append(p(paragraph, styles["body"]))

    story.append(equation("Rta,max = (3GM/Λc²)^(1/3) = [GM/(ΩΛH0²)]^(1/3)", styles["equation"]))

    story.append(p("4. Extensions: Dynamic Dark Energy, Environment And Geometry", styles["h1"]))
    story.append(equation("TDE(R,M,z) = {-[1 + 3w(z)]/2} ΩDE(z) H(z)² R³/(GM)", styles["equation"]))
    story.append(p("For w = -1 and z = 0, this reduces to TΛ. This version asks whether gravitational-basin boundaries evolve measurably with redshift.", styles["body"]))
    if FIG_DYNAMIC_DE.exists():
        story.append(Image(str(FIG_DYNAMIC_DE), width=17 * cm, height=10.1 * cm))
        story.append(p("Figure 1. TEC extension for dynamical dark energy. Curves illustrate how different w(z) histories could shift the boundary-setting term with redshift.", styles["caption"]))
    story.append(equation("Tbasin(R,M,z,η) = TDE(R,Meff,z) · Fenv(η)", styles["equation"]))
    story.append(p("The environmental correction is left as future work because Fenv must be calibrated with simulations or survey data.", styles["body"]))
    story.append(p("4.1 Geometric Basin Dominance (TEC-3 Proposal)", styles["h2"]))
    story.append(p("TEC-3 reframes basin membership through local Weyl or tidal curvature compared with the cosmological dark-energy curvature scale.", styles["body"]))
    story.append(equation("BΛ(x) = sqrt(Cαβγδ C^αβγδ / 48) / (Λ/3)", styles["equation"]))
    story.append(equation("BΛ(R) = GM/(ΩΛ H0² R³) = 1/TΛ(R,M)", styles["equation"]))
    story.append(p("For simulations, a practical tidal proxy is BE(x,z) = ||Eij(x,z)|| / ADE(z), with ADE(z) = -[1 + 3w(z)]ΩDE(z)H(z)²/2. This is proposed, not validated here.", styles["body"]))

    story.append(PageBreak())
    story.append(p("5. Pilot Data And Radius Definitions", styles["h1"]))
    story.append(p("The sample is intentionally small and heterogeneous. Radius type is listed because virial, zero-velocity, turnaround and core radii are not interchangeable.", styles["body"]))
    if FIG_PHASE.exists():
        story.append(Image(str(FIG_PHASE), width=17 * cm, height=10.0 * cm))
        story.append(p("Figure 2. TEC phase diagram: mass, scale and TΛ regime in a synthetic proof-of-concept catalogue.", styles["caption"]))
    if FIG_SUMMARY.exists():
        story.append(Image(str(FIG_SUMMARY), width=17 * cm, height=9.8 * cm))
        story.append(p("Figure 3. Median log10(TΛ) by synthetic class.", styles["caption"]))
    story.append(object_table(df, styles))

    story.append(p("6. Results", styles["h1"]))
    story.append(p(f"All {summary['n_informative_turnaround_like']} central turnaround-like estimates satisfy TΛ ≤ 1. The largest central value is TΛ = {summary['max_T_central_informative']:.3f}. Coma is the only object whose uncertainty envelope can approach or exceed the boundary.", styles["body"]))
    if FIG_VALIDATION.exists():
        story.append(Image(str(FIG_VALIDATION), width=17 * cm, height=12.2 * cm))
        story.append(p("Figure 4. Pilot validation in the mass-radius plane. The solid black line is the TΛ = 1 boundary, i.e. R = RΛ(M).", styles["caption"]))
    if FIG_TURNAROUND.exists():
        story.append(Image(str(FIG_TURNAROUND), width=17 * cm, height=11.0 * cm))
        story.append(p("Figure 5. Synthetic sanity check recovering the expected R ∝ M^(1/3) scaling.", styles["caption"]))

    story.append(p("7. Discussion And Conclusion", styles["h1"]))
    story.append(p("The pilot result supports a cautious claim: structures already interpreted as bound, in turnaround, or in collapse are consistent with the TEC-2 boundary criterion. The result is not yet a discovery of new physics. It is a compact re-expression of a known ΛCDM scale that appears useful as a gravitational-basin classifier.", styles["body"]))
    story.append(p("The next decisive test is comparative: apply TΛ and the proposed TEC-3 tidal proxy to a larger homogeneous simulation or survey sample, then test whether they improve boundary classification relative to mass, density, virial radius, turnaround radius and cosmic-web classifiers.", styles["body"]))

    story.append(p("References", styles["h1"]))
    refs = [
        "Aghanim et al. (Planck Collaboration), 2020, A&A, 641, A6.",
        "Pavlidou & Tomaras, 2014, JCAP, 2014(09), 020, arXiv:1310.1920.",
        "Karachentsev & Kashibadze, 2006, Astrophysics, 49, 3.",
        "Nasonova, de Freitas Pacheco & Karachentsev, 2011, A&A, 532, A104.",
        "Benisty, Wagner, Haridasu & Salucci, 2025, arXiv:2504.04135.",
        "Einasto et al., 2021, A&A, 649, A51, arXiv:2103.02326.",
        "Reisenegger, Quintana, Carrasco & Maze, 2000, AJ, 120, 523.",
        "Kormendy & Ho, 2013, ARA&A, 51, 511.",
        "Binney & Tremaine, 2008, Galactic Dynamics, 2nd ed.",
    ]
    for ref in refs:
        story.append(p(ref, styles["body"]))

    doc.build(story)
    print(PDF_OUT)


if __name__ == "__main__":
    build_pdf()
