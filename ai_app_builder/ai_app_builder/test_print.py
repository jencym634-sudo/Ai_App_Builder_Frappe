import json
import frappe
from ai_app_builder.ai_app_builder.api import generate_doctype, analyze_prompt

# All possible doctype names that any AI model or deterministic parser might create
# for a shopping app prompt - we clean them ALL to ensure a fresh slate.
CLEANUP_NAMES = [
    "Order", "OrderItem", "Customer", "Payment", "PaymentStatus",
    "Item", "ShoppingApp", "Product", "Cart", "CartItem",
    "OrderItemsOrderedItem", "OrderDetailsItem",
    "CustomerOrderItem", "OrderPaymentItem",
]

def run():
    p = "Create a shopping app to manage customer Orders, where each Order has a child table of Items ordered (OrderItem) containing details and cost, and we want to track Customer and Payment status."
    
    print("=" * 60)
    print("COMPREHENSIVE PIPELINE DEBUG TEST")
    print("=" * 60)
    
    print("\n1. Cleaning up ALL possible leftover doctypes...")
    for dt_name in CLEANUP_NAMES:
        if frappe.db.exists("DocType", dt_name):
            print(f"   Deleting leftover: {dt_name}")
            frappe.delete_doc("DocType", dt_name, ignore_missing=True, force=True)
    frappe.db.commit()
    frappe.clear_cache()
    
    print("\n2. Running analyze_prompt...")
    parsed = analyze_prompt(p)
    print(f"   System: {parsed['system_name']}")
    print(f"   Primary: {parsed['primary_doctype']}")
    for dt in parsed["doctypes"]:
        print(f"   DocType: {dt['name']}, istable: {dt.get('istable')}, is_primary: {dt.get('is_primary')}")
        table_fields = [f for f in dt.get("fields", []) if f.get("fieldtype") == "Table"]
        for tf in table_fields:
            print(f"      -> Table field: {tf.get('fieldname')} -> options: {tf.get('options')}")
    
    print("\n3. Running generate_doctype...")
    try:
        res = generate_doctype(p)
        print(f"   Result: success={res.get('success')}, created={res.get('doctypes_created')}")
    except Exception as e:
        print(f"   GENERATION FAILED: {e}")
        # Print error log details
        logs = frappe.get_all("Error Log", filters={"title": "AI App Builder Generation Error"}, fields=["name", "error"], order_by="creation desc", limit=1)
        if logs:
            print(f"   Error details: {logs[0].error[:500]}")
        return
    
    print("\n4. Verifying database values...")
    all_ok = True
    for dt in parsed["doctypes"]:
        dt_name = dt["name"]
        if frappe.db.exists("DocType", dt_name):
            db_istable = frappe.db.get_value("DocType", dt_name, "istable")
            expected = dt.get("istable", 0)
            status = "OK" if db_istable == expected else f"MISMATCH (expected {expected})"
            if db_istable != expected:
                all_ok = False
            print(f"   {dt_name}: DB istable={db_istable} {status}")
            
            # Check Table field references
            doc = frappe.get_doc("DocType", dt_name)
            for f in doc.fields:
                if f.fieldtype == "Table":
                    target_exists = frappe.db.exists("DocType", f.options)
                    target_istable = frappe.db.get_value("DocType", f.options, "istable") if target_exists else "N/A"
                    print(f"      -> Table field '{f.fieldname}' -> '{f.options}' (exists={bool(target_exists)}, istable={target_istable})")
        else:
            print(f"   {dt_name}: DOES NOT EXIST IN DB")
            all_ok = False
    
    print("\n5. Cleanup...")
    for dt_name in CLEANUP_NAMES:
        if frappe.db.exists("DocType", dt_name):
            frappe.delete_doc("DocType", dt_name, ignore_missing=True, force=True)
    frappe.db.commit()
    frappe.clear_cache()
    
    print("\n" + "=" * 60)
    if all_ok:
        print("RESULT: ALL CHECKS PASSED")
    else:
        print("RESULT: SOME CHECKS FAILED - SEE ABOVE")
    print("=" * 60)

if __name__ == "__main__":
    frappe.init(site="ai-builder.local", sites_path="sites")
    frappe.connect()
    run()
