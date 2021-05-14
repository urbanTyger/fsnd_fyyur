from app import db
from sqlalchemy.dialects import postgresql as pg

# Venues Model
class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(pg.ARRAY(db.String(), dimensions=1), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(200))
    shows = db.relationship('Show', backref='venue_shows', lazy=True)

    def create(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.merge(self)
        db.session.commit()
    
    def close():
        db.session.close()

    def rollback():
        db.session.rollback()

    def __repr__(self):
        return f'<Venue ID: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, genres: {self.genres}>'


# Artist Model
class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venues = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(200))
    shows = db.relationship('Show', backref='artist_shows', lazy=True)

    def create(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.merge(self)
        db.session.commit()
    
    def close():
        db.session.close()

    def rollback():
        db.session.rollback()

    def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name}, genres: {self.genres}>'

# Shows Model
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def create(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.merge(self)
        db.session.commit()
    
    def close():
        db.session.close()

    def rollback():
        db.session.rollback()

    def __repr__(self):
        return f'<Artist ID: {self.artist_id}, VENUE ID: {self.venue_id}, Start Time: {self.start_time}>'