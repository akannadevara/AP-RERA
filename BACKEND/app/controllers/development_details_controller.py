
import os
import logging
import json
import pandas as pd

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.models.development_details import DevelopmentDetailsModel
from app.utils.encryption import encrypt_value

development_details_bp = Blueprint("development_details_bp", __name__)

BASE_UPLOAD_FOLDER = "uploads"
EXCEL_UPLOAD_FOLDER = os.path.join(BASE_UPLOAD_FOLDER, "excel")


@development_details_bp.route("/development-details", methods=["POST"])
def save_development_details():
    try:
        logging.info("========== /development-details START ==========")

        # ---------- CREATE UPLOAD FOLDERS ----------
        os.makedirs(EXCEL_UPLOAD_FOLDER, exist_ok=True)

        # ---------- READ BASIC FORM DATA ----------
        project_id = request.form.get("project_id")
        project_type = request.form.get("project_type")
        work_description = request.form.get("work_description")
        work_type = request.form.get("work_type")
        pan_number = request.form.get("pan_number")
        application_number = request.form.get("application_number")

        # ---------- READ JSON FIELDS ----------
        development_details = json.loads(
            request.form.get("development_details", "{}")
        )

        external_development_work = json.loads(
            request.form.get("external_development_work", "{}")
        )

        # ✅ IMPORTANT FIX
        other_external_works = json.loads(
            request.form.get("other_external_works", "[]")
        )

        logging.info(f"other_external_works: {other_external_works}")
        logging.info(f"development_details (before files): {development_details}")

        # ---------- FILE HANDLING ----------
        for project_key in development_details.keys():
            file_field_name = f"{project_key}_file"

            if file_field_name in request.files:
                file = request.files[file_field_name]

                if file and file.filename:
                    safe_name = secure_filename(file.filename)

                    saved_path = os.path.join(
                        EXCEL_UPLOAD_FOLDER,
                        f"{project_id}_{project_key}_{safe_name}"
                    )

                    file.save(saved_path)

                    # ---------- READ EXCEL ----------
                    df = pd.read_excel(saved_path)
                    df = df.fillna(0)

                    excel_rows = df.to_dict(orient="records")

                    development_details[project_key]["file_path"] = saved_path
                    development_details[project_key]["rows"] = excel_rows

                    logging.info(
                        f"Parsed Excel rows for {project_key}: {len(excel_rows)}"
                    )

        logging.info(
            f"development_details (after files): {development_details}"
        )

        # ---------- SAVE TO DATABASE ----------
        row = DevelopmentDetailsModel.insert({
            "project_id": project_id,
            "project_type": project_type,
            "development_details": json.dumps(development_details, default=str),
            "external_development_work": json.dumps(external_development_work, default=str),
            "other_external_works": json.dumps(other_external_works, default=str),
            "work_description": work_description,
            "work_type": work_type,
            "pan_number": encrypt_value(pan_number) if pan_number else pan_number,
            "application_number": application_number
        })

        logging.info(f"Inserted row id: {row.id}")
        logging.info("========== /development-details END ==========")

        return jsonify({
            "message": "Development details saved successfully",
            "id": row.id
        }), 201

    except Exception as e:
        logging.exception("🔥 ERROR in /development-details")
        return jsonify({
            "message": "Internal Server Error",
            "error": "Internal server error"
        }), 500


@development_details_bp.route("/development-details", methods=["GET"])
def get_development_details():
    try:
        application_number = request.args.get("application_number")
        pan_number = request.args.get("pan_number")

        if not application_number or not pan_number:
            return jsonify({
                "status": "error",
                "message": "application_number and pan_number are required"
            }), 400

        result = DevelopmentDetailsModel.get_by_application_and_pan(
            application_number,
            pan_number
        )

        if not result:
            return jsonify({"status": "success", "data": {}}), 200

        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except Exception as e:
        logging.exception("🔥 GET development-details failed")
        return jsonify({
            "status": "error",
            "message": "Internal Server Error",
            "error": "Internal server error"
        }), 500


@development_details_bp.route("/development-details/all", methods=["GET"])
def get_development_detailss():
    try:
        application_number = request.args.get("application_number")
        pan_number = request.args.get("pan_number")

        # ✅ Validate input
        if not application_number or not pan_number:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "application_number and pan_number are required",
                    }
                ),
                400,
            )

        # ✅ Fetch ALL records (IMPORTANT CHANGE)
        results = DevelopmentDetailsModel.get_all_by_application_and_pan(
            application_number, pan_number
        )

        # ✅ If no data
        if not results:
            return jsonify({"status": "success", "count": 0, "data": []}), 200

        # ✅ Success response
        return (
            jsonify({"status": "success", "count": len(results), "data": results}),
            200,
        )

    except Exception as e:
        logging.exception("🔥 GET development-details failed")
        return (
            jsonify(
                {"status": "error", "message": "Internal Server Error", "error": "Internal server error"}
            ),
            500,
        )