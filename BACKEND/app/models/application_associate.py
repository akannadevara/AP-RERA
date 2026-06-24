from app.models.database import db
from app.utils.encryption import decrypt_value


class ApplicationAssociate(db.Model):
    __tablename__ = "application_associates"

    id = db.Column(db.Integer, primary_key=True)
    application_number = db.Column(db.String(50), nullable=False)
    # increased length to store encrypted values
    pan_number = db.Column(db.String(256), nullable=False)
    associate_type = db.Column(db.String(50), nullable=False)
    associate_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "application_number": self.application_number,
            "pan_number": decrypt_value(self.pan_number) if self.pan_number else None,
            "associate_type": self.associate_type,
            "associate_id": self.associate_id,
            "created_at": self.created_at,
        }
