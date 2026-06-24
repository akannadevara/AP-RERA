from sqlalchemy import Column, Integer, String, Text, DateTime, Date
from app.models.database import db
from app.utils.encryption import decrypt_value


class ProjectRegistration(db.Model):
    __tablename__ = 'project_registrations'
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Application
    application_no = Column(String(50), unique=True, nullable=False)
    promoter_type = Column(String(50), default='individual')
    pan_number = Column(Text, nullable=False)
    # Bank Details
    bank_state = Column(String(100))
    bank_name = Column(String(200))
    branch_name = Column(String(200))
    account_no = Column(String(50))
    account_holder = Column(String(200))
    ifsc = Column(String(11))

    # Promoter Details
    name = Column(String(200), nullable=False)
    father_name = Column(String(200))
    aadhaar = Column(Text)
    mobile = Column(Text, nullable=False)
    landline = Column(String(15))
    email = Column(Text, nullable=False)
    promoter_website = Column(String(500))
    state_ut = Column(String(100))
    district = Column(String(100))
    license_no = Column(String(100))
    license_date = Column(Date)
    gst_num = Column(String(15))

    # Other State Registration
    other_state_reg = Column(Text)
    rera_reg_number = Column(String(100))
    rera_state = Column(String(100))
    registration_revoked = Column(Text)

    # Projects Last 5 Years
    last_five_years = Column(Text)
    project_name = Column(String(500))
    project_type = Column(String(100))
    current_status = Column(String(100))
    project_address = Column(Text)
    project_state_ut = Column(String(100))
    project_district = Column(String(100))
    pin_code = Column(String(6))
    survey_no = Column(String(100))

    # Litigations
    litigation = Column(Text)
    case_no = Column(String(100))
    tribunal_place = Column(String(200))
    petitioner_name = Column(String(200))
    respondent_name = Column(String(200))
    case_facts = Column(Text)
    case_status = Column(String(100))
    interim_order = Column(Text)
    final_order_details = Column(Text)

    # Promoter 2
    promoter2 = Column(Text)
    promoter2_is_organization = Column(Text)
    promoter2_is_indian = Column(Text)
    promoter2_name = Column(String(200))
    promoter2_address_line1 = Column(String(500))
    promoter2_address_line2 = Column(String(500))
    promoter2_mobile = Column(Text)
    promoter2_email = Column(Text)
    promoter2_pan_card = Column(Text)

    # =========================
    # FILE UPLOAD COLUMNS
    # =========================
    bank_statement_file = Column(Text)
    pan_file = Column(Text)
    aadhaar_file = Column(Text)
    photograph_file = Column(Text)
    license_certificate_file = Column(Text)
    gst_document_file = Column(Text)
    self_affidavit_file = Column(Text)
    promoter2_documents_file = Column(Text)
    itr_documents_file = Column(Text)
    balance_sheet_file = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        """Convert model to dictionary with decrypted sensitive fields"""
        return {
            "id": self.id,
            "application_no": self.application_no,
            "promoter_type": self.promoter_type,
            "pan_number": decrypt_value(self.pan_number) if self.pan_number else None,
            "bank_state": self.bank_state,
            "bank_name": self.bank_name,
            "branch_name": self.branch_name,
            "account_no": decrypt_value(self.account_no) if self.account_no else None,
            "account_holder": self.account_holder,
            "ifsc": decrypt_value(self.ifsc) if self.ifsc else None,
            "name": self.name,
            "father_name": self.father_name,
            "aadhaar": decrypt_value(self.aadhaar) if self.aadhaar else None,
            "mobile": decrypt_value(self.mobile) if self.mobile else None,
            "landline": self.landline,
            "email": decrypt_value(self.email) if self.email else None,
            "promoter_website": self.promoter_website,
            "state_ut": self.state_ut,
            "district": self.district,
            "license_no": self.license_no,
            "license_date": str(self.license_date) if self.license_date else None,
            "gst_num": self.gst_num,
            "other_state_reg": self.other_state_reg,
            "rera_reg_number": self.rera_reg_number,
            "rera_state": self.rera_state,
            "registration_revoked": self.registration_revoked,
            "last_five_years": self.last_five_years,
            "project_name": self.project_name,
            "project_type": self.project_type,
            "current_status": self.current_status,
            "project_address": self.project_address,
            "project_state_ut": self.project_state_ut,
            "project_district": self.project_district,
            "pin_code": self.pin_code,
            "survey_no": self.survey_no,
            "litigation": self.litigation,
            "case_no": self.case_no,
            "tribunal_place": self.tribunal_place,
            "petitioner_name": self.petitioner_name,
            "respondent_name": self.respondent_name,
            "case_facts": self.case_facts,
            "case_status": self.case_status,
            "interim_order": self.interim_order,
            "final_order_details": self.final_order_details,
            "promoter2": self.promoter2,
            "promoter2_is_organization": self.promoter2_is_organization,
            "promoter2_is_indian": self.promoter2_is_indian,
            "promoter2_name": self.promoter2_name,
            "promoter2_address_line1": self.promoter2_address_line1,
            "promoter2_address_line2": self.promoter2_address_line2,
            "promoter2_mobile": decrypt_value(self.promoter2_mobile) if self.promoter2_mobile else None,
            "promoter2_email": decrypt_value(self.promoter2_email) if self.promoter2_email else None,
            "promoter2_pan_card": decrypt_value(self.promoter2_pan_card) if self.promoter2_pan_card else None,
            "bank_statement_file": self.bank_statement_file,
            "pan_file": self.pan_file,
            "aadhaar_file": self.aadhaar_file,
            "photograph_file": self.photograph_file,
            "license_certificate_file": self.license_certificate_file,
            "gst_document_file": self.gst_document_file,
            "self_affidavit_file": self.self_affidavit_file,
            "promoter2_documents_file": self.promoter2_documents_file,
            "itr_documents_file": self.itr_documents_file,
            "balance_sheet_file": self.balance_sheet_file,
            "created_at": str(self.created_at) if self.created_at else None,
        }


class ProjectWizardModel:

    @staticmethod
    def insert_project(data):
        registration = ProjectRegistration(**data)
        db.session.add(registration)
        db.session.commit()
        return registration

    @staticmethod
    def fetch_all():
        return ProjectRegistration.query.order_by(ProjectRegistration.id.desc()).all()

    @staticmethod
    def fetch_by_application_no(application_no):
        return ProjectRegistration.query.filter_by(application_no=application_no).first()

    # ------------------ Closure --------------------
    # @staticmethod
    # def fetch_closure_projects(pan_number):
    #     from sqlalchemy import text
    #     query = text("""
    #         SELECT
    #             preg.application_no,
    #             preg.name AS promoter_name,
    #             pr.project_name
    #         FROM project_registrations preg
    #         JOIN project_registration pr
    #         ON preg.application_no = pr.application_number
    #         WHERE preg.pan_number = :pan_number
    #         ORDER BY preg.application_no DESC
    #     """)

    #     result = db.session.execute(query, {"pan_number": pan_number}).mappings().all()

    #     return [dict(row) for row in result]
    # @staticmethod
    # def fetch_closure_projects(pan_number):
    #     from sqlalchemy import text
    #     query = text("""
    #         SELECT
    #             preg.application_no,
    #             preg.name AS promoter_name,
    #             pr.project_name
    #         FROM project_registrations preg
    #         JOIN project_registration pr
    #         ON preg.application_no = pr.application_number
    #         WHERE preg.pan_number = :pan_number

    #         UNION

    #         SELECT
    #             ppi.application_no,
    #             ppi.promoter_name,
    #             ppo.project_name
    #         FROM promoter_profile_other_t_indv ppi
    #         JOIN past_projects_other_t_indv ppo
    #         ON ppi.application_no = ppo.application_no
    #         WHERE ppi.pan_number = :pan_number

    #         ORDER BY application_no DESC
    #     """)
    #     result = db.session.execute(query, {"pan_number": pan_number}).mappings().all()
    #     return [dict(row) for row in result]
    # @staticmethod
    # def fetch_closure_projects(pan_number):
    #     from sqlalchemy import text
    #     query = text("""
    #         SELECT
    #             preg.application_no,
    #             preg.name AS promoter_name,
    #             pr.project_name
    #         FROM project_registrations preg
    #         JOIN project_registration pr
    #         ON preg.application_no = pr.application_number
    #         WHERE preg.pan_number = :pan_number

    #         UNION

    #         SELECT
    #             ppi.application_no,
    #             ppi.organization_name AS promoter_name,
    #             ppo.project_name
    #         FROM promoter_profile_other_t_indv ppi
    #         JOIN past_projects_other_t_indv ppo
    #         ON ppi.application_no = ppo.application_no
    #         WHERE ppi.pan_number = :pan_number

    #         ORDER BY application_no DESC
    #     """)
    #     result = db.session.execute(query, {"pan_number": pan_number}).mappings().all()
    #     return [dict(row) for row in result]