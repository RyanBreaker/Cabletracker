import unittest
from collections import Counter

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
        self.util = ModelUtil(self.session)
        self.t_ports = gen_ports()


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


class ModelUtilTest(ModelTest):

    def test_all_ports(self):
        ports = gen_ports()
        self.session.add_all(ports.values())
        ports_query = self.util.all_ports()

        self.assertListEqual(list(ports.values()), ports_query)

    def test_empty_ports(self):
        ports = gen_ports()
        self.session.add_all(ports.values())
        ports_query = self.util.empty_ports()

        p1, p2, p3, p4 = ports.values()

        self.assertEqual(Counter([p1, p2, p3, p4]), Counter(ports_query))

        self.util.create_link(p1, p2)
        ports_query = self.util.empty_ports()

        self.assertEqual(Counter([p3, p4]), Counter(ports_query))
        self.assertNotEqual(Counter([p1, p2]), Counter(ports_query))
        self.assertNotEqual(Counter([p1, p3]), Counter(ports_query))
        self.assertNotEqual(Counter([p1, p4]), Counter(ports_query))
        self.assertNotEqual(Counter([p2, p3]), Counter(ports_query))
        self.assertNotEqual(Counter([p2, p4]), Counter(ports_query))

    # def test_port_links(self):
    #     p1, p2, p3, p4 = self.t_ports.values()
    #
    #     self.assertListEqual()
    #
    # def test_link_exists(self):
    #     p1, p2, p3, p4 = self.t_ports.values()
    #
    #     self.assertFalse(self.util.link_exists(p1, p2))
    #
    #     self.util.create_link(p1, p2)
    #     self.assertTrue(self.util.link_exists(p1, p2))
    #
    # def test_create_link(self):
    #     p1, p2, p3, p4 = self.t_ports.values()
    #
    #     link = self.util.create_link(p1, p2)
    #     self.assertTrue(link.port_a is p1)
    #     self.assertTrue(link.port_b is p2)
    #
    #     # with self.assertRaises(LinkExistsException):
    #     #     self.util.create_link(p1, p2)
