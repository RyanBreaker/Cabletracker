import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from Models import *


def gen_ports() -> {str: Port}:
    return {'p1': Port(name='PP.1:01'), 'p2': Port(name='PP.2:01'),
            'p3': Port(name='PP.3:01'), 'p4': Port(name='PP.4:01')}


class ModelTest(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        self.session: Session = sessionmaker(bind=self.engine)()
        Base.metadata.create_all(self.engine)


class PortTest(ModelTest):
    def test_validate_name(self):
        port = Port(name=' pp.1:01  ')
        # Verify upper() and strip() worked
        self.assertEqual(port.name, 'PP.1:01')
        self.session.add(port)

        # Don't allow blank names
        with self.assertRaises(PortBadNameException):
            Port(name='')
        # Names must start with 'PP', 'FP', or 'RR'
        with self.assertRaises(PortBadNameException):
            Port(name='foo')

    def test_links(self):
        pass

    def test_full(self):
        ports = gen_ports()
        self.session.add_all(ports.values())

        p1, p2, p3, p4 = ports.values()
        Port.create_link(self.session, p1, p2)
        Port.create_link(self.session, p2, p3)

        self.assertFalse(p1.full(self.session))
        self.assertTrue(p2.full(self.session))
        self.assertFalse(p3.full(self.session))


    def test_port_create_link(self):
        p1 = Port(name='PP.1:01')
        p2 = Port(name='PP.2:01')
        p3 = Port(name='PP.3:01')
        p4 = Port(name='PP.4:01')

        self.session.add_all([p1, p2, p3, p4])
        link_1 = Port.create_link(self.session, p1, p2)

        self.assertEqual(link_1.end_a, p1)
        self.assertEqual(link_1.end_b, p2)

        with self.assertRaises(SamePortException):
            Port.create_link(self.session, p1, p1)

        with self.assertRaises(LinkExistsException):
            Port.create_link(self.session, p1, p2)

        link_2 = Port.create_link(self.session, p2, p3)

        self.assertEqual(link_2.end_a, p2)
        self.assertEqual(link_2.end_b, p3)

        with self.assertRaises(PortFullException):
            Port.create_link(self.session, p2, p4)
