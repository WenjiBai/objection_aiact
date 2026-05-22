# StockGlance — Data Inventory

**Last reviewed:** 2026-04-02 with the Data Protection Officer.

## Data sources used by StockGlance

| Source | Description | Personal data? |
|---|---|---|
| `sales_weekly` | Weekly aggregated units sold per SKU per warehouse | No |
| `lead_times` | Supplier lead-time history (median + p90 in days) | No |
| `seasonality` | Manually curated promotional calendar (holidays, sale events) | No |
| `sku_master` | SKU metadata (category, size, supplier ID) | No |
| `warehouse_capacity` | Per-warehouse storage capacity ceilings | No |

## Data StockGlance does **not** see

- Customer identifiers, customer-level purchases, customer email lists.
- Loyalty / membership data.
- Employee records, shift schedules, performance reviews.
- CCTV, biometric, or geolocation data.

## Storage and retention

- Training inputs are stored in a dedicated PostgreSQL schema on-prem.
- Forecast outputs are retained for 24 months for back-testing.
- No data leaves the EU; no third-party processor has access.

## Reassessment trigger

DPO sign-off is required before any of the following:

1. Adding any new data source that contains employee-level or customer-level
   information.
2. Using StockGlance outputs to make decisions about people (e.g. driving
   staffing plans).
3. Expanding StockGlance into a domain (logistics → workforce, finance, etc.)
   where Annex III may apply.
