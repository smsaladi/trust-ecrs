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

    to_name = db.Column(db.String)
    to_email = db.Column(db.String)
    to_group = db.Column(db.String)
    to_orcid = db.Column(db.String, default='')
    to_valid = db.Column(db.Boolean, default=None)
    to_hidden = db.Column(db.Boolean, default=False)
    to_url = db.Column(db.String, default='')

    from_name = db.Column(db.String)
    from_email = db.Column(db.String)
    from_group = db.Column(db.String)
    from_orcid = db.Column(db.String, default='')
    from_valid = db.Column(db.Boolean, default=None)
    from_hidden = db.Column(db.Boolean, default=False)

    citation = db.Column(db.String, default='')

    def __unicode__(self):
        return 'to:{}; from:{}'.format(self.to_email, self.from_email)

    def __repr__(self):
        return '<{}#{}>'.format(self.__class__.__name__, self.id)

class User(db.Model):
    __tablename__ = 'users'
    addr = db.Column(db.String(50), primary_key=True)
    has_access = db.Column(db.Boolean, default=False)
