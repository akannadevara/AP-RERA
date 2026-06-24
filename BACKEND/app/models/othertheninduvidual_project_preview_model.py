from datetime import datetime
from sqlalchemy import text
from app.models.database import db
import os
import json


from app.models.project_upload_documents import ProjectRegistrationDocument
from app.models.othertheninduvidual_project_registration_model import \
    fetch_othertheninduvidual_project_registration

from app.models.development_details import DevelopmentDetailsModel
from app.models.application_associate import ApplicationAssociate
from app.models.architect import Architect
from app.models.engineer import Engineer
from app.models.accountant import Accountant
from app.models.project_agent import AgentModel
from app.models.project_engineer import ProjectEngineer
from app.models.contractor import Contractor

from app.models.organization_profile_model import (
    get_org_profile,
    get_org_rera_details,
    get_org_members,
    get_past_projects
)


def get_project_registration_basic(application_number):
    row = db.session.execute(text("""
        SELECT
            other_state_reg,
            rera_reg_number,
            rera_state,
            registration_revoked,

            last_five_years,
            project_name,
            project_type,
            current_status,
            project_address,
            project_state_ut,
            project_district,
            pin_code,
            survey_no,

            litigation,
            case_no,
            tribunal_place,
            petitioner_name,
            respondent_name,
            case_facts,
            case_status
        FROM project_registrations
        WHERE application_no = :app
    """), {"app": application_number}).fetchone()

    if not row:
        return {}

    return dict(row._mapping)





# --------------------------------------------------
# MASTER LOOKUPS
# --------------------------------------------------
def get_district_name(district_id):
    if not district_id:
        return "N/A"

    row = db.session.execute(
        text("""
            SELECT district_name
            FROM district_master_t
            WHERE district_id = :id
        """),
        {"id": district_id}
    ).fetchone()

    return row[0] if row else "N/A"


def get_mandal_name(mandal_id):
    if not mandal_id:
        return "N/A"

    row = db.session.execute(
        text("""
            SELECT mandal_name
            FROM mandal_master_t
            WHERE mandal_id = :id
        """),
        {"id": mandal_id}
    ).fetchone()

    return row[0] if row else "N/A"


def get_village_name(village_id):
    if not village_id:
        return "N/A"

    row = db.session.execute(
        text("""
            SELECT village_name
            FROM village_master_t
            WHERE village_id = :id
        """),
        {"id": village_id}
    ).fetchone()

    return row[0] if row else "N/A"


PROJECT_TYPE_MAP = {
    1: "Residential",
    2: "Commercial",
    3: "Mixed Development"
}
# --------------------------------------------------
# CONSULTANCY DETAILS
# --------------------------------------------------
def get_consultancy_details(application_number, pan_number):
    """Fetch consultancy details for the project"""

    if not application_number or not pan_number:
        return {}

    try:
        row = db.session.execute(text("""
            SELECT
                consultancy_name,
                consultant_name,
                mobile_number,
                email_id,
                address
            FROM project_registration_consultant_details
            WHERE application_number = :app
              AND pan_number = :pan
            ORDER BY id DESC
            LIMIT 1
        """), {
            "app": application_number,
            "pan": pan_number
        }).fetchone()

        if not row:
            return {}

        return {
            "consultancy_name": row[0] or "N/A",
            "consultant_name": row[1] or "N/A",
            "mobile": row[2] or "N/A",
            "email": row[3] or "N/A",
            "address": row[4] or "N/A"
        }

    except Exception as e:
        print("Error fetching consultancy details:", e)
        return {}


# --------------------------------------------------
# OTHER DEVELOPMENT WORKS
# --------------------------------------------------
def get_other_development_works(application_number, pan_number):
    """Fetch other external development works"""
    if not application_number or not pan_number:
        return []
    
    try:
        rows = db.session.execute(text("""
            SELECT work_description, work_type
            FROM other_development_works
            WHERE application_number = :app AND pan_number = :pan
        """), {"app": application_number, "pan": pan_number}).fetchall()
        
        return [{"description": r[0], "type": r[1]} for r in rows]
    except Exception as e:
        print(f"Error fetching other development works: {e}")
        return []


# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def format_date(date_val):
    if not date_val:
        return "N/A"
    if isinstance(date_val, str):
        try:
            date_val = datetime.fromisoformat(date_val.replace("Z", ""))
        except Exception:
            return date_val
    return date_val.strftime("%d-%m-%Y")


# --------------------------------------------------
# DOCUMENTS (FINAL FIXED)
# --------------------------------------------------
def map_documents(application_number, pan_number):
    if not application_number or not pan_number:
        return []

    record = ProjectRegistrationDocument.query.filter_by(
        application_number=str(application_number),
        pan_number=str(pan_number)
    ).first()

    print("📄 DOC RECORD FOUND:", record)

    if not record or not record.documents:
        return []

    formatted_docs = []

    for doc_id, file_path in record.documents.items():
        formatted_docs.append({
            "document_name": doc_id,
            "file_path": file_path
        })

    return formatted_docs



# --------------------------------------------------
# PREVIEW BUILDER (FINAL + STABLE)
# --------------------------------------------------
def build_project_preview_data(raw):
    application_id = raw.get("applicationNumber")
    pan_number = raw.get("panNumber")

    # --------------------------------------------------
    # 🔥 ORGANIZATION PROFILE FETCH (FIXED)
    # --------------------------------------------------
    org_profile = get_org_profile(application_id) or {}
    org_rera = get_org_rera_details(application_id) or {}
    org_members = get_org_members(application_id) or []
    past_projects = get_past_projects(application_id) or []


    

    if not application_id or not pan_number:
        return {
            "project_details": {},
            "promoter_details": {},
            "associate_details": {
                "architects": [],
                "engineers": [],
                "accountants": [],
                "agents": [],
                "project_engineers": [],
                "contractors": []
            },
            "development_details": {},
            "project_upload_documents": [],
        }

    registration = fetch_othertheninduvidual_project_registration(
    application_id,
    pan_number)

    if not registration:
        registration = {}
    basic_reg = get_project_registration_basic(application_id)
    

    development = DevelopmentDetailsModel.get_by_application_and_pan(
        application_id, pan_number
    )
    
    if not development:
        development = {}
    else:
        if isinstance(development.get("development_details"), str):
            development["development_details"] = json.loads(
                development["development_details"]
            )
        if isinstance(development.get("external_development_work"), str):
            development["external_development_work"] = json.loads(
            development["external_development_work"]
        )

    documents_data = map_documents(application_id, pan_number)
    
    consultancy = get_consultancy_details(application_id, pan_number)
    other_dev_works = get_other_development_works(application_id, pan_number)

    # ✅ SINGLE associate_details definition
    associate_details = {
        "architects": [],
        "engineers": [],
        "accountants": [],
        "agents": [],
        "project_engineers": [],
        "contractors": []
    }

    associates = ApplicationAssociate.query.filter_by(
        application_number=application_id,
        pan_number=pan_number
    ).all()

    # ✅ SINGLE loop
    for a in associates:
        atype = (a.associate_type or "").lower()
        print("🔍 ASSOCIATE TYPE:", atype, "ID:", a.associate_id)

        if atype == "agent":
            ag = AgentModel.query.get(a.associate_id)
            if ag:
                ag_dict = ag.to_dict()
                associate_details["agents"].append({
                    "name": ag.agent_name,
                    "address": ag.agent_address,
                    "mobile": ag_dict.get("mobile_number"),
                    "registration_number": ag.rera_registration_no,
                })

        elif atype == "architect":
            arch = Architect.query.get(a.associate_id)
            if arch:
                arch_dict = arch.to_dict()
                associate_details["architects"].append({
                    "name": arch.architect_name,
                    "email": arch_dict.get("email_id"),
                    "address": arch.address_line1,
                    "address2": arch.address_line2,
                    "state": arch.state_ut,
                    "district": arch.district,
                    "pin_code": arch.pin_code,
                    "mobile": arch_dict.get("mobile_number"),
                    "reg_number": arch.coa_registration_number,
                    "year_of_establishment": arch.year_of_establishment,
                    "number_of_key_projects": arch.number_of_key_projects,
                })

        elif atype == "engineer":
            eng = Engineer.query.get(a.associate_id)
            if eng:
                eng_dict = eng.to_dict()
                associate_details["engineers"].append({
                    "name": eng.engineer_name,
                    "email": eng_dict.get("email_id"),
                    "address": eng.address_line1,
                    "address2": eng.address_line2,
                    "state": eng.state_ut,
                    "district": eng.district,
                    "pin_code": eng.pin_code,
                    "mobile": eng_dict.get("mobile_number"),
                    "licence_number": eng.licence_number,
                    "number_of_key_projects": eng.number_of_key_projects,
                })

        elif atype == "accountant":
            acc = Accountant.query.get(a.associate_id)
            if acc:
                acc_dict = acc.to_dict()
                associate_details["accountants"].append({
                    "name": acc.accountant_name,
                    "email": acc_dict.get("email_id"),
                    "address": acc.address_line1,
                    "address2": acc.address_line2,
                    "state": acc.state_ut,
                    "district": acc.district,
                    "pin_code": acc.pin_code,
                    "mobile": acc_dict.get("mobile_number"),
                    "icai_member_id": acc.icai_member_id,
                    "number_of_key_projects": acc.number_of_key_projects,
                })

        elif atype == "project_engineer":
            pe = ProjectEngineer.query.get(a.associate_id)
            if pe:
                pe_dict = pe.to_dict()
                associate_details["project_engineers"].append({
                    "engineer_name": pe.engineer_name,
                    "email_id": pe_dict.get("email_id"),
                    "address_line1": pe.address_line1,
                    "address_line2": pe.address_line2,
                    "state_ut": pe.state_ut,
                    "district": pe.district,
                    "pin_code": pe.pin_code,
                    "mobile_number": pe_dict.get("mobile_number"),
                    "number_of_key_projects": pe.number_of_key_projects,
                })

        elif atype == "contractor":
            con = Contractor.query.get(a.associate_id)
            if con:
                con_dict = con.to_dict()
                associate_details["contractors"].append({
                    "nature_of_work": con.nature_of_work,
                    "contractor_name": con.contractor_name,
                    "email_id": con_dict.get("email_id"),
                    "address_line1": con.address_line1,
                    "state_ut": con.state_ut,
                    "district": con.district,
                    "pin_code": con.pin_code,
                    "year_of_establishment": con.year_of_establishment,
                    "number_of_key_projects": con.number_of_key_projects,
                    "mobile_number": con_dict.get("mobile_number"),
                })

                

    # -----------------------------
    # PROJECT DETAILS
    # -----------------------------
    project_details = {
        "Application Number": application_id,
        "Project Name": registration.get("project_name") if registration else "N/A",
        "Project Description": registration.get("project_description") if registration else "N/A",
        "Project Type": PROJECT_TYPE_MAP.get(registration.get("project_type"), "N/A") if registration else "N/A",
        "Project Status": registration.get("project_status") if registration else "New Project",
        "Building Plan No": registration.get("building_plan_no") if registration else "N/A",
        "Survey No": registration.get("survey_no") if registration else "N/A",
        "Building Permission Validity From": format_date(registration.get("building_permission_from")) if registration else "N/A",
        "Building Permission Validity To": format_date(registration.get("building_permission_upto")) if registration else "N/A",
        "Project Starting Date": format_date(registration.get("date_of_commencement")) if registration else "N/A",
        "Proposed Completion Date": format_date(registration.get("proposed_completion_date")) if registration else "N/A",
        "Total Area of Land (Sq.m)": registration.get("total_area_of_land") if registration else "N/A",
        "Height of Building (m)": registration.get("building_height") if registration else "0.00",
        "Total Plinth Area (Sq.m)": registration.get("total_plinth_area") if registration else "N/A",
        "Total Open Area (Sq.m)": registration.get("total_open_area") if registration else "N/A",
        "Total Built-up Area (Sq.m)": registration.get("total_built_up_area") if registration else "N/A",
        "Estimated Cost of Construction": registration.get("estimated_construction_cost") if registration else "N/A",
        "Cost of Land": registration.get("cost_of_land") if registration else "N/A",
        "Total Project Cost (₹)": registration.get("total_project_cost") if registration else "N/A",
        "Project Address": ", ".join(filter(None, [
        registration.get("project_address1"),
        registration.get("project_address2"),
        ])),
        "District": registration.get("project_district_name", "N/A"),
        "Mandal": registration.get("project_mandal_name") or "N/A",
        "Village": registration.get("project_village_name") or "N/A",
        "Latitude": registration.get("project_latitude", "N/A"),
        "Longitude": registration.get("project_longitude", "N/A"),

        "Pincode": registration.get("project_pincode", "N/A"),
        # ADD THESE NEW FIELDS:
        "Plan Approving Authority": registration.get("plan_approving_authority") if registration else "N/A",
        "APCRDA Name": registration.get("apcrda_name") if registration else "N/A",
        "Survey No": registration.get("survey_no") if registration else "N/A",
        "Address Proof": registration.get("address_proof_path") if registration else "N/A",
        
        # Local Address Fields
        "Local Address Line1": registration.get("local_address1", "N/A"),
        "Local Address Line2": registration.get("local_address2", "N/A"),
        "Local District": registration.get("local_district_name", "N/A"),
        "Local Mandal": registration.get("local_mandal_name") or "N/A",
        
        "Local Village": registration.get("local_village_name") or "N/A",
        "Local Pincode": registration.get("local_pincode", "N/A"),
        "Project Website": registration.get("project_website_url") if registration else "NA (//)",
        
    # ====================================================
    # 🔥 AUTHORIZED SIGNATORY DETAILS (OTHER THAN INDIVIDUAL)
    # ====================================================
"Authorized Signatory Name": registration.get("authorized_signatory_name") if registration else "N/A",
"Authorized Signatory Mobile": registration.get("authorized_signatory_mobile") if registration else "N/A",
"Authorized Signatory Email": registration.get("authorized_signatory_email") if registration else "N/A",
"Is Existing Director": registration.get("is_existing_director") if registration else "N/A",
"Authorized Signatory Photo": registration.get("authorized_signatory_photo_path") if registration else "N/A",
"Board Resolution Copy": registration.get("board_resolution_copy_path") if registration else "N/A",

        # No of Garages/Parking
        "No of Garages Available for Sale": registration.get("garages_available_for_sale") if registration else "0",
        "Total Area of Garages": registration.get("total_garage_area") if registration else "0.00",
        "No of Open Parking Spaces": registration.get("open_parking_spaces") if registration else "0",
        "Total Open Parking": registration.get("total_open_parking_area") if registration else "0.00",
        "No of Covered Parking": registration.get("covered_parking_spaces") if registration else "0",
        "Total Covered Parking Area": registration.get("total_covered_parking_area") if registration else "0.00",
    }


    # -----------------------------
    # ORGANISATION PROMOTER DETAILS (FINAL FIX)
    # -----------------------------
    promoter_details = {


    "Type Of Promoter": org_profile.get("type_of_promoter", "N/A"),
    "Organisation Name": org_profile.get("organization_name", "N/A"),
    "CIN Number": org_profile.get("registration_number", "N/A"),
    "Registration Date": format_date(org_profile.get("registration_date")),


    "PAN": org_profile.get("pan_number", "N/A"),
    "GST Number": org_profile.get("gst_number", "N/A"),

    "Authorized Signatory Mobile": org_profile.get("authorized_signatory_mobile", "N/A"),
    "Authorized Signatory Email": org_profile.get("authorized_signatory_email", "N/A"),

    "Landline": org_profile.get("authorized_signatory_landline", "N/A"),
    "Promoter Website": org_profile.get("website", "N/A"),

    "State": org_profile.get("state", "N/A"),
    "District": org_profile.get("district", "N/A"),

    "Bank State": org_profile.get("bank_state", "N/A"),
    "Bank Name": org_profile.get("bank_name", "N/A"),
    "Branch Name": org_profile.get("branch_name", "N/A"),
    "Account Number": org_profile.get("account_no", "N/A"),
    "IFSC Code": org_profile.get("ifsc_code", "N/A"),
    "Account Holder Name": org_profile.get("account_holder", "N/A"),
    }


    # Material Facts
    material_facts = {
        "No of Units in the project": registration.get("total_units") if registration else "1",
        "No of Units advances taken": registration.get("units_advances_taken") if registration else "0",
        "No of units where agreement for sale entered": registration.get("units_agreement_sale") if registration else "0",
        "No of units sold in the project": registration.get("units_sold") if registration else "0",
    }
    # -----------------------------
# OTHER STATE / PAST PROJECTS / LITIGATION DETAILS
# -----------------------------
    other_state_details = {
        "has_other_state": "Yes" if basic_reg.get("other_state_reg") == "Yes" else "No",
        "rera_number": basic_reg.get("rera_reg_number"),
        "rera_state": basic_reg.get("rera_state"),
        "revoked": "Yes" if basic_reg.get("registration_revoked") == "Yes" else "No",
        }

    last_five_years_details = {
        "has_projects": "Yes" if basic_reg.get("last_five_years") == "Yes" else "No",
        "project_name": basic_reg.get("project_name"),
        "project_type": PROJECT_TYPE_MAP.get(basic_reg.get("project_type"), "N/A"),
        "status": basic_reg.get("current_status"),
        "address": basic_reg.get("project_address"),
    }

    litigation_details = {
        "has_case": "Yes" if basic_reg.get("litigation") == "Yes" else "No",
        "case_no": basic_reg.get("case_no"),
        "tribunal": basic_reg.get("tribunal_place"),
        "petitioner": basic_reg.get("petitioner_name"),
        "respondent": basic_reg.get("respondent_name"),
        "facts": basic_reg.get("case_facts"),
        "status": basic_reg.get("case_status"),
    }



    # -----------------------------
# DEVELOPMENT DETAILS (FINAL FIX)
# -----------------------------
    raw_dev = development.get("development_details", {}) if development else {}

    normalized_development_details = {
    "apartments_flats": {
        "enabled": bool(raw_dev.get("apartments_flats", {}).get("rows")),
        "rows": raw_dev.get("apartments_flats", {}).get("rows", [])
    },
    "plots": {
        "enabled": bool(raw_dev.get("plots", {}).get("rows")),
        "rows": raw_dev.get("plots", {}).get("rows", [])
    },
    "villas": {
        "enabled": bool(raw_dev.get("villas", {}).get("rows")),
        "rows": raw_dev.get("villas", {}).get("rows", [])
    },
    "commercial": {
        "enabled": bool(raw_dev.get("commercial", {}).get("rows")),
        "rows": raw_dev.get("commercial", {}).get("rows", [])
    }
}

    external_work = (
    development.get("external_development_work", {})
    if development and isinstance(development.get("external_development_work"), dict)
    else {}
)


    dev_details = {
        "Building Type": development.get("building_type") if development else "Apartment",  # ADD THIS
        "Total No of Blocks": len(normalized_development_details.get("apartments_flats", {}).get("rows", [])) or "1",  # ADD THIS
        "Project Type": (
            development.get("project_type").capitalize()
            if development.get("project_type")
            else "N/A"
        ),

        "Development Details": development.get("development_details") if development else {},
        "External Development Works": [
            k.replace("_", " ")
            for k, v in external_work.items()
            if int(v) > 0
        ],
    }

    # -----------------------------
    # FINAL RESPONSE
    # -----------------------------
    return {
        "project_details": project_details,
        "promoter_details": promoter_details,
        
        "other_state_registration": other_state_details,
        "last_five_years_projects": last_five_years_details,
        "litigation_details": litigation_details,
        
        "associate_details": associate_details,
        "development_details": {
            "development_details": normalized_development_details,
            "external_development_work": external_work,
            "Building Type": development.get("building_type") if development else "Apartment",  # ADD
            "Total No of Blocks": len(normalized_development_details.get("apartments_flats", {}).get("rows", [])) or "1",  # ADD
        },
        "project_upload_documents": documents_data,
        
        # ADD THESE NEW SECTIONS:
        "material_facts": material_facts,
        "consultancy_details": consultancy,
        "other_development_works": other_dev_works,


        # -------------------------------
        "org_members": org_members,
        "past_projects": past_projects,
        "rera_details": org_rera,

    }