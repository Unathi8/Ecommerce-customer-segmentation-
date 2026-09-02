"""Quality checks for the e-commerce customer-segmentation workflow."""

from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from segmentation_pipeline import (  # noqa: E402
    EXPECTED_COLUMNS,
    build_customer_features,
    calculate_model_selection_scores,
    load_and_clean_transactions,
    prepare_rfm_matrix,
)


def test_cleaning_removes_invalid_transactions(tmp_path: Path) -> None:
    """Missing IDs, cancellations, and non-positive transactions must be excluded."""
    raw = pd.DataFrame(
        [
            ["10001", "A", "Item A", 2, "2011-01-01", 10.0, 12345, "United Kingdom"],
            ["C10002", "B", "Cancelled", 2, "2011-01-02", 10.0, 12345, "United Kingdom"],
            ["10003", "C", "Negative quantity", -1, "2011-01-03", 20.0, 12345, "United Kingdom"],
            ["10004", "D", "Missing customer", 1, "2011-01-04", 20.0, None, "United Kingdom"],
            ["10005", "E", "Zero price", 1, "2011-01-05", 0.0, 12345, "United Kingdom"],
        ],
        columns=[
            "InvoiceNo",
            "StockCode",
            "Description",
            "Quantity",
            "InvoiceDate",
            "UnitPrice",
            "CustomerID",
            "Country",
        ],
    )
    input_path = tmp_path / "transactions.xlsx"
    raw.to_excel(input_path, index=False)

    cleaned, audit = load_and_clean_transactions(input_path)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["Revenue"] == 20.0
    assert audit["dropped_missing_critical_fields"] == 1
    assert audit["dropped_cancellations"] == 1
    assert audit["dropped_non_positive_transactions"] == 2


def test_rfm_feature_calculation() -> None:
    """Customer aggregation should calculate standard RFM metrics correctly."""
    transactions = pd.DataFrame(
        {
            "CustomerID": ["A", "A", "B"],
            "InvoiceNo": ["1", "2", "3"],
            "InvoiceDate": pd.to_datetime(["2011-01-01", "2011-01-10", "2011-01-08"]),
            "Revenue": [20.0, 30.0, 50.0],
            "Quantity": [2, 3, 5],
            "Country": ["UK", "UK", "France"],
        }
    )

    customers, snapshot = build_customer_features(transactions)
    customer_a = customers.loc[customers["CustomerID"] == "A"].iloc[0]

    assert snapshot == pd.Timestamp("2011-01-11")
    assert customer_a["Recency"] == 1
    assert customer_a["Frequency"] == 2
    assert customer_a["Monetary"] == 50.0
    assert customer_a["AverageOrderValue"] == 25.0


def test_model_selection_includes_selected_cluster_count() -> None:
    """Elbow diagnostics must include the required four-cluster solution."""
    customers = pd.DataFrame(
        {
            "Recency": [1, 2, 3, 10, 12, 14, 50, 55, 60, 100, 105, 110],
            "Frequency": [12, 13, 11, 8, 7, 9, 3, 2, 4, 1, 1, 1],
            "Monetary": [1200, 1300, 1100, 800, 750, 900, 300, 250, 350, 100, 90, 110],
        }
    )
    scaled_rfm, _ = prepare_rfm_matrix(customers)
    diagnostics = calculate_model_selection_scores(scaled_rfm, k_values=range(2, 5))

    assert diagnostics["Clusters"].tolist() == [2, 3, 4]
    assert diagnostics["Inertia"].gt(0).all()
    assert diagnostics["SilhouetteScore"].between(-1, 1).all()


def test_generated_outputs_are_dashboard_ready() -> None:
    """Committed project outputs must be complete, valid, and internally consistent."""
    processed = PROJECT_ROOT / "data" / "processed"
    customers = pd.read_csv(processed / "customer_segments.csv")
    profiles = pd.read_csv(processed / "segment_profiles.csv")
    diagnostics = pd.read_csv(processed / "model_selection_metrics.csv")

    assert len(customers) > 4_000
    assert customers["CustomerID"].is_unique
    assert customers[["Recency", "Frequency", "Monetary", "Segment"]].notna().all().all()
    assert customers["Frequency"].gt(0).all()
    assert customers["Monetary"].gt(0).all()
    assert set(customers["Segment"]) == {
        "Champions",
        "Loyal Customers",
        "Potential Loyalists",
        "At Risk",
    }
    assert profiles["Customers"].sum() == len(customers)
    assert abs(profiles["RevenueSharePct"].sum() - 100) < 0.02
    assert 4 in diagnostics["Clusters"].tolist()
