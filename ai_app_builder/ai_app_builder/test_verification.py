"""
End-to-End Verification Script for AI App Builder
Tests: sanitization, rule engine, layout engine, validation, naming_rule, rollback
"""
import frappe
import json
import sys
import traceback

# Ensure we have a test site context
# This script is meant to be run via: bench --site <site> execute ai_app_builder.ai_app_builder.test_verification.run_all_tests

def run_all_tests():
    results = []
    
    # Import the API module
    from ai_app_builder.ai_app_builder.api import (
        sanitize_doctype_name,
        sanitize_fieldname,
        apply_rule_engine,
        build_layout,
        validate_doctype_payload,
        create_master_doctype,
        create_child_table_doctype,
    )
    
    # =========================================
    # TEST 1: sanitize_doctype_name
    # =========================================
    try:
        assert sanitize_doctype_name("employee") == "Employee"
        assert sanitize_doctype_name("my cool doc") == "MyCoolDoc"
        assert sanitize_doctype_name("") == "DocType_Unnamed"
        assert sanitize_doctype_name("123bad") == "DocType_123Bad"
        assert sanitize_doctype_name("Patient-Record") == "PatientRecord"
        results.append(("sanitize_doctype_name", "PASS", ""))
    except AssertionError as e:
        results.append(("sanitize_doctype_name", "FAIL", str(e)))
    except Exception as e:
        results.append(("sanitize_doctype_name", "FAIL", str(e)))
    
    # =========================================
    # TEST 2: sanitize_fieldname
    # =========================================
    try:
        assert sanitize_fieldname("Employee Name") == "employee_name"
        assert sanitize_fieldname("Joining Date") == "joining_date"
        assert sanitize_fieldname("") == "unnamed_field"
        assert sanitize_fieldname("123field") == "field_123field"
        results.append(("sanitize_fieldname", "PASS", ""))
    except Exception as e:
        results.append(("sanitize_fieldname", "FAIL", str(e)))
    
    # =========================================
    # TEST 3: apply_rule_engine - field type inference
    # =========================================
    try:
        test_fields = [
            {"label": "Salary", "fieldtype": "Data"},
            {"label": "Joining Date", "fieldtype": "Data"},
            {"label": "Age", "fieldtype": "Data"},
            {"label": "Status", "fieldtype": "Data"},
            {"label": "Report", "fieldtype": "Data"},
            {"label": "Remarks", "fieldtype": "Data"},
            {"label": "Items", "fieldtype": "Data"},
            {"label": "Employee Name", "fieldtype": "Data"},
        ]
        refined = apply_rule_engine("Employee", test_fields)
        
        # Check salary -> Currency
        salary_f = next(f for f in refined if f["fieldname"] == "salary")
        assert salary_f["fieldtype"] == "Currency", f"Salary should be Currency, got {salary_f['fieldtype']}"
        
        # Check joining_date -> Date
        jd_f = next(f for f in refined if f["fieldname"] == "joining_date")
        assert jd_f["fieldtype"] == "Date", f"Joining Date should be Date, got {jd_f['fieldtype']}"
        
        # Check age -> Int
        age_f = next(f for f in refined if f["fieldname"] == "age")
        assert age_f["fieldtype"] == "Int", f"Age should be Int, got {age_f['fieldtype']}"
        
        # Check status -> Select
        status_f = next(f for f in refined if f["fieldname"] == "status")
        assert status_f["fieldtype"] == "Select", f"Status should be Select, got {status_f['fieldtype']}"
        
        # Check report -> Attach
        report_f = next(f for f in refined if f["fieldname"] == "report")
        assert report_f["fieldtype"] == "Attach", f"Report should be Attach, got {report_f['fieldtype']}"
        
        # Check remarks -> Small Text
        remarks_f = next(f for f in refined if f["fieldname"] == "remarks")
        assert remarks_f["fieldtype"] == "Small Text", f"Remarks should be Small Text, got {remarks_f['fieldtype']}"
        
        # Check items -> Table
        items_f = next(f for f in refined if f["fieldname"] == "items")
        assert items_f["fieldtype"] == "Table", f"Items should be Table, got {items_f['fieldtype']}"
        
        results.append(("apply_rule_engine", "PASS", ""))
    except Exception as e:
        results.append(("apply_rule_engine", "FAIL", str(e)))
    
    # =========================================
    # TEST 4: Duplicate fieldname prevention
    # =========================================
    try:
        dup_fields = [
            {"label": "Name", "fieldtype": "Data"},
            {"label": "Name", "fieldtype": "Data"},
            {"label": "Name", "fieldtype": "Data"},
        ]
        refined = apply_rule_engine("Test", dup_fields)
        fieldnames = [f["fieldname"] for f in refined]
        assert len(fieldnames) == len(set(fieldnames)), f"Duplicate fieldnames found: {fieldnames}"
        results.append(("duplicate_fieldname_prevention", "PASS", ""))
    except Exception as e:
        results.append(("duplicate_fieldname_prevention", "FAIL", str(e)))
    
    # =========================================
    # TEST 5: build_layout
    # =========================================
    try:
        data_fields = [
            {"fieldname": "name_field", "label": "Name", "fieldtype": "Data"},
            {"fieldname": "salary", "label": "Salary", "fieldtype": "Currency"},
            {"fieldname": "remarks", "label": "Remarks", "fieldtype": "Small Text"},
            {"fieldname": "items", "label": "Items", "fieldtype": "Table", "options": "TestItem"},
        ]
        layout = build_layout(data_fields)
        
        # Must start with Section Break
        assert layout[0]["fieldtype"] == "Section Break", "Layout must start with a Section Break"
        
        # Must have no duplicate section breaks in a row
        for i in range(1, len(layout)):
            if layout[i]["fieldtype"] == "Section Break":
                assert layout[i-1]["fieldtype"] != "Section Break", f"Duplicate section breaks at index {i-1} and {i}"
        
        # Tables should be at the end
        table_idx = next(i for i, f in enumerate(layout) if f.get("fieldtype") == "Table")
        non_table_after = [f for f in layout[table_idx+1:] if f.get("fieldtype") not in ("Section Break", "Column Break", "Table")]
        assert len(non_table_after) == 0, "Non-table data fields found after Table field"
        
        results.append(("build_layout", "PASS", ""))
    except Exception as e:
        results.append(("build_layout", "FAIL", str(e)))
    
    # =========================================
    # TEST 6: validate_doctype_payload - valid payload
    # =========================================
    try:
        valid_payload = {
            "name": "TestValidDocType",
            "naming_rule": "By fieldname",
            "autoname": "field:title",
            "fields": [
                {"fieldname": "title", "label": "Title", "fieldtype": "Data"},
                {"fieldname": "description", "label": "Description", "fieldtype": "Small Text"},
            ]
        }
        # Should not throw
        validate_doctype_payload(valid_payload, ["TestValidDocType"])
        results.append(("validate_payload_valid", "PASS", ""))
    except Exception as e:
        results.append(("validate_payload_valid", "FAIL", str(e)))
    
    # =========================================
    # TEST 7: validate_doctype_payload - invalid naming_rule
    # =========================================
    try:
        bad_payload = {
            "name": "BadNamingDoc",
            "naming_rule": "By field",  # INVALID - this is the original bug
            "autoname": "field:title",
            "fields": [
                {"fieldname": "title", "label": "Title", "fieldtype": "Data"},
            ]
        }
        caught = False
        try:
            validate_doctype_payload(bad_payload, ["BadNamingDoc"])
        except frappe.exceptions.ValidationError:
            caught = True
        except Exception as e:
            if "Invalid naming rule" in str(e):
                caught = True
        
        assert caught, "validate_doctype_payload should reject 'By field' naming_rule"
        results.append(("validate_naming_rule_rejection", "PASS", ""))
    except Exception as e:
        results.append(("validate_naming_rule_rejection", "FAIL", str(e)))
    
    # =========================================
    # TEST 8: validate_doctype_payload - duplicate fieldnames
    # =========================================
    try:
        dup_payload = {
            "name": "DupFieldDoc",
            "naming_rule": "Random",
            "autoname": "hash",
            "fields": [
                {"fieldname": "title", "label": "Title", "fieldtype": "Data"},
                {"fieldname": "title", "label": "Title 2", "fieldtype": "Data"},
            ]
        }
        caught = False
        try:
            validate_doctype_payload(dup_payload, ["DupFieldDoc"])
        except Exception as e:
            if "Duplicate" in str(e) or "duplicate" in str(e):
                caught = True
        assert caught, "validate_doctype_payload should reject duplicate fieldnames"
        results.append(("validate_duplicate_fieldnames", "PASS", ""))
    except Exception as e:
        results.append(("validate_duplicate_fieldnames", "FAIL", str(e)))
    
    # =========================================
    # TEST 9: validate_doctype_payload - autoname field missing
    # =========================================
    try:
        missing_autoname = {
            "name": "MissingAutoDoc",
            "naming_rule": "By fieldname",
            "autoname": "field:nonexistent",
            "fields": [
                {"fieldname": "title", "label": "Title", "fieldtype": "Data"},
            ]
        }
        caught = False
        try:
            validate_doctype_payload(missing_autoname, ["MissingAutoDoc"])
        except Exception as e:
            if "not found" in str(e):
                caught = True
        assert caught, "validate_doctype_payload should reject autoname referencing non-existent field"
        results.append(("validate_autoname_field_check", "PASS", ""))
    except Exception as e:
        results.append(("validate_autoname_field_check", "FAIL", str(e)))
    
    # =========================================
    # TEST 10: validate naming_rule values in create_master_doctype
    # =========================================
    try:
        # Verify the master doctype template uses "By fieldname"
        # We do this by inspecting the source directly
        import inspect
        source = inspect.getsource(create_master_doctype)
        assert '"By fieldname"' in source, "create_master_doctype should use 'By fieldname'"
        assert '"By field"' not in source.replace('"By fieldname"', ''), "create_master_doctype should NOT use 'By field'"
        results.append(("master_doctype_naming_rule", "PASS", ""))
    except Exception as e:
        results.append(("master_doctype_naming_rule", "FAIL", str(e)))
    
    # =========================================
    # TEST 11: validate Link field requires options
    # =========================================
    try:
        link_no_opts = {
            "name": "LinkNoOptsDoc",
            "naming_rule": "Random",
            "autoname": "hash",
            "fields": [
                {"fieldname": "customer", "label": "Customer", "fieldtype": "Link"},
            ]
        }
        caught = False
        try:
            validate_doctype_payload(link_no_opts, ["LinkNoOptsDoc"])
        except Exception as e:
            if "target" in str(e).lower() or "options" in str(e).lower():
                caught = True
        assert caught, "validate_doctype_payload should reject Link field without options"
        results.append(("validate_link_requires_options", "PASS", ""))
    except Exception as e:
        results.append(("validate_link_requires_options", "FAIL", str(e)))
    
    # =========================================
    # TEST 12: validate Table field requires options
    # =========================================
    try:
        table_no_opts = {
            "name": "TableNoOptsDoc",
            "naming_rule": "Random",
            "autoname": "hash",
            "fields": [
                {"fieldname": "items", "label": "Items", "fieldtype": "Table"},
            ]
        }
        caught = False
        try:
            validate_doctype_payload(table_no_opts, ["TableNoOptsDoc"])
        except Exception as e:
            if "child" in str(e).lower() or "options" in str(e).lower():
                caught = True
        assert caught, "validate_doctype_payload should reject Table field without options"
        results.append(("validate_table_requires_options", "PASS", ""))
    except Exception as e:
        results.append(("validate_table_requires_options", "FAIL", str(e)))
    
    # =========================================
    # PRINT RESULTS
    # =========================================
    print("\n" + "=" * 60)
    print("AI APP BUILDER - VERIFICATION RESULTS")
    print("=" * 60)
    
    pass_count = 0
    fail_count = 0
    
    for name, status, detail in results:
        icon = "✓" if status == "PASS" else "✗"
        print(f"  {icon} {name}: {status}")
        if detail:
            print(f"     → {detail}")
        if status == "PASS":
            pass_count += 1
        else:
            fail_count += 1
    
    print(f"\n  Total: {pass_count + fail_count} | Passed: {pass_count} | Failed: {fail_count}")
    print("=" * 60)
    
    return {"passed": pass_count, "failed": fail_count, "results": results}
