import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://localhost/subly_app'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Stripe
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')

    # OAuth Google
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

    # OAuth Apple
    APPLE_CLIENT_ID = os.environ.get('APPLE_CLIENT_ID')
    APPLE_CLIENT_SECRET = os.environ.get('APPLE_CLIENT_SECRET')

    # Limites d'abonnements
    FREE_SUBSCRIPTION_LIMIT = 5

    # Upload
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max pour les logos
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads')
