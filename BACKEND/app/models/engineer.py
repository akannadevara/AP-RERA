from app.models.database import db
from datetime import datetime
# Store associate values as plain text; no decryption performed here

class Engineer(db.Model):
    __tablename__ = 'engineers'
    
    id = db.Column(db.Integer, primary_key=True)
    
    engineer_type = db.Column(db.String(50), nullable=False)  # 'stru'project'
    engineer_name = db.Column(db.String(200), nullable=False)
    email_id = db.Column(db.String(100))
    address_line1 = db.Column(db.String(300), nullable=False)
    address_line2 = db.Column(db.String(300))
    state_ut = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    year_of_establishment = db.Column(db.Integer)
    number_of_key_projects = db.Column(db.Integer)
    licence_number = db.Column(db.String(100), nullable=False)  # Local Authority Licence Number
    mobile_number = db.Column(db.String(15), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'engineer_type': self.engineer_type,
            'engineer_name': self.engineer_name,
            'email_id': self.email_id if self.email_id else None,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'state_ut': self.state_ut,
            'district': self.district,
            'pin_code': self.pin_code,
            'year_of_establishment': self.year_of_establishment,
            'number_of_key_projects': self.number_of_key_projects,
            'licence_number': self.licence_number,
            'mobile_number': self.mobile_number if self.mobile_number else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }