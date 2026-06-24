from app.models.database import db
from datetime import datetime
from app.utils.encryption import decrypt_value


class ProjectUnregisteredDetails(db.Model):
    __tablename__ = "project_unregistered_details_t"

    id = db.Column(db.Integer, primary_key=True)
    s_no = db.Column(db.Integer)
    district = db.Column(db.String(100))
    organisation = db.Column(db.String(255))
    ulb_uda_name = db.Column(db.String(255))
    ba_no = db.Column(db.String(100))
    proceeding_order_date = db.Column(db.Date)
    approved_date = db.Column(db.Date)
    fileno = db.Column(db.String(100))
    lp_no = db.Column(db.String(100))
    owner_name = db.Column(db.String(255))
    owner_mobile_no = db.Column(db.String(20))
    owner_email = db.Column(db.String(100))
    owner_builder_address = db.Column(db.Text)
    building_address = db.Column(db.Text)
    plot_area = db.Column(db.Numeric(12, 2))
    site_area_acres = db.Column(db.Numeric(12, 2))
    approved_bua = db.Column(db.Numeric(12, 2))
    housing_units = db.Column(db.Integer)
    no_of_plots = db.Column(db.Integer)
    landuse_sub_category = db.Column(db.String(255))
    sub_use = db.Column(db.String(255))
    mandal_city = db.Column(db.String(100))
    village_location = db.Column(db.String(255))
    filestatus_vw = db.Column(db.String(100))
    is_ldcc_applied = db.Column(db.Boolean)
    ldcc_approved_on = db.Column(db.Date)
    project_type = db.Column(db.String(20))
    rera_registered = db.Column(db.Boolean, default=False)
    rera_registration_no = db.Column(db.String(100))
    approval_status = db.Column(db.String(30))
    s1_remarks = db.Column(db.Text)
    s2_remarks = db.Column(db.Text)
    s6_remarks = db.Column(db.Text)
    s3_remarks = db.Column(db.Text)
    s4_remarks = db.Column(db.Text)
    s5_remarks = db.Column(db.Text)
    first_notice_doc_path = db.Column(db.Text)
    rera_personal_notice_doc_path = db.Column(db.Text)
    sh_document_path = db.Column(db.Text)
    aprera_register_status = db.Column(db.String(30))
    s1_authority_id = db.Column(db.String(100))
    s2_authority_id = db.Column(db.String(100))
    s3_authority_id = db.Column(db.String(100))
    s4_authority_id = db.Column(db.String(100))
    s5_authority_id = db.Column(db.String(100))
    s6_authority_id = db.Column(db.String(100))
    rera_register_no = db.Column(db.String(100))
    pan_number = db.Column(db.String(10))
    first_notice_sent_date = db.Column(db.Date)
    secound_notice_sent_date = db.Column(db.Date)
    exemption_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "s_no": self.s_no,
            "district": self.district,
            "organisation": self.organisation,
            "ulb_uda_name": self.ulb_uda_name,
            "ba_no": self.ba_no,
            "proceeding_order_date": (
                str(self.proceeding_order_date) if self.proceeding_order_date else None
            ),
            "approved_date": str(self.approved_date) if self.approved_date else None,
            "fileno": self.fileno,
            "lp_no": self.lp_no,
            "owner_name": self.owner_name,
            "owner_mobile_no": decrypt_value(self.owner_mobile_no) if self.owner_mobile_no else None,
            "owner_email": decrypt_value(self.owner_email) if self.owner_email else None,
            "owner_builder_address": self.owner_builder_address,
            "building_address": self.building_address,
            "plot_area": float(self.plot_area) if self.plot_area else None,
            "site_area_acres": (
                float(self.site_area_acres) if self.site_area_acres else None
            ),
            "approved_bua": float(self.approved_bua) if self.approved_bua else None,
            "housing_units": self.housing_units,
            "no_of_plots": self.no_of_plots,
            "landuse_sub_category": self.landuse_sub_category,
            "sub_use": self.sub_use,
            "mandal_city": self.mandal_city,
            "village_location": self.village_location,
            "filestatus_vw": self.filestatus_vw,
            "is_ldcc_applied": self.is_ldcc_applied,
            "ldcc_approved_on": (
                str(self.ldcc_approved_on) if self.ldcc_approved_on else None
            ),
            "project_type": self.project_type,
            "rera_registered": self.rera_registered,
            "rera_registration_no": self.rera_registration_no,
            "approval_status": self.approval_status,
            "s1_remarks": self.s1_remarks,
            "s2_remarks": self.s2_remarks,
            "s3_remarks": self.s3_remarks,
            "s4_remarks": self.s4_remarks,
            "s5_remarks": self.s5_remarks,
            "s6_remarks": self.s6_remarks,
            "first_notice_doc_path": self.first_notice_doc_path,
            "rera_personal_notice_doc_path": self.rera_personal_notice_doc_path,
            "sh_document_path": self.sh_document_path,
            "aprera_register_status": self.aprera_register_status,
            "s1_authority_id": self.s1_authority_id,
            "s2_authority_id": self.s2_authority_id,
            "s3_authority_id": self.s3_authority_id,
            "s4_authority_id": self.s4_authority_id,
            "s5_authority_id": self.s5_authority_id,
            "s6_authority_id": self.s6_authority_id,
            "pan_number": decrypt_value(self.pan_number) if self.pan_number else None,
            "secound_notice_sent_date": (
                str(self.secound_notice_sent_date)
                if self.secound_notice_sent_date
                else None
            ),
            "first_notice_sent_date": (
                str(self.first_notice_sent_date)
                if self.first_notice_sent_date
                else None
            ),
            "rera_register_no": self.rera_register_no,
            "exemption_id": self.exemption_id,
            "created_at": str(self.created_at) if self.created_at else None,
        }