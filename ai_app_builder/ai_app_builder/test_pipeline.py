"""
Dependency Engine, Topological Sort, and Rollback Test Script
"""
import frappe
from ai_app_builder.ai_app_builder.api import (
    get_creation_order, 
    validate_doctype_payload,
    create_stub_doctype,
    create_full_doctype,
    upgrade_existing_stub
)

def run_tests():
    # Setup mock existing doctypes
    existing = {"User", "Employee", "DocType"}
    
    # 1. Circular dependency scenario: A -> B and B -> A
    doctypes = [
        {
            "name": "DocA",
            "fields": [
                {"fieldname": "b_ref", "label": "B Ref", "fieldtype": "Link", "options": "DocB"},
                {"fieldname": "title", "label": "Title", "fieldtype": "Data"}
            ]
        },
        {
            "name": "DocB",
            "fields": [
                {"fieldname": "a_ref", "label": "A Ref", "fieldtype": "Link", "options": "DocA"},
                {"fieldname": "title", "label": "Title", "fieldtype": "Data"}
            ]
        }
    ]
    
    order = get_creation_order(doctypes, existing)
    actions = [action for action, dt in order]
    
    # Verify we have at least one stub, and all are created and upgraded
    assert "stub" in actions, "Circular dependency should introduce a stub action"
    assert "upgrade" in actions, "Circular dependency should introduce an upgrade action"
    
    # 2. Linear dependency scenario: C depends on B, B depends on A
    doctypes_linear = [
        {
            "name": "DocC",
            "fields": [
                {"fieldname": "b_ref", "label": "B Ref", "fieldtype": "Link", "options": "DocB"},
                {"fieldname": "title", "label": "Title", "fieldtype": "Data"}
            ]
        },
        {
            "name": "DocB",
            "fields": [
                {"fieldname": "a_ref", "label": "A Ref", "fieldtype": "Link", "options": "DocA"},
                {"fieldname": "title", "label": "Title", "fieldtype": "Data"}
            ]
        },
        {
            "name": "DocA",
            "fields": [
                {"fieldname": "title", "label": "Title", "fieldtype": "Data"}
            ]
        }
    ]
    
    order_linear = get_creation_order(doctypes_linear, existing)
    order_names = [dt["name"] for action, dt in order_linear if action == "create"]
    
    assert order_names == ["DocA", "DocB", "DocC"], f"Expected order ['DocA', 'DocB', 'DocC'], got {order_names}"
    
    # 3. Simulate execution and rollback loop
    print("Testing pipeline execution and transaction-safe rollback cleanup...")
    created = []
    try:
        # Create DocA as a stub to break the circular dependency
        create_stub_doctype(doctypes[0], ["DocA", "DocB"], existing)
        created.append("DocA")
        
        # DocA is created, now we can create DocB fully
        create_full_doctype(doctypes[1], ["DocA", "DocB"], existing)
        created.append("DocB")
        
        # Upgrade DocA to add back the link field referencing DocB
        upgrade_existing_stub(doctypes[0], ["DocA", "DocB"], existing)
        
        print("Success simulation: created DocA and DocB successfully!")
        
        # Test validation on created stubs
        doc_a = frappe.get_doc("DocType", "DocA")
        assert len(doc_a.fields) >= 2, "DocA should be fully upgraded and contain b_ref"
        
    finally:
        # Tear down created docs immediately to restore clean state (simulating safe rollback)
        print("Cleaning up database test doctypes...")
        frappe.db.rollback()
        for name in reversed(created):
            frappe.delete_doc("DocType", name, ignore_missing=True, force=True)
        frappe.db.commit()
    
    print("\n" + "=" * 60)
    print("AI PIPELINE TESTS PASSED SUCCESSFULY!")
    print("=" * 60)
    return {"status": "SUCCESS"}
