from flask import Flask, render_template, flash, request, session, redirect, url_for, jsonify, Blueprint
from wtforms import Form, StringField, PasswordField, validators, SelectField
import simplejson as json
from flask_mysqldb import MySQL
import hashlib
from functools import wraps
import datetime
from random import randint
from flask_socketio import SocketIO, emit
from waitress import serve
# from gevent.pywsgi import WSGIServer

bp = Blueprint('mainPrefix', __name__,
               url_prefix='/sharemap', static_folder='static' )

app = Flask(__name__)
app.secret_key = 'someThing'


with open('database.json', 'r') as f:
    dbInfo = json.load(f)

mysql = MySQL()
app.config['MYSQL_HOST'] = dbInfo[0]['MYSQL_HOST']
app.config['MYSQL_USER'] = dbInfo[0]['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = dbInfo[0]['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = dbInfo[0]['MYSQL_DB']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql.init_app(app)


# realtime track the live editing maps
liveMaps = {}


class RegistrationForm(Form):
    username = StringField('username', [validators.Length(min=2, max=35)])
    fullname = StringField('fullname', [validators.Length(min=2, max=35)])
    email = StringField('email', [validators.Length(min=6, max=35)])
    password = PasswordField('password', [
        validators.DataRequired(),
        validators.EqualTo('confirmPassword', message='Passwords must match')
    ])
    confirmPassword = PasswordField('confirmPassword')


class CreateMapForm(Form):
    mapTitle = StringField('mapTitle', [validators.Length(min=1, max=50)])
    # mode = StringField('mode', [validators.Length(min=1, max=1)])
    mode = SelectField('mode', choices=[('1', 'private'), ('2', 'public')])


@bp.route('/')
def home():
    return render_template('home.html')


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'loggedIn' in session:
            return f(*args, **kwargs)
        else:
            flash('You need an account to be able to create a Map', 'danger')
            return redirect(url_for('.login'))
    return wrap


@bp.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('.home'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)

    print('>>> form validation', form.validate())

    valid = form.validate()
    if(request.method == 'POST' and valid):
        print('>>> new user registered', form.fullname.data)
        fullname = form.fullname.data
        username = form.username.data
        email = form.email.data
        password = str(form.password.data)

        try:
            cur = mysql.connection.cursor()
            cur.execute('''
            insert into users (fullname, username, email, password)
            values(%s,%s,%s, md5(%s))''', (fullname, username, email, password))
            mysql.connection.commit()

            session['loggedIn'] = True
            session['username'] = username
            session['email'] = email

            flash('Welcome to our platform', 'success')
            return redirect(url_for('.home'))
        except Exception as e:
            flash('Error account was not created: '+str(e), 'danger')
            print('>>>>>', str(e))
            return redirect(url_for('.register'))

    # get request or invalide form
    if valid is False and request.method == 'POST':
        flash('Error account was not created check your inputs', 'danger')

    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if(request.method == 'POST'):
        email = request.form['email']
        password_input = request.form['password']

        cur = mysql.connection.cursor()
        result = cur.execute('select password, username, email from users where email = %s', (email, ))

        data = cur.fetchone()
        print('result', data)
        if result > 0:

            password = data['password']  # password

            print('---->', hashlib.md5(password_input.encode()).hexdigest(), password_input, password)
            if hashlib.md5(password_input.encode()).hexdigest() == password:
                app.logger.info('password matched!')

                session['loggedIn'] = True
                session['username'] = data['username']
                session['email'] = data['email']

                flash('You have successfully logged in', 'success')
                return redirect(url_for('.home'))
            else:
                flash('Unknown user or wrong password!', 'danger')
                return redirect(url_for('.login'))

            #  flash('Welcome to our platform', 'success')
        else:  # no math username
            flash('Unknown user or wrong password', 'danger')
            return redirect(url_for('.login'))

    else:
        return render_template('login.html')


@bp.route('/myMaps')
@is_logged_in
def myMaps():
    email = session.get('email')
    cur = mysql.connection.cursor()
    cur.execute('''select members.role as role, hash_code, md5(maps.id) as id,
                disable_map, mode, title, DATE_FORMAT(create_day,"%%d/%%m/%%Y")
                as date from maps left join members on members.map_id = maps.id
                where members.email = %s ''', (email,))
    data = cur.fetchall()

    return render_template('myMaps.html', maps=data)


@bp.route('/publicMaps')
def publicMaps():
    cur = mysql.connection.cursor()
    cur.execute('''select hash_code, title, DATE_FORMAT(create_day, "%%d/%%m/%%Y")
                as date from maps where mode='public'and disable_map = 'enable' ''', ())
    data = cur.fetchall()

    return render_template('publicMaps.html', maps=data)


@bp.route('/createMap', methods=['GET', 'POST'])
@is_logged_in
def createMap():

    if(request.method == 'POST'):
        form = CreateMapForm(request.form)
        if not form.validate():
            flash('Error, please fill all the fields')
            return redirect(url_for('.createMap'))

        mapTitle = request.form['mapTitle']
        mode = request.form['mode']
        email = session.get('email')

        # generate url
        path = email + str(datetime.datetime.now()) + str(randint(1000, 9999))
        path = hashlib.md5(path.encode()).hexdigest()

        # store to the database
        try:
            cur = mysql.connection.cursor()
            cur.execute('''insert into maps (mode, title, hash_code) values
                         (%s, %s, %s) ''', (mode, mapTitle, path))
            map_id = cur.lastrowid
            # result = cur.execute('''select id from users where email = %s ''',(email,))
            # if result <= 0:
            #     raise ValueError('User does not exists in the database')
            #
            # data = cur.fetchone()
            cur.execute('''insert into members (map_id,role, email)
                         values (%s,'admin', %s)''', (map_id, email))
            mysql.connection.commit()

            return redirect(url_for('.map', hash_id=path))
        except Exception as e:
            flash('Error a problem occured, please try again '+str(e), 'danger')
            return render_template('createMap.html')
    else:
        return render_template('createMap.html')


@bp.route('/deleteMap', methods=['POST'])
@is_logged_in
def deleteMap():
    data = request.get_json()
    mapId = data['mapId']
    email = session.get('email')

    try:
        cur = mysql.connection.cursor()
        cur.execute('''select id from maps where hash_code = %s ''', (mapId,))
        data = cur.fetchone()

        if data is None:
            return '-2'
        mapId = data['id']

        cur.execute('''select role from members where map_id = %s and email
                    = %s''', (mapId, email))
        data = cur.fetchone()

        if data is None:
            return '-3'

        role = data['role']
        if role != 'admin':
            return '-4'

        cur.execute('''delete from maps where id = %s''', (mapId,))
        mysql.connection.commit()

        if cur.rowcount == 0:
            return '0'
        else:
            return '1'

    except Exception as e:
        print('====', str(e))
        return '-1'


@bp.route('/map/<hash_id>')
def map(hash_id):

    cur = mysql.connection.cursor()
    cur.execute('''select mode, id, title from maps where hash_code =%s''', ((hash_id,)))
    data = cur.fetchone()

    if data is None:
        flash('Map not found')
        return redirect(url_for('.home'))

    mode = data['mode']
    if mode == 'public':
        return render_template('map.html', mode=mode, title=data['title'], hash_id=hash_id)
    else:
        if session.get('email'):
            cur.execute('''select email from members where map_id = %s''', ((data['id'],)))
            mem_data = cur.fetchall()

            findUser = False
            for row in mem_data:
                if row['email'] == session.get('email'):
                    findUser = True
                    break

            if findUser is True:
                clientGoLive(hash_id, session.get('email'))
                return render_template('map.html', title=data['title'],
                                       hash_id=hash_id, mode=mode)
            else:
                flash('You do not have access to this map')
                return redirect(url_for('.home'))

        else:
            flash('You need to login to be able to access that map')
            return redirect(url_for('.home'))


@bp.route('/getMembersOfMap/<hash_map>', methods=['GET'])
@is_logged_in
def getMembersOfMap(hash_map):
    email = session.get('email')

    try:
        cur = mysql.connection.cursor()
        cur.execute('''select id from maps where hash_code = %s ''',(hash_map,))
        data = cur.fetchone()
        mapId = data['id']
        cur.execute('''select id from members where email = %s and map_id = %s
                    ''',(email, mapId))
        data = cur.fetchone()
        if data is None:  # len(data) == 1:
            return '-2'

        cur.execute('''select username, role from members left join users on
                    users.email = members.email where map_id = %s''', (mapId,))
        data = cur.fetchall()
        return jsonify(data)

    except Exception as e:
        print('---', str(e))
        return '-1'


@bp.route('/inviteFriendToMap', methods=['POST'])
@is_logged_in
def inviteFriendToMap():

    email = session.get('email')
    data = request.get_json()
    hash_map_id = data['mapId']
    username = data['username']

    try:
        cur = mysql.connection.cursor()
        # get map id from hash
        cur.execute('''select id from maps where hash_code = %s ''',(hash_map_id, ))
        data = cur.fetchone()
        if data is None:
            return '-4'
        mapId = data['id']

        # check if user has writes to add a member
        cur.execute('''select role from members where email = %s and  map_id =
                    %s''', (email, mapId))
        data = cur.fetchone()
        if data is None or data['role'] != 'admin':
            return '-2'

        # get target user's email from given username
        cur.execute('''select email from users where username = %s ''',(username,))
        data = cur.fetchone()
        if data is None:
            return '-3'

        # insert new user to member table
        cur.execute('''insert into members (map_id, email) value (%s, %s)''',(mapId, data['email']))
        mysql.connection.commit()
        return '1'

    except Exception as e:
        return '-1'


@bp.route('/removeFriendFromMap', methods=['POST'])
@is_logged_in
def removeFriendFromMap():

    email = session.get('email')
    data = request.get_json()
    hash_map_id = data['mapId']
    username = data['username']

    try:
        cur = mysql.connection.cursor()
        # get map id from hash
        cur.execute('''select id from maps where hash_code = %s ''',(hash_map_id, ))
        data = cur.fetchone()
        if data is None:
            return '-4'
        mapId = data['id']

        # check if user has rights to remove a member
        cur.execute('''select role from members where email = %s and  map_id = %s''',(email, mapId))
        data = cur.fetchone()
        if data is None or data['role'] != 'admin':
            return '-2'

        # get target user's email from given username
        cur.execute('''select email from users where username = %s ''', (username, ))
        data = cur.fetchone()
        if data is None:
            return '-3'

        # remove user from members table
        cur.execute('''delete from members where map_id = %s and email = %s
                    and role <> 'admin' ''',(mapId, data['email']))
        mysql.connection.commit()

        if cur.rowcount == 0:
            return '0'
        else:
            return '1'

    except Exception as e:
        return '-1'


@bp.route('/findFriend', methods=['GET', 'POST'])
@is_logged_in
def findFriend():

    if(request.method == 'POST'):
        return 'nothing there'
    else:
        searchTxt = request.args.get('txt')
        if len(searchTxt) == 0:
            return jsonify([])

        try:
            cur = mysql.connection.cursor()
            cur.execute('''select md5(id) as id, username from users where
                        username like concat("%%", %s, "%%")''', (searchTxt, ))
            ans = cur.fetchall()
            return jsonify(ans)

        except Exception as e:
            return '-1'


@bp.route('/addMarkerToMap', methods=['POST'])
@is_logged_in
def addMarkerToMap():
    email = session.get('email')
    data = request.get_json()
    title = data['title']
    hash_map_id = data['mapId']
    lat = data['lat']
    lng = data['lng']

    try:
        cur = mysql.connection.cursor()
        # get map id from hash
        cur.execute('''select id from maps where hash_code = %s''', (hash_map_id, ))
        data = cur.fetchone()
        if data is None:
            return '-3'
        mapId = data['id']

        # check if user is a member of the map
        cur.execute('''select id from members where email = %s and
                    map_id = %s''', (email, mapId))
        data = cur.fetchone()
        if data is None:
            return '-2'

        # insert marker to the table
        cur.execute('''insert into markers ( map_id, lat, lng, title)
                    values (%s, %s, %s, %s)''', (mapId, str(lat), str(lng), title))
        mysql.connection.commit()
        return '1'

    except Exception as e:
        print('>>>', str(e))
        return '-1'


@bp.route('/getMarkersFromMap/<map_id>', methods=['GET'])
def getMarkersFromMap(map_id):

    try:
        cur = mysql.connection.cursor()
        cur.execute('''select id, mode from maps where hash_code = %s ''', (map_id, ))
        data = cur.fetchone()

        if data is None:
            return '-2'

        mapId = data['id']
        if data['mode'] == 'private':
            # check if user is a member of the map
            if session.get('email') is not None:
                cur.execute('''select id from members where map_id =%s and
                            email =%s ''', (mapId, session.get('email')))
                data = cur.fetchone()
                if data is None:
                    return '-3'

        cur.execute('''select lat, lng, title from markers where
                     map_id = %s''',(mapId, ))
        ans = cur.fetchall()
        return jsonify(ans)

    except Exception as e:
        return '-1'


@bp.route('/deleteMarkerFromMap', methods=['POST'])
@is_logged_in
def deleteMarkerFromMap():
    email = session.get('email')
    data = request.get_json()
    hash_map_id = data['mapId']
    marker_id = data['markerId']

    try:
        cur = mysql.connection.cursor()
        cur.execute('''select id from maps where hash_code = %s ''', (hash_map_id, ))

        data = cur.fetchone()
        if data is None:
            return '-2'
        mapId = data['id']

        cur.execute('''select id from members where map_id =%s and email = %s ''', (mapId, email))
        data = cur.fetchone()
        if data is None:
            return '-3'

        cur.execute('''delete from markers where concat(lat,lng) = %s''',(marker_id,))
        mysql.connection.commit()

        if cur.rowcount == 0:
            return '0'
        else:
            return '1'

    except Exception as e:
        return '-1'


@bp.route('/postMessageOnMarker', methods=['POST'])
@is_logged_in
def postMessageOnMarker():
    email = session.get('email')
    data = request.get_json()
    hash_map_id = data['mapId']
    marker_id = data['markerId']
    message = data['message']
    username = session.get('username')

    try:
        cur = mysql.connection.cursor()
        cur.execute('''select id from maps where hash_code = %s ''', (hash_map_id, ))
        data = cur.fetchone()

        if data is None:
            return '-2'

        mapId = data['id']
        cur.execute('''select id from members where map_id =%s and email = %s ''', (mapId, email))
        data = cur.fetchone()
        if data is None:
            return '-3'

        print('>>>>>>!!!!!', marker_id)
        cur.execute('''select id from markers where concat(lat,lng) = %s''',(marker_id,))
        data = cur.fetchone()
        if data is None:
            return '-4'
        marker_id =  data['id']  # real marker id not the lat+lng

        cur.execute('''insert into comments (map_id, markerId, username, msg)
                    values (%s, %s, %s, %s)''',(mapId, marker_id, username, message))
        mysql.connection.commit()

        return '1'

    except Exception as e:
        return -1


@bp.route('/getMessagesOfMarker/<map_id>/<marker_id>', methods=['GET'])
def getMessagesOfMarker(map_id, marker_id):
        cur = mysql.connection.cursor()
        cur.execute('''select id from maps where hash_code = %s ''', (map_id, ))
        data = cur.fetchone()
        if data is None:
            return '-2'
        map_id = data['id']

        cur.execute('''select id from markers where map_id = %s and
                    concat(lat, lng) = %s ''', (map_id, marker_id))
        data = cur.fetchone()
        if data is None:
            return '-3'
        marker_id = data['id']

        cur.execute('''select username, msg, datetime from comments where
                    map_id = %s and markerId = %s ''', (map_id, marker_id))
        ans = cur.fetchall()
        return jsonify(ans)


app.register_blueprint(bp)
socketio = SocketIO(app)


def clientGoLive(mapId, userEmail):
    """Call this function when a user connects to a map """

    if mapId in liveMaps.keys():
        liveMaps[mapId]['onlineUsers'].append(userEmail)
    else:
        liveMaps[mapId] = {'onlineUsers': [userEmail], 'sockets': []}
    print('new client!!!', liveMaps)


@socketio.on('connect')
def connect():
    print('Client connected from:' + request.remote_addr)


@socketio.on('initMap')
def initMap(data):
    mapId = data['mapId']
    email = session.get('email')

    if mapId in liveMaps:
        if email in liveMaps[mapId]['onlineUsers']:
            liveMaps[mapId]['sockets'].append(request.sid)
            # join_room(mapId)
        # else not auth on the map
    # map not live

    print('init map  >>>', liveMaps)


@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')
    email = session.get('email')

    for key, value in liveMaps.items():
        if email in liveMaps[key]['onlineUsers']:
            if request.sid in liveMaps[key]['sockets']:
                liveMaps[key]['onlineUsers'].remove(email)
                liveMaps[key]['sockets'].remove(request.sid)
                # leave_room(key)


@socketio.on('markerChange')
def marker(data):
    print('marker change!', data)
    mapId = data['mapId']
    for so in liveMaps[mapId]['sockets']:
        if request.sid != so:
            print('sockets', liveMaps[mapId]["sockets"])
            emit('markerChange', data, room=so)


@socketio.on('commentMarkerChange')
def commentMarkerChange(data):
    print('connet change!', data)
    mapId = data['mapId']
    for so in liveMaps[mapId]['sockets']:
        if request.sid != so:
            print('sockets', liveMaps[mapId]["sockets"])
            emit('commentMarkerChange', data, room=so)


@socketio.on('userMapChange')
def userMapChange(data):
    print('user change!', data)
    mapId = data['mapId']
    for so in liveMaps[mapId]['sockets']:
        if request.sid != so:
            print('sockets', liveMaps[mapId]["sockets"])
            emit('userMapChange', data, room=so)


if __name__ == '__main__':
    # app.run(debug=True)
    print('start the server')
    # http_server = WSGIServer(('', 5000), app)
    # http_server.serve_forever()
    # app.run()
    # socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    # socketio.run(app, host='0.0.0.0')
    # socketio.run(app)
    serve(socketio.run(app, host='0.0.0.0', debug=True), port=5000)
