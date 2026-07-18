# Quasi-Poisson Policy Analysis: Workplace Respiratory Infections

This personal analytics project evaluates workplace respiratory infection counts across a hospital network and identifies which operational factors are most strongly associated with infection rates.

The analysis uses a Poisson count model with an exposure offset for hours worked, then moves to a Quasi-Poisson model after detecting substantial overdispersion. The final model indicates that staff experience is the strongest predictor of lower infection rates, while PPE regime, external training coverage, and wage-increase coverage do not add meaningful explanatory value after experience is accounted for.

## Project Highlights

- Built a reproducible count-modelling workflow for infection-rate analysis.
- Used an exposure offset, `log(hours)`, so groups with different working hours can be compared fairly.
- Diagnosed overdispersion and replaced the standard Poisson model with a Quasi-Poisson specification.
- Translated model coefficients into incidence rate ratios (IRRs) for practical interpretation.
- Converted the original analysis into a portfolio-ready project structure and report.

## Repository Structure

```text
.
|-- analysis/
|   `-- workplace_infection_quasipoisson.Rmd
|-- data/
|   |-- README.md
|   `-- infections.csv
|-- reports/
|   |-- workplace_respiratory_infection_policy_analysis.pdf
|-- scripts/
|   `-- create_portfolio_report.py
|-- .gitignore
`-- README.md
```

## Key Findings

The dataset contains 72 aggregated observations, 397,350 worked hours, and 7,717 recorded infections.

| Finding | Portfolio-ready interpretation |
| --- | --- |
| Overdispersion | The Poisson model materially underestimates uncertainty, so a Quasi-Poisson model is more appropriate. |
| Nursing experience | Higher experience levels are associated with substantially lower infection rates. |
| PPE regime | PPE regime does not remain statistically meaningful after accounting for experience. |
| Wage increases | Wage-increase coverage does not show a clear relationship with infection rates in this dataset. |
| External training | External training coverage does not show a clear relationship with infection rates in this dataset. |

Final-model IRRs, compared with Experience Level 1:

| Experience level | IRR | Approx. interpretation |
| --- | ---: | --- |
| Level 2 | 0.421 | About 58% lower infection rate |
| Level 3 | 0.434 | About 57% lower infection rate |
| Level 4 | 0.254 | About 75% lower infection rate |

## How To Reproduce

Open R from the repository root and run:

```r
install.packages(c("tidyverse", "ggpubr"))
rmarkdown::render("analysis/workplace_infection_quasipoisson.Rmd")
```

To regenerate the portfolio PDF summary with the bundled Python/reportlab workflow:

```powershell
python scripts/create_portfolio_report.py
```

## Portfolio Framing

This repository is framed as a personal statistical modelling project. The public-facing files use neutral professional naming and remove classroom labels, student identifiers, and placeholder citation text. Original coursework-style exports are kept only in the local ignored archive for provenance, so they are not uploaded accidentally with the portfolio version.
