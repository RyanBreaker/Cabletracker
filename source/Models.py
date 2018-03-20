import contextlib

from sqlalchemy import Column, Integer, String, ForeignKey, or_, and_, exists
from sqlalchemy.orm import validates, relationship, Session
from sqlalchemy.ext.declarative import declarative_base

__all__ = ["ModelException", "PortBadNameException", "SamePortException", "PortFullException", "LinkExistsException",
           "LinkDoesntExistException", "Link", "Port", "ModelUtil", "Base"]

Base = declarative_base()


# Model Exceptions
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
    def __init__(self, port_a: "Port", port_b: "Port"):
        self.message = "A link already exists between ports '{}' and '{}'.".format(port_a.name, port_b.name)


class LinkDoesntExistException(ModelException):
    def __init__(self, port_a: "Port", port_b: "Port"):
        self.message = "No link between '{}' and '{}' exists.".format(port_a.name, port_b.name)


# Models
class Port(Base):
    __tablename__ = 'ports'

    id: Column = Column(Integer, primary_key=True)
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

    def __hash__(self):
        return hash(self.name)


class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True)
    description = Column(String, default='', nullable=False)

    port_a_id: Column = Column(Integer, ForeignKey('ports.id'), index=True, nullable=False)
    port_b_id: Column = Column(Integer, ForeignKey('ports.id'), index=True, nullable=False)
    port_a = relationship('Port', foreign_keys=port_a_id)
    port_b = relationship('Port', foreign_keys=port_b_id)

    @property
    def serial(self) -> str:
        """
        :return: Serial of the Link, in Hex form
        """
        return '{:06x}'.format(self.id)

    def __repr__(self):
        port_a = 'None' if self.port_a is None else self.port_a.name
        port_b = 'None' if self.port_b is None else self.port_b.name
        return "<Link(serial='{}', port_a='{}', port_b='{}')>".format(self.serial, port_a, port_b)


class ModelUtil:
    """
    Utility class for running operations on the Port and Link models with the given Session.
    """
    session = None

    def __init__(self, session: Session):
        self.session = session

    def all_ports(self) -> [Port]:
        """
        :return: A list of all Ports in the database
        """
        return self.session.query(Port).order_by(Port.name).all()

    def empty_ports(self) -> [Port]:
        """
        :return: A list of all empty Ports (no Links connected)
        """
        return self.session.query(Port).filter(
            ~exists().where(
                or_(
                    Link.port_a_id == Port.id,
                    Link.port_b_id == Port.id
                )
            )
        ).order_by(Port.name).all()

    def partial_ports(self) -> [Port]:
        """
        :return: A list of all Ports with just one Link connected
        """
        pass

    def all_links(self) -> [Link]:
        """
        :return: A list of all Links in the database
        """
        return self.session.query(Link).order_by(Link.id).all()

    def port_links(self, port: Port) -> [Link]:
        """
        Returns all links relevant to the given Port
        :param port: Port to search for connected links
        :return: A list of Links connected to the given Port.
        """
        return self.session.query(Link).filter(
            or_(
                Link.port_a == port,
                Link.port_b == port
            )
        ).order_by(Link.id).all()

    def port_connection(self, port_a: Port, port_b: Port) -> Link:
        """
        Returns the Link that connects the given Ports, raises LinkDoesntExistException if none exist.
        :return: The Link that connects the given Ports
        """
        if port_a is port_b:
            raise SamePortException()

        port_a_links = self.port_links(port_a)
        while port_a_links:
            link = port_a_links.pop()
            if link.port_a is port_b or link.port_b is port_b:
                return link
        raise LinkDoesntExistException(port_a, port_b)

    def link_exists(self, port_a: Port, port_b: Port) -> bool:
        """
        Convenience function for checking whether a link exists between two Ports
        :return: True if a link exists, False otherwise
        """
        try:
            self.port_connection(port_a, port_b)
            return True
        except LinkDoesntExistException:
            return False

    def create_connection(self, port_a: Port, port_b: Port) -> Link:
        """
        Creates a Link connecting the given port_a and port_b, raises LinkExistsException if a Link already exists
        :return: The Link that was created
        """
        if self.link_exists(port_a, port_b):
            raise LinkExistsException(port_a, port_b)

        link = Link(port_a=port_a, port_b=port_b)
        self.session.add(link)
        return link

    def delete_connection(self, port_a: Port, port_b: Port) -> Link:
        """
        Deletes the Link between the given Ports, raises LinkDoesntExistException if a Link doesn't exist
        :return: The Link that was deleted
        """
        # LinkDoesntExistException will be raised here if the Link doesn't exist
        link = self.port_connection(port_a, port_b)
        self.session.delete(link)
        return link
