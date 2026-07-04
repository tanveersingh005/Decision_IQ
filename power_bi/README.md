# DecisionIQ Power BI Dashboard Specifications

This directory contains the design specifications, layout guides, and DAX calculations required to build the production-ready **DecisionIQ Power BI Dashboard Suite**.

---

## 1. Visual Brand Guidelines

To ensure a cohesive, professional executive look and feel, the following design guidelines must be adhered to:

### Color Palette
*   **Primary Navy** (`#1B2A4A`): Backgrounds for side navigation, headers, and major KPI cards.
*   **Accent Amber/Gold** (`#C5A059`): Primary highlight color for high-performance elements, selected tabs, and targets.
*   **Cool Slate** (`#F4F5F7`): Page background for light-mode dashboards, providing breathing room.
*   **Charcoal Slate** (`#2D3142`): Text body, sub-headings, and chart grid lines.
*   **System Green** (`#2E7D32`): Warm emerald for positive growth and met goals (e.g., revenue increase, positive variance).
*   **System Red** (`#C62828`): Soft crimson for high-risk warnings (e.g., churn spike, supplier delays).

### Typography
*   **Primary Font:** Inter, Segoe UI, or Arial (avoid standard serif or highly stylized fonts).
*   **Title Header:** 20-24pt Semi-bold.
*   **Card KPIs:** 36-40pt Bold.
*   **Body & Labels:** 9-11pt Regular.

---

## 2. Dashboard Navigation & Layouts

The suite consists of five core dashboard pages, linked via an interactive side navigation panel.

### Side Navigation Panel
*   **Position:** Fixed left sidebar (width: 15% of screen width).
*   **Structure:**
    *   *Top:* DecisionIQ Logo (Gold) and "Operational Intelligence" subtitle.
    *   *Links:* CEO Dashboard, Finance Dashboard, Operations Dashboard, Customer Success Dashboard, Marketing & Support.
    *   *Bottom:* "Run Operational Audit" bookmark button (links to Insight Engine page).

---

### Dashboard Page 1: CEO Control Tower
**Objective:** The ultimate executive flight deck summarizing global operations, health scores, and critical root causes.

```
+--------------------------------------------------------------------------------+
|  [Logo] DECISIONIQ       | CEO Control Tower Dashboard          [Filters: Date, Region] |
+--------------------------+-----------------------------------------------------+
| (Left Sidebar Navigation)| [KPI: Health Score]  [KPI: Net Revenue]  [KPI: CSAT]         |
| [X] CEO Control Tower    |       86 / 100            $18.4M            4.1 / 5         |
| [ ] Finance Dashboard    +-----------------------------------------------------+
| [ ] Operations Intel     | [Line Chart: Net Revenue & 12W Forecast Projection] |
| [ ] Customer Success     |   Shows historical revenue, with 90-day ML forecast |
| [ ] Marketing & Support  +-----------------------------------------------------+
|                          | [Diagnostic Insight Feed: Auto-Generated Insights]  |
|                          | - **West Coast Logistics failure** in Q2 2025       |
|                          | - **Social Media ad spend leakage** in EMEA         |
+--------------------------+-----------------------------------------------------+
```

---

### Dashboard Page 2: Finance Intelligence
**Objective:** Track gross-to-net revenue conversions, identify margin leakages, and monitor subscription cash flows.
*   **Top Card Group:** Gross Revenue, Net Revenue, Margin %, Revenue Leakage.
*   **Visual 1 (Waterfall Chart):** Gross Revenue -> Cost of Goods Sold (COGS) -> Shipping Costs -> Refunds -> Cancelled Orders -> Net Profit.
*   **Visual 2 (Bar Chart):** Payment Failure Rate by Payment Method (shows ACH vs. CC vs. PayPal failure volumes).
*   **Visual 3 (Table):** Product Profitability ranking showing Margin per unit and SKU sales.

---

### Dashboard Page 3: Operations & Logistics
**Objective:** Monitor warehouse capacities, supplier reliability ratings, and delivery status trends.
*   **Top Card Group:** Late Delivery Rate, Average Transit Time, Reorder Alerts (Stockouts).
*   **Visual 1 (Scatter Plot):** Supplier Lead Time vs. Reliability Score (highlighting Apex Tech as an outlier in Q2 2025).
*   **Visual 2 (Stacked Bar Chart):** Delivery Status by Warehouse (shows West Coast WH002 having highest % of late orders).
*   **Visual 3 (Table):** Critical Stockout Risks (lists SKU, Warehouse, current stock, and average daily sales rate).

---

### Dashboard Page 4: Customer Success (Retention & Cohorts)
**Objective:** Visualize cohort retention heatmaps, customer segment LTV, and ML-predicted churn risks.
*   **Top Card Group:** Monthly Churn Rate, Average Customer LTV, NPS.
*   **Visual 1 (Matrix Heatmap):** Cohort Retention Month 0 to Month 12 (shows percentage drop in repeat ordering by monthly cohort).
*   **Visual 2 (Bar Chart):** Customer Lifetime Value by Acquisition Channel (Referral vs Direct vs Paid Ads).
*   **Visual 3 (Table):** Customers with High Churn Risk (displays customer ID, Company Name, CSAT, Support Ticket count, and predicted risk probability from the Python model).

---

## 3. Power BI Implementation Instructions

1.  **Themes:** Load the custom JSON theme file using the color hex values defined above.
2.  **Date Table:** Ensure a standard SQL/DAX Date table is created and marked as a Date table to support time intelligence functions (YTD, YoY, rolling averages).
3.  **Relationships:** Create standard active 1-to-many relationships from dimension tables (Customers, Products, Warehouses, Suppliers) to the Fact tables (Orders, Shipments, Customer Support).
4.  **Bookmarks:** Use the Bookmarks pane to toggle the visibility of the "Insights detail" popups to keep dashboards clean.
