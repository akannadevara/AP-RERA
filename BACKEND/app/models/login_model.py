# app/models/login_model.py

from app.models.database import db
from sqlalchemy import text
from app.utils.encryption import decrypt_value
from app.models.project_wizard import ProjectRegistration

# def get_emails_by_pan(pan_number):

#     pan = pan_number.strip().upper()

#     query = text("""
#         SELECT DISTINCT email
#         FROM project_registrations
#         WHERE UPPER(TRIM(pan_number)) = :pan

#         UNION

#         SELECT DISTINCT authorized_signatory_email
#         FROM promoter_profile_other_t_indv
#         WHERE UPPER(TRIM(pan_number)) = :pan
#     """)

#     result = db.session.execute(
#         query,
#         {"pan": pan}
#     ).fetchall()

#     emails = [row[0] for row in result]

#     return emails

# def get_emails_by_pan(pan_number):

#     pan = pan_number.strip().upper()

#     rows = ProjectRegistration.query.all()

#     emails = []

#     for row in rows:
#         try:
#             db_pan = decrypt_value(row.pan_number)

#             if db_pan.upper() == pan:
#                 emails.append(decrypt_value(row.email))

#         except Exception:
#             pass

#     return emails

def get_emails_by_pan(pan_number):

    pan = pan_number.strip().upper()

    emails = []

    # OLD DATA (plain PAN)
    query = text("""
        SELECT DISTINCT email
        FROM project_registrations
        WHERE UPPER(TRIM(pan_number)) = :pan

        UNION

        SELECT DISTINCT authorized_signatory_email
        FROM promoter_profile_other_t_indv
        WHERE UPPER(TRIM(pan_number)) = :pan
    """)

    result = db.session.execute(
        query,
        {"pan": pan}
    ).fetchall()

    if result:
        emails.extend([row[0] for row in result])

    else:
        # NEW DATA (encrypted PAN)
        rows = ProjectRegistration.query.all()

        for row in rows:
            try:
                db_pan = decrypt_value(row.pan_number)

                if db_pan.upper() == pan:
                    emails.append(decrypt_value(row.email))

            except Exception:
                pass

    return emails


def get_projects_by_pan(pan_number):

    query = text("""
        SELECT
            pr.application_number,
            preg.name AS promoter_name,
            preg.mobile AS promoter_mobile,
            preg.email AS promoter_email,
            preg.pan_number AS pan_number,
            pr.building_plan_no AS ba_no,
            pr.id AS project_id,
            pr.project_name AS project_name,
            pr.project_address1 AS project_address1,

            dt.district_name AS project_district,

            pr.project_mandal AS project_mandal,
            pr.project_village AS project_village,
            pr.project_pincode AS project_pincode,
            pr.building_permission_from AS validity_from,
            pr.building_permission_upto AS validity_to

        FROM project_registration pr

        JOIN project_registrations preg
          ON pr.application_number = preg.application_no
         AND pr.pan_number = preg.pan_number

        LEFT JOIN districts_t dt
          ON pr.project_district::integer = dt.id

        WHERE pr.pan_number = :pan

        ORDER BY pr.application_number
    """)

    result = db.session.execute(
        query,
        {"pan": pan_number}
    ).mappings().all()

    return [dict(row) for row in result]