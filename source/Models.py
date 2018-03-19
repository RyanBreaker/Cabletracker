from sqlalchemy import Column, Integer, String, ForeignKey, or_
from sqlalchemy.orm import validates, relationship, Query, Session
from sqlalchemy.ext.declarative import declarative_base

__all__ = ["ModelException", "PortBadNameException", "SamePortException", "PortFullException", "LinkExistsException",
           "LinkDoesntExistException", "Link", "Port", "Base"]

Base = declarative_base()

### Model Exceptions
class ModelException(Exception):
    message = None

    def __str__(self):
        return self.message


class PortBadNameException(ModelException):
    message = "Name must start with 'PP', 'FP', or 'RR'."


class SamePortException(ModelException):
    message = "The given Ports are the same."


class PortFullException(ModelException):
    def __init__(self, port: "Port"):
        self.message = "'{}' is already full.".format(port.name)


class LinkExistsException(ModelException):
    def __init__(self, ports: ["Port"]):
        self.message = "A link already exists between ports '{}' and '{}'.".format(ports[0].name, ports[1].name)


class LinkDoesntExistException(ModelException):
    def __init__(self, ports: ["Port"]):
        self.message = "No link between '{}' and '{}' exists.".format(ports[0].name, ports[1].name)


### Models
class Port(Base):
    __tablename__ = 'ports'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, default='', nullable=False)

    @validates('name')
    def validate_name(self, _, name: str):
        name = name.upper().strip()
        if not name.startswith(('PP', 'FP', 'RR')):
            raise PortBadNameException()
        return name

    def __repr__(self):
        return "<Port(name='{}', description='{}')>".format(self.name, self.description)

    def links(self, session: Session) -> ["Link"]:
        return session.query(Link).filter(
            or_(
                Link.end_a_id == self.id,
                Link.end_b_id == self.id
            )
        ).order_by(Link.id).all()

    def full(self, session: Session) -> bool:
        return len(self.links(session)) is 2

    def linked_to(self, session: Session, port: "Port"):
        links = self.links(session)
        while links:
            link = links.pop()
            if link.end_a is port or link.end_b is port:
                return True
        return False

    @staticmethod
    def create_link(session: Session, port_a: "Port", port_b: "Port") -> "Link":
        if port_a is port_b:
            raise SamePortException()

        existing_a = port_a.links(session)
        existing_b = port_b.links(session)

        # Make sure ports aren't full
        if port_a.full(session):
            raise PortFullException(port_a)
        if port_b.full(session):
            raise PortFullException(port_b)

        # Check for preexisting connections
        if len(existing_a) is 1:
            link = existing_a[0]
            if link.end_a is port_b or link.end_b is port_b:
                raise LinkExistsException([port_a, port_b])

        if len(existing_b) is 1:
            link = existing_b[0]
            if link.end_a is port_a or link.end_b is port_a:
                raise LinkExistsException([port_a, port_b])

        link = Link(end_a=port_a, end_b=port_b)
        session.add(link)

        return link

    @staticmethod
    def remove_link(session: Session, port_a: "Port", port_b: "Port") -> "Link":
        if port_a is port_b:
            raise SamePortException()

        links = port_a.links(session)
        while links:
            link = links.pop()
            if link.end_a is port_b or link.end_b is port_b:
                session.delete(link)
                return link

        # If nothing was returned, then no link existed nor could be deleted
        raise LinkDoesntExistException([port_a, port_b])


class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True)
    description = Column(String, default='', nullable=False)

    end_a_id = Column(Integer, ForeignKey('ports.id'), index=True)
    end_b_id = Column(Integer, ForeignKey('ports.id'), index=True)
    end_a = relationship('Port', foreign_keys=end_a_id)
    end_b = relationship('Port', foreign_keys=end_b_id)

    @property
    def serial(self) -> str:
        return '{:06x}'.format(self.id)

    @property
    def full(self) -> bool:
        return self.end_a and self.end_b

    def __repr__(self):
        end_a = 'None' if self.end_a is None else self.end_a.name
        end_b = 'None' if self.end_b is None else self.end_b.name
        return "<Link(serial='{}', port_a='{}', port_b='{}')>".format(self.serial, end_a, end_b)
