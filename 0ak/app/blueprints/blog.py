import os
from flask import Blueprint
from flask import request, abort, jsonify, make_response, redirect, url_for
from flask import Flask, render_template, send_from_directory
from app.models import Post, Tag, Category
from app.extensions import db, sitemap
from sqlalchemy import distinct, func
import markdown
from app.extensions import csrf
from werkzeug.utils import secure_filename
from app.utils import redirect_back
import time
from datetime import datetime

blog_bp = Blueprint('blog', __name__)
app = Flask('app')
POSTS_FOLDER = '../posts'
app.config['POSTS_FOLDER'] = POSTS_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['txt', 'png', 'jpg', 'JPG', 'PNG', 'gif', 'GIF'])


@blog_bp.route('/')
def index():
    return render_template('blog/index.html')

@blog_bp.route('/<category_name>', methods=['GET'])
def show_category(category_name):
    page = request.args.get('page', 1, type=int)
    per_page = 5
    pagination = Post.query.filter_by(category_name=category_name).order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    tags = Tag.query.filter_by(category_name=category_name).all()
    categories = Category.query.order_by(Category.cid).all()
    modified = Post.query.order_by(Post.timestamp.desc()).first()
    postcount = Post.query.order_by(Post.timestamp.desc()).count()
    posts = pagination.items
    return render_template('blog/category.html', pagination=pagination, posts=posts, cname=category_name, categories=categories, tags=tags, postcount=postcount, modified=modified)

@blog_bp.route('/theme/change')
def change_theme():
    theme = request.cookies.get('theme')
    if(theme == 'dark'):
        theme = 'light'
    else:
        theme = 'dark'
    response = make_response(redirect_back())
    response.set_cookie('theme', theme, max_age=30*24*60*60)
    postdir = os.path.join(basedir, app.config['POSTS_FOLDER'])
    for each in os.listdir(postdir):
        os.remove(os.path.join(postdir, each))
    return response


@blog_bp.route('/sitemap.xml')
def static_from_root():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    sitemap = get_sitemap(posts)
    save_file(sitemap)

    return send_from_directory(app.static_folder, request.path[1:])
def get_sitemap(posts):
    # 参数posts是文章模型哦，组成文章对应的url就可以了
    header = '<?xml version="1.0" encoding="UTF-8"?> '+ '\n' + \
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    footer = '</urlset>'
    contents = []
    body = ''

    if posts:
        for post in posts:
            timestamp = str(post.timestamp)
            timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            timestamp = timestamp.timetuple()
            timeStamp = int(time.mktime(timestamp))
            content = '  <url>' + '\n' + \
                '    <loc>http://localhost:5000/' + post.pslug + '.html' + '</loc>' + '\n' + \
                '    <lastmod>' + str(time.strftime('%Y-%m-%dT%H:%M:%S+08:00', timestamp)) + '</lastmod>' + '\n' + \
                '  </url>'
            contents.append(content)
        for content in contents:
            body = body + '\n' + content
        sitemap = header + '\n' + body + '\n' + footer
        return sitemap
    return None

def save_file(sitemap):
    sitemapdir = os.path.join(basedir, '../static/')
    isExists = os.path.exists(os.path.join(sitemapdir, 'sitemap.xml'))
    if not isExists:
        with open(os.path.join(sitemapdir, 'sitemap.xml'), 'w') as f:
            f.write(sitemap)
    else:
        os.remove(oos.path.join(sitemapdir, 'sitemap.xml'))
        with open(os.path.join(sitemapdir, 'sitemap.xml'), 'w') as f:
            f.write(sitemap)


@blog_bp.route('/<post_slug>', methods=['GET', 'POST'])
def rpost(post_slug):
    return redirect(url_for('blog.show_post', post_slug=post_slug), code=301)

@blog_bp.route('/<post_slug>'+'.html', methods=['GET', 'POST'])
def show_post(post_slug):
    file_dir = os.path.join(basedir, app.config['POSTS_FOLDER'])
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    filename = post_slug + '.html'
    filename = os.path.join(file_dir, filename)
    if os.path.isfile(filename):
        post = open(filename, 'r')
        response = make_response(post.read())
        response.mimetype = 'text/html'
        post.close()
        return response
    else:
        posts = Post.query.filter_by(pslug=post_slug).first_or_404()
        # md = markdown.Markdown(extensions=['toc'])
        # html = md.convert(posts.body)
        toc = None
        post = open(filename, 'tw')
        post_data = str(render_template('blog/post.html', posts=posts, toc=toc))
        post.write(post_data)
        post.close()
        response = make_response(post_data)
        response.mimetype = 'text/html'
        return response
        # return send_file(filename)

@blog_bp.route('/about')
def about():
    return redirect(url_for('blog.show_post', post_slug='about'), code=301)
    #posts = Post.query.filter_by(pslug='about').first_or_404()
    #return render_template('blog/post.html', posts=posts)

@blog_bp.route('/search')
def search():
    
    q = request.args.get('q', '')
    if q == '':
        abort(404)
    
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 5
        pagination = Post.query.msearch(q, fields=['ptitle', 'pslug'],limit=20).paginate(page, per_page=per_page)
        results = pagination.items
        return render_template('blog/category.html', pagination=pagination, cname='Query', posts=results)
    except:
        abort(404)

@blog_bp.route('/tags/<tname>', methods=['GET', 'POST'])
def show_tag(tname):
    # pagination = db.session.query(Post.ptitle, Post.pslug, Post.poster, Post.timestamp, Tag.tname) join(Post.tags). \
    # pagination = Post.query.join(Post.tags).filter(Tag.tname==tname).order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    # pagination = Post.query.filter_by(tag_name=tname).order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    page = request.args.get('page', 1, type=int)
    per_page = 100
    tname = tname.replace('%20', ' ')
    pagination = Post.query.join(Post.tags).filter_by(tname=tname).order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('blog/tags.html', pagination=pagination, posts=posts, tname=tname)


