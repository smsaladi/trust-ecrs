"""
"""

import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Endorsement(db.Model):
    """Basic endorsement model
    from: endorser
    to: endorsee, i.e. ECR
    """
    __tablename__ = 'endorsement'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    mail_err = db.Column(db.Boolean, default=False)

    to_name = db.Column(db.String(100))
    to_email = db.Column(db.String(50))
    to_group = db.Column(db.String(100))
    to_orcid = db.Column(db.Integer, default=None)
    to_valid = db.Column(db.Boolean, default=None)
    to_hidden = db.Column(db.Boolean, default=False)
    to_url = db.Column(db.Text, default='')

    from_name = db.Column(db.String(100))
    from_email = db.Column(db.String(50))
    from_group = db.Column(db.String(100))
    from_orcid = db.Column(db.Integer, default=None)
    from_valid = db.Column(db.Boolean, default=None)
    from_hidden = db.Column(db.Boolean, default=False)

    citation = db.Column(db.Text, default='')

    def __unicode__(self):
        return 'to:{}; from:{}'.format(self.to_email, self.from_email)

    def __repr__(self):
        return '<{}#{}>'.format(self.__class__.__name__, self.id)

class User(db.Model):
    __tablename__ = 'users'
    addr = db.Column(db.String(50), primary_key=True)
    has_access = db.Column(db.Boolean, default=False)
