# Data Dictionary
## DecisionIQ Data Warehouse Schema

This document provides detailed metadata and field-level descriptions for the 14 relational tables defined in the DecisionIQ operational database schema.

---

## 1. Dimensional / Lookup Tables

### `regions`
Represents the global geographic sales territories.
*   `region_id` (VARCHAR, PK): Unique identifier for the region (e.g., `REG01`).
*   `region_name` (VARCHAR): Name of the territory (e.g., `North America`).
*   `country` (VARCHAR): Base country of operations (e.g., `United States`).
*   `manager_name` (VARCHAR): Regional Director managing the territory.

### `employees`
Contains employee information, establishing reporting lines.
*   `employee_id` (VARCHAR, PK): Unique identifier for the employee (e.g., `EMP001`).
*   `first_name` (VARCHAR): First name.
*   `last_name` (VARCHAR): Last name.
*   `email` (VARCHAR, UNIQUE): Corporate email address.
*   `role` (VARCHAR): Job title (e.g., `Sales Representative`).
*   `department` (VARCHAR): Business department (e.g., `Sales`, `Operations`).
*   `region_id` (VARCHAR, FK): References `regions.region_id` (can be null for global execs).
*   `hire_date` (DATE): Date of hire.
*   `reports_to` (VARCHAR, FK): Self-referencing FK to `employees.employee_id`.

### `products`
Catalog of software licenses, hardware items, and support offerings.
*   `product_id` (VARCHAR, PK): Unique identifier (e.g., `PROD001`).
*   `product_name` (VARCHAR): Display name of the product.
*   `sku` (VARCHAR, UNIQUE): Stock Keeping Unit string.
*   `category` (VARCHAR): Product category (`Software`, `Hardware`, `Support`, `Professional Services`).
*   `unit_price` (DECIMAL): Standard sales price.
*   `unit_cost` (DECIMAL): Direct manufacturing/provisioning cost.
*   `status` (VARCHAR): Availability status (`Active`, `Discontinued`).

### `warehouses`
Physical logistics nodes.
*   `warehouse_id` (VARCHAR, PK): Unique identifier (e.g., `WH001`).
*   `warehouse_name` (VARCHAR): Name of the facility.
*   `location` (VARCHAR): City and state/country.
*   `region_id` (VARCHAR, FK): References `regions.region_id`.
*   `capacity_sqft` (INTEGER): Total square footage.
*   `operating_cost_monthly` (DECIMAL): Monthly overhead cost.

### `suppliers`
Logistics component suppliers.
*   `supplier_id` (VARCHAR, PK): Unique identifier (e.g., `SUP001`).
*   `supplier_name` (VARCHAR): Name of the vendor.
*   `contact_name` (VARCHAR): Primary contact name.
*   `email` (VARCHAR): Contact email.
*   `lead_time_days` (INTEGER): Contractual average lead time in days.
*   `reliability_score` (DECIMAL): Historic performance index (between 0.00 and 1.00).

---

## 2. Transactional / Fact Tables

### `customers`
B2B customer accounts.
*   `customer_id` (VARCHAR, PK): Unique account identifier (e.g., `CUST00001`).
*   `company_name` (VARCHAR): Registered corporate name.
*   `contact_name` (VARCHAR): Account contact person.
*   `contact_email` (VARCHAR, UNIQUE): Contact email address.
*   `customer_segment` (VARCHAR): Tier segment (`SMB`, `ENTERPRISE`, `STRATEGIC`).
*   `region_id` (VARCHAR, FK): References `regions.region_id`.
*   `status` (VARCHAR): Current health status (`Active`, `Churned`, `At-Risk`).
*   `acquisition_date` (DATE): Account creation date.
*   `acquisition_channel` (VARCHAR): Acquisition source (`Direct`, `Referral`, `Organic Search`, `Paid Ads`).

### `orders`
Header table for sales transactions.
*   `order_id` (VARCHAR, PK): Unique invoice identifier.
*   `customer_id` (VARCHAR, FK): References `customers.customer_id`.
*   `order_date` (DATE): Transaction date.
*   `status` (VARCHAR): Order status (`Completed`, `Shipped`, `Processing`, `Cancelled`, `Refunded`).
*   `sales_representative_id` (VARCHAR, FK): References `employees.employee_id`.
*   `total_amount` (DECIMAL): Total invoice value including discounts.
*   `currency` (VARCHAR): Standard transaction currency code (`USD`).

### `order_details`
Line items for each order.
*   `order_detail_id` (VARCHAR, PK): Line item identifier.
*   `order_id` (VARCHAR, FK): References `orders.order_id`.
*   `product_id` (VARCHAR, FK): References `products.product_id`.
*   `quantity` (INTEGER): Number of units purchased.
*   `unit_price` (DECIMAL): Sales price at checkout.
*   `discount_amount` (DECIMAL): Discount amount applied to this line.
*   `subtotal` (DECIMAL): Realized amount (`quantity * unit_price - discount_amount`).

### `payments`
Details financial settlements.
*   `payment_id` (VARCHAR, PK): Unique settlement ID.
*   `order_id` (VARCHAR, FK): References `orders.order_id`.
*   `payment_date` (DATE): Transaction settlement date.
*   `payment_method` (VARCHAR): Method used (`Credit Card`, `ACH`, `Wire`, `PayPal`).
*   `payment_status` (VARCHAR): Status (`Success`, `Failed`, `Refunded`).
*   `amount` (DECIMAL): Settled payment amount.
*   `transaction_id` (VARCHAR, UNIQUE): Processor gateway ID.

### `shipments`
Tracks hardware component fulfillment.
*   `shipment_id` (VARCHAR, PK): Logistics tracker ID.
*   `order_id` (VARCHAR, FK): References `orders.order_id`.
*   `warehouse_id` (VARCHAR, FK): References `warehouses.warehouse_id`.
*   `supplier_id` (VARCHAR, FK): References `suppliers.supplier_id`.
*   `carrier` (VARCHAR): Carrier name (`FedEx`, `UPS`, `DHL`, `Freight`).
*   `shipment_date` (DATE): Date left warehouse.
*   `estimated_delivery_date` (DATE): Contractual target delivery date.
*   `actual_delivery_date` (DATE): Actual arrival date.
*   `delivery_status` (VARCHAR): Status (`On Time`, `Late`, `In Transit`, `Returned`).

### `customer_support`
Customer support ticket logs.
*   `ticket_id` (VARCHAR, PK): Ticket identifier.
*   `customer_id` (VARCHAR, FK): References `customers.customer_id`.
*   `created_at` (TIMESTAMP): Date and time opened.
*   `closed_at` (TIMESTAMP): Date and time resolved.
*   `status` (VARCHAR): Lifecycle status (`Open`, `In Progress`, `Resolved`, `Escalated`).
*   `priority` (VARCHAR): Ticket severity (`Low`, `Medium`, `High`, `Critical`).
*   `category` (VARCHAR): Inquiry type (`Billing`, `Technical`, `Product`, `Logistics`).
*   `satisfaction_score` (INTEGER): Rating left by customer (1 to 5).
*   `agent_id` (VARCHAR, FK): References `employees.employee_id`.

### `daily_business_metrics`
Aggregated daily traffic and marketing indicators.
*   `metric_date` (DATE, PK): Date of aggregation.
*   `active_users` (INTEGER): Count of active portal users.
*   `website_visitors` (INTEGER): Unique visitors to the website.
*   `leads_generated` (INTEGER): Number of registered marketing leads.
*   `cac` (DECIMAL): Customer Acquisition Cost on that date.
*   `nps` (INTEGER): Measured Net Promoter Score.
