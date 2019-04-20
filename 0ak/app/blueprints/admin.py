from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.forms import SettingForm, PostForm, CategoryForm, LinkForm
from app.models import Post, Category, Tag, Admin
from app.extensions import db
from sqlalchemy.exc import IntegrityError
from app.utils import redirect_back
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@login_required
def login_protect():
    pass

# @admin_bp.route('/settings', methods=['GET', 'POST'])
# def settings():
#     form = SettingForm()
#     if form.validate_on_submit():
#         current_user.head_title = form.head_title.data
#         current_user.blog_title = form.blog_title.data
#         current_user.blog_sub_title = form.blog_sub_title.data
#         db.session.commit()
#         flash('Setting updated.', 'success')
#         return redirect(url_for('blog.index'))
#     form.head_title.data = current_user.head_title
#     form.blog_title.data = current_user.blog_title
#     form.blog_sub_title.data = current_user.blog_sub_title
#     return render_template('admin/settings.html', form=form)

@admin_bp.route('/post/manage')
def manage_post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=5)
    posts = pagination.items
    return render_template('admin/manage_post.html', page=page, pagination=pagination, posts=posts)

@admin_bp.route('/category/new', methods=['GET', 'POST'])
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(cname=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Category newed.', 'success')
        return redirect(url_for('.manage_post'))
    return render_template('admin/new_category.html', form=form)


@admin_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        slug = form.slug.data
        category = Category.query.get(form.category.data).cname
        tags = form.tags.data

        title = form.title.data
        timestamp = datetime.strptime(form.timestamp.data, '%Y-%m-%d %H:%M:%S')
        desc = form.desc.data
        body = form.Body.data

        lastmodified = datetime.now()
        poster = form.poster.data
        
        post = Post(ptitle=title, body=body, desc=desc, category_name=category, pslug=slug, poster=poster, timestamp=timestamp, lastmodified=lastmodified)     
        # same with:
        # category_id = form.category.data
        # post = Post(title=title, body=body, category_id=category_id)
        tags = tags.split(";")
        db.session.add(post)
        db.session.commit()

        for name in tags:
            tag = Tag.query.filter_by(tname=name).first()
            if tag is None:
                tag = Tag(tname=name, category_name=category)
                db.session.add(tag)
                db.session.commit()
            if tag not in post.tags:
                post.tags.append(tag)
                db.session.commit()
        flash('Post created.', 'success')
        return redirect(url_for('blog.show_post', post_slug=post.pslug, toc=None))
    return render_template('admin/new_post.html', form=form)

@admin_bp.route('/post/<post_slug>/edit', methods=['GET', 'POST'])

def edit_post(post_slug):
    form = PostForm()
    post = Post.query.filter_by(pslug=post_slug).first_or_404()
    if form.validate_on_submit():
        tags = form.tags.data
        tags = tags.split(";")
        for name in tags:
            tag = Tag.query.filter_by(tname=name).first()
            if tag is None:
                tag = Tag(tname=name, category_name=category)
                db.session.add(tag)
                db.session.commit()
            if tag not in post.tags:
                post.tags.append(tag)
                db.session.commit()

        post.ptitle = form.title.data
        post.pslug = form.slug.data
        post.timestamp = datetime.strptime(form.timestamp.data, '%Y-%m-%d %H:%M:%S')
        post.poster = form.poster.data
        post.desc = form.desc.data
        post.body = form.Body.data
        post.category_name = Category.query.get(form.category.data).cname
        lastmodified = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        post.lastmodified = datetime.strptime(lastmodified, '%Y-%m-%d %H:%M:%S')
        db.session.commit()
        flash('Post updated.', 'success')
        return redirect(url_for('blog.show_post', post_slug=post.pslug))
    form.title.data = post.ptitle
    form.slug.data = post.pslug
    form.timestamp.data = post.timestamp
    tags = ""
    for each in post.tags:
        tags = tags + ";" + each.tname
    tags = tags.lstrip(';')
    form.tags.data = tags
    form.poster.data = post.poster
    form.desc.data = post.desc
    form.Body.data = post.body
    form.category.data = post.category_name
    return render_template('admin/edit_post.html', form=form)

@admin_bp.route('/post/<post_slug>/delete', methods=['POST'])
@login_required
def delete_post(post_slug):
    post = Post.query.filter_by(pslug=post_slug).first_or_404()
    for each in post.tags:
        tag = Tag.query.filter_by(tname=each.tname).first()
        if tag in post.tags:
            post.tags.remove(tag)
            db.session.commit()
        if tag not in post.tags:
            db.session.delete(post)
            db.session.commit()
    flash('Post deleted.', 'success')
    return redirect_back('.manage_post')

