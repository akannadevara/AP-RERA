from app import db
from app.utils.encryption import decrypt_value

class Promoter2OtherTINDV(db.Model):
    __tablename__ = "promoter2_other_t_indv"

    id = db.Column(db.Integer, primary_key=True)
    application_no = db.Column(
        db.String(50),
        db.ForeignKey("promoter_profile_other_t_indv.application_no", ondelete="CASCADE")
    )

    is_organization = db.Column(db.String(10))
    is_indian = db.Column(db.String(20))

    name = db.Column(db.String(200))
    state = db.Column(db.String(100))
    district = db.Column(db.String(100))

    address_line1 = db.Column(db.Text)
    address_line2 = db.Column(db.Text)
    pin_code = db.Column(db.String(10))

    mobile = db.Column(db.String(15))
    email = db.Column(db.String(100))

    pan_card = db.Column(db.String(20))
    aadhaar = db.Column(db.String(20))
    passport_no = db.Column(db.String(50))
    supporting_document_path = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        """Convert model to dictionary with decrypted sensitive fields"""
        return {
            "id": self.id,
            "application_no": self.application_no,
            "is_organization": self.is_organization,
            "is_indian": self.is_indian,
            "name": self.name,
            "state": self.state,
            "district": self.district,
            "address_line1": self.address_line1,
            "address_line2": self.address_line2,
            "pin_code": self.pin_code,
            "mobile": decrypt_value(self.mobile) if self.mobile else None,
            "email": decrypt_value(self.email) if self.email else None,
            "pan_card": decrypt_value(self.pan_card) if self.pan_card else None,
            "aadhaar": decrypt_value(self.aadhaar) if self.aadhaar else None,
            "passport_no": self.passport_no,
            "supporting_document_path": self.supporting_document_path,
            "created_at": str(self.created_at) if self.created_at else None,
        }