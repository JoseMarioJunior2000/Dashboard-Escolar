from routes.lista import lista_blueprinte
from routes.detalhes import detalhes_blueprinte
from routes.adicionar import adicionar_blueprinte
from routes.home import home_blueprinte
from routes.upload import upload_blueprint
from routes.professores import professores_blueprint
from routes.turmas import turmas_blueprint
from routes.encontros import trilhas_blueprinte
from routes.eventos import eventos_blueprint
from routes.atividades import atividades_blueprint
from routes.base64 import template_filter_blueprint
from context_processors import inject_totals

def configure_all(app):
    configure_routes(app)
    configure_context_processors(app)

def configure_routes(app):
    app.register_blueprint(home_blueprinte)
    app.register_blueprint(lista_blueprinte)
    app.register_blueprint(detalhes_blueprinte)
    app.register_blueprint(adicionar_blueprinte)
    app.register_blueprint(upload_blueprint)
    app.register_blueprint(eventos_blueprint)
    app.register_blueprint(trilhas_blueprinte)
    app.register_blueprint(turmas_blueprint)
    app.register_blueprint(atividades_blueprint)
    app.register_blueprint(professores_blueprint)
    app.register_blueprint(template_filter_blueprint)

def configure_context_processors(app):
    app.context_processor(inject_totals)