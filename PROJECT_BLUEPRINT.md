# Project Blueprint

## Objective

This repository delivers an end-to-end **e-commerce customer segmentation** workflow. It converts invoice-level transaction data into clean customer-level RFM features, selects a four-cluster K-Means solution using an elbow-method diagnostic, translates clusters into business-friendly customer segments, and publishes dashboard-ready CSV and Excel outputs.

## Dataset

The analysis uses the UCI Machine Learning Repository's **Online Retail** data, a UK non-store retailer transaction dataset covering 1 December 2010 through 9 December 2011. The source has 541,909 invoice-line records and is licensed CC BY 4.0.[1]

## Repository Layout

| Path | Purpose |
| --- | --- |
| `data/raw/` | Raw UCI workbook downloaded locally during setup; excluded from version control. |
| `data/processed/` | Reproducible, dashboard-ready CSV outputs. |
| `notebooks/` | Exploratory-analysis notebook. |
| `src/` | Reusable Python modules and command-line pipeline. |
| `reports/figures/` | Generated analytical visuals. |
| `reports/` | Executive findings and Power BI build guide. |
| `outputs/` | Excel analysis workbook exported by the pipeline. |
| `tests/` | Automated data and output validation checks. |

## Workflow

| Step | Method | Deliverable |
| --- | --- | --- |
| Data ingestion | Read UCI Excel data with explicit parsing and column validation | Typed invoice-line table |
| Cleaning | Remove missing customer IDs, cancellations, non-positive quantities/prices, and duplicate lines | Clean transaction table |
| Feature engineering | Aggregate recency, frequency, monetary value, order items, average order value, tenure, and country | Customer-level RFM feature table |
| Model selection | Standardize log-transformed RFM metrics and calculate inertia for `k=2` to `k=8` | Elbow-method chart |
| Segmentation | Fit deterministic K-Means with `k=4` and name groups from customer behavior | Segment assignments and profiles |
| Business reporting | Plot distributions and create Excel/Power BI inputs | Charts, `.xlsx` report, dashboard CSVs |

## Reproducibility Principles

All paths will be project-relative, the random seed will be fixed, and generated artefacts will be rebuilt through one command. The repository will retain a small transparent analysis sample while the original raw workbook remains excluded to keep the Git history lightweight.

## References

[1]: https://archive.ics.uci.edu/dataset/352/online+retail "UCI Machine Learning Repository — Online Retail"
