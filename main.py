from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Models import *
from Commands import *

engine = create_engine('sqlite:///:memory:', echo=True)
session = sessionmaker(bind=engine)()

Base.metadata.create_all(engine)

# p1 = Port(name='PP.1:01')
# p2 = Port(name='PP.2:01')
#
# session.add_all([p1, p2])
# session.add(Link(end_a=p1, end_b=p2))
#
# print(session.query(Port).all())
# print(session.query(Link).all())

PROMPT = '> '


while True:
    response = input(PROMPT).split()
    if len(response) is 0:
        continue
    if response[0] == 'help':
        print(cmd_help())
