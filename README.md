# Quasi-Poisson Policy Analysis

![R](https://img.shields.io/badge/R-Statistical%20Modelling-276DC3?style=for-the-badge&logo=r&logoColor=white)
![R Markdown](https://img.shields.io/badge/R%20Markdown-Reproducible%20Research-75AADB?style=for-the-badge&logo=rstudio&logoColor=white)
![Python](https://img.shields.io/badge/Python-Report%20Automation-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Model](https://img.shields.io/badge/Model-Quasi--Poisson%20GLM-14324A?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Portfolio%20Ready-brightgreen?style=for-the-badge)

## 📖 Executive Summary (About)

**Quasi-Poisson Policy Analysis** is a reproducible statistical modelling project that evaluates workplace respiratory infection counts across a hospital network. The project models infections as count outcomes, adjusts for unequal work exposure using `log(hours)` as an offset, and translates model coefficients into incidence rate ratios (IRRs) for practical policy interpretation.

The business problem is operationally important: healthcare leaders need to know which workforce and policy factors are meaningfully associated with infection rates after accounting for different exposure levels. A raw comparison of infection counts can be misleading because staff groups worked different total hours and because infection counts are highly overdispersed. This analysis therefore moves from a baseline Poisson model to a **Quasi-Poisson generalised linear model (GLM)** after formal overdispersion diagnostics.

The final outcome is a portfolio-ready policy analytics package with an R Markdown analysis, a clean dataset, and an automated PDF report. The dataset contains **72 aggregated observations**, **397,350 worked hours**, and **7,717 recorded infections**, with an overall rate of **19.4 infections per 1,000 worked hours**. The final model finds nursing experience to be the dominant predictor: compared with Experience Level 1, Levels 2, 3, and 4 are associated with approximately **58%**, **57%**, and **75%** lower infection rates, respectively.

## 🚀 Technical Highlights & Business Value

- **Exposure-adjusted count modelling:** Uses an offset term, `log(hours)`, so infection rates are compared fairly across groups with different working-hour exposure.
- **Overdispersion-aware inference:** Detects severe Poisson overdispersion with a dispersion ratio of **49.4** versus an expected threshold of approximately **1.5**, then applies Quasi-Poisson standard-error correction.
- **Decision-ready effect translation:** Converts log-scale model coefficients into IRRs and rate-reduction language that policy stakeholders can understand.
- **Structured model selection:** Uses F-test based backward elimination for quasi-likelihood models, where standard AIC-based comparison is not appropriate.
- **Actionable workforce insight:** Identifies staff experience and retention as stronger infection-control signals than PPE regime, wage-increase coverage, or external training coverage in this dataset.

## 🛠️ Tech Stack & Skills Demonstrated

* **Languages:** R, Python, Markdown
* **Frameworks & Libraries:** `tidyverse`, `ggpubr`, `rmarkdown`, Python `pandas`, `numpy`, `reportlab`
* **Methodologies:** Poisson regression, Quasi-Poisson GLM, exposure offsets, overdispersion diagnostics, incidence rate ratios, F-test model selection, policy analytics, reproducible reporting
* **Domain Skills:** Healthcare operations analytics, workplace infection-risk analysis, statistical modelling, policy evaluation, executive reporting, quantitative decision support

## 🔑 Keywords & Tags

R, Quasi-Poisson, Poisson regression, GLM, count data, healthcare analytics, policy analysis, infection control, incidence rate ratio, overdispersion, exposure offset, R Markdown, report automation, workforce analytics, statistical consulting

## 🏗️ Architecture & Methodology

The repository is organized as a compact analytics pipeline. The `data/` layer stores the public modelling dataset and schema documentation. The `analysis/` layer contains the R Markdown workflow for data preparation, exploratory visualization, model fitting, overdispersion diagnostics, covariate selection, final-model interpretation, and limitations. The `scripts/` layer contains a Python `reportlab` workflow for generating a polished employer-facing PDF report.

The modelling approach begins with the natural count-data specification:

```r
infections ~ ppe_regime + experience + wage_inc + training
```

Because each row represents a different amount of worked time, the model includes exposure through:

```r
offset = log(hours)
```

This makes the expected infection count proportional to worked hours and allows coefficients to be interpreted as multiplicative effects on the infection rate. The initial Poisson model is then checked using deviance-based goodness-of-fit and dispersion diagnostics. Since the dispersion ratio is far above the acceptable threshold, the final inference uses:

```r
family = quasipoisson(link = "log")
```

The final model-retention strategy removes operational covariates that do not provide meaningful additional explanatory value after accounting for experience. Because Quasi-Poisson models are quasi-likelihood models, the workflow uses F-tests for nested model comparison rather than relying on standard AIC.

## 📂 Repository Structure

```text
Quasi-Poisson-Policy-Analysis/
+-- README.md                                      # Professional project overview
+-- .gitattributes                                # Git file handling rules
+-- .gitignore                                    # Local artifact exclusions
+-- analysis/
|   +-- workplace_infection_quasipoisson.Rmd       # Main R analysis workflow
+-- data/
|   +-- README.md                                  # Data dictionary
|   +-- infections.csv                             # Public modelling dataset
+-- reports/
|   +-- README.md                                  # Report documentation
|   +-- workplace_respiratory_infection_policy_analysis.pdf  # Portfolio PDF report
+-- scripts/
    +-- create_portfolio_report.py                 # Automated PDF generator
```

## 📊 Dataset Snapshot

| Metric | Value |
|---|---:|
| Aggregated observations | `72` |
| Recorded infections | `7,717` |
| Worked hours | `397,350` |
| Overall infection rate | `19.4` per 1,000 hours |
| Missing values | `0` |

## 📈 Final Model Results

Final-model IRRs are interpreted relative to **Experience Level 1**.

| Experience Level | IRR | 95% CI | Approximate Interpretation |
|---|---:|---:|---|
| Level 2 | `0.421` | `0.272` to `0.650` | 58% lower infection rate |
| Level 3 | `0.434` | `0.297` to `0.633` | 57% lower infection rate |
| Level 4 | `0.254` | `0.155` to `0.417` | 75% lower infection rate |

Experience-level descriptive rates reinforce the model interpretation:

| Experience Level | Infections | Worked Hours | Rate per 1,000 Hours |
|---|---:|---:|---:|
| Level 1 | `2,460` | `59,528` | `41.3` |
| Level 2 | `1,580` | `90,865` | `17.4` |
| Level 3 | `2,620` | `146,220` | `17.9` |
| Level 4 | `1,057` | `100,737` | `10.5` |

## 💼 Policy Interpretation

The analysis suggests that workforce experience should be treated as an infection-control asset, not merely a staffing descriptor. PPE regime shows visible differences in unadjusted exploratory plots, but those differences do not remain meaningfully explanatory once experience is included in the multivariable model.

Recommended operational actions:

- Prioritize retention of experienced nursing staff as part of infection-control planning.
- Pair less experienced staff with senior mentors in higher-risk units.
- Review PPE standards as system-level controls rather than selecting a regime from unadjusted infection rates.
- Reassess external training content and measurement, since training coverage alone does not explain lower infection rates in this dataset.

## ⚙️ Reproducibility & Usage

Install the R dependencies:

```r
install.packages(c("tidyverse", "ggpubr"))
```

Render the R Markdown analysis from the repository root:

```r
rmarkdown::render("analysis/workplace_infection_quasipoisson.Rmd")
```

Regenerate the portfolio PDF summary:

```powershell
python scripts/create_portfolio_report.py
```

## 📄 Reports & Deliverables

- `analysis/workplace_infection_quasipoisson.Rmd` - full statistical workflow and interpretation.
- `data/infections.csv` - public aggregated infection dataset used for modelling.
- `data/README.md` - data dictionary and feature descriptions.
- `reports/workplace_respiratory_infection_policy_analysis.pdf` - 2-page employer-facing policy report.
- `scripts/create_portfolio_report.py` - Python report-generation pipeline.

## ⚠️ Limitations

This is an observational analysis of aggregated records. The results should not be interpreted as individual-level causality. Unmeasured factors such as patient load, ward acuity, local outbreak pressure, shift patterns, unit type, and staffing mix may also influence infection rates. The analysis is strongest as a policy-prioritization and modelling demonstration, not as a standalone causal-impact study.

## 🎯 Project Outcome

This project demonstrates end-to-end statistical consulting capability: selecting the correct model family for overdispersed count data, adjusting for exposure, validating assumptions, translating coefficients into policy-ready IRRs, and packaging the work into a clean GitHub portfolio artifact. It is directly relevant to healthcare analytics, workforce planning, public-sector policy analysis, infection-control reporting, and applied GLM modelling roles.
