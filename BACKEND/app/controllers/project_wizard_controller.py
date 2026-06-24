import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.models.project_wizard import ProjectWizardModel
from app.models.database import db
from app.utils.encryption import encrypt_value, decrypt_value

def clean(value):
    if value == "" or value is None:
        return None
    return value


project_wizard_bp = Blueprint("project_wizard_bp", __name__)

# =========================
# File Upload Configuration
# =========================
UPLOAD_FOLDER = "uploads/project_documents"
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, subfolder=""):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        folder_path = os.path.join(UPLOAD_FOLDER, subfolder)
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, filename)
        file.save(file_path)
        return file_path
    return None


# =========================
# CREATE PROJECT REGISTRATION
# =========================
@project_wizard_bp.route("/project-registration-wizard", methods=["POST", "OPTIONS"])
def create_project_registration():
    
    # Handle OPTIONS request for CORS preflight
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    # Accept both JSON and multipart/form-data
    data = request.form.to_dict() if request.form else request.json or {}

    # Validate required fields
    required_fields = [
        "applicationNo", "panNumber", "bankState", "bankName", "accountNo",
        "accountHolder", "ifsc", "name", "fatherName", "aadhaar", "mobile", "email"
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    # =========================
    # Handle File Uploads
    # =========================
    uploaded_files = {}

    file_fields = {
        "bankStatementFile": "bank_statement_file",
        "panFile": "pan_file",
        "aadhaarFile": "aadhaar_file",
        "photographFile": "photograph_file",
        "licenseCertificateFile": "license_certificate_file",
        "gstDocumentFile": "gst_document_file",
        "selfAffidavit": "self_affidavit_file",
        "promoter2DocumentsFile": "promoter2_documents_file",
        "itrDocumentsFile": "itr_documents_file",
        "balanceSheetFile": "balance_sheet_file",
    }

    for form_field, db_column in file_fields.items():
        file = request.files.get(form_field)
        if file:
            saved_path = save_file(file, data.get("applicationNo", "general"))
            uploaded_files[db_column] = saved_path

    # =========================
    # Map Frontend → DB Fields
    # =========================
    mapped_data = {
        "application_no": data.get("applicationNo"),
        "promoter_type": data.get("promoterType", "individual"),
        "pan_number": encrypt_value(data.get("panNumber")),
        "bank_state": data.get("bankState"),
        "bank_name": data.get("bankName"),
        "branch_name": data.get("branchName"),
        "account_no": encrypt_value(data.get("accountNo")),
        "account_holder": data.get("accountHolder"),
        "ifsc": encrypt_value(data.get("ifsc")),
        "name": data.get("name"),
        "father_name": data.get("fatherName"),
        "aadhaar": encrypt_value(data.get("aadhaar")),
        "mobile": encrypt_value(data.get("mobile")),
        "landline": data.get("landline"),
        "email": encrypt_value(data.get("email")),
        "promoter_website": data.get("promoterWebsite"),
        "state_ut": data.get("stateUT"),
        "district": data.get("district"),
        "license_no": data.get("licenseNo"),
        "license_date": clean(data.get("licenseDate")),
        "gst_num": data.get("gstNum"),
        "other_state_reg": data.get("otherStateReg"),
        "rera_reg_number": data.get("reraRegNumber"),
        "rera_state": data.get("reraState"),
        "registration_revoked": data.get("registrationRevoked"),
        "last_five_years": data.get("lastFiveYears"),
        "project_name": data.get("projectName"),
        "project_type": data.get("projectType"),
        "current_status": data.get("currentStatus"),
        "project_address": data.get("projectAddress"),
        "project_state_ut": data.get("projectStateUT"),
        "project_district": data.get("projectDistrict"),
        "pin_code": data.get("pinCode"),
        "survey_no": data.get("surveyNo"),
        "litigation": data.get("litigation"),
        "case_no": data.get("caseNo"),
        "tribunal_place": data.get("tribunalPlace"),
        "petitioner_name": data.get("petitionerName"),
        "respondent_name": data.get("respondentName"),
        "case_facts": data.get("caseFacts"),
        "case_status": data.get("caseStatus"),
        "interim_order": data.get("interimOrder"),
        "final_order_details": data.get("finalOrderDetails"),
        "promoter2": data.get("promoter2"),
        "promoter2_is_organization": data.get("promoter2IsOrganization"),
        "promoter2_is_indian": data.get("promoter2IsIndian"),
        "promoter2_name": data.get("promoter2Name"),
        "promoter2_address_line1": data.get("promoter2AddressLine1"),
        "promoter2_address_line2": data.get("promoter2AddressLine2"),
        "promoter2_mobile": encrypt_value(data.get("promoter2Mobile")) if data.get("promoter2Mobile") else None,
        "promoter2_email": encrypt_value(data.get("promoter2Email")) if data.get("promoter2Email") else None,
        "promoter2_pan_card": encrypt_value(data.get("promoter2PanCard")) if data.get("promoter2PanCard") else None,
    }

    # Merge uploaded file paths into mapped_data
    mapped_data.update(uploaded_files)

    try:
        row = ProjectWizardModel.insert_project(mapped_data)
        return jsonify({
            "id": row.id,
            "application_no": row.application_no,
            "message": "Project registration created successfully"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500


# =========================
# GET ALL REGISTRATIONS
# =========================
@project_wizard_bp.route("/project-registrations", methods=["GET", "OPTIONS"])
def get_project_registrations():
    
    # Handle OPTIONS request for CORS preflight
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        rows = ProjectWizardModel.fetch_all()
        return jsonify([
            {
                "id": r.id,
                "application_no": r.application_no,
                "name": r.name,
                "email": decrypt_value(r.email) if r.email else None,
                "mobile": decrypt_value(r.mobile) if r.mobile else None,
                "pan_number": decrypt_value(r.pan_number) if r.pan_number else None,
                "aadhaar": decrypt_value(r.aadhaar) if r.aadhaar else None,
                "created_at": str(r.created_at)
            } for r in rows
        ])
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


# =========================
# GET BY APPLICATION NO
# =========================
@project_wizard_bp.route("/project-registration/<application_no>", methods=["GET", "OPTIONS"])
def get_project_registration(application_no):
    
    # Handle OPTIONS request for CORS preflight
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        row = ProjectWizardModel.fetch_by_application_no(application_no)
        if not row:
            return jsonify({"error": "Project registration not found"}), 404

        return jsonify({
            "id": row.id,
            "application_no": row.application_no,
            "promoter_type": row.promoter_type,
            "pan_number": decrypt_value(row.pan_number) if row.pan_number else None,
            "bank_state": row.bank_state,
            "bank_name": row.bank_name,
            "branch_name": row.branch_name,
            "account_no": decrypt_value(row.account_no) if row.account_no else None,
            "account_holder": row.account_holder,
            "ifsc": decrypt_value(row.ifsc) if row.ifsc else None,
            "name": row.name,
            "father_name": row.father_name,
            "aadhaar": decrypt_value(row.aadhaar) if row.aadhaar else None,
            "mobile": decrypt_value(row.mobile) if row.mobile else None,
            "landline": row.landline,
            "email": decrypt_value(row.email) if row.email else None,
            "promoter_website": row.promoter_website,
            "state_ut": row.state_ut,
            "district": row.district,
            "license_no": row.license_no,
            "license_date": str(row.license_date) if row.license_date else None,
            "gst_num": row.gst_num,
            "other_state_reg": row.other_state_reg,
            "rera_reg_number": row.rera_reg_number,
            "rera_state": row.rera_state,
            "registration_revoked": row.registration_revoked,
            "last_five_years": row.last_five_years,
            "project_name": row.project_name,
            "project_type": row.project_type,
            "current_status": row.current_status,
            "project_address": row.project_address,
            "project_state_ut": row.project_state_ut,
            "project_district": row.project_district,
            "pin_code": row.pin_code,
            "survey_no": row.survey_no,
            "litigation": row.litigation,
            "case_no": row.case_no,
            "tribunal_place": row.tribunal_place,
            "petitioner_name": row.petitioner_name,
            "respondent_name": row.respondent_name,
            "case_facts": row.case_facts,
            "case_status": row.case_status,
            "interim_order": row.interim_order,
            "final_order_details": row.final_order_details,
            "promoter2": row.promoter2,
            "promoter2_is_organization": row.promoter2_is_organization,
            "promoter2_is_indian": row.promoter2_is_indian,
            "promoter2_name": row.promoter2_name,
            "promoter2_address_line1": row.promoter2_address_line1,
            "promoter2_address_line2": row.promoter2_address_line2,
            "promoter2_mobile": decrypt_value(row.promoter2_mobile) if row.promoter2_mobile else None,
            "promoter2_email": decrypt_value(row.promoter2_email) if row.promoter2_email else None,
            "promoter2_pan_card": decrypt_value(row.promoter2_pan_card) if row.promoter2_pan_card else None,

            # File paths
            "pan_file": row.pan_file,
            "aadhaar_file": row.aadhaar_file,
            "self_affidavit_file": row.self_affidavit_file,

            "created_at": str(row.created_at)
        })
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
 