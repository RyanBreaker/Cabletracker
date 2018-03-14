from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Port(Base):
    __tablename__ = 'ports'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, default='', nullable=False)

    @validates('name')
    def validate_name(self, _, name):
        name = name.upper()
        assert len(name) > 0
        assert name.startswith(('PP', 'FP', 'RR'))
        return name

    def __repr__(self):
        return "<Port(name='{}', description='{}')>".format(self.name, self.description)


class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True)
    description = Column(String, default='', nullable=False)

    end_a_id = Column(Integer, ForeignKey('ports.id'), unique=True)
    end_b_id = Column(Integer, ForeignKey('ports.id'), unique=True)
    end_a = relationship('Port', foreign_keys=end_a_id, backref='side_a')
    end_b = relationship('Port', foreign_keys=end_b_id, backref='side_b')

    @property
    def serial(self):
        return '{:06x}'.format(self.id)

    def __repr__(self):
        end_a = 'None' if self.end_a is None else self.end_a.name
        end_b = 'None' if self.end_b is None else self.end_b.name
        return "<Link(serial='{}', port_a='{}', port_b='{}')>".format(self.serial, end_a, end_b)
