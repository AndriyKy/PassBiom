import datetime 
import numpy as np
from peewee import *

    ## Connecting to the DB
db = SqliteDatabase('Face_rec_data.sqlite')

class BaseModel(Model):
    class Meta:
        database = db

    ## Connecting to the spreadsheets
class Users_data(BaseModel):
    user_id = AutoField(column_name='User ID')
    pos = TextField(column_name='Position')
    doc_id = CharField(column_name='Document ID', unique=True)
    l_n = TextField(column_name='Last name')
    f_n = TextField(column_name='First name')
    m_n = TextField(column_name='Middle name', null=True)
    face = BlobField(column_name='Face coding')

    class Meta:
        table_name = 'Users data'

class Registration(BaseModel):
    id = AutoField(column_name='ID')
    user_id = ForeignKeyField(model=Users_data, field=Users_data.user_id, backref='registrations')
    d_t = DateTimeField(column_name='Date, time', default=datetime.datetime.now)
    temp = FloatField(null=True, column_name='Temperature')
    ver = FixedCharField(max_length=1, column_name='Verification')

    class Meta:
        table_name = 'Registration'

#db.create_tables([Users_data, Registration])

def lists_gen():
    face = []
    name = []
    position = []
    for item in Users_data.select():
        face.append(np.frombuffer(item.face, float))
        name.append(item.f_n)
        position.append(item.pos)
        
    return face, name, position

def ListOfRoles(serial):
    # Get Table object
    table = Table(name='Roles', columns=[serial], _database=db)
    dict_of_roles = table.select().execute()
    values = []

    # Dictionary values -> List
    for role in dict_of_roles:
        values.append(list(role.values())[0])

    return values

db.close()