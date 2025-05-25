from . import db

class Park(db.Model):
    __tablename__ = 'park'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    full_name = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f'<Park {self.name}>'

class Species(db.Model):
    __tablename__ = 'species'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    scientific_name = db.Column(db.String, nullable=True)
    common_name = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f'<Species {self.name}>'

class Image(db.Model):
    __tablename__ = 'image'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.Text, nullable=False, unique=True)
    date = db.Column(db.DateTime, nullable=True)

    # Bounding box coordinates
    bbox_x = db.Column(db.Float, nullable=True)
    bbox_y = db.Column(db.Float, nullable=True)
    bbox_w = db.Column(db.Float, nullable=True)
    bbox_h = db.Column(db.Float, nullable=True)

    species_id = db.Column(db.Integer, db.ForeignKey('species.id'), nullable=False, index=True)
    species = db.relationship('Species', backref=db.backref('images'))

    park_id = db.Column(db.Integer, db.ForeignKey('park.id'), nullable=False, index=True)
    park = db.relationship('Park', backref=db.backref('images'))

    def __repr__(self):
        return f'<Image {self.path}>'