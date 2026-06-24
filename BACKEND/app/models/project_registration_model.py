from app.models.database import db
from sqlalchemy import text
from app.utils.encryption import decrypt_value


# ---------------------------------------------------------
# INSERT PROJECT REGISTRATION (EXISTING - UNCHANGED)
# ---------------------------------------------------------
def insert_project_registration(data):
    query = text("""
        INSERT INTO project_registration (
            application_number, pan_number,

            project_name, project_description, project_type, project_status,
            building_plan_no, building_permission_from, building_permission_upto,
            date_of_commencement, proposed_completion_date,

            total_area_of_land, building_height, total_plinth_area, total_built_up_area,
            garages_available_for_sale, total_garage_area,
            open_parking_spaces, total_open_parking_area,
            covered_parking_spaces, total_covered_parking_area,

            estimated_construction_cost, cost_of_land,
            total_open_area, total_project_cost,

            project_address1, project_address2,
            project_district, project_mandal, project_village,
            project_pincode, project_latitude, project_longitude,
            plan_approving_authority, survey_no, address_proof_path,

            local_address1, local_address2, local_area, local_landmark,
            local_district, local_mandal, local_village,
            local_pincode, project_website_url,

            development_completed, development_pending,
            amount_collected, amount_spent, balance_amount, plan_modified,

            architect_certificate_path, engineer_certificate_path, ca_certificate_path,

            project_delayed, number_of_units, units_advance_taken,
            units_agreement_sale, units_sold, legal_declaration_accepted
        )
        VALUES (
            :application_number, :pan_number,

            :project_name, :project_description, :project_type, :project_status,
            :building_plan_no, :building_permission_from, :building_permission_upto,
            :date_of_commencement, :proposed_completion_date,

            :total_area_of_land, :building_height, :total_plinth_area, :total_built_up_area,
            :garages_available_for_sale, :total_garage_area,
            :open_parking_spaces, :total_open_parking_area,
            :covered_parking_spaces, :total_covered_parking_area,

            :estimated_construction_cost, :cost_of_land,
            :total_open_area, :total_project_cost,

            :project_address1, :project_address2,
            :project_district, :project_mandal, :project_village,
            :project_pincode, :project_latitude, :project_longitude,
            :plan_approving_authority, :survey_no, :address_proof_path,

            :local_address1, :local_address2, :local_area, :local_landmark,
            :local_district, :local_mandal, :local_village,
            :local_pincode, :project_website_url,

            :development_completed, :development_pending,
            :amount_collected, :amount_spent, :balance_amount, :plan_modified,

            :architect_certificate_path, :engineer_certificate_path, :ca_certificate_path,

            :project_delayed, :number_of_units, :units_advance_taken,
            :units_agreement_sale, :units_sold, :legal_declaration_accepted
        )
    """)

    db.session.execute(query, data)
    db.session.commit()

# # ---------------------------------------------------------
# # FETCH PROJECT REGISTRATION (BY PAN + APPLICATION NO)
# # ---------------------------------------------------------
def get_project_registration(application_number, pan_number):

    query = text("""
        SELECT *
        FROM project_registration
        WHERE application_number = :application_number
        LIMIT 1
    """)

    result = db.session.execute(
        query,
        {
            "application_number": application_number
        }
    ).mappings().first()

    if not result:
        return None

    result = dict(result)

    # Compare decrypted PAN with entered PAN
    if result.get("pan_number"):
        db_pan = decrypt_value(result["pan_number"])

        print("DB PAN:", db_pan)
        print("Entered PAN:", pan_number)

        if db_pan.strip().upper() != pan_number.strip().upper():
            return None

    return result
# ---------------------------------------------------------
# FETCH PROJECT REGISTRATION (NEW - FOR PREVIEW & PDF)
# ---------------------------------------------------------

from sqlalchemy import text


def fetch_project_registration(application_number, pan_number):

    query = text("""
    SELECT

    -- ================= BASIC =================
    pr.application_number,
    pr.pan_number,
    pr.project_name,
    pr.project_description,
    pr.project_type,
    pr.project_status,


    -- ================= PERMISSION =================
    pr.building_plan_no,
    pr.building_permission_from,
    pr.building_permission_upto,
    pr.date_of_commencement,
    pr.proposed_completion_date,


    -- ================= AREA =================
    pr.total_area_of_land,
    pr.building_height,
    pr.total_plinth_area,
    pr.total_built_up_area,
    pr.total_open_area,


    -- ================= COST =================
    pr.estimated_construction_cost,
    pr.cost_of_land,
    pr.total_project_cost,


    -- ================= SITE ADDRESS =================
    pr.project_address1,
    pr.project_address2,
    pr.project_pincode,
    pr.project_latitude,
    pr.project_longitude,

    d.district_name    AS project_district_name,
    m.mandal_name      AS project_mandal_name,
    v.village_name     AS project_village_name,


    -- ================= LOCAL ADDRESS =================
    pr.local_address1,
    pr.local_address2,
    pr.local_pincode,

    ld.district_name   AS local_district_name,
    lm.mandal_name     AS local_mandal_name,
    lv.village_name    AS local_village_name,


    -- ================= OTHER =================
    pr.plan_approving_authority,
    pr.address_proof_path,
    pr.project_website_url,


    -- ================= PARKING =================
    pr.garages_available_for_sale,
    pr.total_garage_area,
    pr.open_parking_spaces,
    pr.total_open_parking_area,
    pr.covered_parking_spaces,
    pr.total_covered_parking_area,


    -- ================= MATERIAL =================
    pr.number_of_units,
    pr.units_advance_taken,
    pr.units_agreement_sale,
    pr.units_sold,
    pr.legal_declaration_accepted,


    -- ================= PROMOTER =================
    preg.name              AS promoter_name,
    preg.father_name       AS promoter_father_name,
    preg.aadhaar           AS promoter_aadhaar,
    preg.mobile            AS promoter_mobile,
    preg.email             AS promoter_email,
    preg.landline          AS promoter_landline,
    preg.state_ut          AS promoter_state,
    preg.district          AS promoter_district,
    preg.promoter_website  AS promoter_website,
    preg.litigation        AS promoter_litigation,


    -- ================= BANK =================
    preg.bank_state,
    preg.bank_name,
    preg.branch_name,
    preg.account_no,
    preg.account_holder,
    preg.ifsc


    FROM project_registration pr


    -- ================= PROMOTER JOIN =================
    LEFT JOIN project_registrations preg
      ON pr.application_number = preg.application_no
     AND pr.pan_number = preg.pan_number


    -- ================= PROJECT MASTER =================
    LEFT JOIN district_master_t d
      ON pr.project_district = d.id

    LEFT JOIN mandal_master_t m
  ON pr.project_mandal = m.id


    LEFT JOIN villages_t v
  ON pr.project_village = v.id

    -- ================= LOCAL MASTER =================
    LEFT JOIN district_master_t ld
      ON pr.local_district = ld.id

    LEFT JOIN mandal_master_t lm
  ON pr.local_mandal = lm.id


    LEFT JOIN villages_t lv
  ON pr.local_village = lv.id

    WHERE pr.application_number = :application_number
      AND pr.pan_number = :pan_number
    """)

    result = db.session.execute(
        query,
        {
            "application_number": application_number,
            "pan_number": pan_number
        }
    ).mappings().first()

    if not result:
        return {}

    return dict(result)


# ==========================================================
# ✅ FINAL SAFE DYNAMIC UPDATE
# ==========================================================
def update_project_registration(data):

    from sqlalchemy import text
    from app.models.database import db

    application_number = data.get("application_number")
    pan_number = data.get("pan_number")

    if not application_number or not pan_number:
        return 0

    # ------------------------------------------------------
    # 🔁 Convert camelCase → snake_case
    # ------------------------------------------------------
    field_mapping = {
        "projectName": "project_name",
        "projectDescription": "project_description",
        "projectType": "project_type",
        "projectStatus": "project_status",
        "buildingPlanNo": "building_plan_no",
        "buildingPermissionFrom": "building_permission_from",
        "buildingPermissionUpto": "building_permission_upto",
        "dateOfCommencement": "date_of_commencement",
        "proposedCompletionDate": "proposed_completion_date",
        "totalAreaOfLand": "total_area_of_land",
        "buildingHeight": "building_height",
        "totalPlinthArea": "total_plinth_area",
        "totalBuiltUpArea": "total_built_up_area",
        "garagesAvailableForSale": "garages_available_for_sale",
        "totalGarageArea": "total_garage_area",
        "openParkingSpaces": "open_parking_spaces",
        "totalOpenParkingArea": "total_open_parking_area",
        "coveredParkingSpaces": "covered_parking_spaces",
        "totalCoveredParkingArea": "total_covered_parking_area",
        "estimatedConstructionCost": "estimated_construction_cost",
        "costOfLand": "cost_of_land",
        "totalOpenArea": "total_open_area",
        "totalProjectCost": "total_project_cost",
        "projectAddress1": "project_address1",
        "projectAddress2": "project_address2",
        "projectDistrict": "project_district",
        "projectMandal": "project_mandal",
        "projectVillage": "project_village",
        "projectPincode": "project_pincode",
        "projectLatitude": "project_latitude",
        "projectLongitude": "project_longitude",
        "planApprovingAuthority": "plan_approving_authority",
        "surveyNo": "survey_no",
        "localAddress1": "local_address1",
        "localAddress2": "local_address2",
        "localArea": "local_area",
        "localLandmark": "local_landmark",
        "localDistrict": "local_district",
        "localMandal": "local_mandal",
        "localVillage": "local_village",
        "localPincode": "local_pincode",
        "developmentCompleted": "development_completed",
        "developmentPending": "development_pending",
        "amountCollected": "amount_collected",
        "amountSpent": "amount_spent",
        "balanceAmount": "balance_amount",
        "planModified": "plan_modified",
        "projectDelayed": "project_delayed",
        "numberOfUnits": "number_of_units",
        "unitsAdvanceTaken": "units_advance_taken",
        "unitsAgreementSale": "units_agreement_sale",
        "unitsSold": "units_sold",
        "legalDeclarationAccepted": "legal_declaration_accepted"
    }

    converted_data = {}
    for key, value in data.items():
        converted_key = field_mapping.get(key, key)
        converted_data[converted_key] = value

    data = converted_data

    # ------------------------------------------------------
    # Convert empty string → NULL
    # ------------------------------------------------------
    for key in data:
        if data[key] == "":
            data[key] = None

    # ------------------------------------------------------
    # Allowed columns only
    # ------------------------------------------------------
    protected_fields = {"id", "created_at", "application_number", "pan_number"}

    valid_columns = {
        "project_name","project_description","project_type","project_status",
        "building_plan_no","building_permission_from","building_permission_upto",
        "date_of_commencement","proposed_completion_date",
        "total_area_of_land","building_height","total_plinth_area","total_built_up_area",
        "garages_available_for_sale","total_garage_area",
        "open_parking_spaces","total_open_parking_area",
        "covered_parking_spaces","total_covered_parking_area",
        "estimated_construction_cost","cost_of_land",
        "total_open_area","total_project_cost",
        "project_address1","project_address2",
        "project_district","project_mandal","project_village",
        "project_pincode","project_latitude","project_longitude",
        "plan_approving_authority","survey_no",
        "local_address1","local_address2","local_area","local_landmark",
        "local_district","local_mandal","local_village",
        "local_pincode",
        "development_completed","development_pending",
        "amount_collected","amount_spent","balance_amount","plan_modified",
        "project_delayed","number_of_units","units_advance_taken",
        "units_agreement_sale","units_sold","legal_declaration_accepted",
        "address_proof_path",
        "architect_certificate_path",
        "engineer_certificate_path",
        "ca_certificate_path"
    }

    update_data = {
        key: value
        for key, value in data.items()
        if key not in protected_fields and key in valid_columns
    }

    if not update_data:
        return 0

    set_clause = ", ".join([f"{key} = :{key}" for key in update_data])

    query = text(f"""
        UPDATE project_registration
        SET {set_clause}
        WHERE application_number = :application_number
        AND pan_number = :pan_number
    """)

    update_data["application_number"] = application_number
    update_data["pan_number"] = pan_number

    result = db.session.execute(query, update_data)
    db.session.commit()

    return result.rowcount