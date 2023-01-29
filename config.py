import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
    LANGUAGES = ['en', 'es']
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    POSTS_PER_PAGE = 25
    UPLOAD_PATH = 'app/static/'
    DEFAULT_TRAILS = [
        ['gr5','GR5','Noordzee - Midellandse Zee'],
        ['gr5a-kust','GR5A-K','Kustroute'],
        ['gr5a-ronde','GR5A-W','Wandelronde van Vlaanderen'],
        ['gr12','GR12','Amsterdam - Parijs'],
        ['gr122','GR122','Scheldeland'],
        ['gr126','GR126','Brussegem - Mariekere'],
        ['gr128','GR128','Vlaanderenroute'],
        ['gr129','GR129','Dwars door Belgie'],
        ['gr130','GR130','IJzer'],
        ['gr131','GR131','Brugse Ommeland - Ieperboog'],
        ['gr512','GR512','Brabantse Heuvelroute'],
        ['gr561','GR561','Kempen - Maaspad'],
        ['gr564','GR564','Loonse Route'],
        ['gr565','GR565','Sniederspad'],
        ['grp-antwerpen','GRP Antwerpen','Stads-GR Antwerpen'],
        ['grp-dijleland','GRP Dijleland','Streek-GR Dijleland'],
        ['grp-groenegordel','GRP Groene Gordel','Streek-GR Groene Gordel'],
        ['grp-hageland','GRP Hageland','Streek-GR Hageland'],
        ['grp-haspengouw','GRP Haspengouw','Streek-GR Haspengouw'],
        ['grp-heuvelland','GRP Heuvelland','Streek-GR Heuvelland'],
        ['grp-kempen','GRP Kempen','Streek-GR Kempen'],
        ['grp-molom','GRP Mol Om','Streek-GR Mol Om'],
        ['grp-uilenspiegel','GRP Uilenspiegel','Streek-GR Uilenspiegel'],
        ['grp-vlardennen','GRP Vl. Ardennen','Streek-GR Vlaamse Ardennen'],
        ['grp-waasreynaert','GRP Waas-Reynaert','Streek-GR Waas-Reynaert'],
    ]