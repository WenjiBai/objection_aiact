# StockGlance — internal inventory forecaster

**Owner:** Supply Chain Engineering, Nordic Logistics Group
**Status:** In production since 2025-Q3 · v1.4

## What StockGlance does

StockGlance produces **weekly stock-need forecasts** for ~12,000 SKUs across
five regional warehouses. The output is a CSV file picked up by the
purchasing team's planning tool; purchasing officers review it and place all
purchase orders manually.

## Why we built it

Before StockGlance, our supply planners forecast SKU demand using a
hand-tuned Excel model. Stock-out rate was 4.2% on fast-moving SKUs; overstock
on slow movers tied up around €3.1M in working capital.

StockGlance has reduced stock-outs to 1.6% and freed about €1.8M in
working-capital savings over its first 12 months.

## How it works

- **Inputs:** SKU-level weekly sales (3 years history), supplier lead times,
  seasonality flags, planned promotions calendar.
- **Method:** Ensemble of classical time-series models — Prophet,
  exponentially weighted moving average, and a gradient-boosted residual
  corrector. No deep learning, no LLMs.
- **Outputs:** Forecast quantity per SKU per warehouse for the upcoming 12
  weeks, plus an uncertainty band.

## Decision-making

StockGlance produces forecasts; it does **not** place orders, set prices, or
make any decision about people. Human purchasing officers make all order
decisions and may freely deviate from the forecast.

## No personal data

StockGlance processes only inventory, sales aggregates, and supplier metadata.
No customer-level data, employee data, or personally identifying information
enters the model. This was confirmed with our DPO at deployment.

## Scope discipline

StockGlance is for inventory only. If the team ever wants to repurpose it for,
e.g., workforce planning or scheduling shift assignments, we'd treat that as a
new system and re-evaluate.
