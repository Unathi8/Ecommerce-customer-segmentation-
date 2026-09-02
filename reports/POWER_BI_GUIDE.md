# Power BI Dashboard Build Guide

## Purpose

This guide converts the generated customer-segmentation outputs into a clean, interactive Power BI report. The intended audience is a commercial or CRM stakeholder who needs to understand customer value, prioritise marketing audiences, and drill from segment-level metrics to customer-level detail.

> **Primary input:** `data/processed/customer_segments.csv` is one row per customer and should be the centre of the dashboard model.

## Import and data model

Import the five CSV files from `data/processed/` through **Get Data → Text/CSV**. Confirm that `CustomerID` is treated as text; numeric fields are decimal or whole number as appropriate; and `FirstPurchaseDate` and `LastPurchaseDate` are Date fields. In the model view, make the relationship below active with a single-direction filter from `Segment Profiles` to `Customer Segments`.

| Table | Grain | Role | Key field |
| --- | --- | --- | --- |
| `Customer Segments` | One row per customer | Fact-style analytical table for all customer KPIs and details | `CustomerID` |
| `Segment Profiles` | One row per segment | Segment-level context, revenue/customer share, and recommendation text | `Segment` |
| `Segment Recommendations` | One row per segment | Campaign playbook content | `Segment` |
| `Model Selection Metrics` | One row per candidate cluster count | Methodology diagnostic only | `Clusters` |
| `Cleaning Audit` | One row per cleaning measure | Data-quality documentation only | `CleaningMetric` |

| Relationship | Cardinality | Cross-filter direction |
| --- | --- | --- |
| `Segment Profiles[Segment]` → `Customer Segments[Segment]` | One-to-many | Single |
| `Segment Recommendations[Segment]` → `Customer Segments[Segment]` | One-to-many | Single |

Sort `Customer Segments[Segment]` by `Customer Segments[SegmentOrder]`. Sort `Segment Profiles[Segment]` by `Segment Profiles[SegmentOrder]`. This keeps the business-priority sequence consistent: Champions, Loyal Customers, Potential Loyalists, and At Risk.

## Measures

Create the following measures in the `Customer Segments` table. The formulas use customer-level fields intentionally, so `Total Revenue` equals the sum of each customer's historical Monetary value and `Customers` counts the distinct customer identifier.

```DAX
Customers =
DISTINCTCOUNT ( 'Customer Segments'[CustomerID] )

Total Revenue =
SUM ( 'Customer Segments'[Monetary] )

Average Customer Value =
DIVIDE ( [Total Revenue], [Customers] )

Average Recency (Days) =
AVERAGE ( 'Customer Segments'[Recency] )

Average Frequency =
AVERAGE ( 'Customer Segments'[Frequency] )

Average Order Value =
AVERAGE ( 'Customer Segments'[AverageOrderValue] )

Revenue Share % =
DIVIDE (
    [Total Revenue],
    CALCULATE ( [Total Revenue], ALL ( 'Customer Segments'[Segment] ) )
)

Customer Share % =
DIVIDE (
    [Customers],
    CALCULATE ( [Customers], ALL ( 'Customer Segments'[Segment] ) )
)

At-Risk Customers =
CALCULATE ( [Customers], 'Customer Segments'[Segment] = "At Risk" )

At-Risk Revenue =
CALCULATE ( [Total Revenue], 'Customer Segments'[Segment] = "At Risk" )
```

Format `Total Revenue`, `Average Customer Value`, `Average Order Value`, and `At-Risk Revenue` as **Currency (GBP)**. Format the share metrics as a percentage with one decimal place. Format recency and frequency measures as whole or one-decimal numeric values.

## Report layout

The recommended report has two pages. Page 1 communicates the executive story in less than a minute; Page 2 supports CRM activation and customer-level review.

### Page 1 — Executive segmentation overview

Use a 16:9 canvas with a light neutral background, a dark navy title band, and one clear statement beneath the title: **“Protect Champions, grow Loyal Customers, convert recent buyers, and reactivate At Risk customers.”** Place slicers for `Country` and `Segment` across the top. Use the following visual design.

| Visual | Configuration | Decision it supports |
| --- | --- | --- |
| KPI cards | `Customers`, `Total Revenue`, `Average Customer Value`, `At-Risk Customers` | High-level portfolio scale and risk exposure |
| Donut chart | Legend: `Segment`; Values: `Customers` | Customer mix by segment |
| Clustered bar chart | Y-axis: `Segment`; X-axis: `Total Revenue` | Revenue concentration by segment |
| Scatter chart | X-axis: average `Recency`; Y-axis: `Total Revenue`; Size: `Customers`; Details: `Segment` | Compare value and inactivity at once |
| Matrix | Rows: `Segment`; Values: customer/revenue shares, average recency, frequency, and customer value | Segment performance benchmarking |
| Table | `Segment`, `RecommendedAction` from `Segment Profiles` | Convert findings into next actions |

### Page 2 — Customer activation and diagnostic detail

Use the same segment and country slicers. Include a detail table with `CustomerID`, `Country`, `LastPurchaseDate`, `Recency`, `Frequency`, `Monetary`, `AverageOrderValue`, and `Segment`. Apply conditional formatting to Recency so higher values show a stronger warning colour. A top-N customer bar chart, segmented by `Segment`, supports VIP-list development. Place a line chart from `Model Selection Metrics` with `Clusters` on the X-axis and `Inertia` on the Y-axis in a methodology panel; add the `SilhouetteScore` to a tooltip.

## Segment colour system

Use this fixed colour system in every visual. Consistent colour assignment reduces cognitive load and makes cross-page comparison immediate.

| Segment | Hex colour | Semantic intent |
| --- | --- | --- |
| Champions | `#0F766E` | Established, high-value relationship |
| Loyal Customers | `#2563EB` | Trusted, growth-ready base |
| Potential Loyalists | `#D97706` | Opportunity requiring conversion |
| At Risk | `#DC2626` | Inactivity requiring intervention |

## Quality checks before sharing

Before publishing, filter each segment one at a time and confirm that customer count and total revenue agree with `segment_profiles.csv`. The source-output checks are shown below; minor differences only occur if report-level filters have been applied.

| Segment | Customers | Total revenue | Average recency |
| --- | ---: | ---: | ---: |
| Champions | 731 | £5,792,418.42 | 12.45 days |
| Loyal Customers | 1,177 | £2,110,874.60 | 68.03 days |
| Potential Loyalists | 889 | £438,524.82 | 21.98 days |
| At Risk | 1,541 | £545,391.05 | 191.42 days |

The dashboard should communicate that higher recency represents **longer time since the last purchase**, which is a risk signal. Do not apply a green-good / red-bad interpretation to raw recency values without explaining this directionality.

## Refresh process

When fresh transaction data arrives, replace the raw workbook, run the Python command in the project README, and refresh the Power BI queries. Keep the field names unchanged so all measures and visuals continue to work. Reassess the four-cluster choice when the customer mix or business strategy changes, and retain the `Model Selection Metrics` table as a transparent model-governance artefact.
