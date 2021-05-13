#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql as pg
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# imported above
from models import *


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    sortedList = []
    list = Venue.query.order_by('state', 'city').all()
    # print(list[0].name, len(sortedList))
    for venue in list:
        if len(sortedList) == 0:
            sortedList.append({
                "city": venue.city,
                "state": venue.state,
                "venues": [{
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": 0,
                }]
            })
        else:
            currentState = sortedList[len(sortedList)-1]['state']
            currentCity = sortedList[len(sortedList)-1]['city']
            if (currentState == venue.state) and (currentCity == venue.city):
                sortedList[len(sortedList)-1]['venues'].append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": 0,
                })
            else:
                sortedList.append({
                    "city": venue.city,
                    "state": venue.state,
                    "venues": [{
                        "id": venue.id,
                        "name": venue.name,
                        "num_upcoming_shows": 0,
                    }]
                })

    return render_template('pages/venues.html', areas=sortedList)


@ app.route('/venues/search', methods=['POST'])
def search_venues():
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search = request.form['search_term']
    results_venues = db.session.query(Venue).filter(Venue.name.ilike(f'%{search}%')).all()
    results_genres = Venue.query.filter(Venue.genres.any(f"{search}")).all()
    temp_results = results_venues + results_genres
    total_results = []
    for i in temp_results:
        if i not in total_results: 
            total_results.append(i)
    count = len(total_results)
    response = {
        "count": count,
        "data": total_results
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    showsAtVenue = Show.query.filter(Show.venue_id == venue_id).all()
    upcoming = Show.query.filter(Show.venue_id == venue_id, Show.start_time > datetime.now()).all()
    past = Show.query.filter(Show.venue_id == venue_id, Show.start_time <= datetime.now()).all()
    upcoming_list = []
    past_list = []
    for up in upcoming:
        z = Artist.query.filter(Artist.id == up.artist_id).first()
        upcoming_list.append({
            "artist_image_link": z.image_link,
            "start_time": format_datetime(str(up.start_time)),
            "artist_id": up.artist_id,
            "artist_name": z.name
        })

    for pa in past:
        z = Artist.query.filter(Artist.id == pa.artist_id).first()
        past_list.append({
            "artist_image_link": z.image_link,
            "start_time": format_datetime(str(pa.start_time)),
            "artist_id": pa.artist_id,
            "artist_name": z.name
        })

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_list,
        "upcoming_shows": upcoming_list,
        "past_shows_count": len(past),
        "upcoming_shows_count": len(upcoming)
        }
    
    return render_template('pages/show_venue.html', venue=data)

#  ----------------------------------------------------------------


#  Create Venue
@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    data = request.form
    seekTalent = True if data.get('seeking_talent', False) else False
    genreList = request.form.getlist('genres')
    try:
        venue = Venue(name=data['name'], city=data['city'], state=data['state'],
                      address=data['address'], phone=data['phone'], genres=genreList,
                      facebook_link=data['facebook_link'], image_link=data['image_link'],
                      website_link=data['website_link'], seeking_description=data['seeking_description'],
                      seeking_talent=seekTalent)
        db.session.add(venue)
        db.session.commit()
        print(venue)
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
        print("done mate!!!")
    if error:
        flash('Error: Venue ' + request.form['name'] + ' could not be added!')
        # abort(500)
    else:
        return render_template('pages/home.html')

    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@ app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    data = Artist.query.order_by('name').all()
    return render_template('pages/artists.html', artists=data)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    search = request.form['search_term']
    results_artists = db.session.query(Artist).filter(Artist.name.ilike(f'%{search}%')).all()
    results_genres = Artist.query.filter(Artist.genres.any(f"{search}")).all()
    temp_results = results_artists + results_genres
    total_results = []
    for i in temp_results:
        if i not in total_results: 
            total_results.append(i)
    count = len(total_results)
    response = {
        "count": count,
        "data": total_results
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist = Artist.query.get(artist_id)
    showsForArtist = Show.query.filter(Show.artist_id == artist_id).all()
    upcoming = Show.query.filter(Show.artist_id == artist_id, Show.start_time >= datetime.now()).all()
    past = Show.query.filter(Show.artist_id == artist_id, Show.start_time < datetime.now()).all()
    upcoming_list = []
    past_list = []
    for up in upcoming:
        z = Venue.query.filter(Venue.id == up.venue_id).first()
        upcoming_list.append({
            "venue_image_link": z.image_link,
            "start_time": format_datetime(str(up.start_time)),
            "venue_id": up.venue_id,
            "venue_name": z.name
        })

    for pa in past:
        z = Venue.query.filter(Venue.id == up.venue_id).first()
        past_list.append({
            "venue_image_link": z.image_link,
            "start_time": format_datetime(str(pa.start_time)),
            "venue_id": pa.venue_id,
            "venue_name": z.name
        })

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venues,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_list,
        "upcoming_shows": upcoming_list,
        "past_shows_count": len(past),
        "upcoming_shows_count": len(upcoming)
  }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website_link
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.seeking_venue.data = artist.seeking_venues
    form.seeking_description.data = artist.seeking_description
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    data = request.form
    error = False
    try:
        artist.name = data['name']
        artist.city = data['city']
        artist.state = data['state']
        artist.phone = data['phone']
        artist.genres = data.getlist('genres')
        artist.facebook_link = data['facebook_link']
        artist.image_link = data['image_link']
        artist.website_link = data['website_link']
        artist.seeking_venues = True if data.get(
            'seeking_venue', False) else False
        artist.seeking_description = data['seeking_description']
        db.session.merge(artist)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
        print("done the artist update mate!!!")
    if error:
        flash('Error: Artist ' +
              request.form['name'] + ' could not be updated!')
        abort(500)
    else:
        return redirect(url_for('show_artist', artist_id=artist_id))


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.website_link.data = venue.website_link
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    data = request.form
    error = False
    try:
        venue.name = data['name']
        venue.city = data['city']
        venue.state = data['state']
        venue.address = data['address']
        venue.phone = data['phone']
        venue.genres = data.getlist('genres')
        venue.facebook_link = data['facebook_link']
        venue.image_link = data['image_link']
        venue.website_link = data['website_link']
        venue.seeking_talent = True if data.get(
            'seeking_talent', False) else False
        venue.seeking_description = data['seeking_description']
        db.session.merge(venue)
        db.session.commit()
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
        print("done the update mate!!!")
    if error:
        flash('Error: Venue ' +
              request.form['name'] + ' could not be updated!')
        # abort(500)
    else:
        return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    error = False
    data = request.form
    seekVenue = True if data.get('seeking_venue', False) else False
    genreList = request.form.getlist('genres')
    print(data, genreList, seekVenue)

    try:
        artist = Artist(name=data['name'], city=data['city'], state=data['state'],
                        phone=data['phone'], genres=genreList,
                        facebook_link=data['facebook_link'], image_link=data['image_link'],
                        website_link=data['website_link'], seeking_description=data['seeking_description'],
                        seeking_venues=seekVenue)
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
        print("done mate!!!")
    if error:
        flash('Error: Artist ' + request.form['name'] + ' could not be added!')
        abort(500)
    else:
        return render_template('pages/home.html')
    # on successful db insert, flash success


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    # displays list of shows at /shows
    shows = Show.query.order_by('artist_id','start_time').all()
    data = []
    for show in shows:
        data.append(
            {
                "venue_id": show.venue_id,
                "venue_name": Venue.query.get(show.venue_id).name,
                "artist_id": show.artist_id,
                "artist_name": Artist.query.get(show.artist_id).name,
                "artist_image_link": Artist.query.get(show.artist_id).image_link,
                "start_time": format_datetime(str(show.start_time))
            }
        )
    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    data = request.form
    error = False
    try:
        show = Show(artist_id=data['artist_id'], venue_id=data['venue_id'], start_time=(data['start_time']))
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
        print("done adding show mate!!!")
    if error:
        flash('Error: Show could not be added!')
    else:
        return render_template('pages/home.html')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
