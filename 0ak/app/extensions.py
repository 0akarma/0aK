import sys
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_ckeditor import CKEditor
from flask_pagedown import PageDown
from flask_migrate import Migrate
from flask_sitemap import Sitemap
from flask_msearch import Search

db = SQLAlchemy()
moment = Moment()
bootstrap = Bootstrap()
login_manager = LoginManager()
csrf = CSRFProtect()
ckeditor = CKEditor()
pagedown = PageDown()
migrate = Migrate()
sitemap = Sitemap()
search = Search()

@login_manager.user_loader
def load_user(user_id):
    from app.models import Admin
    user = Admin.query.get(int(user_id))
    return user


login_manager.login_view = 'auth.login'
login_manager.login_message = u'请先登录！'
login_manager.login_message_category = 'warning'