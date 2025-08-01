#!/usr/bin/env python3
"""
Real-world use cases for Mermaid Render.

This script demonstrates practical applications including software architecture
documentation, API documentation, business process modeling, and database design.
"""

from pathlib import Path
from mermaid_render import (
    MermaidRenderer,
    FlowchartDiagram,
    SequenceDiagram,
    ClassDiagram,
    ERDiagram,
    UserJourneyDiagram,
    StateDiagram,
)
from mermaid_render.models.class_diagram import ClassMethod, ClassAttribute


def create_output_dir():
    """Create output directory for examples."""
    output_dir = Path("output/real_world")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def software_architecture_documentation(output_dir: Path):
    """Create comprehensive software architecture documentation."""
    print("Software architecture documentation example...")
    
    # 1. System Overview Flowchart
    system_overview = FlowchartDiagram(
        direction="TD", 
        title="E-commerce Platform Architecture Overview"
    )
    
    # Add main components
    system_overview.add_node("users", "Users", shape="rectangle")
    system_overview.add_node("cdn", "CDN", shape="rectangle")
    system_overview.add_node("lb", "Load Balancer", shape="rectangle")
    system_overview.add_node("web", "Web Servers", shape="rectangle")
    system_overview.add_node("api", "API Gateway", shape="rectangle")
    system_overview.add_node("auth", "Auth Service", shape="rectangle")
    system_overview.add_node("catalog", "Catalog Service", shape="rectangle")
    system_overview.add_node("cart", "Cart Service", shape="rectangle")
    system_overview.add_node("order", "Order Service", shape="rectangle")
    system_overview.add_node("payment", "Payment Service", shape="rectangle")
    system_overview.add_node("db", "Database Cluster", shape="cylinder")
    system_overview.add_node("cache", "Redis Cache", shape="cylinder")
    system_overview.add_node("queue", "Message Queue", shape="rectangle")
    
    # Add connections
    system_overview.add_edge("users", "cdn", "Static Assets")
    system_overview.add_edge("users", "lb", "API Requests")
    system_overview.add_edge("lb", "web", "Route")
    system_overview.add_edge("web", "api", "API Calls")
    system_overview.add_edge("api", "auth", "Authentication")
    system_overview.add_edge("api", "catalog", "Product Data")
    system_overview.add_edge("api", "cart", "Cart Operations")
    system_overview.add_edge("api", "order", "Order Processing")
    system_overview.add_edge("order", "payment", "Payment Processing")
    system_overview.add_edge("auth", "cache", "Session Store")
    system_overview.add_edge("catalog", "db", "Product DB")
    system_overview.add_edge("cart", "cache", "Cart Cache")
    system_overview.add_edge("order", "db", "Order DB")
    system_overview.add_edge("order", "queue", "Order Events")
    
    # Add styling
    system_overview.add_style("users", {"fill": "#e1f5fe"})
    system_overview.add_style("db", {"fill": "#f3e5f5"})
    system_overview.add_style("cache", {"fill": "#fff3e0"})
    
    # Save system overview
    renderer = MermaidRenderer()
    overview_path = output_dir / "system_architecture.svg"
    renderer.save(system_overview, overview_path)
    print(f"📁 System architecture saved to {overview_path}")
    
    # 2. Microservices Communication Sequence
    microservices_seq = SequenceDiagram(
        title="Order Processing Microservices Flow",
        autonumber=True
    )
    
    # Add participants
    microservices_seq.add_participant("client", "Client App")
    microservices_seq.add_participant("gateway", "API Gateway")
    microservices_seq.add_participant("auth", "Auth Service")
    microservices_seq.add_participant("catalog", "Catalog Service")
    microservices_seq.add_participant("cart", "Cart Service")
    microservices_seq.add_participant("order", "Order Service")
    microservices_seq.add_participant("payment", "Payment Service")
    microservices_seq.add_participant("inventory", "Inventory Service")
    microservices_seq.add_participant("notification", "Notification Service")
    
    # Add order flow
    microservices_seq.add_message("client", "gateway", "POST /orders")
    microservices_seq.add_message("gateway", "auth", "validate_token()")
    microservices_seq.add_message("auth", "gateway", "user_info", message_type="return")
    microservices_seq.add_message("gateway", "cart", "get_cart_items()")
    microservices_seq.add_message("cart", "gateway", "cart_data", message_type="return")
    microservices_seq.add_message("gateway", "catalog", "validate_products()")
    microservices_seq.add_message("catalog", "gateway", "product_info", message_type="return")
    microservices_seq.add_message("gateway", "inventory", "check_availability()")
    microservices_seq.add_message("inventory", "gateway", "availability_status", message_type="return")
    microservices_seq.add_message("gateway", "order", "create_order()")
    microservices_seq.add_message("order", "payment", "process_payment()")
    microservices_seq.add_message("payment", "order", "payment_result", message_type="return")
    microservices_seq.add_message("order", "inventory", "reserve_items()")
    microservices_seq.add_message("order", "notification", "send_confirmation()")
    microservices_seq.add_message("order", "gateway", "order_created", message_type="return")
    microservices_seq.add_message("gateway", "client", "201 Created", message_type="return")
    
    # Save microservices sequence
    seq_path = output_dir / "microservices_flow.svg"
    renderer.save(microservices_seq, seq_path)
    print(f"📁 Microservices flow saved to {seq_path}")


def api_documentation_example(output_dir: Path):
    """Create comprehensive API documentation diagrams."""
    print("API documentation example...")
    
    # 1. REST API Endpoints Flowchart
    api_flow = FlowchartDiagram(
        direction="TD",
        title="REST API Endpoint Structure"
    )
    
    # Add API structure
    api_flow.add_node("root", "/api/v1", shape="rectangle")
    api_flow.add_node("auth", "/auth", shape="rectangle")
    api_flow.add_node("users", "/users", shape="rectangle")
    api_flow.add_node("products", "/products", shape="rectangle")
    api_flow.add_node("orders", "/orders", shape="rectangle")
    
    # Auth endpoints
    api_flow.add_node("login", "POST /login", shape="rectangle")
    api_flow.add_node("logout", "POST /logout", shape="rectangle")
    api_flow.add_node("refresh", "POST /refresh", shape="rectangle")
    
    # User endpoints
    api_flow.add_node("get_users", "GET /users", shape="rectangle")
    api_flow.add_node("create_user", "POST /users", shape="rectangle")
    api_flow.add_node("get_user", "GET /users/{id}", shape="rectangle")
    api_flow.add_node("update_user", "PUT /users/{id}", shape="rectangle")
    
    # Product endpoints
    api_flow.add_node("get_products", "GET /products", shape="rectangle")
    api_flow.add_node("create_product", "POST /products", shape="rectangle")
    api_flow.add_node("get_product", "GET /products/{id}", shape="rectangle")
    
    # Order endpoints
    api_flow.add_node("get_orders", "GET /orders", shape="rectangle")
    api_flow.add_node("create_order", "POST /orders", shape="rectangle")
    api_flow.add_node("get_order", "GET /orders/{id}", shape="rectangle")
    
    # Add connections
    api_flow.add_edge("root", "auth")
    api_flow.add_edge("root", "users")
    api_flow.add_edge("root", "products")
    api_flow.add_edge("root", "orders")
    
    api_flow.add_edge("auth", "login")
    api_flow.add_edge("auth", "logout")
    api_flow.add_edge("auth", "refresh")
    
    api_flow.add_edge("users", "get_users")
    api_flow.add_edge("users", "create_user")
    api_flow.add_edge("users", "get_user")
    api_flow.add_edge("users", "update_user")
    
    api_flow.add_edge("products", "get_products")
    api_flow.add_edge("products", "create_product")
    api_flow.add_edge("products", "get_product")
    
    api_flow.add_edge("orders", "get_orders")
    api_flow.add_edge("orders", "create_order")
    api_flow.add_edge("orders", "get_order")
    
    # Add styling
    api_flow.add_style("root", {"fill": "#e8f5e8"})
    api_flow.add_style("auth", {"fill": "#fff3cd"})
    api_flow.add_style("users", {"fill": "#d1ecf1"})
    api_flow.add_style("products", {"fill": "#f8d7da"})
    api_flow.add_style("orders", {"fill": "#d4edda"})
    
    # Save API structure
    renderer = MermaidRenderer()
    api_path = output_dir / "api_structure.svg"
    renderer.save(api_flow, api_path)
    print(f"📁 API structure saved to {api_path}")
    
    # 2. Authentication Flow Sequence
    auth_seq = SequenceDiagram(
        title="JWT Authentication Flow",
        autonumber=True
    )
    
    auth_seq.add_participant("client", "Client App")
    auth_seq.add_participant("api", "API Server")
    auth_seq.add_participant("auth", "Auth Service")
    auth_seq.add_participant("db", "User Database")
    
    # Login flow
    auth_seq.add_message("client", "api", "POST /auth/login")
    auth_seq.add_message("api", "auth", "validate_credentials()")
    auth_seq.add_message("auth", "db", "SELECT user WHERE email = ?")
    auth_seq.add_message("db", "auth", "user_data", message_type="return")
    auth_seq.add_message("auth", "auth", "verify_password()", message_type="self")
    auth_seq.add_message("auth", "auth", "generate_jwt_token()", message_type="self")
    auth_seq.add_message("auth", "api", "jwt_token", message_type="return")
    auth_seq.add_message("api", "client", "200 OK + JWT", message_type="return")
    
    # Protected request flow
    auth_seq.add_note("Subsequent protected requests", "client", "right of")
    auth_seq.add_message("client", "api", "GET /users (with JWT header)")
    auth_seq.add_message("api", "auth", "verify_jwt_token()")
    auth_seq.add_message("auth", "api", "user_claims", message_type="return")
    auth_seq.add_message("api", "db", "SELECT users")
    auth_seq.add_message("db", "api", "users_data", message_type="return")
    auth_seq.add_message("api", "client", "200 OK + users", message_type="return")
    
    # Save auth sequence
    auth_path = output_dir / "auth_flow.svg"
    renderer.save(auth_seq, auth_path)
    print(f"📁 Authentication flow saved to {auth_path}")


def business_process_modeling(output_dir: Path):
    """Create business process models."""
    print("Business process modeling example...")
    
    # 1. Customer Onboarding Process
    onboarding = FlowchartDiagram(
        direction="TD",
        title="Customer Onboarding Process"
    )
    
    # Add process steps
    onboarding.add_node("start", "New Customer", shape="circle")
    onboarding.add_node("register", "Customer Registration", shape="rectangle")
    onboarding.add_node("verify_email", "Email Verification", shape="rectangle")
    onboarding.add_node("email_verified", "Email Verified?", shape="rhombus")
    onboarding.add_node("kyc", "KYC Verification", shape="rectangle")
    onboarding.add_node("kyc_review", "KYC Review", shape="rectangle")
    onboarding.add_node("kyc_approved", "KYC Approved?", shape="rhombus")
    onboarding.add_node("account_setup", "Account Setup", shape="rectangle")
    onboarding.add_node("welcome", "Send Welcome Package", shape="rectangle")
    onboarding.add_node("training", "Product Training", shape="rectangle")
    onboarding.add_node("first_purchase", "First Purchase Incentive", shape="rectangle")
    onboarding.add_node("complete", "Onboarding Complete", shape="circle")
    onboarding.add_node("rejected", "Application Rejected", shape="circle")
    onboarding.add_node("resend_email", "Resend Verification", shape="rectangle")
    
    # Add process flow
    onboarding.add_edge("start", "register")
    onboarding.add_edge("register", "verify_email")
    onboarding.add_edge("verify_email", "email_verified")
    onboarding.add_edge("email_verified", "kyc", label="Yes")
    onboarding.add_edge("email_verified", "resend_email", label="No")
    onboarding.add_edge("resend_email", "verify_email")
    onboarding.add_edge("kyc", "kyc_review")
    onboarding.add_edge("kyc_review", "kyc_approved")
    onboarding.add_edge("kyc_approved", "account_setup", label="Yes")
    onboarding.add_edge("kyc_approved", "rejected", label="No")
    onboarding.add_edge("account_setup", "welcome")
    onboarding.add_edge("welcome", "training")
    onboarding.add_edge("training", "first_purchase")
    onboarding.add_edge("first_purchase", "complete")
    
    # Add styling
    onboarding.add_style("start", {"fill": "#90EE90"})
    onboarding.add_style("complete", {"fill": "#90EE90"})
    onboarding.add_style("rejected", {"fill": "#FFB6C1"})
    
    # Save onboarding process
    renderer = MermaidRenderer()
    onboarding_path = output_dir / "customer_onboarding.svg"
    renderer.save(onboarding, onboarding_path)
    print(f"📁 Customer onboarding saved to {onboarding_path}")
    
    # 2. Customer Journey Map
    journey = UserJourneyDiagram(title="E-commerce Customer Journey")
    
    # Add journey stages
    journey.add_step("Awareness", "Customer discovers brand", 3, ["Social Media", "Search", "Referral"])
    journey.add_step("Interest", "Browses products", 4, ["Website", "Reviews", "Comparison"])
    journey.add_step("Consideration", "Evaluates options", 3, ["Product Details", "Pricing", "Support"])
    journey.add_step("Purchase", "Makes first purchase", 5, ["Checkout", "Payment", "Confirmation"])
    journey.add_step("Delivery", "Receives product", 4, ["Shipping", "Tracking", "Unboxing"])
    journey.add_step("Experience", "Uses product", 5, ["Quality", "Performance", "Satisfaction"])
    journey.add_step("Support", "Contacts support", 2, ["Help Center", "Chat", "Email"])
    journey.add_step("Loyalty", "Becomes repeat customer", 5, ["Rewards", "Recommendations", "Reviews"])
    
    # Save customer journey
    journey_path = output_dir / "customer_journey.svg"
    renderer.save(journey, journey_path)
    print(f"📁 Customer journey saved to {journey_path}")


def database_design_example(output_dir: Path):
    """Create database design documentation."""
    print("Database design example...")
    
    # Create comprehensive ER diagram for e-commerce
    er = ERDiagram(title="E-commerce Database Schema")
    
    # Add entities with detailed attributes
    er.add_entity("User", {
        "user_id": "PK",
        "email": "UNIQUE NOT NULL",
        "password_hash": "NOT NULL",
        "first_name": "VARCHAR(50)",
        "last_name": "VARCHAR(50)",
        "phone": "VARCHAR(20)",
        "date_of_birth": "DATE",
        "created_at": "TIMESTAMP",
        "updated_at": "TIMESTAMP",
        "is_active": "BOOLEAN DEFAULT TRUE",
        "email_verified": "BOOLEAN DEFAULT FALSE"
    })
    
    er.add_entity("Address", {
        "address_id": "PK",
        "user_id": "FK",
        "type": "ENUM('billing', 'shipping')",
        "street_address": "VARCHAR(255)",
        "city": "VARCHAR(100)",
        "state": "VARCHAR(100)",
        "postal_code": "VARCHAR(20)",
        "country": "VARCHAR(100)",
        "is_default": "BOOLEAN DEFAULT FALSE"
    })
    
    er.add_entity("Category", {
        "category_id": "PK",
        "parent_id": "FK NULLABLE",
        "name": "VARCHAR(100) NOT NULL",
        "description": "TEXT",
        "slug": "VARCHAR(100) UNIQUE",
        "is_active": "BOOLEAN DEFAULT TRUE",
        "sort_order": "INTEGER"
    })
    
    er.add_entity("Product", {
        "product_id": "PK",
        "category_id": "FK",
        "name": "VARCHAR(255) NOT NULL",
        "description": "TEXT",
        "sku": "VARCHAR(100) UNIQUE",
        "price": "DECIMAL(10,2)",
        "cost": "DECIMAL(10,2)",
        "weight": "DECIMAL(8,2)",
        "dimensions": "VARCHAR(50)",
        "stock_quantity": "INTEGER DEFAULT 0",
        "min_stock_level": "INTEGER DEFAULT 0",
        "is_active": "BOOLEAN DEFAULT TRUE",
        "created_at": "TIMESTAMP",
        "updated_at": "TIMESTAMP"
    })
    
    er.add_entity("Order", {
        "order_id": "PK",
        "user_id": "FK",
        "billing_address_id": "FK",
        "shipping_address_id": "FK",
        "order_number": "VARCHAR(50) UNIQUE",
        "status": "ENUM('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')",
        "subtotal": "DECIMAL(10,2)",
        "tax_amount": "DECIMAL(10,2)",
        "shipping_amount": "DECIMAL(10,2)",
        "total_amount": "DECIMAL(10,2)",
        "payment_status": "ENUM('pending', 'paid', 'failed', 'refunded')",
        "created_at": "TIMESTAMP",
        "updated_at": "TIMESTAMP"
    })
    
    er.add_entity("OrderItem", {
        "order_item_id": "PK",
        "order_id": "FK",
        "product_id": "FK",
        "quantity": "INTEGER NOT NULL",
        "unit_price": "DECIMAL(10,2)",
        "total_price": "DECIMAL(10,2)"
    })
    
    er.add_entity("Payment", {
        "payment_id": "PK",
        "order_id": "FK",
        "payment_method": "ENUM('credit_card', 'debit_card', 'paypal', 'bank_transfer')",
        "amount": "DECIMAL(10,2)",
        "status": "ENUM('pending', 'completed', 'failed', 'refunded')",
        "transaction_id": "VARCHAR(255)",
        "gateway_response": "JSON",
        "processed_at": "TIMESTAMP"
    })
    
    # Add relationships
    er.add_relationship("User", "Address", "one-to-many", "has")
    er.add_relationship("User", "Order", "one-to-many", "places")
    er.add_relationship("Category", "Category", "one-to-many", "parent_child")
    er.add_relationship("Category", "Product", "one-to-many", "contains")
    er.add_relationship("Product", "OrderItem", "one-to-many", "included_in")
    er.add_relationship("Order", "OrderItem", "one-to-many", "contains")
    er.add_relationship("Order", "Payment", "one-to-many", "paid_by")
    er.add_relationship("Address", "Order", "one-to-many", "billing_address")
    er.add_relationship("Address", "Order", "one-to-many", "shipping_address")
    
    # Save ER diagram
    renderer = MermaidRenderer()
    er_path = output_dir / "database_schema.svg"
    renderer.save(er, er_path)
    print(f"📁 Database schema saved to {er_path}")


def main():
    """Run all real-world use case examples."""
    print("=== Mermaid Render Real-World Use Cases ===\n")
    
    # Create output directory
    output_dir = create_output_dir()
    print(f"Output directory: {output_dir.absolute()}\n")
    
    # Run examples
    try:
        software_architecture_documentation(output_dir)
        print()
        
        api_documentation_example(output_dir)
        print()
        
        business_process_modeling(output_dir)
        print()
        
        database_design_example(output_dir)
        print()
        
        print("✅ All real-world use case examples completed successfully!")
        print(f"Check the {output_dir} directory for generated diagrams.")
        
    except Exception as e:
        print(f"❌ Error running real-world examples: {e}")
        raise


if __name__ == "__main__":
    main()
