from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Models import *
from Commands import *

engine = create_engine('sqlite:///:memory:')
session = sessionmaker(bind=engine)()

Base.metadata.create_all(engine)

p1 = Port(name='PP.1:01')
p2 = Port(name='PP.2:01')
p3 = Port(name='PP.3:01')

session.add_all([p1, p2, p3])
Port.create_link(session, p1, p2)
Port.create_link(session, p1, p2)

print(session.query(Port).all())
print(session.query(Link).all())
print(p2.links(session))

# PROMPT = '> '
#
#
# while True:
#     response = input(PROMPT).split()
#     if len(response) is 0:
#         continue
#     if response[0] == 'help':
#         print(cmd_help())
