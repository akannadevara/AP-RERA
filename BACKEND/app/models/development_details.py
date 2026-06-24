# import logging
# from sqlalchemy import text
# from app.models.database import db


# class DevelopmentDetailsModel:
#     """
#     Handles insert and fetch operations for development_details table
#     """

#     # -------------------------------------------------
#     # INSERT DEVELOPMENT DETAILS
#     # -------------------------------------------------
#     @staticmethod
#     def insert(data):
#         logging.info("===== INSERT development_details START =====")
#         logging.info(f"Input data: {data}")

#         query = text("""
#             INSERT INTO development_details (
#                 project_id,
#                 project_type,
#                 development_details,
#                 external_development_work,
#                 work_description,
#                 work_type,
#                 pan_number,
#                 application_number
#             )
#             VALUES (
#                 :project_id,
#                 :project_type,
#                 CAST(:development_details AS jsonb),
#                 CAST(:external_development_work AS jsonb),
#                 :work_description,
#                 :work_type,
#                 :pan_number,
#                 :application_number
#             )
#             RETURNING id
#         """)

#         result = db.session.execute(query, {
#             "project_id": data["project_id"],
#             "project_type": data["project_type"],
#             "development_details": data["development_details"],
#             "external_development_work": data["external_development_work"],
#             "work_description": data["work_description"],
#             "work_type": data["work_type"],
#             "pan_number": data["pan_number"],
#             "application_number": data["application_number"]
#         })

#         row = result.fetchone()

#         if not row:
#             db.session.rollback()
#             raise Exception("Insert failed: no ID returned")

#         db.session.commit()

#         logging.info(f"Inserted ID from DB: {row.id}")
#         logging.info("===== INSERT development_details END =====")

#         return row

#     # -------------------------------------------------
#     # FETCH LATEST DEVELOPMENT DETAILS (FOR PREVIEW / PDF)
#     # -------------------------------------------------
#     @staticmethod
#     def get_by_application_and_pan(application_number, pan_number):
#         logs = []
#         logs.append("START: Fetch development_details + application_associates")

#         logging.info("===== FETCH development_details + application_associates START =====")

#         # --------------------------------------------------
#         # 1️⃣ DEVELOPMENT DETAILS (LATEST)
#         # --------------------------------------------------
#         dev_query = text("""
#             SELECT id, project_id, project_type, development_details,
#                 external_development_work, work_description, work_type,
#                 pan_number, application_number
#             FROM development_details
#             WHERE application_number = :application_number
#             AND pan_number = :pan_number
#             ORDER BY id DESC
#             LIMIT 1
#         """)

#         dev_result = db.session.execute(
#             dev_query,
#             {
#                 "application_number": application_number,
#                 "pan_number": pan_number
#             }
#         ).mappings().first()

#         development_data = dict(dev_result) if dev_result else {}
#         logs.append(f"Development record found: {'YES' if dev_result else 'NO'}")

#         # --------------------------------------------------
#         # 2️⃣ APPLICATION ASSOCIATES (MERGED)
#         # --------------------------------------------------
#         associates_data = {
#             "agents": [],
#             "architects": [],
#             "contractors": [],
#             "engineers": [],
#             "accountants": [],
#             "project engineers": []
        
        
#         }

#         # 🔹 Project Agents
#         agent_query = text("""
#             SELECT *
#             FROM project_agents
#             WHERE application_number = :application_number
#         """)

#         agent_results = db.session.execute(
#             agent_query,
#             {"application_number": application_number}
#         ).mappings().all()

#         associates_data["agents"] = [dict(row) for row in agent_results] if agent_results else []
#         logs.append(f"Agents fetched: {len(associates_data['agents'])}")

#         # 🔹 Architects
#         architect_query = text("""
#             SELECT *
#             FROM architects
#             WHERE application_number = :application_number
#         """)
#         logging.info(f"checkthe querrykjdfskljsd: '{architect_query}'")     
#         architect_results = db.session.execute(
#             architect_query,
#             {"application_number": application_number}
#         ).mappings().all()

#         associates_data["architects"] = [dict(row) for row in architect_results] if architect_results else []
#         logs.append(f"Architects fetched: {len(associates_data['architects'])}")
#         # 🔹 Contractors
#         contractor_query = text("""
#             SELECT *
#             FROM contractors
#             WHERE application_number = :application_number
#         """)
#         logging.info(f"checkthe querrykjdfskljsd: '{contractor_query}'")
#         contractor_results = db.session.execute(
#             contractor_query,
#             {"application_number": application_number}
#         ).mappings().all()

#         associates_data["contractors"] = [dict(row) for row in contractor_results] if contractor_results else []
#         logs.append(f"Contractors fetched: {len(associates_data['contractors'])}")
#         # 🔹 Engineers
#         engineer_query = text("""
#             SELECT *
#             FROM engineers
#             WHERE application_number = :application_number
#         """)
#         logging.info(f"checkthe querrykjdfskljsd: '{engineer_query}'")
#         engineer_results = db.session.execute(
#             engineer_query,
#             {"application_number": application_number}
#         ).mappings().all()

#         associates_data["engineers"] = [dict(row) for row in engineer_results] if engineer_results else []
#         logs.append(f"Engineers fetched: {len(associates_data['engineers'])}")
#         # 🔹 Accountants
#         accountant_query = text("""
#             SELECT *
#             FROM accountants
#             WHERE application_number = :application_number
#         """)
#         logging.info(f"checkthe querrykjdfskljsd: '{accountant_query}'")
#         accountant_results = db.session.execute(
#             accountant_query,
#             {"application_number": application_number}
#         ).mappings().all()

#         associates_data["accountants"] = [dict(row) for row in accountant_results] if accountant_results else []
#         logs.append(f"Accountants fetched: {len(associates_data['accountants'])}")
#         # 🔹 Project Engineers
#         project_engineer_query = text("""
#     SELECT *
#     FROM project_engineers
#     WHERE application_numnber = :application_number
# """)

#         logging.info(f"checkthe querrykjdfskljsd: '{project_engineer_query}'")
#         project_engineer_results = db.session.execute(
#             project_engineer_query,
#             {"application_number": application_number}
#         ).mappings().all()

#         associates_data["project engineers"] = [dict(row) for row in project_engineer_results] if project_engineer_results else []
#         logs.append(f"Project Engineers fetched: {len(associates_data['project engineers'])}")

#         # --------------------------------------------------
#         # 3️⃣ MERGE OUTPUT
#         # --------------------------------------------------
#         final_data = {
#             **development_data,
#             "application_associates": associates_data,
#             "_logs": logs  # 👈 logs included in response
#         }

#         logging.info(
#             f"===== FETCH END | Dev: {'YES' if dev_result else 'NO'} | "
#             f"Agents: {len(associates_data['agents'])} | "
#             f"Architects: {len(associates_data['architects'])} ====="

#         )

#         return final_data if final_data else None


import logging
from sqlalchemy import text
from app.models.database import db
from app.utils.encryption import decrypt_value


class DevelopmentDetailsModel:

    @staticmethod
    def insert(data):
        logging.info("===== INSERT development_details START =====")

        query = text("""
            INSERT INTO development_details (
                project_id,
                project_type,
                development_details,
                external_development_work,
                other_external_works,
                work_description,
                work_type,
                pan_number,
                application_number
            )
            VALUES (
                :project_id,
                :project_type,
                CAST(:development_details AS jsonb),
                CAST(:external_development_work AS jsonb),
                CAST(:other_external_works AS jsonb),
                :work_description,
                :work_type,
                :pan_number,
                :application_number
            )
            RETURNING id
        """)

        result = db.session.execute(query, {
            "project_id": data["project_id"],
            "project_type": data["project_type"],
            "development_details": data["development_details"],
            "external_development_work": data["external_development_work"],
            "other_external_works": data["other_external_works"],
            "work_description": data["work_description"],
            "work_type": data["work_type"],
            "pan_number": data["pan_number"],
            "application_number": data["application_number"]
        })

        row = result.fetchone()

        if not row:
            db.session.rollback()
            raise Exception("Insert failed")

        db.session.commit()
        logging.info(f"Inserted ID: {row.id}")
        return row

    @staticmethod
    def get_by_application_and_pan(application_number, pan_number):
        query = text("""
            SELECT
                id,
                project_id,
                project_type,
                development_details,
                external_development_work,
                work_description,
                work_type,
                pan_number,
                application_number,
                created_at
            FROM development_details
           WHERE application_number = :application_number
ORDER BY id DESC
        """)

        result_rows = db.session.execute(
            query,
            {
                "application_number": application_number
            }
        ).mappings().all()

        if not result_rows:
            return None

        for row in result_rows:
            db_row = dict(row)
            db_pan = db_row.get("pan_number")

            try:
                compare_pan = decrypt_value(db_pan) if db_pan else db_pan
            except Exception:
                compare_pan = db_pan

            if compare_pan and compare_pan.strip().upper() == pan_number.strip().upper():
                db_row["pan_number"] = compare_pan
                return db_row

        return None


    @staticmethod
    def get_all_by_application_and_pan(application_number, pan_number):
        query = text("""
            SELECT
                id,
                project_id,
                project_type,
                development_details,
                external_development_work,
                other_external_works,
                work_description,
                work_type,
                pan_number,
                application_number,
                created_at
            FROM development_details
            WHERE application_number = :application_number
            ORDER BY id DESC
        """)

        rows = db.session.execute(
            query,
            {
                "application_number": application_number
            }
        ).mappings().all()

        results = []

        for row in rows:
            row_dict = dict(row)
            db_pan = row_dict.get("pan_number")

            try:
                compare_pan = decrypt_value(db_pan) if db_pan else db_pan
            except Exception:
                compare_pan = db_pan

            if compare_pan and compare_pan.strip().upper() == pan_number.strip().upper():
                row_dict["pan_number"] = compare_pan
                results.append(row_dict)

        return results
