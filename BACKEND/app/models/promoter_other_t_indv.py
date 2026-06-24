from app import db
from app.utils.encryption import decrypt_value

class PromoterOtherTINDV(db.Model):
    __tablename__ = "promoter_profile_other_t_indv"


    id = db.Column(db.Integer, primary_key=True)
    application_no = db.Column(db.String(50), unique=True, nullable=False)

    promoter_type = db.Column(db.String(50))
    type_of_promoter = db.Column(db.String(100))

    organization_name = db.Column(db.String(255))
    registration_number = db.Column(db.String(150))
    registration_date = db.Column(db.Date)
    gst_number = db.Column(db.String(20))
    pan_number = db.Column(db.String(20))

    authorized_signatory_mobile = db.Column(db.String(15))
    authorized_signatory_email = db.Column(db.String(100))
    authorized_signatory_landline = db.Column(db.String(15))
    website = db.Column(db.String(255))

    state = db.Column(db.String(100))
    district = db.Column(db.String(100))

    bank_state = db.Column(db.String(100))
    bank_name = db.Column(db.String(200))
    branch_name = db.Column(db.String(200))
    account_no = db.Column(db.String(20))
    account_holder = db.Column(db.String(200))
    ifsc_code = db.Column(db.String(20))
    bank_statement_path = db.Column(db.Text)

    other_state_reg = db.Column(db.String(10))
    last_five_years = db.Column(db.String(10))
    litigation = db.Column(db.String(10))
    promoter2 = db.Column(db.String(10))
    organization_registration_doc_path = db.Column(db.Text)
    gst_document_path = db.Column(db.Text)
    pan_card_doc_path = db.Column(db.Text)
    address_proof_doc_path = db.Column(db.Text)
    self_affidavit_path = db.Column(db.Text)
    itr_returns_path = db.Column(db.Text)
    balance_sheet_path = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        """Convert model to dictionary with decrypted sensitive fields"""
        return {
            "id": self.id,
            "application_no": self.application_no,
            "promoter_type": self.promoter_type,
            "type_of_promoter": self.type_of_promoter,
            "organization_name": self.organization_name,
            "registration_number": self.registration_number,
            "registration_date": str(self.registration_date) if self.registration_date else None,
            "gst_number": self.gst_number,
            "pan_number": decrypt_value(self.pan_number) if self.pan_number else None,
            "authorized_signatory_mobile": decrypt_value(self.authorized_signatory_mobile) if self.authorized_signatory_mobile else None,
            "authorized_signatory_email": decrypt_value(self.authorized_signatory_email) if self.authorized_signatory_email else None,
            "authorized_signatory_landline": self.authorized_signatory_landline,
            "website": self.website,
            "state": self.state,
            "district": self.district,
            "bank_state": self.bank_state,
            "bank_name": self.bank_name,
            "branch_name": self.branch_name,
            "account_no": decrypt_value(self.account_no) if self.account_no else None,
            "account_holder": self.account_holder,
            "ifsc_code": decrypt_value(self.ifsc_code) if self.ifsc_code else None,
            "bank_statement_path": self.bank_statement_path,
            "other_state_reg": self.other_state_reg,
            "last_five_years": self.last_five_years,
            "litigation": self.litigation,
            "promoter2": self.promoter2,
            "organization_registration_doc_path": self.organization_registration_doc_path,
            "gst_document_path": self.gst_document_path,
            "pan_card_doc_path": self.pan_card_doc_path,
            "address_proof_doc_path": self.address_proof_doc_path,
            "self_affidavit_path": self.self_affidavit_path,
            "itr_returns_path": self.itr_returns_path,
            "balance_sheet_path": self.balance_sheet_path,
            "created_at": str(self.created_at) if self.created_at else None,
        }