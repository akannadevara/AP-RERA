import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.utils.encryption import encrypt_value, decrypt_value
from app.models.project_registration_model import (
    insert_project_registration,
    get_project_registration
)
# from app.models.extension_project_application_details_models import (
#     get_project_basic_details_by_pan,
#     insert_extension_project_application
# )



project_registration_bp = Blueprint("project_registration_bp", __name__)

def save_file(file, subfolder):
    if not file:
        return None

    upload_base = current_app.config["UPLOAD_FOLDER"]
    folder = os.path.join(upload_base, subfolder)
    os.makedirs(folder, exist_ok=True)

    filename = secure_filename(file.filename)
    file_path = os.path.join(folder, filename)
    file.save(file_path)
  
    # store relative path in DB
    return f"uploads/{subfolder}/{filename}"


def empty_to_none(value):
    return None if value in ("", None) else value
        
@project_registration_bp.route("/project-registration", methods=["POST"])
def project_registration():
    try:
        form = request.form
        files = request.files

        data = {
            "application_number": form.get("applicationNumber"),
            "pan_number": encrypt_value(form.get("panNumber")),  # Encrypt PAN before storing

            "project_name": form.get("projectName"),
            "project_description": form.get("projectDescription"),
            "project_type": form.get("projectType"),
            "project_status": form.get("projectStatus"),

            "building_plan_no": form.get("buildingPlanNo"),
            "building_permission_from": form.get("buildingPermissionFrom"),
            "building_permission_upto": form.get("buildingPermissionUpto"),
            "date_of_commencement": form.get("dateOfCommencement"),
            "proposed_completion_date": form.get("proposedCompletionDate"),

            "total_area_of_land": empty_to_none(form.get("totalAreaOfLand")),
            "building_height": empty_to_none(form.get("buildingHeight")),
            "total_plinth_area": empty_to_none(form.get("totalPlinthArea")),
            "total_built_up_area": empty_to_none(form.get("totalBuiltUpArea")),

            "garages_available_for_sale": empty_to_none(form.get("garagesAvailableForSale")),
            "total_garage_area": empty_to_none(form.get("totalGarageArea")),
            "open_parking_spaces": empty_to_none(form.get("openParkingSpaces")),
            "total_open_parking_area": empty_to_none(form.get("totalOpenParkingArea")),
            "covered_parking_spaces": empty_to_none(form.get("coveredParkingSpaces")),
            "total_covered_parking_area": empty_to_none(form.get("totalCoveredParkingArea")),

            "estimated_construction_cost": empty_to_none(form.get("estimatedConstructionCost")),
            "cost_of_land": empty_to_none(form.get("costOfLand")),
            "total_open_area": empty_to_none(form.get("totalOpenArea")),
            "total_project_cost": empty_to_none(form.get("totalProjectCost")),

            "project_address1": form.get("projectAddress1"),
            "project_address2": form.get("projectAddress2"),
            "project_district": form.get("projectDistrict"),
            "project_mandal": form.get("projectMandal"),
            "project_village": form.get("projectVillage"),
            "project_pincode": form.get("projectPincode"),
            "project_latitude": form.get("projectLatitude"),
            "project_longitude": form.get("projectLongitude"),
            "plan_approving_authority": form.get("planApprovingAuthority"),
            "survey_no": form.get("surveyNo"),

            "address_proof_path": save_file(files.get("addressProof"), "address_proofs"),

            "local_address1": form.get("localAddress1"),
            "local_address2": form.get("localAddress2"),
            "local_area": form.get("localArea"),
            "local_landmark": form.get("localLandmark"),
            "local_district": form.get("localDistrict"),
            "local_mandal": form.get("localMandal"),
            "local_village": form.get("localVillage"),
            "local_pincode": form.get("localPincode"),
            "project_website_url": form.get("projectWebsiteURL"),

            "development_completed": empty_to_none(form.get("developmentCompleted")),
            "development_pending": empty_to_none(form.get("developmentPending")),
            "amount_collected": empty_to_none(form.get("amountCollected")),
            "amount_spent": empty_to_none(form.get("amountSpent")),
            "balance_amount": empty_to_none(form.get("balanceAmount")),
            "plan_modified": form.get("planModified") == "true",

            "architect_certificate_path": save_file(files.get("architectCertificate"), "certificates"),
            "engineer_certificate_path": save_file(files.get("engineerCertificate"), "certificates"),
            "ca_certificate_path": save_file(files.get("caCertificate"), "certificates"),

            "project_delayed": form.get("projectDelayed") == "true",
            "number_of_units": empty_to_none(form.get("numberOfUnits")),
            "units_advance_taken": empty_to_none(form.get("unitsAdvanceTaken")),
            "units_agreement_sale": empty_to_none(form.get("unitsAgreementSale")),
            "units_sold": empty_to_none(form.get("unitsSold")),

            "legal_declaration_accepted": form.get("legalDeclarationAccepted") == "true",
        }

        existing = get_project_registration(
            data["application_number"],
            form.get("panNumber")
        )
        
        if existing:
            return jsonify({
                "success": True,
                "message": "Already Saved"
            }), 200
        
        insert_project_registration(data)

        return jsonify({"message": "Project registered successfully"}), 201
    except Exception as e:
        import traceback
        traceback.print_exc()
    
        return jsonify({
            "error": str(e)
        }), 500
    
    # =====================================
# CHECK + FETCH API  (MAIN API YOU WANT)
# =====================================

@project_registration_bp.route("/get-project-by-application", methods=["POST"])
def get_project_by_application():

    try:

        data = request.get_json()

        application_number = data.get("applicationNumber")
        pan_number = data.get("panNumber")


        if not application_number or not pan_number:
            return jsonify({"error": "Missing data"}), 400


        # 🔹 Check DB
        result = get_project_registration(
            application_number,
            pan_number
        )


        # ✅ If exists → send data with decrypted fields
        if result:
            # Decrypt encrypted fields
            if result.get("pan_number"):
                result["pan_number"] = decrypt_value(result["pan_number"])
            if result.get("account_no"):
                result["account_no"] = decrypt_value(result["account_no"])
            if result.get("ifsc"):
                result["ifsc"] = decrypt_value(result["ifsc"])
            if result.get("aadhaar"):
                result["aadhaar"] = decrypt_value(result["aadhaar"])
            if result.get("mobile"):
                result["mobile"] = decrypt_value(result["mobile"])
            if result.get("email"):
                result["email"] = decrypt_value(result["email"])

            return jsonify({
                "exists": True,
                "data": result
            }), 200


        # ❌ If not exists → allow insert
        return jsonify({
            "exists": False,
            "data": {}
        }), 200


    except Exception as e:

        print("Fetch Error:", e)

        return jsonify({"error": "Internal server error"}), 500
    





# ==========================================================
# ✅ NEW GET API (SEPARATE – SAFE)
# ==========================================================
@project_registration_bp.route("/project-registration/details", methods=["GET"])
def get_project_registration_details():

    try:
        application_number = request.args.get("applicationNumber")
        pan_number = request.args.get("panNumber")

        if not application_number or not pan_number:
            return jsonify({
                "success": False,
                "message": "applicationNumber and panNumber required"
            }), 400

        print("Application Number:", application_number)
        print("PAN Number:", pan_number)

        result = get_project_registration(application_number, pan_number)

        print("Result:", result)

        # Decrypt encrypted fields if result exists
        if result:
            if result.get("pan_number"):
                result["pan_number"] = decrypt_value(result["pan_number"])
            if result.get("account_no"):
                result["account_no"] = decrypt_value(result["account_no"])
            if result.get("ifsc"):
                result["ifsc"] = decrypt_value(result["ifsc"])
            if result.get("aadhaar"):
                result["aadhaar"] = decrypt_value(result["aadhaar"])
            if result.get("mobile"):
                result["mobile"] = decrypt_value(result["mobile"])
            if result.get("email"):
                result["email"] = decrypt_value(result["email"])

        return jsonify({
            "success": True,
            "data": result if result else {}
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500
        
        
        

@project_registration_bp.route("/project-registration/update", methods=["PUT"])
def update_project_registration_new():

    from app.models.project_registration_model import update_project_registration
    from werkzeug.utils import secure_filename
    import os

    try:
        # 🔥 Detect if request is JSON or multipart
        if request.content_type.startswith("multipart/form-data"):
            data = request.form.to_dict()
            files = request.files
        else:
            data = request.get_json()
            files = {}

        if not data:
            return jsonify({
                "success": False,
                "message": "No data received"
            }), 400

        application_number = data.get("applicationNumber")
        pan_number = data.get("panNumber")

        if not application_number or not pan_number:
            return jsonify({
                "success": False,
                "message": "applicationNumber and panNumber required"
            }), 400

        # ✅ Add DB keys
        data["application_number"] = application_number
        data["pan_number"] = pan_number

        # =====================================================
        # 🔹 HANDLE FILE UPDATES (ONLY IF FILES SENT)
        # =====================================================

        if files:

            upload_folder = os.path.join(
                "uploads",
                "project_registration",
                application_number
            )
            os.makedirs(upload_folder, exist_ok=True)

            file_fields = {
                "addressProof": "address_proof_path",
                "architectCertificate": "architect_certificate_path",
                "engineerCertificate": "engineer_certificate_path",
                "caCertificate": "ca_certificate_path",
                "authorizedSignatoryPhoto": "authorized_signatory_photo_path",
                "boardResolutionCopy": "board_resolution_copy_path",
            }

            for frontend_key, db_column in file_fields.items():
                if frontend_key in files:
                    file = files[frontend_key]

                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        filepath = os.path.join(upload_folder, filename)
                        file.save(filepath)

                        # Save path into data for DB update
                        data[db_column] = filepath

        # =====================================================
        # 🔹 CALL YOUR EXISTING UPDATE FUNCTION
        # =====================================================

        rows = update_project_registration(data)

        if rows > 0:
            return jsonify({
                "success": True,
                "message": "Project updated successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "No record updated"
            }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

# ------------------------------vamsi anna apis --------------------------------

    

    
@project_registration_bp.route("/project/basic-details-by-pan", methods=["GET"])
def get_project_basic_details_by_pan_controller():
    from app.models.extension_project_application_details_models import get_project_basic_details_by_pan
    pan_number = request.args.get("pan")

    if not pan_number:
        return jsonify({
            "success": False,
            "message": "pan is required"
        }), 400

    data = get_project_basic_details_by_pan(pan_number)

    return jsonify({
        "success": True,
        "data": data
    }), 200

# =====================================
# ✅ SINGLE PROJECT (AUTO TYPE - BEST API)
# =====================================
@project_registration_bp.route("/planning-single", methods=["GET"])
def planning_single():

    application_number = request.args.get("applicationNumber")
    pan_number = request.args.get("panNumber")

    if not application_number or not pan_number:
        return jsonify({"error": "Missing data"}), 400

    from app.models.planning_documents_model import get_planning_single

    data = get_planning_single(application_number, pan_number)

    if not data:
        return jsonify({"error": "No project found"}), 404

    return jsonify({
        "success": True,
        "data": data
    }), 200


# =====================================
# ✅ ALL PROJECTS (INDIVIDUAL + OTHER)
# =====================================
@project_registration_bp.route("/planning-dashboard-all", methods=["GET"])
def planning_dashboard_all():

    from app.models.planning_documents_model import get_all_planning_dashboard_mixed

    data = get_all_planning_dashboard_mixed()

    return jsonify({
        "success": True,
        "data": data
    }), 200


# =====================================
# ✅ FILTER BY TYPE
# =====================================
@project_registration_bp.route("/planning-dashboard-all-by-type", methods=["GET"])
def planning_dashboard_all_by_type():

    user_type = request.args.get("type")  # individual / other

    if not user_type:
        return jsonify({"error": "type required"}), 400

    from app.models.planning_documents_model import get_all_planning_dashboard_by_type

    data = get_all_planning_dashboard_by_type(user_type)

    return jsonify({
        "success": True,
        "data": data
    }), 200
    