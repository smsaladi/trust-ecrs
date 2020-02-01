"""

A simple app to collect and search for endorsements

"""

import os
import sys

import flask
from flask import Flask, render_template, request, jsonify, url_for
from flask_dotenv import DotEnv
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from itsdangerous import URLSafeSerializer

from datatables import ColumnDT, DataTables

from models import db, Endorsement, User

app = Flask(__name__)


app.config['BASE_URL'] = os.environ['BASE_URL']

# For data storage
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)

# for notification
app.config['MAIL_SERVER'] = os.environ['MAIL_SERVER']
app.config['MAIL_PORT'] = int(os.environ['MAIL_PORT'])
app.config['MAIL_USE_TLS'] = bool(int(os.environ['MAIL_USE_TLS']))
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
app.config['MAIL_DEFAULT_SENDER'] = 'trust-ecrs@ecrlife.org'
mail = Mail(app)

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
csrf = CSRFProtect(app)
def serializer(*args, **kwargs):
    return URLSafeSerializer(app.config['SECRET_KEY'], *args, **kwargs)


@app.cli.command()
def initdb():
    """Initialize the database with filler data"""
    db.create_all()

    attr = dict(
        to_email="test-to_email",
        to_orcid="test-to_orcid",
        to_valid=True,
        from_name="test-from_name",
        from_email="test-from_email",
        from_orcid="test-from_orcid",
        from_valid = True
    )

    for i in range(30):
        obj = Endorsement(to_name="test-to_name-" + str(i), **attr)
        db.session.add(obj)
    db.session.commit()
    
    return

@app.route("/")
def register():
    return render_template('register.html')
    

"""Query entries
"""

@app.route("/profile")
@app.route("/profile/<userkey>")
def profile(userkey=None):
    if userkey is None:
        return redirect("/")

    addr = serializer().loads(userkey)
    q = Endorsement.query.find(
        (Endorsement.to_email == addr) |
        (Endorsement.from_email == addr))

    if len(q) == 0:
        return render_template('query.html', message="No records for you in the database")
    
    return render_template('query.html')


@app.route('/profile/<userkey>/data', methods=['POST'])
def profile_data():
    """Returns server side data
    """
    columns = [
        ColumnDT(Endorsement.from_name),
        ColumnDT(Endorsement.to_name),
        ColumnDT(Endorsement.to_email),
        ColumnDT(Endorsement.created_at)
    ]

    addr = serializer().loads(userkey)
    q = Endorsement.query.find(
        (Endorsement.to_email == addr) |
        (Endorsement.from_email == addr))

    rowTable = DataTables(params, query, columns)

    n_results = len(rowTable.results)
    print(n_results)

    return jsonify(rowTable.output_result())


@app.route("/query")
@app.route("/query/<userkey>")
def query(userkey=None):
    if not userkey:
        return render_template("learn_more.html")

    addr = serializer().loads(userkey)
    q = User.query.get(addr)
    if len(q) == 0:
        return "Bad URL. Contact help", 400

    return render_template('query.html')

@app.route('/query/<userkey>/data', methods=['POST'])
def query_data():
    """Returns server side data
    """
    columns = [
        ColumnDT(Endorsement.from_name),
        ColumnDT(Endorsement.to_name),
        ColumnDT(Endorsement.to_email),
        ColumnDT(Endorsement.created_at)
    ]

    addr = serializer().loads(userkey)
    q = User.query.get(addr)
    if len(q) == 0:
        return jsonify([{}])

    params = request.form
    print(params)

    userquery = params['search[value]']

    if len(userquery) < 5:
        return jsonify([{}])

    query = (db.session.query()
        .select_from(Endorsement)
        .filter(Endorsement.to_valid & Endorsement.from_valid)
    )

    rowTable = DataTables(params, query, columns)

    n_results = len(rowTable.results)
    print(n_results)

    return jsonify(rowTable.output_result())



"""Submission reciever
"""

map_ids = {
    'to_name_input':    'to_name',
    'to_group_input':   'to_group',
    'to_email_input':   'to_email',
    'to_orcid_input':   'to_orcid',
    'to_url_input':     'to_url',
    'from_name_input':  'from_name',
    'from_group_input': 'from_group',
    'from_email_input': 'from_email',
    'from_orcid_input': 'from_orcid',
    'citation_input':   'citation',
}

@app.route("/submit", methods=['POST'])
def submit():
    params = request.form
    keep = {}
    for k, v in map_ids.items():
        keep[v] = params.get(k, '')
    
    if 'role_to' in params.keys() and params['role_to'] == 'on':
        who = 'to'
    else:
        who = 'from'

    try:
        obj = Endorsement(**keep)
        obj = db.session.merge(obj)
        db.session.commit()
    except:
        return jsonify({'success': False}), 400, {'ContentType': 'application/json'}
    
    send_verify_email(obj, who)
    return jsonify({'sucess': True}), 200, {'ContentType': 'application/json'}


def send_verify_email(obj, who):
    if who == 'from':
        addr = obj.from_email
        name = obj.from_name
    else:
        addr = obj.to_email
        name = obj.to_name
    userkey = serializer().dumps(addr)

    try:
        msg = Message(
            "Please verify your submission",
            recipients=[addr])
        msg.html = flask.render_template("verify_request.txt", obj=obj, userkey=userkey)
        mail.send(msg)
    except Exception as e:
        print(e, file=sys.stderr)
        obj.mail_err = True
    
    obj = db.session.merge(obj)
    return


"""Confirmation by Endorser and Endorsee
"""

@app.route("/validate/<userkey>/<int:row>")
def validate(userkey, row):
    obj = Endorsement.query.get(row)
    addr = serializer().loads(userkey)

    if obj.to_email == addr:
        obj.to_valid = True
        if not obj.from_valid:
            send_verify_email(obj, "from")
    elif obj.from_email == addr:
        obj.from_valid = True
        if not obj.to_valid:
            send_verify_email(obj, "to")
    else:
        return "Unexpected url. Contact administrator", 400

    obj = db.session.merge(obj)
    db.session.commit()
    return redirect(url_for('profile', userkey=userkey))


@app.route("/reject/<userkey>/<int:row>")
def reject(userkey, row):
    obj = Endorsement.query.get(row)
    addr = serializer().loads(userkey)

    if obj.to_email == addr:
        obj.to_valid = False
    elif obj.from_email == addr:
        obj.from_valid = False
    else:
        return "Unexpected url. Contact administrator", 400

    obj = db.session.merge(obj)
    db.session.commit()
    return redirect(url_for('profile', userkey=userkey))


"""Toggle whether an endorsement is shown
"""

@app.route("/hide/<userkey>/<int:row>")
def hide(userkey, row):
    obj = Endorsement.query.get(row)
    addr = serializer().loads(userkey)

    if obj.to_email == addr:
        obj.to_hidden = True
    elif obj.from_email == addr:
        obj.to_hidden = True
    else:
        return jsonify({'success': False}), 400, {'ContentType': 'application/json'}

    obj = db.session.merge(obj)
    db.session.commit()
    return jsonify({'sucess': True}), 200, {'ContentType': 'application/json'}

@app.route("/show/<userkey>/<int:row>")
def show(userkey, row):
    obj = Endorsement.query.get(row)
    addr = serializer().loads(userkey)

    if obj.to_email == addr:
        obj.to_hidden = False
    elif obj.from_email == addr:
        obj.to_hidden = False
    else:
        return jsonify({'success': False}), 400, {'ContentType': 'application/json'}

    obj = db.session.merge(obj)
    db.session.commit()
    return jsonify({'sucess': True}), 200, {'ContentType': 'application/json'}

