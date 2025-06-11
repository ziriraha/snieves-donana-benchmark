import uuid
from .extensions import db

class Park(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String)

    def to_json(self):
        return {
            'code': self.code,
            'name': self.name
        }

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name
        }

    def __repr__(self):
        return f'<Park {self.code}>'

class Species(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False, unique=True)
    scientific_name = db.Column(db.String)
    name = db.Column(db.String)

    def to_json(self):
        return {
            'code': self.code,
            'scientific_name': self.scientific_name,
            'name': self.name
        }

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'scientific_name': self.scientific_name,
            'name': self.name
        }

    def __repr__(self):
        return f'<Species {self.code}>'

class Image(db.Model):
    id = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    path = db.Column(db.Text, nullable=False, unique=True)
    date = db.Column(db.DateTime)
    bbox = db.Column(db.JSON)

    species_id = db.Column(db.Integer, db.ForeignKey('species.id'), nullable=False, index=True)
    species = db.relationship('Species', backref=db.backref('images'))

    park_id = db.Column(db.Integer, db.ForeignKey('park.id'), nullable=False, index=True)
    park = db.relationship('Park', backref=db.backref('images'))

    def to_json(self):
        return {
            'id': str(self.id),
            'date': self.date.isoformat() if self.date else None,
            **({'bbox': self.bbox} if self.species.code != 'emp' else {}),
            'species': self.species.code,
            'park': self.park.code
        }
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'path': self.path,
            'date': self.date.isoformat() if self.date else None,
            'bbox': self.bbox,
            'species': self.species.to_dict(),
            'species_id': self.species.id,
            'park': self.park.to_dict(),
            'park_id': self.park.id
        }

    def __repr__(self):
        return f'<Image {self.path}>'