from openai import OpenAI
import json
import time
import re
import sys
import os
import frappe

# ---------------------------------------------------
# OpenRouter Client Setup
# ---------------------------------------------------
# OpenRouter Base URL and pre-configured free API key
api_key = (
    frappe.conf.get("openrouter_api_key")
    or os.environ.get("OPENROUTER_API_KEY")
    or "sk-or-v1-placeholder-please-set-in-common-site-config-json"
)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
    )

# Ordered list of free models for fallback failover orchestration
FREE_MODELS = [
    "openrouter/free",
    "deepseek/deepseek-v4-flash:free",
    "qwen/qwen3-coder:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-4-31b-it:free"
]

# ---------------------------------------------------
# JSON Recovery and Cleanup Helper
# ---------------------------------------------------
def clean_and_parse_json(text):
    """
    Cleans raw LLM outputs, strips markdown code blocks, extracts JSON
    substrings using regex, and performs structural recovery if needed.
    """
    if not text:
        raise ValueError("Empty response received from LLM.")

    # Remove markdown formatting markers if present
    cleaned = text.strip()
    cleaned = re.sub(r'^```json\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'^```\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*```$', '', cleaned)

    try:
        # Standard parsing first
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback regex extraction: find the outermost curly braces
        match = re.search(r'(\{.*\})', cleaned, re.DOTALL)
        if match:
            extracted_json = match.group(1).strip()
            try:
                return json.loads(extracted_json)
            except json.JSONDecodeError as e:
                # Basic bracket balancer recovery
                open_braces = extracted_json.count('{')
                close_braces = extracted_json.count('}')
                if open_braces > close_braces:
                    extracted_json += '}' * (open_braces - close_braces)
                try:
                    return json.loads(extracted_json)
                except json.JSONDecodeError:
                    pass
                raise ValueError(f"Extracted JSON substring remains malformed: {e}\nRaw segment: {extracted_json}")
        raise ValueError("No JSON block or curly braces found in the LLM response.")

# ---------------------------------------------------
# Orchestration AI Schema Generator
# ---------------------------------------------------
def generate_schema(prompt):
    """
    Generates a structured multi-DocType system schema from a natural language prompt.
    Uses free OpenRouter models with robust fallback, timeouts, retries, and JSON recovery.
    """
    system_prompt = """You are an expert ERP and database architect specialized in the Frappe Framework.
Analyze the user's business system requirements and design a highly professional, connected relational schema.

Allowed fieldtypes in Frappe:
- Data (short text inputs, codes, identifiers, tracking numbers)
- Currency (for monetary amounts, e.g. salary, cost, price, fees, budget)
- Date (for calendar dates, e.g. birthday, appointment date, joining date)
- Link (for foreign key relationships. The linked DocType must be passed in the 'options' field)
- Select (dropdown choices. List options in the 'options' field separated by newlines, e.g., 'Active\\nInactive')
- Attach (for files, reports, proof, images, attachments)
- Check (for boolean switches, e.g. active, has_license, standard)
- Small Text (multi-line notes, remarks, description, address)
- Int (for integer numbers, e.g. age, quantity, count, score)
- Table (for Child Tables / one-to-many items. The target Child Table DocType must be passed in 'options')

DocType Properties:
- "istable": Set to 1 for Child Table DocTypes (embedded inside a parent via a Table field). Set to 0 for standard standalone DocTypes.
  Child Table DocTypes (istable=1) do NOT appear independently; they are always embedded in a parent DocType through a Table field.
  Standard DocTypes (istable=0) have their own list view and form view.

CRITICAL Rules:
- When the user mentions a "child table of X" or "items in Y", you MUST create a Child Table DocType with "istable": 1 AND add a Table field in the parent DocType with "options" pointing to it.
- When the user mentions simple attributes to "track" or "manage" (e.g. "track Delivery Address and Shipment Tracking"), add those as FIELDS on the relevant DocType. Do NOT create separate DocTypes for simple attributes like addresses, tracking numbers, or status fields.
- Every DocType MUST include the "istable" property (either 0 or 1).

Instructions:
1. Identify the 'system_name' (e.g. 'Hospital Management System').
2. Identify the main or 'primary_doctype' (e.g. 'Appointment' or 'Employee' or 'Book Issue').
3. Produce a cohesive set of related DocTypes under the 'doctypes' list.
4. For each DocType, set "istable": 1 if it is a Child Table, otherwise set "istable": 0.
5. For multi-DocType prompts (e.g., 'Hospital Management System'), list ALL core entities: Patient, Doctor, Appointment, Billing, Prescription.
6. For simpler prompts (e.g., 'Create employee management system with name, department, salary'), output the primary DocType (e.g. Employee) and identify related Master DocTypes (e.g. Department) or Child Tables that will enrich the system.
7. For each field:
   - Provide a clear, professional 'label' (e.g. 'Employee Name', 'Salary').
   - Provide a logical 'fieldtype' from the allowed list.
   - For Link and Table fields, set 'options' to the target DocType name. Ensure it is title-cased and represents a related entity.
8. Return ONLY a valid JSON object matching the schema below. Do not output any markdown wrappers, conversational text, or explanations.

Example JSON Output:
{
  "system_name": "Hospital Management",
  "primary_doctype": "Patient",
  "doctypes": [
    {
      "name": "Patient",
      "istable": 0,
      "description": "Patient information master",
      "fields": [
        {
          "label": "Full Name",
          "fieldtype": "Data"
        },
        {
          "label": "Age",
          "fieldtype": "Int"
        },
        {
          "label": "Date of Birth",
          "fieldtype": "Date"
        },
        {
          "label": "Prescriptions",
          "fieldtype": "Table",
          "options": "PrescriptionItem"
        },
        {
          "label": "Remarks",
          "fieldtype": "Small Text"
        }
      ]
    },
    {
      "name": "PrescriptionItem",
      "istable": 1,
      "description": "Child table for patient prescriptions",
      "fields": [
        {
          "label": "Medicine Name",
          "fieldtype": "Data"
        },
        {
          "label": "Dosage",
          "fieldtype": "Data"
        },
        {
          "label": "Quantity",
          "fieldtype": "Int"
        }
      ]
    }
  ]
}
"""

    user_content = f"Design a complete ERP system for: {prompt}"

    last_exception = None

    for model in FREE_MODELS:
        # Try each model up to 3 times with exponential backoff on retriable errors
        for retry in range(3):
            try:
                # 15 seconds strict timeout
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.1,  # Highly deterministic responses
                    timeout=15.0
                )

                if not response.choices or not response.choices[0].message.content:
                    raise ValueError(f"Empty response from model {model}")

                text = response.choices[0].message.content
                data = clean_and_parse_json(text)

                # Post-validation to ensure minimal fields exist
                if not data.get("doctypes") or not data.get("primary_doctype"):
                    raise ValueError("JSON parsed successfully but is missing required system structure keys.")

                return data

            except Exception as e:
                last_exception = e
                # Wait briefly before retrying
                time.sleep(1.5 * (retry + 1))
                continue

    # If all models and retries fail, raise a descriptive exception
    raise RuntimeError(f"All free OpenRouter models failed to generate a valid schema. Last error: {last_exception}")
