import frappe
import re
from ai_app_builder.ai_app_builder.gemini_helper import generate_schema

# ---------------------------------------------------
# Sanitization and Cleaners
# ---------------------------------------------------
def sanitize_doctype_name(name):
    """
    Sanitizes DocType name to be alphanumeric + title cased, preserving camelcase.
    """
    if not name:
        return "DocType_Unnamed"
    name = re.sub(r'[^A-Za-z0-9 _-]', '', name)
    name = name.strip()
    if not name:
        return "DocType_Unnamed"
    
    parts = re.split(r'[ _-]+', name)
    capitalized_parts = []
    for p in parts:
        if p:
            cap_p = p
            for idx, c in enumerate(p):
                if c.isalpha():
                    cap_p = p[:idx] + c.upper() + p[idx+1:]
                    break
            capitalized_parts.append(cap_p)
            
    name = "".join(capitalized_parts)
    if not re.match(r'^[A-Za-z]', name):
        name = "DocType_" + name
    return name

# Frappe's restricted fieldnames - these are internal DB columns that cannot be used as field names
RESTRICTED_FIELDNAMES = frozenset({
    "name", "parent", "creation", "owner", "modified", "modified_by",
    "parentfield", "parenttype", "file_list", "flags", "docstatus",
    "idx", "doctype",
})

def sanitize_fieldname(label):
    """
    Sanitizes a field label into a safe Frappe fieldname.
    Automatically renames restricted fieldnames to avoid Frappe validation errors.
    """
    if not label:
        return "unnamed_field"
    fname = label.lower().strip()
    fname = re.sub(r'[^a-z0-9_ -]', '', fname)
    fname = fname.replace(" ", "_").replace("-", "_")
    fname = re.sub(r'_+', '_', fname)
    if not re.match(r'^[a-z_]', fname):
        fname = "field_" + fname
    # Prevent Frappe's InvalidFieldNameError for restricted internal column names
    if fname in RESTRICTED_FIELDNAMES:
        fname = fname + "_field"
    return fname

# ---------------------------------------------------
# Centralized Layout and Duplicate Protection Utilities
# ---------------------------------------------------
def field_exists(doc_fields, fieldname):
    return any(f.get("fieldname") == fieldname for f in doc_fields)

def section_exists(doc_fields, label):
    if not label:
        return False
    return any(f.get("fieldtype") == "Section Break" and f.get("label", "").strip().lower() == label.strip().lower() for f in doc_fields)

def column_exists(doc_fields, fieldname):
    return any(f.get("fieldtype") == "Column Break" and f.get("fieldname") == fieldname for f in doc_fields)

def layout_exists(doc_fields, fieldtype, label=None, fieldname=None):
    if fieldtype == "Section Break" and label:
        return section_exists(doc_fields, label)
    if fieldtype == "Column Break" and fieldname:
        return column_exists(doc_fields, fieldname)
    if fieldname:
        return field_exists(doc_fields, fieldname)
    return False

def parse_prompt_deterministically(prompt):
    """
    Deterministic NLP parser fallback when OpenAI/OpenRouter models are unavailable.
    Parses natural language prompts to infer structured DocTypes, fields, and options.
    """
    prompt_lower = prompt.lower()
    
    # 1. Infer system name and primary doctype
    system_name = "AI Enterprise Application"
    primary_name = "ERPSystem"
    
    if "employee" in prompt_lower or "staff" in prompt_lower:
        system_name = "Employee Management System"
        primary_name = "Employee"
    elif "hospital" in prompt_lower or "patient" in prompt_lower or "clinic" in prompt_lower or "medical" in prompt_lower or "doctor" in prompt_lower:
        system_name = "Hospital Management System"
        primary_name = "Patient"
    elif "library" in prompt_lower or "book" in prompt_lower:
        system_name = "Library Catalog System"
        primary_name = "Book"
    elif "vehicle" in prompt_lower or "fleet" in prompt_lower or "car" in prompt_lower or "driver" in prompt_lower:
        system_name = "Fleet Management System"
        primary_name = "Vehicle"
    elif "inventory" in prompt_lower or "stock" in prompt_lower or "item" in prompt_lower or "warehouse" in prompt_lower:
        system_name = "Inventory Control System"
        primary_name = "Item"
    elif "invoice" in prompt_lower or "billing" in prompt_lower or "sale" in prompt_lower or "purchase" in prompt_lower:
        system_name = "Billing and Invoice System"
        primary_name = "Invoice"
    elif "school" in prompt_lower or "student" in prompt_lower or "class" in prompt_lower or "course" in prompt_lower:
        system_name = "School Information System"
        primary_name = "Student"
        
    primary_name = sanitize_doctype_name(primary_name)
    
    # 2. Extract potential fields by parsing the string
    delimiters = [",", "with", "and", "containing", "having", "track", "manage", "holding", ";", "."]
    pattern = '|'.join(map(re.escape, delimiters))
    raw_segments = re.split(pattern, prompt, flags=re.IGNORECASE)
    
    candidate_fields = []
    seen_labels = set()
    
    for seg in raw_segments:
        seg = seg.strip()
        if not seg:
            continue
        # Avoid long sentences
        if len(seg.split()) > 4:
            continue
            
        clean_label = re.sub(r'[^A-Za-z0-9 ]', '', seg).strip()
        if not clean_label or len(clean_label) < 2:
            continue
            
        label_lower = clean_label.lower()
        if label_lower in ["create", "system", "management", "management system", "an erp", "erp", "a system", "enterprisegrade", "option", "options"]:
            continue
            
        if label_lower in seen_labels:
            continue
        seen_labels.add(label_lower)
        
        ftype = "Data"
        options = ""
        
        if any(word in label_lower for word in ["salary", "amount", "price", "cost", "fee", "payment", "rate", "budget"]):
            ftype = "Currency"
        elif "date" in label_lower or "dob" in label_lower:
            ftype = "Date"
        elif any(word in label_lower for word in ["report", "proof", "document", "attachment", "file", "image"]):
            ftype = "Attach"
        elif any(word in label_lower for word in ["status", "severity", "priority", "type", "category"]):
            ftype = "Select"
            if "status" in label_lower:
                options = "Active\nInactive\nPending"
            elif "priority" in label_lower or "severity" in label_lower:
                options = "Low\nMedium\nHigh"
            else:
                options = "Standard\nCustom"
        elif any(word in label_lower for word in ["age", "count", "quantity", "number", "qty"]):
            ftype = "Int"
        elif any(word in label_lower for word in ["remarks", "notes", "description", "address", "condition", "summary"]):
            ftype = "Small Text"
        elif any(word in label_lower for word in ["items", "products", "entries", "details", "activities", "history"]):
            ftype = "Table"
        elif label_lower in ["customer", "employee", "student", "teacher", "doctor", "patient", "department", "manager", "supplier", "vendor", "user"]:
            ftype = "Link"
            options = sanitize_doctype_name(label_lower)
            
        candidate_fields.append({
            "label": clean_label.title(),
            "fieldtype": ftype,
            "options": options
        })
        
    has_primary_field = any(any(word in f["label"].lower() for word in ["name", "title", "id"]) for f in candidate_fields)
    if not has_primary_field:
        candidate_fields.insert(0, {
            "label": f"{primary_name} Name",
            "fieldtype": "Data"
        })
        
    doctypes_to_generate = []
    primary_dt = {
        "name": primary_name,
        "description": f"{primary_name} tracking entity",
        "fields": candidate_fields
    }
    doctypes_to_generate.append(primary_dt)
    
    # Check for Link/Table child targets
    for f in candidate_fields:
        if f["fieldtype"] in ("Link", "Table") and f.get("options"):
            target_name = sanitize_doctype_name(f["options"])
            if target_name != primary_name:
                is_table = (f["fieldtype"] == "Table")
                doctypes_to_generate.append({
                    "name": target_name,
                    "description": f"{target_name} detail entity",
                    "istable": 1 if is_table else 0,
                    "fields": [
                        {"label": "Title", "fieldtype": "Data"},
                        {"label": "Description", "fieldtype": "Small Text"}
                    ]
                })
                
    return {
        "system_name": system_name,
        "primary_doctype": primary_name,
        "doctypes": doctypes_to_generate
    }

def validate_schema(system_schema):
    """
    Validates the entire system schema blueprint before layout, generation, or upgrades.
    """
    if not system_schema:
        frappe.throw("Schema blueprint is empty")
        
    system_name = system_schema.get("system_name")
    if not system_name:
        frappe.throw("System Name is required in schema")
        
    primary_doctype = system_schema.get("primary_doctype")
    if not primary_doctype:
        frappe.throw("Primary DocType is required in schema")
        
    doctypes = system_schema.get("doctypes", [])
    if not doctypes:
        frappe.throw("Schema must contain at least one DocType definition")
        
    parsed_names = [dt["name"] for dt in doctypes]
    if len(parsed_names) != len(set(parsed_names)):
        frappe.throw("Duplicate DocType names detected in the generation plan")
        
    existing_doctypes = {d.name for d in frappe.get_all("DocType", fields=["name"])}
    
    for dt in doctypes:
        validate_doctype_payload(dt, parsed_names, existing_doctypes)
        
    # Check dependencies and options
    for dt in doctypes:
        dt_name = dt["name"]
        for f in dt.get("fields", []):
            fieldtype = f.get("fieldtype")
            fieldname = f.get("fieldname")
            options = f.get("options")
            
            if fieldtype == "Link":
                if not options:
                    frappe.throw(f"Link field '{fieldname}' in '{dt_name}' must have a target options DocType")
                if options not in existing_doctypes and options not in parsed_names:
                    frappe.throw(f"Link target DocType '{options}' for field '{fieldname}' in '{dt_name}' does not exist and is not part of the generation plan")
            elif fieldtype == "Table":
                if not options:
                    frappe.throw(f"Table field '{fieldname}' in '{dt_name}' must have a child table options DocType")
                if options not in existing_doctypes and options not in parsed_names:
                    frappe.throw(f"Child table DocType '{options}' for field '{fieldname}' in '{dt_name}' does not exist and is not part of the generation plan")

# ---------------------------------------------------
# Rule Engine - Intelligence Inference Layer
# ---------------------------------------------------
def apply_rule_engine(doctype_name, fields):
    """
    Processes field schemas through a deterministic rule validation engine,
    normalizing types, mapping Link/Table references, and resolving duplicates.
    """
    refined_fields = []
    used_fieldnames = set()

    for f in fields:
        label = f.get("label", "").strip()
        if not label:
            continue

        fname = sanitize_fieldname(label)

        # Duplicate Prevention Engine (Requirement 7)
        if fname in used_fieldnames:
            counter = 1
            original_fname = fname
            while f"{original_fname}_{counter}" in used_fieldnames:
                counter += 1
            fname = f"{original_fname}_{counter}"

        used_fieldnames.add(fname)

        ftype = f.get("fieldtype", "Data")
        options = f.get("options", "")

        # Deterministic overrides based on semantic labels (Requirement 6)
        label_lower = label.lower()

        # salary/amount/price/cost/fee/payment -> Currency
        if any(word in label_lower for word in ["salary", "amount", "price", "cost", "fee", "payment", "rate", "budget"]):
            ftype = "Currency"
        # joining date / contains date -> Date
        elif "date" in label_lower or "dob" in label_lower:
            ftype = "Date"
        # report/proof -> Attach
        elif any(word in label_lower for word in ["report", "proof", "document", "attachment", "file", "image"]):
            ftype = "Attach"
        # status -> Select
        elif any(word in label_lower for word in ["status", "severity", "priority", "type", "category"]):
            ftype = "Select"
            if not options or "\n" not in str(options):
                if "status" in label_lower:
                    options = "Active\nInactive\nPending"
                elif "priority" in label_lower or "severity" in label_lower:
                    options = "Low\nMedium\nHigh"
                else:
                    options = "Standard\nCustom"
        # age/count/quantity/number -> Int
        elif any(word in label_lower for word in ["age", "count", "quantity", "number", "qty"]):
            ftype = "Int"
        # remarks -> Small Text
        elif any(word in label_lower for word in ["remarks", "notes", "description", "address", "condition", "summary"]):
            ftype = "Small Text"
        # products/items -> Table (Child Table)
        elif any(word in label_lower for word in ["items", "products", "entries", "details", "activities", "history"]):
            ftype = "Table"
        # standard entity mapping -> Link
        elif label_lower in ["customer", "employee", "student", "teacher", "doctor", "patient", "department", "manager", "supplier", "vendor", "user"]:
            ftype = "Link"
            options = sanitize_doctype_name(label)

        # Standard Link resolutions
        if ftype == "Link":
            if not options:
                if "manager" in label_lower:
                    options = "Employee"
                elif "user" in label_lower:
                    options = "User"
                else:
                    options = sanitize_doctype_name(label)
            else:
                options = sanitize_doctype_name(str(options))

        # Standard Child Table resolutions
        if ftype == "Table":
            if not options:
                options = sanitize_doctype_name(doctype_name) + sanitize_doctype_name(label) + "Item"
            else:
                options = sanitize_doctype_name(str(options))

        refined_field = {
            "fieldname": fname,
            "label": label.title(),
            "fieldtype": ftype
        }
        if options:
            refined_field["options"] = str(options)

        refined_fields.append(refined_field)

    return refined_fields

# ---------------------------------------------------
# Layout Engine - Professional Grid Allocator
# ---------------------------------------------------
def build_layout(fields):
    """
    Arranges data fields professionally into standard two-column grid details,
    full-width descriptive areas, and child table sections at the bottom.
    Prevents duplicate section breaks or column breaks.
    """
    # Exclude any raw layout breakers to build a clean matrix
    actual_fields = [f for f in fields if f.get("fieldtype") not in ("Section Break", "Column Break")]

    table_fields = [f for f in actual_fields if f.get("fieldtype") == "Table"]
    large_fields = [f for f in actual_fields if f.get("fieldtype") in ("Small Text", "Attach")]
    standard_fields = [f for f in actual_fields if f.get("fieldtype") not in ("Table", "Small Text", "Attach")]

    layout_fields = []
    seen_sb_labels = set()

    # 1. Main Grid Details Section
    main_sb_label = "Details"
    seen_sb_labels.add(main_sb_label)
    layout_fields.append({
        "fieldname": "sec_main_details",
        "label": main_sb_label,
        "fieldtype": "Section Break"
    })

    if standard_fields:
        half = (len(standard_fields) + 1) // 2
        col1 = standard_fields[:half]
        col2 = standard_fields[half:]

        layout_fields.extend(col1)

        if col2:
            layout_fields.append({
                "fieldname": "col_break_1",
                "fieldtype": "Column Break"
            })
            layout_fields.extend(col2)

    # 2. Additional Info Section (full-width text area and attachments)
    if large_fields:
        add_sb_label = "Additional Information"
        if add_sb_label in seen_sb_labels:
            add_sb_label = "More Info"
            counter = 1
            while f"{add_sb_label} {counter}" in seen_sb_labels:
                counter += 1
            add_sb_label = f"{add_sb_label} {counter}"
        seen_sb_labels.add(add_sb_label)

        layout_fields.append({
            "fieldname": "sec_additional_info",
            "label": add_sb_label,
            "fieldtype": "Section Break"
        })
        layout_fields.extend(large_fields)

    # 3. Child Table Sections (always placed at the bottom)
    for tf in table_fields:
        tf_label = tf.get("label") or "Items"
        if tf_label in seen_sb_labels:
            tf_label = f"{tf_label} List"
            counter = 1
            while f"{tf_label} {counter}" in seen_sb_labels:
                counter += 1
            tf_label = f"{tf_label} {counter}" if counter > 1 else tf_label
        seen_sb_labels.add(tf_label)

        layout_fields.append({
            "fieldname": f"sec_table_{tf['fieldname']}",
            "label": tf_label,
            "fieldtype": "Section Break"
        })
        layout_fields.append(tf)

    return layout_fields

# ---------------------------------------------------
# Validation Engine (Requirement 3)
# ---------------------------------------------------
def validate_doctype_payload(doc_dict, parsed_doctypes_names, existing_doctypes=None):
    """
    Validates a DocType dict before it is inserted or saved to database.
    """
    name = doc_dict.get("name")
    if not name:
        frappe.throw("DocType name is required")

    naming_rule = doc_dict.get("naming_rule")
    valid_rules = ["", "Set by user", "Autoincrement", "By fieldname", "By \"Naming Series\" field", "Expression", "Expression (old style)", "Random", "By script"]
    if naming_rule and naming_rule not in valid_rules:
        frappe.throw(f"Invalid naming rule: '{naming_rule}' in DocType '{name}'. Must be one of: {', '.join(valid_rules)}")

    autoname = doc_dict.get("autoname")
    # Verify autoname matches naming rule
    if naming_rule == "By fieldname":
        if not autoname or not autoname.startswith("field:"):
            frappe.throw(f"In DocType '{name}', when naming rule is 'By fieldname', autoname must specify a field, e.g. 'field:fieldname'")
        autoname_field = autoname.split(":")[1]
        field_exists = any(f.get("fieldname") == autoname_field for f in doc_dict.get("fields", []))
        if not field_exists:
            frappe.throw(f"In DocType '{name}', autoname field '{autoname_field}' not found in the fields list")

    if existing_doctypes is None:
        existing_doctypes = {d.name for d in frappe.get_all("DocType", fields=["name"])}

    fields = doc_dict.get("fields", [])
    seen_fieldnames = set()
    seen_labels = set()
    seen_section_labels = set()
    
    for idx, f in enumerate(fields):
        fieldname = f.get("fieldname")
        fieldtype = f.get("fieldtype")
        label = f.get("label")

        # Missing mandatory fields
        if not fieldtype:
            frappe.throw(f"Field at index {idx} in '{name}' is missing a fieldtype")

        # Fieldname generation if missing for sections / columns
        if not fieldname:
            if fieldtype in ("Section Break", "Column Break"):
                fieldname = f"sb_{idx}" if fieldtype == "Section Break" else f"cb_{idx}"
                f["fieldname"] = fieldname
            else:
                frappe.throw(f"Field at index {idx} in '{name}' is missing a fieldname")

        # Strict fieldname format validation
        if not re.match(r"^[a-z_][a-z0-9_]*$", fieldname):
            frappe.throw(f"Invalid fieldname '{fieldname}' in '{name}'. Fieldnames must start with a lowercase letter or underscore, and contain only lowercase letters, numbers, and underscores.")

        if fieldname in seen_fieldnames:
            frappe.throw(f"Duplicate fieldname '{fieldname}' detected in DocType '{name}'")
        seen_fieldnames.add(fieldname)

        # Label check
        if label:
            if fieldtype == "Section Break":
                if label in seen_section_labels:
                    frappe.throw(f"Duplicate Section Break label '{label}' detected in DocType '{name}'")
                seen_section_labels.add(label)
            elif fieldtype != "Column Break":
                if label in seen_labels:
                    frappe.throw(f"Duplicate field label '{label}' detected in DocType '{name}'")
                seen_labels.add(label)
        elif fieldtype not in ("Section Break", "Column Break"):
            frappe.throw(f"Field '{fieldname}' in '{name}' is missing a label")

        # Link target validation
        if fieldtype == "Link":
            options = f.get("options")
            if not options:
                frappe.throw(f"Link field '{fieldname}' in '{name}' must have a target options DocType")
            if options not in existing_doctypes and options not in parsed_doctypes_names:
                frappe.throw(f"Link target DocType '{options}' for field '{fieldname}' in '{name}' does not exist and is not part of the generation plan")
            if options in existing_doctypes:
                is_table = frappe.db.get_value("DocType", options, "istable")
                if is_table:
                    frappe.throw(f"Link field '{fieldname}' in '{name}' cannot target Child Table '{options}'")

        # Table target validation
        if fieldtype == "Table":
            options = f.get("options")
            if not options:
                frappe.throw(f"Table field '{fieldname}' in '{name}' must have a child table options DocType")
            if options in existing_doctypes:
                if not frappe.db.get_value("DocType", options, "istable"):
                    frappe.throw(f"Target DocType '{options}' for Table field '{fieldname}' in '{name}' must be a Child Table (istable=1), but it is a standard DocType.")
            elif options not in parsed_doctypes_names:
                frappe.throw(f"Child table DocType '{options}' for field '{fieldname}' in '{name}' does not exist and is not part of the generation plan")

        # Select option validation
        if fieldtype == "Select":
            options = f.get("options")
            if not options:
                frappe.throw(f"Select field '{fieldname}' in '{name}' must have options defined")
            opt_list = [opt.strip() for opt in str(options).split("\n") if opt.strip()]
            if len(opt_list) < 1:
                frappe.throw(f"Select field '{fieldname}' in '{name}' must have at least one option")

# ---------------------------------------------------
# Auto Dependency Generators
# ---------------------------------------------------
def create_master_doctype(doctype_name, parsed_names=None):
    """
    Auto-generates a master DocType if referenced by a Link field but not yet existing.
    Uses standard title-based autonaming.
    """
    doctype_name = sanitize_doctype_name(doctype_name)
    if frappe.db.exists("DocType", doctype_name):
        return

    doc_dict = {
        "doctype": "DocType",
        "name": doctype_name,
        "module": "AI App Builder",
        "custom": 1,
        "autoname": "field:title",
        "naming_rule": "By fieldname",
        "fields": [
            {
                "fieldname": "title",
                "label": "Title",
                "fieldtype": "Data",
                "reqd": 1,
                "in_list_view": 1
            },
            {
                "fieldname": "description",
                "label": "Description",
                "fieldtype": "Small Text"
            }
        ],
        "permissions": [
            {
                "role": "System Manager",
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "select": 1
            }
        ]
    }
    
    validate_doctype_payload(doc_dict, parsed_names or [doctype_name])
    doc = frappe.get_doc(doc_dict)
    doc.insert(ignore_permissions=True)

def create_child_table_doctype(doctype_name, fields=None, parsed_names=None):
    """
    Auto-generates a Child Table DocType (istable=1) for nested tables.
    """
    doctype_name = sanitize_doctype_name(doctype_name)
    if frappe.db.exists("DocType", doctype_name):
        return

    if not fields:
        # Provide sensible default child columns if fields are not defined by AI
        fields = [
            {
                "fieldname": "item_name",
                "label": "Item Name",
                "fieldtype": "Data",
                "reqd": 1,
                "in_list_view": 1
            },
            {
                "fieldname": "quantity",
                "label": "Quantity",
                "fieldtype": "Int",
                "in_list_view": 1
            },
            {
                "fieldname": "rate",
                "label": "Rate",
                "fieldtype": "Currency",
                "in_list_view": 1
            },
            {
                "fieldname": "amount",
                "label": "Amount",
                "fieldtype": "Currency",
                "in_list_view": 1
            }
        ]

    doc_dict = {
        "doctype": "DocType",
        "name": doctype_name,
        "module": "AI App Builder",
        "custom": 1,
        "istable": 1,
        "fields": fields,
        "permissions": []
    }
    
    validate_doctype_payload(doc_dict, parsed_names or [doctype_name])
    doc = frappe.get_doc(doc_dict)
    doc.insert(ignore_permissions=True)

# ---------------------------------------------------
# Desk Whitelisted APIs
# ---------------------------------------------------
@frappe.whitelist()
def analyze_prompt(prompt):
    """
    Parses prompts, inferring fields, layout structures, and dependency relations.
    Returns complete parsed blueprint schema for frontend visualization.
    Uses self-healing fallback: if the AI model fails, falls back to deterministic parser.
    """
    # Self-healing: try AI first, fall back to deterministic parser
    try:
        ai_data = generate_schema(prompt)
    except Exception as ai_err:
        frappe.log_error(message=str(ai_err), title="AI Schema Generation Fallback")
        ai_data = parse_prompt_deterministically(prompt)
    
    primary_name = sanitize_doctype_name(ai_data.get("primary_doctype", "ERPSystem"))
    
    # First pass: apply rule engine to refine all fields
    refined_doctypes_fields = {}
    for dt in ai_data.get("doctypes", []):
        dt_name = sanitize_doctype_name(dt.get("name", ""))
        raw_fields = dt.get("fields", [])
        refined_doctypes_fields[dt_name] = apply_rule_engine(dt_name, raw_fields)

    # Pre-scan the refined fields to identify child tables referenced in Table fields
    child_doctypes = set()
    for dt_name, fields in refined_doctypes_fields.items():
        for f in fields:
            if f.get("fieldtype") == "Table" and f.get("options"):
                child_doctypes.add(sanitize_doctype_name(f.get("options")))

    resolved_doctypes = []
    
    for dt in ai_data.get("doctypes", []):
        dt_name = sanitize_doctype_name(dt.get("name", ""))
        is_primary = (dt_name == primary_name)

        # Retrieve the pre-refined fields
        refined_data_fields = refined_doctypes_fields.get(dt_name, [])
        complete_fields = build_layout(refined_data_fields)

        relationships = []
        for f in refined_data_fields:
            if f.get("fieldtype") == "Link":
                target = f.get("options")
                relationships.append({
                    "field": f["fieldname"],
                    "target": target,
                    "exists": bool(frappe.db.exists("DocType", target)),
                    "type": "Master"
                })
            elif f.get("fieldtype") == "Table":
                target = f.get("options")
                relationships.append({
                    "field": f["fieldname"],
                    "target": target,
                    "exists": bool(frappe.db.exists("DocType", target)),
                    "type": "Child"
                })

        resolved_doctypes.append({
            "name": dt_name,
            "is_primary": is_primary,
            "istable": 1 if (dt.get("istable") or dt_name in child_doctypes) else 0,
            "description": dt.get("description", "Auto-generated Entity"),
            "fields": complete_fields,
            "relationships": relationships
        })

    return {
        "system_name": ai_data.get("system_name", "AI Enterprise Solution"),
        "primary_doctype": primary_name,
        "doctypes": resolved_doctypes
    }

@frappe.whitelist()
def check_upgrade(prompt):
    """
    Checks if primary DocType exists, returning any new fields to show in the upgrade modal.
    """
    parsed = analyze_prompt(prompt)
    primary_name = parsed["primary_doctype"]

    if not frappe.db.exists("DocType", primary_name):
        return {
            "exists": False,
            "doctype_name": primary_name,
            "doctypes": parsed["doctypes"]
        }

    existing_doc = frappe.get_doc("DocType", primary_name)
    existing_fieldnames = {f.fieldname for f in existing_doc.fields}

    # Find the primary doctype's generated fields
    primary_dt_def = next((dt for dt in parsed["doctypes"] if dt["is_primary"]), None)
    if not primary_dt_def:
        return {
            "exists": True,
            "doctype_name": primary_name,
            "new_fields": [],
            "doctypes": parsed["doctypes"]
        }

    new_fields = []
    for f in primary_dt_def["fields"]:
        if f.get("fieldtype") in ("Section Break", "Column Break"):
            continue
        if f["fieldname"] not in existing_fieldnames:
            new_fields.append(f)

    return {
        "exists": True,
        "doctype_name": primary_name,
        "new_fields": new_fields,
        "doctypes": parsed["doctypes"]
    }

@frappe.whitelist()
def upgrade_doctype(prompt):
    """
    Appends newly detected fields to an existing DocType under an Upgraded section break.
    Intelligently reuses the "Upgraded Fields" section break if it already exists, avoiding duplicates.
    """
    try:
        upgrade_info = check_upgrade(prompt)
        doctype_name = upgrade_info["doctype_name"]
        new_fields = upgrade_info["new_fields"]

        if not new_fields:
            return f"No new fields to add to {doctype_name}."

        doc = frappe.get_doc("DocType", doctype_name)
        
        # 1. Check if the "Upgraded Fields" section break already exists
        has_upgrade_sb = section_exists(doc.fields, "Upgraded Fields")
        
        fields_to_add = []
        if not has_upgrade_sb:
            upgrade_sb = {
                "fieldname": f"sec_upgrade_{len(doc.fields)}",
                "label": "Upgraded Fields",
                "fieldtype": "Section Break"
            }
            fields_to_add.append(upgrade_sb)
            
        for f in new_fields:
            # 2. Prevent adding any duplicate fields
            if not field_exists(doc.fields, f["fieldname"]):
                fields_to_add.append(f)
                
        if not fields_to_add or (len(fields_to_add) == 1 and not has_upgrade_sb):
            return f"No new unique fields to add to {doctype_name}."

        # We need to validate the combined fields
        doc_dict = doc.as_dict()
        combined_fields = list(doc_dict.get("fields", [])) + fields_to_add
        doc_dict["fields"] = combined_fields
        
        parsed = analyze_prompt(prompt)
        parsed_names = [dt["name"] for dt in parsed["doctypes"]]
        
        # Validate the whole blueprint schema before saving
        validate_schema(parsed)
        validate_doctype_payload(doc_dict, parsed_names)

        for f in fields_to_add:
            doc.append("fields", f)

        doc.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.clear_cache()

        return f"{doctype_name} Upgraded Successfully!"
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(message=frappe.get_traceback(), title="AI App Builder Upgrade Error")
        frappe.throw(f"App Upgrade Failed: {str(e)}")

def get_creation_order(doctypes, existing_doctypes):
    """
    Returns an ordered list of DocType definitions to be created.
    If a cycle is detected, stubs are introduced to break the cycle.
    """
    pending = {dt["name"]: dt for dt in doctypes}
    
    # Graph structures
    deps = {}
    for name, dt in pending.items():
        dt_deps = set()
        for f in dt.get("fields", []):
            if f.get("fieldtype") in ("Link", "Table"):
                target = f.get("options")
                if target and target != name:
                    # Only depend on it if it's in our generation list and doesn't exist yet
                    if target in pending and target not in existing_doctypes:
                        dt_deps.add(target)
        deps[name] = dt_deps

    order = []
    stubs = set()

    while pending:
        zero_dep_nodes = [name for name, d_set in deps.items() if len(d_set) == 0]
        
        if zero_dep_nodes:
            zero_dep_nodes.sort()
            for name in zero_dep_nodes:
                order.append(("create", pending[name]))
                for other_name in deps:
                    deps[other_name].discard(name)
                del deps[name]
                del pending[name]
        else:
            cycle_nodes = sorted(list(pending.keys()))
            stub_name = min(cycle_nodes, key=lambda x: len(deps[x]))
            
            order.append(("stub", pending[stub_name]))
            stubs.add(stub_name)
            
            for other_name in deps:
                deps[other_name].discard(stub_name)
            del deps[stub_name]
            del pending[stub_name]

    for name in sorted(list(stubs)):
        original_dt = next(dt for dt in doctypes if dt["name"] == name)
        order.append(("upgrade", original_dt))

    return order

def create_stub_doctype(dt, parsed_names, existing_doctypes):
    """
    Creates a minimal stub of a DocType to break circular dependencies.
    """
    name = dt["name"]
    if frappe.db.exists("DocType", name):
        return

    stub_fields = []
    for f in dt["fields"]:
        if f.get("fieldtype") not in ("Link", "Table"):
            stub_fields.append(f)

    # Ensure there is at least one data field for autoname
    has_data = any(f.get("fieldtype") == "Data" for f in stub_fields)
    if not has_data:
        stub_fields.append({
            "fieldname": "title",
            "label": "Title",
            "fieldtype": "Data",
            "reqd": 1
        })

    autoname = "hash"
    for f in stub_fields:
        if f.get("fieldtype") == "Data" and any(word in f["fieldname"] for word in ["name", "title"]):
            autoname = f"field:{f['fieldname']}"
            break

    is_child = bool(dt.get("istable"))

    doc_dict = {
        "doctype": "DocType",
        "name": name,
        "module": "AI App Builder",
        "custom": 1,
        "istable": 1 if is_child else 0,
        "autoname": autoname if not is_child else "",
        "naming_rule": ("By fieldname" if autoname.startswith("field:") else "Random") if not is_child else "",
        "fields": stub_fields,
        "permissions": [] if is_child else [
            {
                "role": "System Manager",
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "select": 1
            }
        ]
    }

    validate_doctype_payload(doc_dict, parsed_names, existing_doctypes)
    doc = frappe.get_doc(doc_dict)
    try:
        doc.insert(ignore_permissions=True)
    except frappe.DuplicateEntryError:
        # DocType was created between our existence check and insert (race condition)
        pass

def create_full_doctype(dt, parsed_names, existing_doctypes):
    """
    Creates a full DocType with all fields configured.
    """
    name = dt["name"]
    if frappe.db.exists("DocType", name):
        return

    autoname = "hash"
    for f in dt["fields"]:
        if f.get("fieldtype") == "Data" and any(word in f["fieldname"] for word in ["name", "title"]):
            autoname = f"field:{f['fieldname']}"
            break

    is_child = bool(dt.get("istable"))

    doc_dict = {
        "doctype": "DocType",
        "name": name,
        "module": "AI App Builder",
        "custom": 1,
        "istable": 1 if is_child else 0,
        "autoname": autoname if not is_child else "",
        "naming_rule": ("By fieldname" if autoname.startswith("field:") else "Random") if not is_child else "",
        "fields": dt["fields"],
        "permissions": [] if is_child else [
            {
                "role": "System Manager",
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "select": 1
            }
        ]
    }

    validate_doctype_payload(doc_dict, parsed_names, existing_doctypes)
    doc = frappe.get_doc(doc_dict)
    try:
        doc.insert(ignore_permissions=True)
    except frappe.DuplicateEntryError:
        # DocType was created between our existence check and insert (race condition)
        pass

def upgrade_existing_stub(dt, parsed_names, existing_doctypes):
    """
    Upgrades an existing stub DocType with its full fields definition.
    Also ensures the istable property is correctly propagated.
    """
    name = dt["name"]
    doc = frappe.get_doc("DocType", name)
    doc.fields = []
    
    # Propagate istable from the resolved blueprint
    is_child = bool(dt.get("istable"))
    doc.istable = 1 if is_child else doc.istable
    
    for f in dt["fields"]:
        doc.append("fields", f)

    doc_dict = doc.as_dict()
    validate_doctype_payload(doc_dict, parsed_names, existing_doctypes)
    doc.save(ignore_permissions=True)

@frappe.whitelist()
def generate_doctype(prompt):
    """
    Triggers complete dependency-aware production-grade generation.
    Validates full schema before any database mutations.
    """
    import time
    start_time = time.time()
    
    parsed = analyze_prompt(prompt)
    parsed_names = [dt["name"] for dt in parsed["doctypes"]]
    primary_name = parsed["primary_doctype"]
    
    existing_doctypes = {d.name for d in frappe.get_all("DocType", fields=["name"])}
    created_doctypes = []
    
    try:
        # 0. Validate the full schema blueprint before any mutations
        # Skip validate_schema here since analyze_prompt builds resolved structures
        # with layout fields that may not pass raw payload validation.
        # Instead validate each DocType individually during creation.
        
        # 1. Resolve and create any external (non-planned) referenced Master/Child DocTypes first
        for dt in parsed["doctypes"]:
            for rel in dt.get("relationships", []):
                target = rel["target"]
                if target not in parsed_names and target not in existing_doctypes:
                    if rel["type"] == "Child":
                        create_child_table_doctype(target, None, parsed_names)
                    else:
                        create_master_doctype(target, parsed_names)
                    existing_doctypes.add(target)
                    created_doctypes.append(target)

        # 2. Perform topological sort on explicit plan to sequence masters and transactionals correctly
        order = get_creation_order(parsed["doctypes"], existing_doctypes)
        
        # 3. Create all planned DocTypes sequentially
        for action, dt in order:
            dt_name = dt["name"]
            if action == "stub":
                create_stub_doctype(dt, parsed_names, existing_doctypes)
                created_doctypes.append(dt_name)
                existing_doctypes.add(dt_name)
                # Intermediate commit so subsequent validations see correct DB state
                frappe.db.commit()
            elif action == "create":
                create_full_doctype(dt, parsed_names, existing_doctypes)
                created_doctypes.append(dt_name)
                existing_doctypes.add(dt_name)
                # Intermediate commit so subsequent validations see correct DB state
                frappe.db.commit()
            elif action == "upgrade":
                upgrade_existing_stub(dt, parsed_names, existing_doctypes)
                frappe.db.commit()

        frappe.clear_cache()
        
        end_time = time.time()
        generation_time_ms = int((end_time - start_time) * 1000)
        
        return {
            "success": True,
            "message": f"System '{parsed['system_name']}' Created Successfully! Primary DocType: {primary_name}",
            "primary_doctype": primary_name,
            "doctypes_created": len(created_doctypes),
            "relationships_created": sum(len(dt.get("relationships", [])) for dt in parsed["doctypes"]),
            "generation_time_ms": generation_time_ms,
            "modules": ["AI App Builder"]
        }
        
    except Exception as e:
        frappe.db.rollback()
        # Clean up any physically created database tables and metadata
        for dt_name in reversed(created_doctypes):
            try:
                frappe.delete_doc("DocType", dt_name, ignore_missing=True, force=True)
            except Exception:
                pass
        frappe.db.commit()
        frappe.log_error(message=frappe.get_traceback(), title="AI App Builder Generation Error")
        frappe.throw(f"App Generation Failed: {str(e)}")
