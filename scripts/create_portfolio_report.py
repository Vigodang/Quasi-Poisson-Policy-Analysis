from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "infections.csv"
OUTPUT_PATH = ROOT / "reports" / "workplace_respiratory_infection_policy_analysis.pdf"


def build_design_frame(data: pd.DataFrame, columns: list[str]) -> tuple[np.ndarray, list[str]]:
    matrix = [np.ones(len(data))]
    names = ["Intercept"]

    if "ppe_regime" in columns:
        for level in [2, 3, 4]:
            matrix.append((data["ppe_regime"].to_numpy() == level).astype(float))
            names.append(f"PPE regime {level}")

    if "experience" in columns:
        for level in [2, 3, 4]:
            matrix.append((data["experience"].to_numpy() == level).astype(float))
            names.append(f"Experience level {level}")

    if "wage_inc" in columns:
        matrix.append(data["wage_inc"].to_numpy(dtype=float))
        names.append("Wage increase coverage")

    if "training" in columns:
        matrix.append(data["training"].to_numpy(dtype=float))
        names.append("External training coverage")

    return np.column_stack(matrix), names


def fit_poisson(data: pd.DataFrame, columns: list[str]) -> dict[str, object]:
    y = data["infections"].to_numpy(dtype=float)
    offset = np.log(data["hours"].to_numpy(dtype=float))
    x, names = build_design_frame(data, columns)
    beta = np.zeros(x.shape[1])
    beta[0] = math.log(y.sum() / data["hours"].sum())

    for _ in range(100):
        eta = offset + x @ beta
        mu = np.exp(np.clip(eta, -50, 50))
        z = eta - offset + (y - mu) / mu
        weights = mu
        xtw = x.T * weights
        next_beta = np.linalg.solve(xtw @ x, xtw @ z)
        if np.max(np.abs(next_beta - beta)) < 1e-10:
            beta = next_beta
            break
        beta = next_beta

    eta = offset + x @ beta
    mu = np.exp(np.clip(eta, -50, 50))
    deviance_terms = np.where(y == 0, 0, y * np.log(y / mu)) - (y - mu)
    deviance = float(2 * deviance_terms.sum())
    residual_df = len(y) - x.shape[1]
    phi = deviance / residual_df
    covariance = phi * np.linalg.inv((x.T * mu) @ x)
    standard_errors = np.sqrt(np.diag(covariance))

    return {
        "names": names,
        "beta": beta,
        "standard_errors": standard_errors,
        "deviance": deviance,
        "residual_df": residual_df,
        "phi": phi,
    }


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def page_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#5F6B7A"))
    canvas.drawString(0.72 * inch, 0.45 * inch, "Quasi-Poisson Policy Analysis")
    canvas.drawRightString(A4[0] - 0.72 * inch, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()


def styled_table(data, widths=None) -> Table:
    table = Table(data, colWidths=widths, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#14324A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.6),
                ("LEADING", (0, 0), (-1, -1), 10.5),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#C8D0D8")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F7FA")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def main() -> None:
    data = pd.read_csv(DATA_PATH)
    data["infection_rate"] = data["infections"] / data["hours"] * 1000

    full_model = fit_poisson(data, ["ppe_regime", "experience", "wage_inc", "training"])
    final_model = fit_poisson(data, ["experience"])

    total_records = len(data)
    total_infections = int(data["infections"].sum())
    total_hours = int(data["hours"].sum())
    overall_rate = total_infections / total_hours * 1000
    poisson_threshold = 1 + 3 * math.sqrt(2 / int(full_model["residual_df"]))

    beta = final_model["beta"]
    se = final_model["standard_errors"]
    names = final_model["names"]
    irr_rows = [["Term", "IRR", "95% CI", "Interpretation"]]
    for name, estimate, stderr in zip(names[1:], beta[1:], se[1:]):
        irr = math.exp(estimate)
        low = math.exp(estimate - 1.96 * stderr)
        high = math.exp(estimate + 1.96 * stderr)
        reduction = (1 - irr) * 100
        irr_rows.append(
            [
                name,
                f"{irr:.3f}",
                f"{low:.3f} to {high:.3f}",
                f"Approx. {reduction:.0f}% lower rate than Level 1",
            ]
        )

    experience_summary = (
        data.groupby("experience")
        .agg(infections=("infections", "sum"), hours=("hours", "sum"))
        .reset_index()
    )
    experience_summary["rate"] = experience_summary["infections"] / experience_summary["hours"] * 1000
    experience_rows = [["Experience", "Infections", "Worked hours", "Rate per 1,000 hours"]]
    for row in experience_summary.itertuples(index=False):
        experience_rows.append(
            [
                f"Level {int(row.experience)}",
                f"{int(row.infections):,}",
                f"{int(row.hours):,}",
                f"{row.rate:.1f}",
            ]
        )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=21,
            leading=26,
            textColor=colors.HexColor("#14324A"),
            spaceAfter=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Subtitle",
            parent=styles["Normal"],
            fontSize=10.5,
            leading=15,
            textColor=colors.HexColor("#3D4A57"),
            spaceAfter=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Section",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#14324A"),
            spaceBefore=12,
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#202B36"),
            spaceAfter=8,
        )
    )

    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        rightMargin=0.72 * inch,
        leftMargin=0.72 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.72 * inch,
        title="Workplace Respiratory Infection Policy Analysis",
        author="Truong Lieu Dong Dang",
    )

    story = []
    story.append(paragraph("Workplace Respiratory Infection Policy Analysis", styles["ReportTitle"]))
    story.append(
        paragraph(
            "A personal portfolio project using Quasi-Poisson regression to model infection counts with worked-hours exposure.",
            styles["Subtitle"],
        )
    )
    story.append(paragraph("Executive Summary", styles["Section"]))
    story.append(
        paragraph(
            "This project evaluates aggregated respiratory infection records from a hospital network to identify which operational factors are associated with lower infection rates. The analysis starts with a Poisson count model and uses log(worked hours) as an offset, then switches to a Quasi-Poisson model after detecting substantial overdispersion.",
            styles["Body"],
        )
    )
    story.append(
        paragraph(
            "The final model indicates that staff experience is the strongest predictor of infection risk. PPE regime, wage-increase coverage, and external training coverage do not add meaningful explanatory value once experience is included.",
            styles["Body"],
        )
    )

    story.append(paragraph("Dataset Snapshot", styles["Section"]))
    story.append(
        styled_table(
            [
                ["Metric", "Value"],
                ["Aggregated records", f"{total_records:,}"],
                ["Recorded infections", f"{total_infections:,}"],
                ["Worked hours", f"{total_hours:,}"],
                ["Overall infection rate", f"{overall_rate:.1f} per 1,000 hours"],
            ],
            widths=[2.4 * inch, 3.0 * inch],
        )
    )

    story.append(paragraph("Model Choice", styles["Section"]))
    story.append(
        paragraph(
            f"The initial Poisson model produced a dispersion ratio of {full_model['phi']:.1f}, far above the overdispersion threshold of {poisson_threshold:.1f}. A standard Poisson model would understate uncertainty, so the project uses a Quasi-Poisson model for inference.",
            styles["Body"],
        )
    )

    story.append(paragraph("Final Model Results", styles["Section"]))
    story.append(styled_table(irr_rows, widths=[1.55 * inch, 0.72 * inch, 1.35 * inch, 2.6 * inch]))
    story.append(Spacer(1, 0.08 * inch))
    story.append(styled_table(experience_rows, widths=[1.25 * inch, 1.15 * inch, 1.45 * inch, 1.55 * inch]))

    story.append(PageBreak())
    story.append(paragraph("Professional Interpretation", styles["Section"]))
    story.append(
        paragraph(
            "The analysis suggests that experienced staff function as an infection-control asset. Compared with Level 1 staff, Level 4 staff are associated with an estimated 75% lower infection rate. This is a stronger and more stable signal than the PPE-regime differences visible in the raw exploratory plots.",
            styles["Body"],
        )
    )
    story.append(
        paragraph(
            "A reasonable operational response is to focus on retention, mentoring, and knowledge transfer. PPE policy should still be maintained and audited, but this dataset does not support choosing a single PPE regime based on raw infection counts alone.",
            styles["Body"],
        )
    )

    story.append(paragraph("Recommendations", styles["Section"]))
    recommendations = [
        "Prioritise retention of experienced nursing staff as part of infection-control planning.",
        "Pair less experienced staff with senior mentors in higher-risk units.",
        "Review PPE standards as a system-level control rather than selecting a regime from unadjusted rates.",
        "Reassess external training content and measurement, since training coverage alone does not explain lower infection rates here.",
    ]
    for item in recommendations:
        story.append(paragraph(f"- {item}", styles["Body"]))

    story.append(paragraph("Limitations", styles["Section"]))
    story.append(
        paragraph(
            "The data is observational and aggregated, so the results should not be interpreted as individual-level causality. Unmeasured factors such as patient acuity, local outbreak pressure, ward type, shift pattern, and staffing mix may also influence infection rates.",
            styles["Body"],
        )
    )

    story.append(paragraph("Portfolio Notes", styles["Section"]))
    story.append(
        paragraph(
            "This PDF is the polished, employer-facing version of the analysis. The repository preserves the original source exports in an archive folder for provenance, while the main README, analysis source, and report are written as a personal statistical modelling project.",
            styles["Body"],
        )
    )

    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)


if __name__ == "__main__":
    main()
