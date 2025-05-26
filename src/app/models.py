from . import db

class Park(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    full_name = db.Column(db.String)

    def __repr__(self):
        return f'<Park {self.name}>'

class Species(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    scientific_name = db.Column(db.String)
    common_name = db.Column(db.String)

    def __repr__(self):
        return f'<Species {self.name}>'

class Image(db.Model):
    id = db.Column(db.UUID, primary_key=True)
    path = db.Column(db.Text, nullable=False, unique=True)
    date = db.Column(db.DateTime)
    bbox = db.Column(db.JSON)

    species_id = db.Column(db.Integer, db.ForeignKey('species.id'), nullable=False, index=True)
    species = db.relationship('Species', backref=db.backref('images'))

    park_id = db.Column(db.Integer, db.ForeignKey('park.id'), nullable=False, index=True)
    park = db.relationship('Park', backref=db.backref('images'))

    def __repr__(self):
        return f'<Image {self.path}>'