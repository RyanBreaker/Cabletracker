from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cabletracker.models import ModelUtil, Base, Port

engine = create_engine('sqlite:///:memory:')
session = sessionmaker(bind=engine)()
Base.metadata.create_all(engine)

util = ModelUtil(session)

p1 = Port(name='PP.1:01')
p2 = Port(name='PP.2:01')
p3 = Port(name='PP.3:01')

session.add_all([p1, p2, p3])
util.create_connection(p1, p2)
util.create_connection(p2, p3)
