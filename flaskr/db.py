from pymongo import MongoClient
import pymongo
import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.client = MongoClient('mongodb://root:example@172.18.0.2')

        g.db = g.client.test
    return g.db


def close_db(e=None):
    client = g.pop('client', None)
    if client is not None:
        client.close()

def init_db():
    db = get_db()
    db.users.create_index([('user_name', pymongo.ASCENDING)], unique=True)


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)