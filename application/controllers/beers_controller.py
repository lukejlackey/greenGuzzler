from application import app
from application.models.breweries_model import Brewery
from application.models.users_model import User
from application.models.beers_model import Beer
from flask import render_template, redirect, request, session

@app.route('/beers')
def show_all_beer():
    current_user = User.get_user(id=session['logged_user']) if 'logged_user' in session else False
    all_beers = Beer.get_all_beers()
    sorted_beers = []
    for t in Beer.BEER_TYPES:
        sorted_beers.append([beer for beer in all_beers if beer.type == t])
    return render_template('beers.html', user=current_user, beers=sorted_beers)

@app.route('/beers/<int:id>')
def show_beer(id):
    if 'logged_user' not in session:
        return redirect('/login')
    current_user = User.get_user(id=session['logged_user']) if 'logged_user' in session else False
    current_beer = Beer.get_beer(id)
    return render_template('beer.html', user=current_user, beer=current_beer)

@app.route('/beers/new')
def create_beer():
    if 'logged_user' not in session:
        return redirect('/login')
    current_user = User.get_user(id=session['logged_user'])
    breweries = Brewery.get_all_breweries()
    return render_template('new_beer.html', user=current_user, breweries=breweries)

@app.route('/beers/new/create', methods=['POST'])
def create_new_beer():
    if 'logged_user' not in session:
        return redirect('/login')
    if Beer.validate_create_beer(request.form):
        new_beer_data = {
            **request.form,
            'poster_id' : session['logged_user']
        }
        new_beer = Beer.create_new_beer(new_beer_data)
        if new_beer:
            new_rating = Beer.rate_beer(new_beer_data)
        return redirect(f"/")
    return redirect('/beers/new')

@app.route('/beers/edit/<int:id>')
def display_edit_beer(id):
    if 'logged_user' not in session:
        return redirect('/login')
    current_user = User.get_user(id=session['logged_user'])
    beer = Beer.get_beer(id)
    if session['logged_user'] == beer.user_id:
        return render_template('edit_beer.html', user=current_user, beer=beer)
    return redirect(f"/users/dashboard/{session['logged_user']}")

@app.route('/beers/edit/<int:id>/process', methods=['POST'])
def edit_beer(id):
    if 'logged_user' not in session:
        return redirect('/login')
    if session['logged_user'] == Beer.get_beer(id).poster_id:
        new_info = {
            **request.form,
            'id' : id,
            'poster_id' : session['logged_user']
        }
        if not Beer.validate_create_beer(new_info):
            return redirect(f'/beers/edit/{id}')
        rslt = Beer.update_beer(new_info)
    return redirect(f"/users/dashboard/{session['logged_user']}")

@app.route('/beers/destroy/<int:id>')
def delete_beer(id):
    if 'logged_user' not in session:
        return redirect('/login')
    if session['logged_user'] == Beer.get_beer(id).user_id:
        rslt = Beer.delete_beer(id)
    return redirect(f"/users/account/{session['logged_user']}")