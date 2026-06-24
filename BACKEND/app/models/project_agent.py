from app.models.database import db
# Store associate values as plain text; no decryption performed here

from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")
class AgentModel(db.Model):
    __tablename__ = 'project_agents'

    id = db.Column(db.Integer, primary_key=True)
    rera_registration_no = db.Column(db.String(100), nullable=False)
    agent_name = db.Column(db.String(200), nullable=False)
    agent_address = db.Column(db.Text, nullable=False)
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
            'rera_registration_no': self.rera_registration_no,
            'agent_name': self.agent_name,
            'agent_address': self.agent_address,
            'mobile_number': self.mobile_number if self.mobile_number else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
