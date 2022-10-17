from application import app
from application.models.breweries_model import Brewery
from application.models.beers_model import Beer
from application.controllers.controller_functions import check_user
from flask import render_template, redirect, request, session

@app.route('/beers')
def show_all_beer():
    current_user = check_user()
    sorted_beers = [Beer.get_all_beers('taste'), Beer.get_all_beers('val'), Beer.get_all_beers('cost', False), Beer.get_all_beers()]
    return render_template('beers.html', user=current_user, beers=sorted_beers)

@app.route('/beers/<int:id>', methods=['GET','POST'])
def show_beer(id):
    current_user = check_user()
    if request.method == 'GET':
        current_beer = Beer.get_beer(id)
        return render_template('beer.html', user=current_user, beer=current_beer)
    elif request.method == 'POST':
        if not current_user:
            return redirect('/login')
        new_beer_data = {
            **request.form,
            'users_id' : session['logged_user'],
            'beers_id' : id
        }
        new_rating = Beer.rate_beer(new_beer_data)
        return redirect(f"/beers/{id}")

@app.route('/beers/new', methods=['GET','POST'])
def create_beer():
    current_user = check_user()
    if not current_user: 
        return redirect('/login')
    if request.method == 'GET':
        breweries = Brewery.get_all_breweries()
        return render_template('new_beer.html', user=current_user, breweries=breweries)
    elif request.method == 'POST':
        new_beer_data = {
            **request.form,
            'poster_id' : session['logged_user']
        }
        new_beer = Beer.create_new_beer(new_beer_data)
        if new_beer:
            new_beer_data = {
                **new_beer_data,
                'users_id' : session['logged_user'],
                'beers_id' : new_beer
            }
            new_rating = Beer.rate_beer(new_beer_data)
            return redirect("/")
        return redirect('/beers/new')

@app.route('/beers/<int:id>/edit', methods=['GET','POST', 'DELETE'])
def edit_beer(id):
    current_user = check_user()
    if not current_user:
        return redirect('/login')
    beer = Beer.get_beer(id)
    if current_user.id != beer.poster_id:
        return redirect(f"/")
    if request.method == 'GET':
        return render_template('edit_beer.html', user=current_user, beer=beer)
    elif request.method == 'POST':
        new_info = {
            **request.form,
            'id' : id,
            'poster_id' : current_user.id
        }
        if not Beer.validate_new_beer(new_info):
            return redirect(f'/beers/edit/{id}')
        rslt = Beer.update_beer(new_info)
        return redirect(f"/beers/{id}")
    elif request.method == 'DELETE':
        rslt = Beer.delete_beer(id)
        return redirect("/")