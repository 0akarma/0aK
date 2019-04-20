import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Tag, Category, Post

fake = Faker()

def fake_categories(count=10):
    category = Category(cname='Default')
    db.session.add(category)

    for i in range(count):
        category = Category(cname=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

def fake_tags(count=10):
    tag = Tag(tname='Default')
    db.session.add(tag)

    for i in range(count):
        tag = Tag(tname=fake.word())
        db.session.add(tag)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=50):
    for i in range(count):
        post = Post(
            ptitle=fake.sentence(),
            pslug=fake.word(),
            body=fake.text(2000),
            timestamp=fake.date_time_this_year()
        )

        db.session.add(post)
    db.session.commit()