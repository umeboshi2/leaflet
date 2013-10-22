from crypt import crypt
import random
from string import ascii_letters

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from sqlalchemy.orm.exc import NoResultFound

from trumpet.security import make_authn_authz_policies

from leaflet.models.usergroup import User, Password


def make_salt(id=5, length=10):
    phrase = ''
    for ignore in range(length):
        phrase += random.choice(ascii_letters)
    return '$%d$%s$' % (id, phrase)


def encrypt_password(password):
    salt = make_salt()
    encrypted = crypt(password, salt)
    return encrypted


def check_password(encrypted, password):
    if '$' not in encrypted:
        raise RuntimeError("we are supposed to be using random salt.")
    ignore, id, salt, epass = encrypted.split('$')
    salt = '$%s$%s$' % (id, salt)
    check = crypt(password, salt)
    return check == encrypted


def authenticate(userid, request):
    #print "called authenticate", request.params
    dbsession = request.db
    user = None
    try:
        user = dbsession.query(User).filter_by(username=userid).one()
    except NoResultFound:
        pass
    if user is None:
        pass
    else:
        #print "GROUPS--->", user.get_groups()
        return user.get_groups()


