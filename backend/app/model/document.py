from app import db

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kra_pin = db.Column(db.String(20), nullable=True)
    taxpayer_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    police_clearance_ref = db.Column(db.String(50), nullable=True)
    id_number = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f'<Document {self.kra_pin or self.police_clearance_ref}>'