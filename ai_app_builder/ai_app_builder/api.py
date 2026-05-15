import frappe
import re

from ai_app_builder.ai_app_builder.gemini_helper import generate_schema


# ---------------------------------------------------
# Smart Field Creator
# ---------------------------------------------------

def create_field(label):

    fieldname = label.lower().replace(" ", "_")

    label_lower = label.lower()

    fieldtype = "Data"

    options = ""

    # ---------------------------------------------------
    # AI Rule Engine
    # ---------------------------------------------------

    if any(word in label_lower for word in [
        "amount",
        "salary",
        "price",
        "cost",
        "fee",
        "payment"
    ]):

        fieldtype = "Currency"

    elif "date" in label_lower:

        fieldtype = "Date"

    elif any(word in label_lower for word in [
        "report",
        "document",
        "attachment",
        "file",
        "proof"
    ]):

        fieldtype = "Attach"

    elif any(word in label_lower for word in [
        "status",
        "severity",
        "priority",
        "type",
        "category"
    ]):

        fieldtype = "Select"

        options = "Low\nMedium\nHigh"

    elif any(word in label_lower for word in [
        "is ",
        "has ",
        "enable",
        "active",
        "critical"
    ]):

        fieldtype = "Check"

    elif any(word in label_lower for word in [
        "description",
        "remarks",
        "notes",
        "address",
        "condition"
    ]):

        fieldtype = "Small Text"

    elif any(word in label_lower for word in [
        "age",
        "count",
        "quantity",
        "number"
    ]):

        fieldtype = "Int"

    elif any(word in label_lower for word in [
        "items",
        "products",
        "entries"
    ]):

        fieldtype = "Table"

    elif label_lower in [
        "customer",
        "employee",
        "student",
        "teacher",
        "doctor",
        "patient",
        "department",
        "manager",
        "supplier",
        "vendor"
    ]:

        fieldtype = "Link"

        options = label.title()
    field = {
        "fieldname": fieldname,
        "label": label.title(),
        "fieldtype": fieldtype
    }

    if options:
        field["options"] = options

    return field


# ---------------------------------------------------
# Prompt Parser
# ---------------------------------------------------

def parse_prompt(prompt):

    prompt = prompt.lower()

    match = re.search(r'create (.+?) with', prompt)

    if match:

        doctype_name = match.group(1).strip()

    else:

        match = re.search(r'create (.+)', prompt)

        if not match:

            return {
                "error": "Could not understand prompt"
            }

        doctype_name = match.group(1).strip()

    doctype_name = doctype_name.title()

    doctype_name = doctype_name.replace(" App", "")
    doctype_name = doctype_name.replace(" System", "")

    fields = []

    used_fieldnames = set()

    field_match = re.search(r'with (.+)', prompt)

    if field_match:

        field_text = field_match.group(1)

        sections = re.split(r'and', field_text)

        for section in sections:

            section = section.strip()

            # ---------------------------------------------------
            # Personal Details Section
            # ---------------------------------------------------

            if "personal details" in section:

                fields.append({
                    "fieldname": "personal_details_section",
                    "label": "Personal Details",
                    "fieldtype": "Section Break"
                })

                section = section.replace("personal details like", "")

            # ---------------------------------------------------
            # Work Details Section
            # ---------------------------------------------------

            elif "work details" in section:

                fields.append({
                    "fieldname": "work_details_section",
                    "label": "Work Details",
                    "fieldtype": "Section Break"
                })

                section = section.replace("work details like", "")

            # ---------------------------------------------------
            # AI Schema Detection
            # ---------------------------------------------------

            ai_response = generate_schema(section)

            ai_fields = ai_response.get("fields", [])

            field_counter = 0

            for ai_field in ai_fields:

                label = ai_field.get("label", "").strip()

                ai_fieldtype = ai_field.get("fieldtype", "Data")

                field_dict = create_field(label)

                if not field_dict:
                    continue

                if field_dict["fieldtype"] == "Data":

                    field_dict["fieldtype"] = ai_fieldtype

                fieldname = field_dict.get("fieldname")

                # ---------------------------------------------------
                # Duplicate Prevention
                # ---------------------------------------------------

                if fieldname in used_fieldnames:
                    continue

                used_fieldnames.add(fieldname)

                fields.append(field_dict)

                field_counter += 1

                # ---------------------------------------------------
                # Smart Layout Engine
                # ---------------------------------------------------

                if field_counter % 2 == 0:

                    fields.append({
                        "fieldname": f"column_break_{len(fields)}",
                        "fieldtype": "Column Break"
                    })

                if field_counter % 4 == 0:

                    fields.append({
                        "fieldname": f"section_break_{len(fields)}",
                        "fieldtype": "Section Break"
                    })

    return {
        "doctype_name": doctype_name,
        "fields": fields
    }


# ---------------------------------------------------
# Analyze Prompt
# ---------------------------------------------------

@frappe.whitelist()

def analyze_prompt(prompt):

    return parse_prompt(prompt)
# ---------------------------------------------------
# Generate DocType
# ---------------------------------------------------

@frappe.whitelist()

def generate_doctype(prompt):

    parsed = parse_prompt(prompt)

    doctype_name = parsed["doctype_name"]

    fields = parsed["fields"]

    # ---------------------------------------------------
    # Auto Create Missing Linked DocTypes
    # ---------------------------------------------------

    for field in fields:

        if field.get("fieldtype") == "Link":

            options = field.get("options")

            if options:

                if not frappe.db.exists("DocType", options):

                    link_doc = frappe.get_doc({
                        "doctype": "DocType",
                        "name": options,
                        "module": "AI App Builder",
                        "custom": 1,
                        "fields": [
                            {
                                "fieldname": "title",
                                "label": "Title",
                                "fieldtype": "Data"
                            }
                        ]
                    })

                    link_doc.insert(ignore_permissions=True)

                    frappe.db.commit()

    # ---------------------------------------------------
    # Prevent Duplicate Main DocType
    # ---------------------------------------------------

    if frappe.db.exists("DocType", doctype_name):

        return f"{doctype_name} already exists"

    # ---------------------------------------------------
    # Create Main DocType
    # ---------------------------------------------------

    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": doctype_name,
        "module": "AI App Builder",
        "custom": 1,
        "fields": fields
    })

    doc.insert(ignore_permissions=True)

    frappe.db.commit()

    return f"{doctype_name} Created Successfully"


# ---------------------------------------------------
# Check Upgrade
# ---------------------------------------------------

@frappe.whitelist()

def check_upgrade(prompt):

    parsed = parse_prompt(prompt)

    doctype_name = parsed["doctype_name"]

    fields = parsed["fields"]

    if not frappe.db.exists("DocType", doctype_name):

        return {
            "exists": False
        }

    existing_doc = frappe.get_doc("DocType", doctype_name)

    existing_fields = [
        field.fieldname
        for field in existing_doc.fields
    ]

    new_fields = []

    for field in fields:

        if field.get("fieldtype") in [
            "Section Break",
            "Column Break"
        ]:
            continue

        if field["fieldname"] not in existing_fields:

            new_fields.append(field)

    return {
        "exists": True,
        "doctype_name": doctype_name,
        "new_fields": new_fields
    }


# ---------------------------------------------------
# Upgrade Existing DocType
# ---------------------------------------------------

@frappe.whitelist()

def upgrade_doctype(prompt):

    parsed = parse_prompt(prompt)

    doctype_name = parsed["doctype_name"]

    fields = parsed["fields"]

    doc = frappe.get_doc("DocType", doctype_name)

    existing_fields = [
        field.fieldname
        for field in doc.fields
    ]

    for field in fields:

        if field.get("fieldtype") in [
            "Section Break",
            "Column Break"
        ]:
            continue

        if field["fieldname"] in existing_fields:

            continue


        doc.append("fields", field)

    doc.save(ignore_permissions=True)

    frappe.db.commit()

    return f"{doctype_name} upgraded successfully"
