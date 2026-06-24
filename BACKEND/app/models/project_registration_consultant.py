from app.models.database import db
from datetime import datetime
from app.utils.encryption import decrypt_value


class ProjectRegistrationConsultant(db.Model):
    __tablename__ = "project_registration_consultant_details"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    application_number = db.Column(db.String(50), nullable=False)
    pan_number = db.Column(db.String(20), nullable=False)

    consultancy_name = db.Column(db.String(200))
    consultant_name = db.Column(db.String(150))
    mobile_number = db.Column(db.String(10))
    email_id = db.Column(db.String(100))
    address = db.Column(db.String(500))

    declaration_name = db.Column(db.String(200))
    declaration_accept = db.Column(db.String(1))  # Y / N
    note1_accept = db.Column(db.String(1))        # Y / N
    note2_accept = db.Column(db.String(1))        # Y / N

    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    # Prevent duplicate application + pan
    __table_args__ = (
        db.UniqueConstraint(
            "application_number",
            "pan_number",
            name="uq_application_pan_consultant"
        ),
    )

    def to_dict(self):
        return {
            "application_number": self.application_number,
            "pan_number": decrypt_value(self.pan_number) if self.pan_number else None,
            "consultancy_name": self.consultancy_name,
            "consultant_name": self.consultant_name,
            "mobile_number": decrypt_value(self.mobile_number) if self.mobile_number else None,
            "email_id": decrypt_value(self.email_id) if self.email_id else None,
            "address": self.address,
            "declaration_name": self.declaration_name,
            "declaration_accept": self.declaration_accept,
            "note1_accept": self.note1_accept,
            "note2_accept": self.note2_accept,
            "created_on": self.created_on
        }