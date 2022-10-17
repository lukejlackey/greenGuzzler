from flask import flash 

def validate_data(data, validations):
    validity = True
    for (k, v) in validations.items():
        if not data[k]:
            flash('This field is required.', v['tag'])
            validity = False
        elif not v['condition'] and v['condition'] is not None:
            flash(v['msg'], v['tag'])
            validity = False
    return validity