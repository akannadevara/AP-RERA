from app.models.database import db
from datetime import datetime
import pytz
# Store associate values as plain text; no decryption performed here

IST = pytz.timezone("Asia/Kolkata")


class Accountant(db.Model):
    __tablename__ = 'accountants'
    
    id = db.Column(db.Integer, primary_key=True)
    accountant_name = db.Column(db.String(200), nullable=False)
    email_id = db.Column(db.String(100))
    address_line1 = db.Column(db.String(300), nullable=False)
    address_line2 = db.Column(db.String(300))
    state_ut = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    icai_member_id = db.Column(db.String(100), nullable=False)
    number_of_key_projects = db.Column(db.Integer)
    mobile_number = db.Column(db.String(15), nullable=False)
    created_at = db.Column(
    db.DateTime,
    default=lambda: datetime.now(IST).replace(tzinfo=None)
    )
    updated_at = db.Column(
    db.DateTime,
    default=lambda: datetime.now(IST).replace(tzinfo=None),
    onupdate=lambda: datetime.now(IST).replace(tzinfo=None)
    )

    
    def to_dict(self):
        return {
            'id': self.id,
            'accountant_name': self.accountant_name,
            'email_id': self.email_id if self.email_id else None,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'state_ut': self.state_ut,
            'district': self.district,
            'pin_code': self.pin_code,
            'icai_member_id': self.icai_member_id,
            'number_of_key_projects': self.number_of_key_projects,
            'mobile_number': self.mobile_number if self.mobile_number else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }