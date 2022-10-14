from application import app
from application.models.beers_model import Beer
from application.models.users_model import User
from application.models.breweries_model import Brewery
from flask import render_template, redirect, request, session

@app.route('/breweries')
def show_all_brewery():
    current_user = User.get_user(id=session['logged_user']) if 'logged_user' in session else False
    all_breweries = Brewery.get_all_breweries()
    sorted_breweries = []
    for t in Brewery.BREWERY_TYPES:
        sorted_breweries.append([brewery for brewery in all_breweries if brewery.type == t])
    return render_template('breweries.html', user=current_user, breweries=sorted_breweries)

@app.route('/breweries/<int:id>')
def show_brewery(id):
    current_user = User.get_user(id=session['logged_user']) if 'logged_user' in session else False
    current_brewery = Brewery.get_brewery(id)
    beers = Beer.get_all_beers_by_brewery(id)
    return render_template('brewery.html', user=current_user, brewery=current_brewery, beers=beers)

@app.route('/breweries/new')
def create_brewery():
    if 'logged_user' not in session:
        return redirect('/login')
    current_user = User.get_user(id=session['logged_user'])
    return render_template('new_brewery.html', user=current_user, types=Brewery.BREWERY_TYPES)

@app.route('/breweries/new/create', methods=['POST'])
def create_new_brewery():
    if 'logged_user' not in session:
        return redirect('/login')
    if Brewery.validate_create_brewery(request.form):
        new_brewery_data = {
            **request.form,
            'poster_id' : session['logged_user']
        }
        new_brewery = Brewery.create_new_brewery(new_brewery_data)
        return redirect(f"/breweries/{new_brewery}")
    return redirect('/breweries/new')

@app.route('/breweries/<int:id>/visit', methods=['POST'])
def visit_brewery(id):
    if 'logged_user' not in session:
        return redirect('/login')
    visit_data = {
        'breweries_id': id,
        'users_id' : session['logged_user']
    }
    new_visit = Brewery.visit_brewery(visit_data)
    return redirect(f"/breweries/{id}")

@app.route('/breweries/edit/<int:id>')
def displayEditPage(id):
    if 'logged_user' not in session:
        return redirect('/login')
    current_user = User.get_user(id=session['logged_user'])
    brewery = Brewery.get_brewery(id)
    if session['logged_user'] == brewery.user_id:
        return render_template('edit_brewery.html', user=current_user, brewery=brewery)
    return redirect(f"/users/dashboard/{session['logged_user']}")

@app.route('/breweries/edit/<int:id>/process', methods=['POST'])
def editBrewery(id):
    if 'logged_user' not in session:
        return redirect('/login')
    if session['logged_user'] == Brewery.get_brewery(id).poster_id:
        new_info = {
            **request.form,
            'id' : id,
            'poster_id' : session['logged_user']
        }
        if not Brewery.validate_create_brewery(new_info):
            return redirect(f'/breweries/edit/{id}')
        rslt = Brewery.update_brewery(new_info)
    return redirect(f"/users/dashboard/{session['logged_user']}")

@app.route('/breweries/destroy/<int:id>')
def deleteBrewery(id):
    if 'logged_user' not in session:
        return redirect('/login')
    if session['logged_user'] == Brewery.get_brewery(id).user_id:
        rslt = Brewery.delete_brewery(id)
    return redirect(f"/users/account/{session['logged_user']}")