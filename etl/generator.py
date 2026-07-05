import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import uuid
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("DataGenerator")

# Set random seed for reproducibility
np.random.seed(42)

def generate_synthetic_data(start_date_str="2023-07-01", end_date_str="2026-06-30"):
    """
    Generates realistic enterprise dataset.
    Randomly selects or overrides one of twelve business scenarios to inject during the final 6 months.
    """
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    total_days = (end_date - start_date).days + 1
    date_list = [start_date + timedelta(days=x) for x in range(total_days)]
    
    # 6-Month Crisis Period: Jan 1, 2026 to June 30, 2026
    crisis_start = datetime(2026, 1, 1).date()
    
    # Read environment override or pick randomly
    scenarios = [
        "SUPPLY_CHAIN_CRISIS", "MARKETING_INEFFICIENCY", "CUSTOMER_CHURN_SURGE", "INVENTORY_OVERSTOCK",
        "REGIONAL_SALES_COLLAPSE", "CASH_FLOW_CRISIS", "DEMAND_SPIKE", "SUPPLIER_RELIABILITY_CRISIS",
        "SUPPORT_BACKLOG", "PRODUCT_RECALL", "WAREHOUSE_CONGESTION", "SEASONAL_HOLIDAY_DEMAND"
    ]
    env_scenario = os.environ.get("SIMULATION_SCENARIO")
    if env_scenario and env_scenario in scenarios:
        selected_scenario = env_scenario
    else:
        selected_scenario = np.random.choice(scenarios)
        
    logger.info(f"Selected Simulation Scenario: {selected_scenario}")
    
    # ----------------------------------------------------
    # 1. REGIONS
    # ----------------------------------------------------
    regions_df = pd.DataFrame([
        {"region_id": "REG01", "region_name": "North America", "country": "United States", "manager_name": "Sarah Jenkins"},
        {"region_id": "REG02", "region_name": "Europe", "country": "Germany", "manager_name": "Hans Mueller"},
        {"region_id": "REG03", "region_name": "Asia-Pacific", "country": "Singapore", "manager_name": "Lin Wei"}
    ])
    
    # ----------------------------------------------------
    # 2. EMPLOYEES (Hierarchical Organization)
    # ----------------------------------------------------
    employees_data = [
        # Executives
        {"employee_id": "EMP001", "first_name": "Arthur", "last_name": "Pendelton", "email": "a.pendelton@decisioniq.com", "role": "CEO", "department": "Executive", "region_id": None, "hire_date": "2020-01-15", "reports_to": None},
        {"employee_id": "EMP002", "first_name": "Marcus", "last_name": "Vance", "email": "m.vance@decisioniq.com", "role": "COO", "department": "Operations", "region_id": None, "hire_date": "2020-03-10", "reports_to": "EMP001"},
        {"employee_id": "EMP003", "first_name": "Diana", "last_name": "Prince", "email": "d.prince@decisioniq.com", "role": "CFO", "department": "Finance", "region_id": None, "hire_date": "2020-04-01", "reports_to": "EMP001"},
        {"employee_id": "EMP004", "first_name": "Vikram", "last_name": "Nair", "email": "v.nair@decisioniq.com", "role": "VP Sales", "department": "Sales", "region_id": None, "hire_date": "2021-02-15", "reports_to": "EMP001"},
        
        # Regional Sales Directors (report to VP Sales)
        {"employee_id": "EMP005", "first_name": "John", "last_name": "Doe", "email": "j.doe@decisioniq.com", "role": "Director of Sales NA", "department": "Sales", "region_id": "REG01", "hire_date": "2021-06-01", "reports_to": "EMP004"},
        {"employee_id": "EMP006", "first_name": "Emma", "last_name": "Schmidt", "email": "e.schmidt@decisioniq.com", "role": "Director of Sales EMEA", "department": "Sales", "region_id": "REG02", "hire_date": "2021-08-15", "reports_to": "EMP004"},
        {"employee_id": "EMP007", "first_name": "Kenji", "last_name": "Sato", "email": "k.sato@decisioniq.com", "role": "Director of Sales APAC", "department": "Sales", "region_id": "REG03", "hire_date": "2022-01-10", "reports_to": "EMP004"},
        
        # Sales Reps NA (report to Director NA)
        {"employee_id": "EMP008", "first_name": "Alice", "last_name": "Smith", "email": "a.smith@decisioniq.com", "role": "Sales Representative", "department": "Sales", "region_id": "REG01", "hire_date": "2022-06-01", "reports_to": "EMP005"},
        {"employee_id": "EMP009", "first_name": "Bob", "last_name": "Jones", "email": "b.jones@decisioniq.com", "role": "Sales Representative", "department": "Sales", "region_id": "REG01", "hire_date": "2022-11-15", "reports_to": "EMP005"},
        
        # Sales Reps EMEA (report to Director EMEA)
        {"employee_id": "EMP010", "first_name": "Pierre", "last_name": "Dubois", "email": "p.dubois@decisioniq.com", "role": "Sales Representative", "department": "Sales", "region_id": "REG02", "hire_date": "2022-03-01", "reports_to": "EMP006"},
        {"employee_id": "EMP011", "first_name": "Chloe", "last_name": "Leroy", "email": "c.leroy@decisioniq.com", "role": "Sales Representative", "department": "Sales", "region_id": "REG02", "hire_date": "2023-01-15", "reports_to": "EMP006"},
        
        # Sales Reps APAC (report to Director APAC)
        {"employee_id": "EMP012", "first_name": "Haruto", "last_name": "Tanaka", "email": "h.tanaka@decisioniq.com", "role": "Sales Representative", "department": "Sales", "region_id": "REG03", "hire_date": "2023-02-01", "reports_to": "EMP007"},
        
        # Operations & Logistics Manager (reports to COO)
        {"employee_id": "EMP013", "first_name": "Carlos", "last_name": "Mendez", "email": "c.mendez@decisioniq.com", "role": "Logistics Manager", "department": "Operations", "region_id": "REG01", "hire_date": "2021-09-01", "reports_to": "EMP002"},
        
        # Support Agents (report to COO)
        {"employee_id": "EMP014", "first_name": "David", "last_name": "Lee", "email": "d.lee@decisioniq.com", "role": "Support Agent Level 1", "department": "Customer Support", "region_id": "REG01", "hire_date": "2022-04-15", "reports_to": "EMP002"},
        {"employee_id": "EMP015", "first_name": "Eva", "last_name": "Green", "email": "e.green@decisioniq.com", "role": "Support Agent Level 2", "department": "Customer Support", "region_id": "REG02", "hire_date": "2022-07-01", "reports_to": "EMP002"}
    ]
    employees_df = pd.DataFrame(employees_data)
    
    # ----------------------------------------------------
    # 3. PRODUCTS
    # ----------------------------------------------------
    products_data = [
        {"product_id": "PROD001", "product_name": "Cloud Infrastructure Suite", "sku": "SF-CIS-100", "category": "Software", "unit_price": 1200.00, "unit_cost": 200.00, "status": "Active"},
        {"product_id": "PROD002", "product_name": "Enterprise Server X", "sku": "HW-ESX-200", "category": "Hardware", "unit_price": 5000.00, "unit_cost": 3500.00, "status": "Active"},
        {"product_id": "PROD003", "product_name": "Database Optimization License", "sku": "SF-DOL-300", "category": "Software", "unit_price": 800.00, "unit_cost": 100.00, "status": "Active"},
        {"product_id": "PROD004", "product_name": "Data Integration Pipeline", "sku": "SF-DIP-400", "category": "Software", "unit_price": 1500.00, "unit_cost": 250.00, "status": "Active"},
        {"product_id": "PROD005", "product_name": "Network Switch 24p", "sku": "HW-NSW-500", "category": "Hardware", "unit_price": 1200.00, "unit_cost": 800.00, "status": "Active"},
        {"product_id": "PROD006", "product_name": "Premium Dedicated Support", "sku": "SP-PDS-600", "category": "Support", "unit_price": 500.00, "unit_cost": 300.00, "status": "Active"},
        {"product_id": "PROD007", "product_name": "Architecture Consulting", "sku": "SV-ARC-700", "category": "Professional Services", "unit_price": 2500.00, "unit_cost": 1500.00, "status": "Active"},
        {"product_id": "PROD008", "product_name": "Cyber Security Package", "sku": "SF-CSP-800", "category": "Software", "unit_price": 2000.00, "unit_cost": 400.00, "status": "Active"}
    ]
    products_df = pd.DataFrame(products_data)
    
    # ----------------------------------------------------
    # 4. WAREHOUSES
    # ----------------------------------------------------
    warehouses_data = [
        {"warehouse_id": "WH001", "warehouse_name": "East Coast Logistics Hub", "location": "Boston, MA", "region_id": "REG01", "capacity_sqft": 150000, "operating_cost_monthly": 18000.00},
        {"warehouse_id": "WH002", "warehouse_name": "West Coast Fulfillment Center", "location": "Oakland, CA", "region_id": "REG01", "capacity_sqft": 200000, "operating_cost_monthly": 25000.00},
        {"warehouse_id": "WH003", "warehouse_name": "EMEA Central Depot", "location": "Frankfurt, Germany", "region_id": "REG02", "capacity_sqft": 120000, "operating_cost_monthly": 15000.00},
        {"warehouse_id": "WH004", "warehouse_name": "APAC Logistics Hub", "location": "Singapore", "region_id": "REG03", "capacity_sqft": 100000, "operating_cost_monthly": 22000.00}
    ]
    
    # Inject INVENTORY_OVERSTOCK: Increase operating cost by 50% for WH001/WH002
    if selected_scenario == "INVENTORY_OVERSTOCK":
        for w in warehouses_data:
            if w["warehouse_id"] in ["WH001", "WH002"]:
                w["operating_cost_monthly"] = float(round(w["operating_cost_monthly"] * 1.5, 2))
                
    warehouses_df = pd.DataFrame(warehouses_data)
    
    # ----------------------------------------------------
    # 5. SUPPLIERS
    # ----------------------------------------------------
    suppliers_data = [
        {"supplier_id": "SUP001", "supplier_name": "Apex Technology Corp", "contact_name": "Jonathan Vance", "email": "j.vance@apextech.com", "lead_time_days": 10, "reliability_score": 0.95},
        {"supplier_id": "SUP002", "supplier_name": "Global Component Logistics", "contact_name": "Sanjay Mehta", "email": "s.mehta@gcl.com", "lead_time_days": 15, "reliability_score": 0.88},
        {"supplier_id": "SUP003", "supplier_name": "Silicon Manufacturing Ltd", "contact_name": "Cynthia Lau", "email": "c.lau@siliconmfg.com", "lead_time_days": 12, "reliability_score": 0.92},
        {"supplier_id": "SUP004", "supplier_name": "EuroChip AG", "contact_name": "Dieter Brandt", "email": "d.brandt@eurochip.de", "lead_time_days": 14, "reliability_score": 0.90}
    ]
    
    # Inject SUPPLY_CHAIN_CRISIS: Apex reliability drops
    if selected_scenario == "SUPPLY_CHAIN_CRISIS":
        suppliers_data[0]["reliability_score"] = 0.72
        
    suppliers_df = pd.DataFrame(suppliers_data)
    
    # ----------------------------------------------------
    # 6. INVENTORY
    # ----------------------------------------------------
    inventory_data = []
    inv_id_counter = 1
    for _, wh in warehouses_df.iterrows():
        for _, prod in products_df.iterrows():
            if prod["category"] in ["Software", "Hardware"]:
                qty = int(np.random.randint(50, 500))
                # Inject INVENTORY_OVERSTOCK
                if selected_scenario == "INVENTORY_OVERSTOCK" and wh["warehouse_id"] in ["WH001", "WH002"]:
                    qty = int(qty * 3.5)
                    
                inventory_data.append({
                    "inventory_id": f"INV{inv_id_counter:04d}",
                    "warehouse_id": wh["warehouse_id"],
                    "product_id": prod["product_id"],
                    "quantity_on_hand": qty,
                    "reorder_point": int(np.random.choice([30, 50, 75])),
                    "last_stock_count_date": end_date - timedelta(days=np.random.randint(1, 10))
                })
                inv_id_counter += 1
    inventory_df = pd.DataFrame(inventory_data)
    
    # ----------------------------------------------------
    # 7. MARKETING CAMPAIGNS
    # ----------------------------------------------------
    campaigns_data = []
    campaign_names = [
        ("Enterprise IT PPC", "PPC"), ("Global CIO Summit Event", "Event"),
        ("SaaS Email Nurture", "Email"), ("Tech Leaders Webinar", "Social Media"),
        ("Google Search Ads", "SEO"), ("TechCrunch Banner Ads", "PPC"),
        ("CIO Roundtable APAC", "Event"), ("EMEA IT Execs Campaign", "Social Media"),
        ("Organic SEO Drive", "SEO"), ("Partner Channel Referral", "Referral")
    ]
    for i, (name, channel) in enumerate(campaign_names):
        camp_start = start_date + timedelta(days=np.random.randint(0, 365))
        camp_end = camp_start + timedelta(days=np.random.randint(30, 90))
        budget = float(np.random.choice([15000, 25000, 50000, 75000]))
        
        # Inject MARKETING_INEFFICIENCY
        if selected_scenario == "MARKETING_INEFFICIENCY" and channel in ["Social Media", "PPC"]:
            budget = float(budget * 3.0)
            
        impressions = int(budget * np.random.uniform(5, 10))
        clicks = int(impressions * np.random.uniform(0.015, 0.04))
        
        conversions = int(clicks * np.random.uniform(0.02, 0.06))
        # Inject MARKETING_INEFFICIENCY: Conversions drop
        if selected_scenario == "MARKETING_INEFFICIENCY" and channel in ["Social Media", "PPC"]:
            conversions = int(conversions * 0.15)
            
        campaigns_data.append({
            "campaign_id": f"CAMP{i+1:03d}",
            "campaign_name": name,
            "channel": channel,
            "start_date": camp_start,
            "end_date": camp_end,
            "budget": budget,
            "clicks": clicks,
            "impressions": impressions,
            "conversions": conversions
        })
    marketing_campaigns_df = pd.DataFrame(campaigns_data)
    
    # ----------------------------------------------------
    # 8. CUSTOMERS
    # ----------------------------------------------------
    segments = ["SMB", "Enterprise", "Strategic"]
    channels = ["Direct", "Referral", "Organic Search", "Paid Ads"]
    
    customers_data = []
    customer_companies = [
        "Initech", "Dunder Mifflin", "Saber Corp", "Veer Technologies", "Omni Consumer Products",
        "Aperture Science", "Black Mesa", "Cyberdyne Systems", "Tyrell Corp", "Weyland-Yutani",
        "Stark Industries", "Wayne Enterprises", "Oscorp", "LexCorp", "Gekko & Co", "Hooli",
        "Globex Corp", "Soylent Corp", "Bluth Company", "E Corp", "Allsafe Cybersecurity",
        "Sterling Cooper", "Acme Corp", "Virtucon", "MomCorp", "Devin Logistics", "Titan Systems",
        "Zenith Media", "Hyperion", "Goliath National Bank", "Central Perk", "Vandelay Industries",
        "Kramerica Industries", "Prestige Worldwide", "Entertainment 720", "Gryzzl", "Pawnee Parks"
    ]
    
    for i in range(500):
        comp_name = f"{np.random.choice(customer_companies)} {np.random.choice(['Inc.', 'LLC', 'Corp', 'Group', 'Solutions'])} {i+1}"
        cont_name = f"{np.random.choice(['Alex', 'Jamie', 'Morgan', 'Taylor', 'Jordan', 'Pat', 'Chris', 'Sam'])} {np.random.choice(['Miller', 'Davis', 'Wilson', 'Anderson', 'Thomas', 'Jackson', 'White'])}"
        domain = comp_name.lower().replace(" ", "").replace(".", "").replace(",", "")[:12] + ".com"
        email = f"{cont_name.lower().replace(' ', '.')}@{domain}"
        
        region = np.random.choice(["REG01", "REG02", "REG03"], p=[0.50, 0.30, 0.20])
        seg = np.random.choice(segments, p=[0.40, 0.45, 0.15])
        
        status = "Active"
        acq_date = start_date + timedelta(days=np.random.randint(0, total_days - 250))
        acq_chan = np.random.choice(channels)
        
        # Inject CUSTOMER_CHURN_SURGE: Churn strategic segments
        if selected_scenario == "CUSTOMER_CHURN_SURGE" and seg == "SMB" and region == "REG02" and np.random.rand() > 0.4:
            status = np.random.choice(["Churned", "At-Risk"], p=[0.70, 0.30])
        elif np.random.rand() > 0.94:
            status = np.random.choice(["Churned", "At-Risk"], p=[0.50, 0.50])
            
        customers_data.append({
            "customer_id": f"CUST{i+1:05d}",
            "company_name": comp_name,
            "contact_name": cont_name,
            "contact_email": email,
            "customer_segment": seg,
            "region_id": region,
            "status": status,
            "acquisition_date": acq_date,
            "acquisition_channel": acq_chan
        })
        
    # Duplicate entries
    cust_id_counter = 501
    for i in range(5):
        dup = customers_data[np.random.randint(0, 100)].copy()
        dup["customer_id"] = f"CUST{cust_id_counter:05d}"
        dup["company_name"] = dup["company_name"] + " (Duplicate Entry)"
        dup["acquisition_date"] = dup["acquisition_date"] + timedelta(days=1)
        customers_data.append(dup)
        cust_id_counter += 1
        
    customers_df = pd.DataFrame(customers_data)
    
    # ----------------------------------------------------
    # 9. ORDERS & ORDER DETAILS & PAYMENTS & SHIPMENTS (Combined Generation)
    # ----------------------------------------------------
    orders_list = []
    order_details_list = []
    payments_list = []
    shipments_list = []
    
    order_id_counter = 1
    detail_id_counter = 1
    payment_id_counter = 1
    shipment_id_counter = 1
    
    active_custs = customers_df[~customers_df["status"].isin(["Churned"])]
    
    for dt in date_list:
        day_index = (dt - start_date).days
        growth_mult = 1.0 + (day_index / total_days) * 0.6
        
        month = dt.month
        season_mult = 1.35 if month in [11, 12] else 0.75 if month in [1, 2] else 1.00
        
        is_crisis_active = (dt >= crisis_start)
        
        # Base daily order count
        base_orders = int(np.random.poisson(12 * growth_mult * season_mult))
        
        # Scenario adjustments to order volume:
        if is_crisis_active:
            if selected_scenario == "SUPPLY_CHAIN_CRISIS":
                base_orders = int(base_orders * 0.85)
            elif selected_scenario == "INVENTORY_OVERSTOCK":
                base_orders = int(base_orders * 0.75)
            elif selected_scenario == "REGIONAL_SALES_COLLAPSE":
                # Regional Sales Collapse: Decrease orders generated in REG02
                base_orders = int(base_orders * 0.80)
            elif selected_scenario == "DEMAND_SPIKE":
                # Demand Spike: orders volume spikes 2.2x
                base_orders = int(base_orders * 2.2)
                
        for _ in range(base_orders):
            cust = active_custs.sample(1).iloc[0]
            cust_id = cust["customer_id"]
            cust_region = cust["region_id"]
            
            # Regional sales collapse skip orders
            if is_crisis_active and selected_scenario == "REGIONAL_SALES_COLLAPSE" and cust_region == "REG02":
                if np.random.rand() < 0.60:
                    continue # Skip order generation in Europe
                    
            reps = employees_df[(employees_df["region_id"] == cust_region) & (employees_df["role"] == "Sales Representative")]
            rep_id = reps.sample(1).iloc[0]["employee_id"] if len(reps) > 0 else "EMP008"
            
            status_opts = ["Completed", "Shipped", "Processing", "Cancelled", "Refunded"]
            status_p = [0.85, 0.08, 0.03, 0.02, 0.02]
            
            # Scenario: Supply Chain Crisis refund spikes in NA (REG01)
            if is_crisis_active and selected_scenario == "SUPPLY_CHAIN_CRISIS" and cust_region == "REG01":
                status_p = [0.55, 0.10, 0.05, 0.12, 0.18]
            # Scenario: Cash Flow Crisis order cancellations spike
            elif is_crisis_active and selected_scenario == "CASH_FLOW_CRISIS":
                status_p = [0.45, 0.10, 0.05, 0.25, 0.15]
            # Scenario: Product Recall on Hardware switches in NA
            elif is_crisis_active and selected_scenario == "PRODUCT_RECALL" and cust_region == "REG01":
                status_p = [0.50, 0.05, 0.05, 0.10, 0.30]
                
            order_status = np.random.choice(status_opts, p=status_p)
            
            # Items in order
            num_items = np.random.choice([1, 2, 3], p=[0.70, 0.22, 0.08])
            
            if is_crisis_active and selected_scenario == "INVENTORY_OVERSTOCK":
                sampled_prods = products_df[products_df["category"] == "Software"].sample(min(num_items, 3))
                if len(sampled_prods) == 0:
                    sampled_prods = products_df.sample(num_items)
            else:
                sampled_prods = products_df.sample(num_items)
                
            order_total = 0.0
            order_id = f"ORD{order_id_counter:06d}"
            
            order_details_temp = []
            has_hardware = False
            
            for _, prod in sampled_prods.iterrows():
                qty = int(np.random.choice([1, 2, 5, 10], p=[0.75, 0.15, 0.08, 0.02]))
                price = float(prod["unit_price"])
                
                # Product Recall specific refund override
                if is_crisis_active and selected_scenario == "PRODUCT_RECALL" and prod["product_id"] == "PROD005" and cust_region == "REG01":
                    order_status = "Refunded"
                    
                discount = 0.0
                if cust["customer_segment"] == "Enterprise" and np.random.rand() > 0.6:
                    discount = float(round(price * qty * 0.10, 2))
                subtotal = float(round((price * qty) - discount, 2))
                
                order_total += subtotal
                
                order_details_temp.append({
                    "order_detail_id": f"OD{detail_id_counter:07d}",
                    "order_id": order_id,
                    "product_id": prod["product_id"],
                    "quantity": qty,
                    "unit_price": price,
                    "discount_amount": discount,
                    "subtotal": subtotal
                })
                detail_id_counter += 1
                
                if prod["category"] == "Hardware":
                    has_hardware = True
                    
            order_total = round(order_total, 2)
            orders_list.append({
                "order_id": order_id,
                "customer_id": cust_id,
                "order_date": dt,
                "status": order_status,
                "sales_representative_id": rep_id,
                "total_amount": order_total,
                "currency": "USD"
            })
            order_details_list.extend(order_details_temp)
            
            # Payments
            pay_method = np.random.choice(["Credit Card", "ACH", "Wire", "PayPal"], p=[0.50, 0.30, 0.15, 0.05])
            pay_status_opts = ["Success", "Success", "Failed"]
            pay_status_p = [0.94, 0.03, 0.03]
            
            if is_crisis_active and selected_scenario == "CASH_FLOW_CRISIS":
                # High payment failures
                pay_status_p = [0.45, 0.45, 0.10]
                
            pay_status = np.random.choice(pay_status_opts, p=pay_status_p)
            
            if order_status == "Refunded":
                pay_status = "Refunded"
            elif order_status == "Cancelled":
                pay_status = "Failed"
                
            payments_list.append({
                "payment_id": f"PAY{payment_id_counter:06d}",
                "order_id": order_id,
                "payment_date": dt + timedelta(days=np.random.randint(0, 2)),
                "payment_method": pay_method,
                "payment_status": pay_status,
                "amount": order_total,
                "transaction_id": str(uuid.uuid4())[:18].upper()
            })
            payment_id_counter += 1
            
            # Shipments
            if has_hardware and order_status in ["Shipped", "Completed", "Refunded"]:
                whs = warehouses_df[warehouses_df["region_id"] == cust_region]
                wh_id = whs.sample(1).iloc[0]["warehouse_id"] if len(whs) > 0 else "WH001"
                
                sup_id = np.random.choice(suppliers_df["supplier_id"])
                carrier = np.random.choice(["FedEx", "UPS", "DHL", "Freight"], p=[0.40, 0.35, 0.15, 0.10])
                
                ship_dt = dt + timedelta(days=np.random.randint(1, 3))
                est_delivery = ship_dt + timedelta(days=np.random.randint(3, 7))
                
                # Default delay
                delay_days = int(np.random.choice([0, 1, 2, 3, 4], p=[0.75, 0.12, 0.08, 0.04, 0.01]))
                
                # Apply Scenario Delays
                if is_crisis_active:
                    if selected_scenario == "SUPPLY_CHAIN_CRISIS":
                        if sup_id == "SUP001":
                            delay_days += np.random.randint(10, 16)
                        if wh_id == "WH002":
                            delay_days += np.random.randint(5, 8)
                    elif selected_scenario == "SUPPLIER_RELIABILITY_CRISIS":
                        # Delays across all suppliers
                        delay_days += np.random.randint(6, 11)
                    elif selected_scenario == "WAREHOUSE_CONGESTION" and wh_id == "WH003":
                        # EMEA Warehouse bottlenecks
                        delay_days += np.random.randint(8, 14)
                    elif selected_scenario == "SEASONAL_HOLIDAY_DEMAND":
                        # General Q4/Holiday shipment delays
                        delay_days += np.random.randint(3, 7)
                        
                act_delivery = est_delivery + timedelta(days=delay_days)
                
                deliv_status = "On Time"
                if delay_days > 2:
                    deliv_status = "Late"
                if order_status == "Refunded" and delay_days > 7:
                    deliv_status = "Returned"
                    
                shipments_list.append({
                    "shipment_id": f"SHP{shipment_id_counter:06d}",
                    "order_id": order_id,
                    "warehouse_id": wh_id,
                    "supplier_id": sup_id,
                    "carrier": carrier,
                    "shipment_date": ship_dt,
                    "estimated_delivery_date": est_delivery,
                    "actual_delivery_date": act_delivery if order_status != "Shipped" else None,
                    "delivery_status": deliv_status if order_status != "Shipped" else "In Transit"
                })
                shipment_id_counter += 1
                
            order_id_counter += 1
            
    orders_df = pd.DataFrame(orders_list)
    order_details_df = pd.DataFrame(order_details_list)
    payments_df = pd.DataFrame(payments_list)
    shipments_df = pd.DataFrame(shipments_list)
    
    # ----------------------------------------------------
    # 10. CUSTOMER SUPPORT TICKETS
    # ----------------------------------------------------
    support_data = []
    ticket_id_counter = 1
    
    categories = ["Billing", "Technical", "Product", "Logistics"]
    priorities = ["Low", "Medium", "High", "Critical"]
    
    late_shipments = shipments_df[shipments_df["delivery_status"] == "Late"]
    failed_payments = payments_df[payments_df["payment_status"] == "Failed"]
    
    # Generate tickets for late shipments
    for _, ship in late_shipments.iterrows():
        ord_info = orders_df[orders_df["order_id"] == ship["order_id"]].iloc[0]
        cust_id = ord_info["customer_id"]
        create_dt = datetime.combine(ship["estimated_delivery_date"] + timedelta(days=1), datetime.min.time()) + timedelta(hours=np.random.randint(8, 17))
        
        is_crisis = (ship["estimated_delivery_date"] >= crisis_start)
        
        status = "Resolved"
        if is_crisis and selected_scenario == "SUPPLY_CHAIN_CRISIS" and np.random.rand() > 0.5:
            status = np.random.choice(["Escalated", "In Progress"])
            
        priority = "High" if not is_crisis else "Critical"
        
        if is_crisis and selected_scenario == "SUPPLY_CHAIN_CRISIS":
            csat = int(np.random.choice([1, 2, 3], p=[0.65, 0.25, 0.10]))
        else:
            csat = int(np.random.choice([2, 3, 4], p=[0.20, 0.50, 0.30]))
            
        close_dt = None
        if status == "Resolved":
            res_days = np.random.randint(1, 4)
            if is_crisis and selected_scenario == "SUPPLY_CHAIN_CRISIS":
                res_days = int(res_days * 3.5)
            close_dt = create_dt + timedelta(days=res_days, hours=np.random.randint(1, 12))
            
        agent = employees_df[employees_df["department"] == "Customer Support"].sample(1).iloc[0]["employee_id"]
        
        support_data.append({
            "ticket_id": f"TCK{ticket_id_counter:06d}",
            "customer_id": cust_id,
            "created_at": create_dt,
            "closed_at": close_dt,
            "status": status,
            "priority": priority,
            "category": "Logistics",
            "satisfaction_score": csat if status == "Resolved" else None,
            "agent_id": agent
        })
        ticket_id_counter += 1
        
    # Generate tickets for failed payments
    for _, pay in failed_payments.sample(min(len(failed_payments), 200)).iterrows():
        ord_info = orders_df[orders_df["order_id"] == pay["order_id"]].iloc[0]
        cust_id = ord_info["customer_id"]
        create_dt = datetime.combine(pay["payment_date"], datetime.min.time()) + timedelta(hours=np.random.randint(9, 17))
        
        close_dt = create_dt + timedelta(days=1, hours=np.random.randint(1, 10))
        agent = employees_df[employees_df["department"] == "Customer Support"].sample(1).iloc[0]["employee_id"]
        
        support_data.append({
            "ticket_id": f"TCK{ticket_id_counter:06d}",
            "customer_id": cust_id,
            "created_at": create_dt,
            "closed_at": close_dt,
            "status": "Resolved",
            "priority": "Medium",
            "category": "Billing",
            "satisfaction_score": int(np.random.choice([3, 4, 5], p=[0.15, 0.45, 0.40])),
            "agent_id": agent
        })
        ticket_id_counter += 1
        
    # Generate baseline customer queries
    for _ in range(500):
        cust = customers_df.sample(1).iloc[0]
        cust_id = cust["customer_id"]
        create_dt = datetime.combine(start_date + timedelta(days=np.random.randint(0, total_days)), datetime.min.time()) + timedelta(hours=np.random.randint(8, 18))
        
        is_crisis = (create_dt.date() >= crisis_start)
        
        cat = np.random.choice(categories, p=[0.20, 0.40, 0.30, 0.10])
        prio = np.random.choice(priorities, p=[0.40, 0.40, 0.15, 0.05])
        
        stat = "Resolved"
        if is_crisis and selected_scenario == "CUSTOMER_CHURN_SURGE" and cat in ["Technical", "Product"]:
            stat = np.random.choice(["Resolved", "In Progress", "Escalated"], p=[0.40, 0.40, 0.20])
            prio = "High"
        elif is_crisis and selected_scenario == "SUPPORT_BACKLOG" and cat in ["Technical", "Billing"]:
            stat = np.random.choice(["Resolved", "In Progress", "Escalated"], p=[0.30, 0.40, 0.30])
            prio = "Critical"
            
        close_dt = None
        if stat == "Resolved":
            res_days = np.random.randint(1, 5)
            if is_crisis and selected_scenario == "CUSTOMER_CHURN_SURGE" and cat in ["Technical", "Product"]:
                res_days = int(res_days * 3.0)
            elif is_crisis and selected_scenario == "SUPPORT_BACKLOG" and cat in ["Technical", "Billing"]:
                res_days = int(res_days * 4.0)
                
            close_dt = create_dt + timedelta(days=res_days)
            
            if is_crisis and selected_scenario == "CUSTOMER_CHURN_SURGE" and cat in ["Technical", "Product"]:
                csat = int(np.random.choice([1, 2, 3], p=[0.60, 0.30, 0.10]))
            elif is_crisis and selected_scenario == "SUPPORT_BACKLOG" and cat in ["Technical", "Billing"]:
                csat = int(np.random.choice([1, 2], p=[0.70, 0.30]))
            else:
                csat = int(np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.10, 0.20, 0.40, 0.25]))
        else:
            csat = None
            
        agent = employees_df[employees_df["department"] == "Customer Support"].sample(1).iloc[0]["employee_id"]
        
        support_data.append({
            "ticket_id": f"TCK{ticket_id_counter:06d}",
            "customer_id": cust_id,
            "created_at": create_dt,
            "closed_at": close_dt,
            "status": stat,
            "priority": prio,
            "category": cat,
            "satisfaction_score": csat,
            "agent_id": agent
        })
        ticket_id_counter += 1
        
    customer_support_df = pd.DataFrame(support_data)
    
    # ----------------------------------------------------
    # 11. DAILY BUSINESS METRICS
    # ----------------------------------------------------
    daily_metrics_list = []
    
    for dt in date_list:
        day_index = (dt - start_date).days
        growth_mult = 1.0 + (day_index / total_days) * 0.7
        
        is_crisis_active = (dt >= crisis_start)
        
        base_visitors = int(np.random.poisson(2500 * growth_mult))
        
        # Inject MARKETING_INEFFICIENCY: Spikes website visitors
        if is_crisis_active and selected_scenario == "MARKETING_INEFFICIENCY":
            base_visitors = int(base_visitors * 1.8)
            
        base_leads = int(base_visitors * np.random.uniform(0.04, 0.06))
        active_u = int(base_visitors * np.random.uniform(0.35, 0.45))
        cac = float(np.random.uniform(150.00, 220.00))
        
        # Inject MARKETING_INEFFICIENCY: CAC spikes
        if is_crisis_active and selected_scenario == "MARKETING_INEFFICIENCY":
            cac = float(cac * 2.5)
            
        # NPS drops during crises:
        if is_crisis_active:
            if selected_scenario in ["SUPPLY_CHAIN_CRISIS", "CUSTOMER_CHURN_SURGE", "SUPPORT_BACKLOG"]:
                nps = int(np.random.randint(5, 20))
            else:
                nps = int(np.random.randint(30, 45))
        else:
            nps = int(np.random.randint(45, 65))
            
        daily_metrics_list.append({
            "metric_date": dt,
            "active_users": active_u,
            "website_visitors": base_visitors,
            "leads_generated": base_leads,
            "cac": round(cac, 2),
            "nps": nps
        })
        
    daily_business_metrics_df = pd.DataFrame(daily_metrics_list)
    
    return {
        "regions": regions_df,
        "employees": employees_df,
        "customers": customers_df,
        "products": products_df,
        "warehouses": warehouses_df,
        "suppliers": suppliers_df,
        "inventory": inventory_df,
        "marketing_campaigns": marketing_campaigns_df,
        "orders": orders_df,
        "order_details": order_details_df,
        "payments": payments_df,
        "shipments": shipments_df,
        "customer_support": customer_support_df,
        "daily_business_metrics": daily_business_metrics_df
    }

if __name__ == "__main__":
    dfs = generate_synthetic_data()
    for name, df in dfs.items():
        print(f"Generated {name}: {df.shape[0]} rows, columns: {list(df.columns)}")
