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
        ['gr5-vlaanderen','GR5 Vlaanderen','Noordzee - Midellandse Zee'],
        ['gr5-wallonie','GR5 Wallonië','Noordzee - Midellandse Zee'],
        ['gr5a-kust','GR5A-K','Kustroute'],
        ['gr5a-ronde','GR5A-W','Wandelronde van Vlaanderen'],
        ['gr12-vlaanderen','GR12 Vlaanderen','Amsterdam - Parijs'],
        ['gr12-wallonie','GR12 Wallonië','Amsterdam - Parijs'],
        ['gr14','GR14',"Sentiers de l'Ardenne"],
        ['gr15','GR15',"Sentiers de l'Ardenne"],
        ['gr16','GR16','Sentier de la Semois'],
        ['gr17','GR17','Entre Lesse et Lomme'],
        ['gr56','GR56',"Sentiers de l'Est de la Belgique"],
        ['gr57','GR57',"Sentiers de l'Ourthe"],
        ['gr57-west','GR57 West',"Sentiers de l'Ourthe (Westelijke Variant)"],
        ['gr121','GR121',"Wavre - Boulogne-sur-Mer"],
        ['gr122-vlaanderen','GR122 Vlaanderen','Scheldeland'],
        ['gr122-wallonie','GR122 Wallonië','Scheldeland'],
        ['gr123','GR123','Tour de la Wallonie Picarde'],
        ['gr125','GR125',"Tour de l'Entre-Sambre-et-Meuse"],
        ['gr126-vlaanderen','GR126 Vlaanderen','Brussegem - Mariekere'],
        ['gr126-wallonie','GR126 Wallonië','Membre-sur-Semois - Brussegem'],
        ['gr127','GR127','Tour du Brabant Wallon'],
        ['gr128','GR128','Vlaanderenroute'],
        ['gr129a','GR129-A','Dwars door België (Vlaanderen)'],
        ['gr129b','GR129-B','Dwars door België (Dinant-Arlon)'],
        ['gr129c','GR129-C','Dwars door België (Ellezelles-Dinant)'],
        ['gr130','GR130','IJzer'],
        ['gr131','GR131','Brugse Ommeland - Ieperboog'],
        ['gr151','GR151','Tour du Luxembourg belge'],
        ['gr412','GR412','Sentier des Terrils'],
        ['gr512','GR512','Brabantse Heuvelroute'],
        ['gr561','GR561','Kempen - Maaspad'],
        ['gr563','GR563','Tour du Pays de Herve'],
        ['gr564','GR564','Loonse Route'],
        ['gr565','GR565','Sniederspad'],
        ['gr571','GR571','Tour des Vallees des Legendes'],
        ['gr573','GR573','Vesdre et Hautes Fagnes'],
        ['gr575','GR575','À travers le Condroz'],
        ['gr577','GR577','Tour de la Famenne'],
        ['gr579','GR579','Bruxelles - Huy'],
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

class TestConfig(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_db.sqlite'
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