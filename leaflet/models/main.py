import transaction

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey


from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError

from leaflet.models.base import Base, DBSession

# these models depend on the Base object above

import leaflet.models.usergroup
import leaflet.models.sitecontent


class LoginHistory(Base):
    __tablename__ = 'login_history'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    when = Column(DateTime, primary_key=True)
    

populate = leaflet.models.usergroup.populate


def make_test_data(session):
    from leaflet.security import encrypt_password
    from leaflet.models.usergroup import User, Group, UserGroup
    from leaflet.models.usergroup import Password
    db = session
    users = ['thor', 'zeus', 'loki']
    id_count = 1 # admin is already 1
    manager_group_id = 4 # magic number
    # add users
    try:
        with transaction.manager:
            for uname in users:
                id_count += 1
                user = User(uname)
                password = encrypt_password('p22wd')
                db.add(user)
                pw = Password(id_count, password)
                db.add(pw)
                ug = UserGroup(manager_group_id, id_count)
                db.add(ug)
    except IntegrityError:
        transaction.abort()
