from application import app
from application.models.beers_model import Beer
from application.models.users_model import User
from application.models.breweries_model import Brewery
from application.controllers.controller_functions import check_user
from flask import render_template, redirect, request, session

@app.route('/breweries')
def show_all_breweries():
    current_user = check_user()
    all_breweries = Brewery.get_all_breweries()
    breweries_dict = {
        'nano' : {
            'title' : 'Nanobreweries',
            'breweries' : [brewery for brewery in all_breweries if brewery.type == 'Nano']
        },
        'micro' : {
            'title' : 'Microbreweries',
            'breweries' : [brewery for brewery in all_breweries if brewery.type == 'Micro']
        },
        'pub' : {
            'title' : 'Brewpubs',
            'breweries' : [brewery for brewery in all_breweries if brewery.type == 'Pub']
        },
        'regional' : {
            'title' : 'Regional',
            'breweries' : [brewery for brewery in all_breweries if brewery.type == 'Regional']
        },
        'regional_craft' : {
            'title' : 'Regional Craft',
            'breweries' : [brewery for brewery in all_breweries if brewery.type == 'Regional Craft']
        },
        'large' : {
            'title' : 'Large',
            'breweries' : [brewery for brewery in all_breweries if brewery.type == 'Large']
        }
    }
    return render_template('breweries.html', user=current_user, breweries_dict=breweries_dict)

@app.route('/breweries/<int:id>', methods=['GET','POST'])
def show_brewery(id):
    current_user = check_user()
    if request.method == 'GET':
        current_brewery = Brewery.get_brewery(id)
        beers = Beer.get_all_beers_by_brewery(id)
        return render_template('brewery.html', user=current_user, brewery=current_brewery, beers=beers)
    elif request.method == 'POST':
        if not current_user:
            return redirect('/login')
        visit_data = {
            'breweries_id': id,
            'users_id' : session['logged_user']
        }
        new_visit = Brewery.visit_brewery(visit_data)
        return redirect(f"/breweries/{id}")

@app.route('/breweries/new', methods=['GET','POST'])
def create_brewery():
    current_user = check_user()
    if not current_user:
        return redirect('/login')
    if request.method == 'GET':
        return render_template('new_brewery.html', user=current_user, types=Brewery.BREWERY_TYPES)
    elif request.method == 'POST':
        new_brewery_data = {
            **request.form,
            'poster_id' : current_user.id
        }
        new_brewery = Brewery.create_new_brewery(new_brewery_data)
        if new_brewery:
            return redirect(f"/breweries/{new_brewery}")
        return redirect('/breweries/new')

@app.route('/breweries/<int:id>/edit', methods=['GET','POST', 'DELETE'])
def edit_brewery(id):
    current_user = check_user()
    if not current_user:
        return redirect('/login')
    brewery = Brewery.get_brewery(id)
    if current_user.id != brewery.poster_id:
        return redirect(f"/")
    if request.method == 'GET':
        return render_template('edit_brewery.html', user=current_user, brewery=brewery, types=Brewery.BREWERY_TYPES, states=Brewery.STATES)
    elif request.method == 'POST':
        new_info = {
            **request.form,
            'id' : id,
            'poster_id' : current_user.id
        }
        rslt = Brewery.update_brewery(new_info)
        if rslt is not None:
            return redirect(f'/breweries/{id}/edit')
        return redirect(f"/breweries/{id}")
    elif request.method == 'DELETE':
        rslt = Brewery.delete_brewery(id)
        return redirect("/")