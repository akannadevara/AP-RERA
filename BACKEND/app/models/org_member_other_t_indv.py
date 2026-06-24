from app import db
from app.utils.encryption import decrypt_value

class OrgMemberOtherTINDV(db.Model):
    __tablename__ = "org_members_other_t_indv"

    id = db.Column(db.Integer, primary_key=True)
    application_no = db.Column(
        db.String(50),
        db.ForeignKey("promoter_profile_other_t_indv.application_no", ondelete="CASCADE")
    )

    is_indian = db.Column(db.String(20))
    name = db.Column(db.String(200))
    designation = db.Column(db.String(100))
    mobile = db.Column(db.String(15))
    email = db.Column(db.String(100))

    address_line1 = db.Column(db.Text)
    address_line2 = db.Column(db.Text)
    state = db.Column(db.String(100))
    district = db.Column(db.String(100))
    pin_code = db.Column(db.String(10))

    aadhaar = db.Column(db.String(20))
    pan = db.Column(db.String(20))
    din = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        """Convert model to dictionary with decrypted sensitive fields"""
        return {
            "id": self.id,
            "application_no": self.application_no,
            "is_indian": self.is_indian,
            "name": self.name,
            "designation": self.designation,
            "mobile": decrypt_value(self.mobile) if self.mobile else None,
            "email": decrypt_value(self.email) if self.email else None,
            "address_line1": self.address_line1,
            "address_line2": self.address_line2,
            "state": self.state,
            "district": self.district,
            "pin_code": self.pin_code,
            "aadhaar": decrypt_value(self.aadhaar) if self.aadhaar else None,
            "pan": decrypt_value(self.pan) if self.pan else None,
            "din": self.din,
            "created_at": str(self.created_at) if self.created_at else None,
        }
