from flask import Blueprint, render_template

atividades_blueprint = Blueprint('atividades', __name__)

@atividades_blueprint.route('/atividades')
def atividades():
    return render_template('atividades.html')