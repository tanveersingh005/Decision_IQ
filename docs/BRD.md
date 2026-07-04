# Business Requirements Document (BRD)
## Project DecisionIQ: Enterprise Operational Intelligence Platform

**Date:** July 4, 2026  
**Author:** Principal Data Analytics Architect & Senior BI Consultant  
**Status:** Approved for Implementation  
**Audience:** C-Suite Executives, Department Directors, Operations Lead, and Technical Developers  

---

## 1. Executive Summary

DecisionIQ is the company's internal Operational Intelligence Command Center. In modern enterprises, departments operate in silos: Sales manages CRM data, Finance tracks invoicing, Operations tracks inventory levels, and Customer Success monitors support tickets. Although huge volumes of data exist, executives cannot trace dependencies across departments. When revenue drops, the CEO cannot instantly identify if it was caused by a marketing campaign failure, supplier component shortages, warehouse delays, or customer support backlogs.

DecisionIQ connects these disparate data sources into a unified normalized Star/Snowflake schema data warehouse, executes advanced analytical window aggregations, runs predictive ML models, and operates an automated **Insight and Recommendation Engine** that translates data patterns into quantifiable business impacts and strategic decisions.

---

## 2. Business Objectives & Problem Statements

The platform addresses several critical enterprise queries:

| Business Department | Key Question Addressed | Impact of Failing to Answer |
| :--- | :--- | :--- |
| **C-Suite (CEO/COO)** | Why did overall revenue change? Which department caused the issue? | Slow response to systemic inefficiencies, leading to market share loss. |
| **Finance (CFO)** | Where is revenue leaking? What is the gross-to-net waterfall conversion? | Margin compression from unmonitored customer refunds and transaction failures. |
| **Operations & Logistics** | Which warehouses and suppliers are failing to meet delivery and reliability contracts? | Logistics delays and product stockouts, leading to order cancellation and CSAT drops. |
| **Customer Success** | Which accounts are at risk of churn based on satisfaction (CSAT) and support history? | Contract churn, directly decreasing Annual Recurring Revenue (ARR). |
| **Marketing** | Which ad campaigns are wasting budget and driving up Customer Acquisition Cost (CAC)? | Budget waste and declining return on ad spend (ROAS). |

---

## 3. Scope of Work

The project delivery comprises:
1.  **A Normalized Database Schema:** A 13-table Snowflake design supporting full referential integrity and optimized indexes.
2.  **ETL Pipeline:** Extract, clean (de-duplication, normalization), validate (schema check, numeric ranges, FK references), and bulk-load data.
3.  **Advanced Analytics SQL queries:** Realization of time-intelligence, cohort retention, and customer RFM segmentations directly in SQL.
4.  **Machine Learning Suite:** Three models targeting Customer Churn prediction, Weekly Revenue Forecasting, and Supplier Logistics Risk rating.
5.  **Insight and Recommendation Engine:** Automated root-cause heuristics correlating delayed deliveries to refund rates and customer support complaints.
6.  **Interactive Executive Web Dashboard:** Minimalist, consulting-grade visualization of all KPIs and insights with role-based filtering.

---

## 4. Key Performance Indicators (KPIs)

The platform computes and monitors the following target metrics:
*   **Business Health Score:** A weighted indicator (0-100) aggregating customer satisfaction, gross margins, account churn, and net revenue growth.
*   **Net Revenue:** Realized bookings excluding refunds and cancellations.
*   **Revenue Leakage Rate:** Percent of gross potential bookings lost to cancellations, refund requests, and payment failure.
*   **Late Shipment Rate:** Percent of deliveries shipped past the estimated delivery date.
*   **Customer Lifetime Value (LTV):** Average cumulative revenue generated per customer.
*   **CSAT Rating:** Average customer satisfaction score (1.0 to 5.0) collected via support ticket closures.
*   **Return on Ad Spend (ROAS):** Ratio of generated conversions value to marketing campaign budget.
