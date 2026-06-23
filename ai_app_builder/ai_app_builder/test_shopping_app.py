import frappe
from ai_app_builder.ai_app_builder.api import generate_doctype, check_upgrade, upgrade_doctype

def run_shopping_app_test():
    prompt = "Create a shopping app to manage customer Orders, where each Order has a child table of Items ordered (OrderItem) containing details and cost, and we want to track Customer and Payment status."
    
    print(f"Running shopping app generation test with prompt: '{prompt}'")
    
    # Clean up first if they exist
    print("Clearing any existing test doctypes...")
    for dt_name in ["Order", "OrderItem", "Customer", "PaymentStatus"]:
        if frappe.db.exists("DocType", dt_name):
            frappe.delete_doc("DocType", dt_name, ignore_missing=True, force=True)
    frappe.db.commit()
    frappe.clear_cache()
    
    # 1. Run the generation
    res = generate_doctype(prompt)
    print("Generation result:", res)
    
    # Check successes
    assert res.get("success"), "Generation failed!"
    
    order_exists = frappe.db.exists("DocType", "Order")
    order_item_exists = frappe.db.exists("DocType", "OrderItem")
    
    print(f"Order exists: {bool(order_exists)}")
    print(f"OrderItem exists: {bool(order_item_exists)}")
    
    assert order_exists, "Order DocType should be created"
    assert order_item_exists, "OrderItem DocType should be created"
    
    # Verify OrderItem is indeed a Child Table (istable=1)
    istable = frappe.db.get_value("DocType", "OrderItem", "istable")
    assert istable == 1, f"OrderItem must be a Child Table (istable=1), got {istable}"
    
    # Verify Order has the Table field referencing OrderItem
    order_doc = frappe.get_doc("DocType", "Order")
    table_field = next((f for f in order_doc.fields if f.fieldtype == "Table"), None)
    assert table_field is not None, "Order should have a Table field"
    assert table_field.options == "OrderItem", f"Table field should point to OrderItem, got {table_field.options}"
    
    # 2. Run the upgrade check and validation
    upgrade_prompt = "Create a shopping app to manage customer Orders, where each Order has a child table of Items ordered (OrderItem) containing details and cost, and we want to track Customer, Payment status, Delivery Address, and Shipment Tracking."
    print(f"Running check_upgrade with prompt: '{upgrade_prompt}'")
    
    up_info = check_upgrade(upgrade_prompt)
    print("Upgrade check result:", up_info)
    assert up_info.get("exists") is True, "Order should exist for upgrading"
    assert len(up_info.get("new_fields", [])) > 0, "Should detect new fields for upgrading (Delivery Address, Shipment Tracking)"
    
    # Perform upgrade
    print("Running upgrade_doctype...")
    up_res = upgrade_doctype(upgrade_prompt)
    print("Upgrade result:", up_res)
    
    # Verify new fields exist
    updated_order_doc = frappe.get_doc("DocType", "Order")
    existing_fieldnames = {f.fieldname for f in updated_order_doc.fields}
    assert "delivery_address" in existing_fieldnames, "delivery_address field should be added"
    assert "shipment_tracking" in existing_fieldnames or "shipment_tracking_number" in existing_fieldnames, "shipment tracking field should be added"
    
    # Cleanup to leave a clean database state
    print("Tearing down generated doctypes...")
    for dt_name in ["Order", "OrderItem", "Customer", "PaymentStatus", "PaymentStatusItem"]:
        if frappe.db.exists("DocType", dt_name):
            frappe.delete_doc("DocType", dt_name, ignore_missing=True, force=True)
    frappe.db.commit()
    frappe.clear_cache()
    
    print("Shopping App generation and upgrade test completed successfully with ZERO errors!")

if __name__ == "__main__":
    run_shopping_app_test()
