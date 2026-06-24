from app.models.database import db
import pytz
from datetime import datetime
# Store associate values as plain text; no decryption performed here

IST = pytz.timezone("Asia/Kolkata")

class Architect(db.Model):
    __tablename__ = 'architects'

    id = db.Column(db.Integer, primary_key=True)

    architect_name = db.Column(db.String(200), nullable=False)
    email_id = db.Column(db.String(100), nullable=True)

    address_line1 = db.Column(db.String(300), nullable=False)
    address_line2 = db.Column(db.String(300), nullable=True)

    state_ut = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)

    # Optional numeric fields
    year_of_establishment = db.Column(db.Integer, nullable=True)
    number_of_key_projects = db.Column(db.Integer, nullable=True)

    coa_registration_number = db.Column(db.String(100), nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)

    created_at = db.Column(
    db.DateTime,
    default=lambda: datetime.now(IST).replace(tzinfo=None),
    nullable=False
    )
    updated_at = db.Column(
    db.DateTime,
    default=lambda: datetime.now(IST).replace(tzinfo=None),
    onupdate=lambda: datetime.now(IST).replace(tzinfo=None),
    nullable=False
    )


    def to_dict(self):
        return {
            "id": self.id,
            "architect_name": self.architect_name,
            "email_id": self.email_id if self.email_id else None,
            "address_line1": self.address_line1,
            "address_line2": self.address_line2,
            "state_ut": self.state_ut,
            "district": self.district,
            "pin_code": self.pin_code,
            "year_of_establishment": self.year_of_establishment,
            "number_of_key_projects": self.number_of_key_projects,
            "coa_registration_number": self.coa_registration_number,
            "mobile_number": self.mobile_number if self.mobile_number else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }