# app/controllers/project_extention_controller.py

from attrs import field
from flask import Blueprint, request, jsonify, current_app
from app.models.database import db
from app.models.extension_project_application_details_models import ExtensionProjectApplicationDetails
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)
from werkzeug.utils import secure_filename
from flask_mail import Message
from app import mail
from flask import send_from_directory
from flask_jwt_extended import jwt_required
from datetime import datetime
from app.utils.encryption import encrypt_value, decrypt_value
import os
import uuid


project_extention_bp = Blueprint(
    "project_extention_bp",
    __name__
)

# =========================================================
# UPLOAD FOLDER
# =========================================================

UPLOAD_FOLDER ="uploads/project_extention"

ALLOWED_EXTENSIONS = {
    "pdf",
    "jpg",
    "jpeg",
    "png",
    "doc",
    "docx"
}


# =========================================================
# HELPERS
# =========================================================

def allowed_file(filename):

    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def save_file(file):

    if not file:
        return None

    if file.filename == "":
        return None

    if allowed_file(file.filename):

        filename = secure_filename(file.filename)

        unique_name = f"{uuid.uuid4()}_{filename}"

        upload_path = os.path.join(
            UPLOAD_FOLDER
        )

        os.makedirs(upload_path, exist_ok=True)

        file_path = os.path.join(upload_path, unique_name)

        file.save(file_path)

        return f"/uploads/project_extention/{unique_name}"

    return None


# =========================================================
# CREATE API
# =========================================================

@project_extention_bp.route(
    "/project-extension/create",
    methods=["POST"]
)
def create_project_extension():

    try:

        data = request.form

        representation_letter = save_file(
            request.files.get("representation_letter")
        )

        form_b = save_file(
            request.files.get("form_b")
        )

        consent_letter = save_file(
            request.files.get("consent_letter")
        )

        form_e = save_file(
            request.files.get("form_e")
        )

        form_p4 = save_file(
            request.files.get("form_p4")
        )

        extension_proceeding = save_file(
            request.files.get("extension_proceeding")
        )

        form_1 = save_file(
            request.files.get("form_1")
        )

        form_2 = save_file(
            request.files.get("form_2")
        )

        form_3 = save_file(
            request.files.get("form_3")
        )

        receipt_path = save_file(
            request.files.get("receipt_path")
        )

        certificate_path = save_file(
            request.files.get("certificate_path")
        )

        obj = ExtensionProjectApplicationDetails(

            application_number=data.get("application_number"),
            project_id=data.get("project_id"),
            project_name=data.get("project_name"),
            promoter_pan_number=encrypt_value(data.get("promoter_pan")),
            promoter_email=encrypt_value(data.get("promoter_email")),


            validity_from=data.get("validity_from"),
            validity_to=data.get("validity_to"),

            new_validity_from=data.get("new_validity_from"),
            new_validity_to=data.get("new_validity_to"),

            representation_letter=representation_letter,
            form_b=form_b,
            consent_letter=consent_letter,
            form_e=form_e,
            form_p4=form_p4,
            extension_proceeding=extension_proceeding,

            form_1=form_1,
            form_2=form_2,
            form_3=form_3,

            payment_status=data.get("payment_status"),
            payment_amount=data.get("payment_amount"),
             
            payment_reference_no=data.get("payment_reference_no"),
            payment_mode=data.get("payment_mode"),

            bank_name=data.get("bank_name"),

            payment_date=datetime.strptime(
                data.get("payment_date"),
                "%Y-%m-%d %H:%M:%S"
            ) if data.get("payment_date") else None,

            gateway_response=data.get("gateway_response"),
            receipt_path=receipt_path,
            project_district=data.get("project_district"),
            current_stage=data.get("current_stage"),
            application_status=data.get("application_status"),

            planning_team=data.get("planning_team"),
            planning_team_remarks=data.get("planning_team_remarks"),
            planning_team_authority_id=data.get("planning_team_authority_id"),

            ad_remarks=data.get("ad_remarks"),
            ad_id=data.get("ad_id"),

            dd_remarks=data.get("dd_remarks"),
            dd_id=data.get("dd_id"),

            director_remarks=data.get("director_remarks"),
            director_id=data.get("director_id"),

            chairman_remarks=data.get("chairman_remarks"),
            chairman_id=data.get("chairman_id"),

            shortfall_reason=data.get("shortfall_reason"),

            final_status=data.get("final_status"),
            certificate_path=certificate_path,

            created_by=data.get("created_by")
        )

        db.session.add(obj)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Project Extension Application Created Successfully",
            "data": obj.to_dict()
        }), 201

    except Exception as e:

        db.session.rollback()

        print("=================================")
        print("PROJECT EXTENSION ERROR")
        print(str(e))
        print("=================================")

        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


# =========================================================
# GET ALL WITH PAGINATION
# =========================================================
@project_extention_bp.route(
    "/project-extension/list",
    methods=["GET"]
)
def get_all_project_extensions():

    try:

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        pagination = ExtensionProjectApplicationDetails.query.order_by(
            ExtensionProjectApplicationDetails.id.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        data = [
            {
                "id": item.id,
                "project_name": item.project_name,
                "promoter_email": decrypt_value(item.promoter_email) if item.promoter_email else None,
                "promoter_pan_number": decrypt_value(item.promoter_pan_number) if item.promoter_pan_number else None,
                "application_status": item.application_status,
                "project_district": item.project_district,
                "created_on": str(item.created_on) if item.created_on else None
            }
            for item in pagination.items
        ]

        return jsonify({
            "success": True,
            "total_records": pagination.total,
            "total_pages": pagination.pages,
            "current_page": pagination.page,
            "per_page": per_page,
            "data": data
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


@project_extention_bp.route(
    "/project-extension/<int:id>",
    methods=["GET"]
)
def get_project_extension_by_id(id):

    try:

        obj = ExtensionProjectApplicationDetails.query.get(id)

        if not obj:

            return jsonify({
                "success": False,
                "message": "Record Not Found"
            }), 404

        return jsonify({
            "success": True,
            "data": obj.to_dict()
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


# =========================================================
# PATCH API
# =========================================================
@project_extention_bp.route(
    "/project-extension/update/<int:id>",
    methods=["PATCH"]
)
def update_project_extension(id):

    try:

        obj = ExtensionProjectApplicationDetails.query.get(id)

        if not obj:

            return jsonify({
                "success": False,
                "message": "Record Not Found"
            }), 404

        data = request.form

        fields = [
            "application_number",
            "project_id",
            "project_name",
            "promoter_pan_number",
            "promoter_email",
            "payment_status",
            "payment_amount",
            "transaction_id",
            "payment_reference_no",
            "payment_mode",
            "bank_name",
            "gateway_response",
            "current_stage",
            "application_status",

            "planning_team",
            "planning_team_remarks",
            "planning_team_authority_id",
            "planning_team_replay_date",

            "ad_remarks",
            "ad_id",

            "dd_remarks",
            "dd_id",

            "ad_or_dd_replay_date",

            "director_remarks",
            "director_id",
            "director_replay_date",

            "chairman_remarks",
            "chairman_id",
            "chairman_replay_date",

            "shortfall_reason",
            "final_status"
        ]

        date_fields = [
            "planning_team_replay_date",
            "ad_or_dd_replay_date",
            "director_replay_date",
            "chairman_replay_date"
        ]

        for field in fields:

            if field in data:

                value = data.get(field)

                if field in [
                    "promoter_pan_number",
                    "promoter_email"
                ]:
                    value = encrypt_value(value)

                if field in date_fields and value:

                    value = datetime.strptime(
                        value,
                        "%Y-%m-%d"
                    ).date()

                setattr(obj, field, value)

        # FILE UPDATE

        file_fields = {
            "representation_letter": "representation_letter",
            "form_b": "form_b",
            "consent_letter": "consent_letter",
            "form_e": "form_e",
            "form_p4": "form_p4",
            "extension_proceeding": "extension_proceeding",
            "form_1": "form_1",
            "form_2": "form_2",
            "form_3": "form_3",
            "receipt_path": "receipt_path",
            "certificate_path": "certificate_path"
        }

        for key, attr in file_fields.items():

            file = request.files.get(key)

            if file:

                saved_path = save_file(file)

                setattr(obj, attr, saved_path)

        # ===============================
        # AUTO UPDATE PLANNING TEAM DATA
        # ===============================

        from datetime import date

        if data.get("planning_team_remarks"):

            obj.planning_team_authority_id = data.get(
                "planning_team"
            )

            obj.planning_team_replay_date = date.today()

            print(
                "Planning Team User ID :",
                obj.planning_team_authority_id
            )

            print(
                "Replay Date :",
                obj.planning_team_replay_date
            )

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Updated Successfully",
            "data": obj.to_dict()
        }), 200

        return jsonify({
            "success": True,
            "message": "Updated Successfully",
            "data": obj.to_dict()
        }), 200

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500
# =========================================================
# MAIL SEND API
# =========================================================

@project_extention_bp.route(
    "/project-extension/send-mail",
    methods=["POST"]
)
def send_project_extension_mail():

    try:

        data = request.json

        email = data.get("email")

        subject = data.get("subject")

        body = data.get("body")

        msg = Message(
            subject,
            recipients=[email]
        )

        msg.body = body

        mail.send(msg)

        return jsonify({
            "success": True,
            "message": "Mail Sent Successfully"
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500

@project_extention_bp.route(
    "/uploads/project_extention/<path:filename>",
    methods=["GET"]
)
@jwt_required()
def view_project_extension_file(filename):

    try:

        print("========== PDF API HIT ==========")

        user_id = get_jwt_identity()

        print("JWT USER ID =", user_id)

        upload_folder = os.path.join(
            current_app.root_path,
            "..",
            "uploads",
            "project_extention"
        )

        print("FILE =", filename)
        print("PATH =", upload_folder)

        return send_from_directory(
            upload_folder,
            filename
        )

    except Exception as e:

        print("PDF ERROR =", str(e))

        return jsonify({
            "success": False,
            "message": str(e)
        }), 404