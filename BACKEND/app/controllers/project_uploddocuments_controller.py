import os
import logging
import json
import time
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from app.models.database import db
from app.models.project_upload_documents import ProjectRegistrationDocument
from app.models.project_registration_consultant import ProjectRegistrationConsultant
from app.utils.encryption import encrypt_value, decrypt_value

logger = logging.getLogger(__name__)

project_upload_documents_bp = Blueprint(
    "project_upload_documents",
    __name__
)

# =====================================================
# 1️⃣ GET DOCUMENTS + CONSULTANT (POST)
# =====================================================
@project_upload_documents_bp.route(
    "/project/documents-consultant/get",
    methods=["POST"]
)
def get_documents_consultant():
    try:
        data = request.json
        logger.info(f"GET request received: {data}")

        application_number = data.get("application_number")
        pan_number = data.get("pan_number")

        if not application_number or not pan_number:
            return jsonify({
                "status": "error",
                "message": "application_number and pan_number required"
            }), 400

        # Fetch document record
        document_record = ProjectRegistrationDocument.query.filter_by(
            application_number=application_number,
        ).first()

        if document_record:
            db_pan = decrypt_value(document_record.pan_number)

            if db_pan != pan_number:
                document_record = None

        # Fetch consultant record
        consultant_record = ProjectRegistrationConsultant.query.filter_by(
            application_number=application_number,
            pan_number=pan_number
        ).first()

        # Prepare documents with URLs
        documents_with_urls = {}
        if document_record and document_record.documents:
            base_url = request.host_url.rstrip('/')
            for doc_id, file_path in document_record.documents.items():
                if file_path:
                    # Extract filename from path
                    filename = os.path.basename(file_path)
                    url_path = f"/uploads/project_documents/{application_number}/{filename}"
                    documents_with_urls[doc_id] = f"{base_url}{url_path}"

        # Prepare consultant data
        consultant_data = {}
        if consultant_record:
            consultant_data = {
                "consultancy_name": consultant_record.consultancy_name or "",
                "consultant_name": consultant_record.consultant_name or "",
                "mobile_number": consultant_record.mobile_number,
                "email_id": consultant_record.email_id,
                "address": consultant_record.address or "",
                "declaration_accept": consultant_record.declaration_accept or "N",
                "note1_accept": consultant_record.note1_accept or "N",
                "note2_accept": consultant_record.note2_accept or "N"
            }

        return jsonify({
            "status": "success",
            "documents": documents_with_urls,
            "consultant": consultant_data
        }), 200

    except Exception as e:
        logger.exception("GET FAILED")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


# =====================================================
# 2️⃣ UPLOAD/UPDATE DOCUMENTS (POST)
# =====================================================
@project_upload_documents_bp.route(
    "/project/documents/upload",
    methods=["POST"]
)
def upload_documents():
    try:
        application_number = request.form.get("application_number")
        pan_number = request.form.get("pan_number")
        files = request.files
        existing_documents_json = request.form.get("existing_documents", "{}")

        logger.info(f"Upload request for app: {application_number}, pan: {pan_number}")

        if not application_number or not pan_number:
            return jsonify({
                "status": "error",
                "message": "application_number and pan_number required"
            }), 400

        # Parse existing documents
        existing_docs = {}
        try:
            existing_docs = json.loads(existing_documents_json)
            # Extract just the path if it's a full URL
            for doc_id, value in existing_docs.items():
                if value and 'http' in value:
                    # Extract filename from URL
                    filename = value.split('/')[-1]
                    existing_docs[doc_id] = os.path.join("uploads", "project_documents", str(application_number), filename)
        except Exception as e:
            logger.error(f"Error parsing existing_documents: {e}")

        # Create upload directory
        base_path = os.path.join(
            current_app.root_path,
            "uploads",
            "project_documents",
            str(application_number)
        )
        os.makedirs(base_path, exist_ok=True)

        # Process new file uploads
        new_documents = {}

        for key in files:
            if key.startswith("doc_"):
                doc_id = key.split("_")[1]
                file = files[key]

                if file and file.filename:
                    filename = secure_filename(file.filename)
                    # Add timestamp to avoid duplicate filenames
                    name, ext = os.path.splitext(filename)
                    timestamp = int(time.time())
                    filename = f"{name}_{timestamp}{ext}"
                    
                    saved_path = os.path.join(base_path, filename)
                    file.save(saved_path)
                    
                    # Store relative path for database
                    relative_path = os.path.join("uploads", "project_documents", str(application_number), filename)
                    new_documents[doc_id] = relative_path

        # Merge existing and new documents
        all_documents = {**existing_docs, **new_documents}

        # Find or create record
        record = ProjectRegistrationDocument.query.filter_by(
            application_number=application_number,
        ).first()

        if record:
         db_pan = decrypt_value(record.pan_number)

         if db_pan != pan_number:
             return jsonify({
                 "status": "error",
                 "message": "PAN mismatch"
             }), 404

        if record:
            logger.info(f"Updating existing document record")
            record.documents = all_documents
        else:
            logger.info("Creating new document record")
            record = ProjectRegistrationDocument(
                application_number=application_number,
                pan_number=encrypt_value(pan_number),
                documents=all_documents
            )
            db.session.add(record)

        db.session.commit()

        return jsonify({
            "status": "success",
            "documents": all_documents
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.exception("UPLOAD FAILED")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


# =====================================================
# 3️⃣ SAVE/UPDATE CONSULTANT (POST - UPSERT)
# =====================================================
@project_upload_documents_bp.route(
    "/project/consultant-declaration/save",
    methods=["POST"]
)
def save_consultant_declaration():
    try:
        data = request.json
        logger.info(f"Save consultant request: {data}")

        application_number = data.get("application_number")
        pan_number = data.get("pan_number")

        if not application_number or not pan_number:
            return jsonify({
                "status": "error",
                "message": "application_number and pan_number required"
            }), 400

        record = ProjectRegistrationConsultant.query.filter_by(
            application_number=application_number,
            pan_number=pan_number
        ).first()

        if record:
            # Update existing
            logger.info(f"Updating existing consultant record")
            record.consultancy_name = data.get("consultancy_name")
            record.consultant_name = data.get("consultant_name")
            record.mobile_number = encrypt_value(data.get("mobile_number")) if data.get("mobile_number") else None
            record.email_id = encrypt_value(data.get("email_id")) if data.get("email_id") else None
            record.address = data.get("address")
            record.declaration_name = data.get("consultant_name")  # Use consultant name
            record.declaration_accept = data.get("declaration_accept")
            record.note1_accept = data.get("note1_accept")
            record.note2_accept = data.get("note2_accept")
        else:
            # Create new
            logger.info("Creating new consultant record")
            data["declaration_name"] = data.get("consultant_name")
            record = ProjectRegistrationConsultant(**data)
            db.session.add(record)

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Consultant saved successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.exception("SAVE FAILED")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


# =====================================================
# 4️⃣ UPDATE CONSULTANT (PUT)
# =====================================================
@project_upload_documents_bp.route(
    "/project/consultant-declaration/update",
    methods=["PUT"]
)
def update_consultant_declaration():
    try:
        data = request.json
        logger.info(f"Update consultant request: {data}")

        application_number = data.get("application_number")
        pan_number = data.get("pan_number")

        record = ProjectRegistrationConsultant.query.filter_by(
            application_number=application_number,
            pan_number=pan_number
        ).first()

        if not record:
            return jsonify({
                "status": "error",
                "message": "Record not found"
            }), 404

        record.consultancy_name = data.get("consultancy_name")
        record.consultant_name = data.get("consultant_name")
        record.mobile_number = encrypt_value(data.get("mobile_number")) if data.get("mobile_number") else None
        record.email_id = encrypt_value(data.get("email_id")) if data.get("email_id") else None
        record.address = data.get("address")
        record.declaration_name = data.get("consultant_name")  # Use consultant name
        record.declaration_accept = data.get("declaration_accept")
        record.note1_accept = data.get("note1_accept")
        record.note2_accept = data.get("note2_accept")

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Updated successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.exception("UPDATE FAILED")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500
    
@project_upload_documents_bp.route("/project/documents/details", methods=["GET"])
def get_project_documents_details():
    try:
        # ✅ Accept BOTH formats
        application_number = request.args.get("application_number") or request.args.get(
            "applicationNumber"
        )
        pan_number = request.args.get("pan_number") or request.args.get("panNumber")

        print("APP:", application_number)
        print("PAN:", pan_number)

        if not application_number or not pan_number:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "application_number and pan_number required",
                    }
                ),
                400,
            )

        # =========================
        # 🔹 GET DOCUMENTS
        # =========================
        document_record = ProjectRegistrationDocument.query.filter_by(
            application_number=application_number
        ).first()

        if document_record:
             db_pan = decrypt_value(document_record.pan_number)

             if db_pan != pan_number:
                 document_record = None

        # =========================
        # 🔹 GET CONSULTANT
        # =========================
        consultant_record = ProjectRegistrationConsultant.query.filter_by(
            application_number=application_number, pan_number=pan_number
        ).first()

        # =========================
        # 🔹 FORMAT DOCUMENTS (OPTIONAL URL)
        # =========================
        documents_data = {}
        if document_record and document_record.documents:
            base_url = request.host_url.rstrip("/")
            for key, path in document_record.documents.items():
                if path:
                    filename = path.split("/")[-1]
                    documents_data[key] = (
                        f"{base_url}/uploads/project_documents/{application_number}/{filename}"
                    )

        # =========================
        # 🔹 FORMAT CONSULTANT
        # =========================
        consultant_data = consultant_record.to_dict() if consultant_record else {}

        if consultant_data:
            consultant_data["mobile_number"] = decrypt_value(consultant_data.get("mobile_number")) if consultant_data.get("mobile_number") else None
            consultant_data["email_id"] = decrypt_value(consultant_data.get("email_id")) if consultant_data.get("email_id") else None

        # =========================
        # 🔹 FINAL RESPONSE
        # =========================
        if not document_record and not consultant_record:
            return jsonify({"status": "error", "message": "No data found"}), 404

        return (
            jsonify(
                {
                    "status": "success",
                    "documents": documents_data,
                    "consultant": consultant_data,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"status": "error", "message": "Internal server error"}), 500