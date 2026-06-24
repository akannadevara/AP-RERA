import logging
import os
import json
from flask import Blueprint, request, jsonify
# Storing values as plain text for associate details (no encryption/decryption)
from app.models.project_agent import AgentModel
from app.models.architect import Architect
from app.models.engineer import Engineer
from app.models.contractor import Contractor
from app.models.accountant import Accountant
from app.models.project_engineer import ProjectEngineer
from app.models.database import db
from app.models.application_associate import ApplicationAssociate
from app.utils.encryption import encrypt_value
from app.utils.encryption import decrypt_value



# ---------------------------------------------------
# Blueprint
# ---------------------------------------------------
associate_bp = Blueprint("associate", __name__)

# ---------------------------------------------------
# Helpers
# ---------------------------------------------------
def empty_to_none(value):
    """Convert empty string to None for DB safety"""
    return None if value in ("", None) else value


def validate_required(data, fields):
    for field in fields:
        if not data.get(field):
            return field
    return None

# ---------------------------------------------------
# Response Mappers (Frontend-friendly)
# ---------------------------------------------------

def map_project_agents(agents):
    return [{
        "id": a.id,
        "name": a.agent_name,
        "registrationNo": a.rera_registration_no,
        "address": a.agent_address,
        "mobile": a.to_dict().get("mobile_number")
    } for a in agents]


def map_architects(architects):
    return [{
        "id": a.id,
        "name": a.architect_name,
        "email": decrypt_value(a.to_dict().get("email_id")) if a.to_dict().get("email_id") else None,
        "address": a.address_line1,
        "state": a.state_ut,
        "district": a.district,
        "mobile": decrypt_value(a.to_dict().get("mobile_number")) if a.to_dict().get("mobile_number") else None,
        "coaRegistrationNumber": a.coa_registration_number
    } for a in architects]


def map_structural_engineers(engineers):
    return [{
        "id": e.id,
        "name": e.engineer_name,
        "email": decrypt_value(e.to_dict().get("email_id")) if e.to_dict().get("email_id") else None,
        "address": e.address_line1,
        "state": e.state_ut,
        "district": e.district,
        "mobile": decrypt_value(e.to_dict().get("mobile_number")) if e.to_dict().get("mobile_number") else None,
        "licenceNumber": e.licence_number
    } for e in engineers]


def map_contractors(contractors):
    return [{
        "id": c.id,
        "name": c.contractor_name,
        "natureOfWork": c.nature_of_work,
        "email": decrypt_value(c.to_dict().get("email_id")) if c.to_dict().get("email_id") else None,
        "address": c.address_line1,
        "state": c.state_ut,
        "district": c.district,
        "mobile": decrypt_value(c.to_dict().get("mobile_number")) if c.to_dict().get("mobile_number") else None
    } for c in contractors]


def map_accountants(accountants):
    return [{
        "id": a.id,
        "name": a.accountant_name,
        "email": decrypt_value(a.to_dict().get("email_id")) if a.to_dict().get("email_id") else None,
        "address": a.address_line1,
        "state": a.state_ut,
        "district": a.district,
        "mobile": decrypt_value(a.to_dict().get("mobile_number")) if a.to_dict().get("mobile_number") else None,
        "icaiMemberId": a.icai_member_id
    } for a in accountants]


def map_project_engineers(engineers):
    return [{
        "id": e.id,
        "name": e.engineer_name,
        "email": decrypt_value(e.to_dict().get("email_id")) if e.to_dict().get("email_id") else None,
        "address": e.address_line1,
        "state": e.state_ut,
        "district": e.district,
        "mobile": decrypt_value(e.to_dict().get("mobile_number")) if e.to_dict().get("mobile_number") else None
    } for e in engineers]



# ---------------------------------------------------
# GET ALL ASSOCIATE DETAILS
# ---------------------------------------------------
@associate_bp.route("/associate", methods=["GET"])
def get_all_associate_details():
    try:
        return jsonify({
            "success": True,
            "data": {
                "project_agents": map_project_agents(
                    AgentModel.query.all()
                ),
                "architects": map_architects(
                    Architect.query.all()
                ),
                "structural_engineers": map_structural_engineers(
                    Engineer.query.filter_by(engineer_type="structural").all()
                ),
                "contractors": map_contractors(
                    Contractor.query.all()
                ),
                "accountants": map_accountants(
                    Accountant.query.all()
                ),
                "project_engineers": map_project_engineers(
                    ProjectEngineer.query.all()
                ),
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": "Internal server error"}), 500


# ===================================================
# PROJECT AGENT
# ===================================================
@associate_bp.route("/associate/project-agent", methods=["POST"])
def add_project_agent():
    try:
        data = request.get_json()

        missing = validate_required(data, [
            "rera_registration_no",
            "agent_name",
            "agent_address",
            "mobile_number",
        ])
        if missing:
            return jsonify({"success": False, "message": f"{missing} is required"}), 400

        agent = AgentModel(
            rera_registration_no=data["rera_registration_no"],
            agent_name=data["agent_name"],
            agent_address=data["agent_address"],
            mobile_number=data.get("mobile_number"),
        )

        db.session.add(agent)
        db.session.commit()

        return jsonify({"success": True, "data": agent.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Internal server error"}), 500


@associate_bp.route("/associate/project-agent/<int:agent_id>", methods=["DELETE"])
def delete_project_agent(agent_id):
    try:
        agent = AgentModel.query.get_or_404(agent_id)
        db.session.delete(agent)
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Internal server error"}), 500


# ===================================================
# ARCHITECT
# ===================================================
@associate_bp.route("/associate/architect", methods=["POST"])
def add_architect():

    try:
        data = request.get_json()
        logging.info(f"checkthe input: '{data}'")   
        missing = validate_required(data, [
            "architect_name",
            "address_line1",
            "state_ut",
            "district",
            "pin_code",
            "coa_registration_number",
            "mobile_number",
        ])
        if missing:
            return jsonify({"success": False, "message": f"{missing} is required"}), 400

        architect = Architect(
            architect_name=data["architect_name"],
            email_id=encrypt_value(data.get("email_id")) if data.get("email_id") else None,
            address_line1=data["address_line1"],
            address_line2=data.get("address_line2"),
            state_ut=data["state_ut"],
            district=data["district"],
            pin_code=data["pin_code"],
            year_of_establishment=empty_to_none(data.get("year_of_establishment")),
            number_of_key_projects=empty_to_none(data.get("number_of_key_projects")),
            coa_registration_number=data["coa_registration_number"],
            mobile_number=encrypt_value(data.get("mobile_number")) if data.get("mobile_number") else None,
        )

        db.session.add(architect)
        db.session.commit()

        return jsonify({"success": True, "data": architect.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Internal server error"}), 500


@associate_bp.route("/associate/architect/<int:architect_id>", methods=["DELETE"])
def delete_architect(architect_id):
    try:
        architect = Architect.query.get_or_404(architect_id)
        db.session.delete(architect)
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Internal server error"}), 500


# ===================================================
# STRUCTURAL ENGINEER
# ===================================================
@associate_bp.route("/associate/structural-engineer", methods=["POST"])
def add_structural_engineer():
    try:
        data = request.get_json()

        missing = validate_required(data, [
            "engineer_name",
            "address_line1",
            "state_ut",
            "district",
            "pin_code",
            "licence_number",
            "mobile_number",
        ])
        if missing:
            return jsonify({
                "success": False,
                "message": f"{missing} is required"
            }), 400

        engineer = Engineer(
            engineer_type="structural",
            engineer_name=data["engineer_name"],
            email_id=encrypt_value(data.get("email_id")) if data.get("email_id") else None,
            address_line1=data["address_line1"],
            address_line2=data.get("address_line2"),
            state_ut=data["state_ut"],
            district=data["district"],
            pin_code=data["pin_code"],
            year_of_establishment=empty_to_none(
                data.get("year_of_establishment")
            ),
            number_of_key_projects=empty_to_none(
                data.get("number_of_key_projects")
            ),
            licence_number=data["licence_number"],
            mobile_number=encrypt_value(data.get("mobile_number")) if data.get("mobile_number") else None,
        )

        db.session.add(engineer)
        db.session.commit()

        return jsonify({
            "success": True,
            "data": engineer.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500


# ===================================================
# CONTRACTOR
# ===================================================
@associate_bp.route("/associate/contractor", methods=["POST"])
def add_contractor():
    try:
        data = request.get_json()

        missing = validate_required(data, [
            "application_number",
            "pan_number",
            "nature_of_work",
            "contractor_name",
            "address_line1",
            "state_ut",
            "district",
            "pin_code",
            "mobile_number",
        ])
        if missing:
            return jsonify({
                "success": False,
                "message": f"{missing} is required"
            }), 400

        # 1️⃣ Create contractor (STRINGS ONLY)
        contractor = Contractor(
            nature_of_work=data["nature_of_work"],
            contractor_name=data["contractor_name"],
            email_id= encrypt_value(data.get("email_id")) if data.get("email_id") else None,

            address_line1=data["address_line1"],
            address_line2=data.get("address_line2"),

            state_ut=str(data["state_ut"]),
            district=str(data["district"]),
            pin_code=str(data["pin_code"]),

            year_of_establishment=empty_to_none(
                data.get("year_of_establishment")
            ),
            number_of_key_projects=empty_to_none(
                data.get("number_of_key_projects")
            ),
            mobile_number=encrypt_value(data.get("mobile_number")) if data.get("mobile_number") else None,
        )

        # 2️⃣ Save contractor & get ID
        db.session.add(contractor)
        db.session.flush()  # 🔑 contractor.id available

        # 3️⃣ Link contractor to application
        link = ApplicationAssociate(
            application_number=data["application_number"],
            pan_number=data.get("pan_number"),
            associate_type="contractor",
            associate_id=contractor.id,
        )

        db.session.add(link)
        db.session.commit()

        return jsonify({
            "success": True,
            "data": contractor.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500

# ===================================================
# ACCOUNTANT
# ===================================================
@associate_bp.route("/associate/accountant", methods=["POST"])
def add_accountant():
    try:
        data = request.get_json()

        missing = validate_required(data, [
            "accountant_name",
            "address_line1",
            "state_ut",
            "district",
            "pin_code",
            "icai_member_id",
            "mobile_number",
        ])
        if missing:
            return jsonify({"success": False, "message": f"{missing} is required"}), 400

        accountant = Accountant(
            accountant_name=data["accountant_name"],
            email_id=encrypt_value(data.get("email_id")) if data.get("email_id") else None,
            address_line1=data["address_line1"],
            address_line2=data.get("address_line2"),
            state_ut=data["state_ut"],
            district=data["district"],
            pin_code=data["pin_code"],
            icai_member_id=data["icai_member_id"],
            number_of_key_projects=empty_to_none(data.get("number_of_key_projects")),
            mobile_number=encrypt_value(data.get("mobile_number")) if data.get("mobile_number") else None,
        )

        db.session.add(accountant)
        db.session.commit()

        return jsonify({"success": True, "data": accountant.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Internal server error"}), 500


@associate_bp.route("/associate/accountant/<int:accountant_id>", methods=["DELETE"])
def delete_accountant(accountant_id):
    try:
        accountant = Accountant.query.get_or_404(accountant_id)
        db.session.delete(accountant)
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Internal server error"}), 500


# ===================================================
# PROJECT ENGINEER
# ===================================================
@associate_bp.route("/associate/project-engineer", methods=["POST"])
def add_project_engineer():
    try:
        data = request.get_json()

        # 🔥 STEP 1 DEBUG LOG
        import logging
        logging.warning("🔥 PROJECT ENGINEER PAYLOAD RECEIVED 🔥")
        logging.warning(data)

        missing = validate_required(data, [
            "engineer_name",
            "address_line1",
            "state_ut",
            "district",
            "pin_code",
            "mobile_number",
        ])
        if missing:
            return jsonify({"success": False, "message": f"{missing} is required"}), 400

        engineer = ProjectEngineer(
            engineer_name=data["engineer_name"],
            email_id=encrypt_value(data.get("email_id")) if data.get("email_id") else None,
            address_line1=data["address_line1"],
            address_line2=data.get("address_line2"),
            state_ut=data["state_ut"],
            district=data["district"],
            pin_code=data["pin_code"],
            mobile_number=encrypt_value(data.get("mobile_number")) if data.get("mobile_number") else None,
            number_of_key_projects=empty_to_none(data.get("number_of_key_projects")),
        )

        db.session.add(engineer)
        db.session.flush()

        link = ApplicationAssociate(
            application_number=data["application_number"],
            pan_number=data.get("pan_number"),
            associate_type="project_engineer",
            associate_id=engineer.id
        )

        db.session.add(link)
        db.session.commit()

        return jsonify({
            "success": True,
            "data": engineer.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Internal server error"}), 500



@associate_bp.route("/associate/project-engineer/<int:engineer_id>", methods=["DELETE"])
def delete_project_engineer(engineer_id):
    try:
        engineer = ProjectEngineer.query.get_or_404(engineer_id)
        db.session.delete(engineer)
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Internal server error"}), 500


# ---------------------------------------------------
# SAVE & CONTINUE
# ---------------------------------------------------
@associate_bp.route("/associate/save-and-continue", methods=["POST"])
def save_and_continue():
    return jsonify({
        "success": True,
        "message": "Associate details saved successfully",
        "next_step": "upload_documents"
    }), 200