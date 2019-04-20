from datetime import datetime
from markdown import markdown
import bleach
from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

import os, sys
import logging



class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    blog_title = db.Column(db.String(60))
    blog_sub_title = db.Column(db.String(100))
    head_title = db.Column(db.String(30))
    blog_author_name = db.Column(db.String(30))
    blog_author_avator = db.Column(db.String(30))
    blog_author_description = db.Column(db.String(30))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = 'category'
    cid = db.Column(db.Integer, primary_key=True)
    cname = db.Column(db.String(30), unique=True)
    posts = db.relationship('Post', back_populates='category')
    tag = db.relationship('Tag', back_populates='category')

    def delete(self):
        default_category = Category.query.get(1)
        posts = self.posts[:]
        for post in posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()
    #repr()方法显示一个可读字符串，虽然不是完全必要，不过用于调试和测试还是很不错的。
    def __repr__(self):
        return '<Category {}> '.format(self.name)

association_table = db.Table('association',
                             db.Column('tag_name', db.String(50), db.ForeignKey('tag.tname')),
                             db.Column('post_name', db.String(50), db.ForeignKey('post.pslug'))
                             )

class Tag(db.Model):
    __tablename__ = 'tag'
    tid = db.Column(db.Integer, primary_key=True)
    tname = db.Column(db.String(50), unique=True)
    posts = db.relationship('Post', back_populates='tags', secondary=association_table, lazy='dynamic',cascade='save-update, merge, delete')
    category_name = db.Column(db.String(30), db.ForeignKey('category.cname'))
    category = db.relationship('Category', back_populates='tag')
    def delete(self):
        default_category = Category.query.get(1)
        posts = self.posts[:]
        for post in posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()

class Post(db.Model):
    __tablename__ = 'post'
    __searchable__ = ['ptitle', 'pslug']
    pid = db.Column(db.Integer, primary_key=True)
    ptitle = db.Column(db.String(150), index=True)
    pslug = db.Column(db.String(50), unique=True)
    desc = db.Column(db.Text)
    desc_html = db.Column(db.Text)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    poster = db.Column(db.String(200))
    lastmodified = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    category_name = db.Column(db.String(30), db.ForeignKey('category.cname'))

    category = db.relationship('Category', back_populates='posts')
    tags = db.relationship('Tag', back_populates='posts', secondary=association_table, lazy='dynamic', cascade='save-update, merge, delete')

    
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        config = {
        'codehilite': {
        'use_pygments': False,
        'css_class': 'prettyprint linenums',
        }
    }  
        attrs = {
                '*': ['class'],
                'a': ['href', 'rel'],
                'img': ['src', 'alt'],
                'h1': ['id'],
                'h2': ['id'],
                'h3': ['id'],
                'h4': ['id'],
                'h5': ['id']
            }
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
            'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul','h1', 'h2', 'h3', 'h4', 'p','img', 'span', 'pre', 'div']

        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html', extensions=['extra', 'codehilite', 'toc', 'mdx_truly_sane_lists'], extension_configs=config), tags=allowed_tags, strip=True, attributes=attrs))


    def on_changed_desc(target, value, oldvalue, initiator):
        config = {
        'codehilite': {
        'use_pygments': False,
        'css_class': 'prettyprint linenums',
            }
        }  
        attrs = {
                '*': ['class'],
                'a': ['href', 'rel'],
                'img': ['src', 'alt'],
            }
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
            'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul','h1', 'h2', 'h3', 'h4', 'p','img', 'span', 'pre', 'div']

        target.desc_html = bleach.linkify(bleach.clean(markdown(value, output_format='html', extensions=['extra', 'codehilite', 'mdx_truly_sane_lists'], extension_configs=config), tags=allowed_tags, strip=True, attributes=attrs))

        logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s %(levelname)s %(message)s')
        logger = logging.getLogger(__name__)
        f = str(target.pslug) + '.html'
        filedir = os.path.join(os.getcwd(), 'app/posts/')
        filename = os.path.join(filedir, f)
        try:
            if os.path.isfile(filename):
                os.remove(filename)
                logger.info('Deleting ' + filename)
        except Exception as e:
            logger.info('Delete Failed.')


db.event.listen(Post.body, 'set', Post.on_changed_body)
db.event.listen(Post.desc, 'set', Post.on_changed_desc)
