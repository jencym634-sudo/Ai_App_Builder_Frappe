import frappe
from ai_app_builder.ai_app_builder.api import generate_doctype

def run_e2e_circular_test():
    prompt = "Create hospital system where Patient links to Doctor and Doctor links to Patient, with a child table for Medical Records"
    print(f"Running generate_doctype with prompt: '{prompt}'")
    
    # Run the generation
    res = generate_doctype(prompt)
    print("Generation result:", res)
    
    # Let's inspect the database
    patient_exists = frappe.db.exists("DocType", "Patient")
    doctor_exists = frappe.db.exists("DocType", "Doctor")
    
    print(f"Patient exists: {bool(patient_exists)}")
    print(f"Doctor exists: {bool(doctor_exists)}")
    
    # Cleanup to leave a clean database state
    print("Tearing down generated doctypes...")
    for dt_name in ["Patient", "Doctor", "MedicalRecord", "PatientMedicalRecordItem", "DoctorMedicalRecordItem", "MedicalRecords"]:
        if frappe.db.exists("DocType", dt_name):
            frappe.delete_doc("DocType", dt_name, ignore_missing=True, force=True)
    frappe.db.commit()
    
    assert patient_exists, "Patient DocType should be created"
    assert doctor_exists, "Doctor DocType should be created"
    print("E2E Circular test completed successfully!")

if __name__ == "__main__":
    run_e2e_circular_test()
