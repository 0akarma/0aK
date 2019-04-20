import os
import click
import sys
import logging
from flask import Flask, render_template
from app.blueprints.blog import blog_bp
from app.blueprints.auth import auth_bp
from app.blueprints.admin import admin_bp
from app.extensions import db, moment, bootstrap, login_manager, csrf, ckeditor, pagedown, migrate, sitemap, search
from app.models import Admin, Post, Category, Tag
from flask_wtf.csrf import CSRFError
from logging.handlers import SMTPHandler, RotatingFileHandler

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def create_app(config_name = None):
	
    app = Flask('app')
    register_logging(app)
    register_errors(app)
    register_blueprints(app)
    register_commands(app)
    # SQLite URI compatible
    WIN = sys.platform.startswith('win')
    if WIN:
        prefix = 'sqlite:///'
    else:
        prefix = 'sqlite:////'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', prefix + os.path.join(app.root_path, 'data.db'))
    # mysql
    # app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:root@127.0.0.1:3306/0ak'
	#设置这一项是每次请求结束后都会自动提交数据库中的变动
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "secret_key"
    
    register_extensions(app)
    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'Post': Post}
    return app

def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')

def register_logging(app):
    class RequestFormatter(logging.Formatter):

        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    request_formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
        '%(levelname)s in %(module)s: %(message)s'
    )

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(os.path.join(basedir, 'logs/app.log'),
                                       maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)


    if not app.debug:
        app.logger.addHandler(file_handler)



def register_extensions(app):
    
    db.init_app(app)
    bootstrap.init_app(app)
    ckeditor.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    pagedown.init_app(app)
    moment.init_app(app)
    migrate.init_app(app, db)
    sitemap.init_app(app)
    search.init_app(app)

   
def register_errors(app):

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/404.html'), 500

def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.')
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True, help='The password used to login.')
    def init(username, password):
        """Building Bluelog, just for you."""

        click.echo('Initializing the database...')
        db.create_all()

        admin = Admin.query.first()
        if admin is not None:
            click.echo('The administrator already exists, updating...')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('Creating the temporary administrator account...')
            admin = Admin(
                username=username
            )
            admin.set_password(password)
            db.session.add(admin)

        category = Category.query.first()
        if category is None:
            click.echo('Creating the default category...')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()
        click.echo('Done.')

    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--tag', default=10, help='Quantity of tags, default is 10.')
    def forge(category, post, tag):
        """Generate fake data."""
        from app.fakes import fake_categories, fake_posts, fake_tags

        db.drop_all()
        db.create_all()

        click.echo('Generating %d categories...' % category)
        fake_categories(category)

        click.echo('Generating %d tags...' % tag)
        fake_tags(tag)

        click.echo('Generating %d posts...' % post)
        fake_posts(post)

        
        click.echo('Done.')


