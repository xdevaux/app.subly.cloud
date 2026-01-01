from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'

    from app.routes import auth, main, subscriptions, api, categories, services
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(subscriptions.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(categories.bp)
    app.register_blueprint(services.bp)

    # Initialiser OAuth
    auth.init_oauth(app)

    # Filtres Jinja2 personnalisés
    @app.template_filter('translate_cycle')
    def translate_cycle(cycle):
        """Traduit les cycles de facturation en français"""
        translations = {
            'monthly': 'Mensuel',
            'yearly': 'Annuel',
            'weekly': 'Hebdomadaire',
            'quarterly': 'Trimestriel'
        }
        return translations.get(cycle, cycle)

    @app.template_filter('currency_symbol')
    def currency_symbol(currency_code):
        """Convertit les codes de devise en symboles"""
        symbols = {
            'EUR': '€',
            'USD': '$',
            'GBP': '£'
        }
        return symbols.get(currency_code, currency_code)

    @app.template_filter('format_amount')
    def format_amount(amount):
        """Formate un montant au format français (virgule pour décimales, espace pour milliers)"""
        try:
            value = float(amount)
            # Formater avec 2 décimales
            formatted = f"{value:,.2f}"
            # Remplacer le séparateur de milliers par un espace
            formatted = formatted.replace(',', ' ')
            # Remplacer le point décimal par une virgule
            formatted = formatted.replace('.', ',')
            return formatted
        except (ValueError, TypeError):
            return "0,00"

    return app


from app import models
