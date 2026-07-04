-- DecisionIQ Enterprise Data Warehouse Schema
-- Compatible with PostgreSQL and SQLite

-- DROP EXISTING TABLES (Reverse Dependency Order)
DROP TABLE IF EXISTS daily_business_metrics;
DROP TABLE IF EXISTS customer_support;
DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS order_details;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS marketing_campaigns;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS warehouses;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS regions;

-- 1. REGIONS
CREATE TABLE IF NOT EXISTS regions (
    region_id VARCHAR(50) PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    manager_name VARCHAR(100) NOT NULL
);

-- 2. EMPLOYEES
CREATE TABLE IF NOT EXISTS employees (
    employee_id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    role VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    region_id VARCHAR(50),
    hire_date DATE NOT NULL,
    reports_to VARCHAR(50),
    FOREIGN KEY (region_id) REFERENCES regions(region_id),
    FOREIGN KEY (reports_to) REFERENCES employees(employee_id)
);

-- 3. CUSTOMERS
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    contact_email VARCHAR(150) UNIQUE NOT NULL,
    customer_segment VARCHAR(50) NOT NULL, -- SMB, Enterprise, Strategic
    region_id VARCHAR(50),
    status VARCHAR(50) NOT NULL, -- Active, Churned, At-Risk
    acquisition_date DATE NOT NULL,
    acquisition_channel VARCHAR(100) NOT NULL, -- Direct, Referral, Organic Search, Paid Ads
    FOREIGN KEY (region_id) REFERENCES regions(region_id)
);

-- 4. PRODUCTS
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    sku VARCHAR(50) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL, -- Software, Hardware, Professional Services, Support
    unit_price DECIMAL(12, 2) NOT NULL CHECK (unit_price >= 0),
    unit_cost DECIMAL(12, 2) NOT NULL CHECK (unit_cost >= 0),
    status VARCHAR(50) NOT NULL -- Active, Discontinued
);

-- 5. WAREHOUSES
CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id VARCHAR(50) PRIMARY KEY,
    warehouse_name VARCHAR(100) NOT NULL,
    location VARCHAR(150) NOT NULL,
    region_id VARCHAR(50),
    capacity_sqft INTEGER NOT NULL,
    operating_cost_monthly DECIMAL(12, 2) NOT NULL CHECK (operating_cost_monthly >= 0),
    FOREIGN KEY (region_id) REFERENCES regions(region_id)
);

-- 6. INVENTORY
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id VARCHAR(50) PRIMARY KEY,
    warehouse_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    quantity_on_hand INTEGER NOT NULL CHECK (quantity_on_hand >= 0),
    reorder_point INTEGER NOT NULL CHECK (reorder_point >= 0),
    last_stock_count_date DATE NOT NULL,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    UNIQUE (warehouse_id, product_id)
);

-- 7. SUPPLIERS
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id VARCHAR(50) PRIMARY KEY,
    supplier_name VARCHAR(150) NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    lead_time_days INTEGER NOT NULL CHECK (lead_time_days >= 0),
    reliability_score DECIMAL(5, 2) NOT NULL CHECK (reliability_score >= 0.0 AND reliability_score <= 1.0)
);

-- 8. ORDERS
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    order_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL, -- Completed, Shipped, Processing, Cancelled, Refunded
    sales_representative_id VARCHAR(50),
    total_amount DECIMAL(12, 2) NOT NULL CHECK (total_amount >= 0),
    currency VARCHAR(10) NOT NULL DEFAULT 'USD',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (sales_representative_id) REFERENCES employees(employee_id)
);

-- 9. ORDER_DETAILS
CREATE TABLE IF NOT EXISTS order_details (
    order_detail_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(12, 2) NOT NULL CHECK (unit_price >= 0),
    discount_amount DECIMAL(12, 2) NOT NULL DEFAULT 0.0 CHECK (discount_amount >= 0),
    subtotal DECIMAL(12, 2) NOT NULL CHECK (subtotal >= 0),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 10. PAYMENTS
CREATE TABLE IF NOT EXISTS payments (
    payment_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    payment_date DATE NOT NULL,
    payment_method VARCHAR(50) NOT NULL, -- ACH, Credit Card, Wire, PayPal
    payment_status VARCHAR(50) NOT NULL, -- Success, Failed, Refunded
    amount DECIMAL(12, 2) NOT NULL CHECK (amount >= 0),
    transaction_id VARCHAR(100) UNIQUE,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- 11. SHIPMENTS
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    warehouse_id VARCHAR(50) NOT NULL,
    supplier_id VARCHAR(50) NOT NULL,
    carrier VARCHAR(50) NOT NULL, -- FedEx, UPS, DHL, Freight
    shipment_date DATE,
    estimated_delivery_date DATE NOT NULL,
    actual_delivery_date DATE,
    delivery_status VARCHAR(50) NOT NULL, -- On Time, Late, In Transit, Returned
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

-- 12. MARKETING_CAMPAIGNS
CREATE TABLE IF NOT EXISTS marketing_campaigns (
    campaign_id VARCHAR(50) PRIMARY KEY,
    campaign_name VARCHAR(150) NOT NULL,
    channel VARCHAR(100) NOT NULL, -- Social Media, PPC, Email, SEO, Event
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    budget DECIMAL(12, 2) NOT NULL CHECK (budget >= 0),
    clicks INTEGER NOT NULL CHECK (clicks >= 0),
    impressions INTEGER NOT NULL CHECK (impressions >= 0),
    conversions INTEGER NOT NULL CHECK (conversions >= 0)
);

-- 13. CUSTOMER_SUPPORT
CREATE TABLE IF NOT EXISTS customer_support (
    ticket_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    closed_at TIMESTAMP,
    status VARCHAR(50) NOT NULL, -- Open, In Progress, Resolved, Escalated
    priority VARCHAR(50) NOT NULL, -- Low, Medium, High, Critical
    category VARCHAR(100) NOT NULL, -- Billing, Technical, Product, Logistics
    satisfaction_score INTEGER CHECK (satisfaction_score >= 1 AND satisfaction_score <= 5),
    agent_id VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (agent_id) REFERENCES employees(employee_id)
);

-- 14. DAILY_BUSINESS_METRICS
CREATE TABLE IF NOT EXISTS daily_business_metrics (
    metric_date DATE PRIMARY KEY,
    active_users INTEGER NOT NULL CHECK (active_users >= 0),
    website_visitors INTEGER NOT NULL CHECK (website_visitors >= 0),
    leads_generated INTEGER NOT NULL CHECK (leads_generated >= 0),
    cac DECIMAL(12, 2) NOT NULL CHECK (cac >= 0),
    nps INTEGER CHECK (nps >= -100 AND nps <= 100)
);

-- INDEXES FOR PERFORMANCE OPTIMIZATION
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_details_order_id ON order_details(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments(order_id);
CREATE INDEX IF NOT EXISTS idx_shipments_order_id ON shipments(order_id);
CREATE INDEX IF NOT EXISTS idx_shipments_actual_delivery ON shipments(actual_delivery_date);
CREATE INDEX IF NOT EXISTS idx_customer_support_customer ON customer_support(customer_id);
CREATE INDEX IF NOT EXISTS idx_inventory_warehouse_product ON inventory(warehouse_id, product_id);
