import unittest
from collections import Counter

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from cabletracker.Models import *
from cabletracker.Exceptions import *


def gen_ports() -> {str: Port}:
    return {'p1': Port(name='PP.1:01'), 'p2': Port(name='PP.2:01'),
            'p3': Port(name='PP.3:01'), 'p4': Port(name='PP.4:01')}


class ModelTest(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        self.session: Session = sessionmaker(bind=self.engine)()
        Base.metadata.create_all(self.engine)
        self.t_util = ModelUtil(self.session)
        self.t_ports = gen_ports()
        self.session.add_all(self.t_ports.values())


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
        ports_query = self.t_util.all_ports()
        self.assertEqual(list(self.t_ports.values()), ports_query)

    def test_empty_ports(self):
        ports_query = self.t_util.empty_ports()

        p1, p2, p3, p4 = self.t_ports.values()

        self.assertEqual(Counter([p1, p2, p3, p4]), Counter(ports_query))

        self.t_util.create_connection(p1, p2)
        ports_query = self.t_util.empty_ports()

        self.assertEqual(Counter([p3, p4]), Counter(ports_query))
        self.assertNotEqual(Counter([p1, p2]), Counter(ports_query))
        self.assertNotEqual(Counter([p1, p3]), Counter(ports_query))
        self.assertNotEqual(Counter([p1, p4]), Counter(ports_query))
        self.assertNotEqual(Counter([p2, p3]), Counter(ports_query))
        self.assertNotEqual(Counter([p2, p4]), Counter(ports_query))

    def test_all_links(self):
        # Should return nothing
        self.assertEqual(self.t_util.all_links(), [])

        p1, p2, _, _ = self.t_ports.values()
        link = self.t_util.create_connection(p1, p2)
        self.assertEqual([link], self.t_util.all_links())

        self.t_util.delete_connection(p1, p2)
        self.assertEqual([], self.t_util.all_links())

    def test_port_links(self):
        p1, p2, p3, _ = self.t_ports.values()

        # Test for empty list
        self.assertEqual(self.t_util.port_links(p1), [])

        link = self.t_util.create_connection(p1, p2)
        self.assertIn(link, self.t_util.port_links(p1))
        self.assertIn(link, self.t_util.port_links(p2))
        self.assertNotIn(link, self.t_util.port_links(p3))

    def test_port_connection(self):
        p1, p2, _, _ = self.t_ports.values()

        with self.assertRaises(SamePortException):
            self.t_util.port_connection(p1, p1)

        link = self.t_util.create_connection(p1, p2)
        self.assertTrue([link], self.t_util.port_connection(p1, p2))

    def test_link_exists(self):
        p1, p2, p3, _ = self.t_ports.values()

        # Test for False for non-existant Links
        self.assertFalse(self.t_util.link_exists(p1, p2))

        # Create Link to test
        self.t_util.create_connection(p1, p2)
        # Test for True for Link, and False for Port with only 1 Link
        self.assertTrue(self.t_util.link_exists(p1, p2))
        self.assertFalse(self.t_util.link_exists(p2, p3))

    def test_create_link(self):
        p1, p2, p3, _ = self.t_ports.values()

        link = self.t_util.create_connection(p1, p2)
        self.assertTrue(link.port_a is p1)
        self.assertTrue(link.port_b is p2)

        with self.assertRaises(LinkExistsException):
            self.t_util.create_connection(p1, p2)

    def test_delete_link(self):
        p1, p2, p3, _ = self.t_ports.values()

        with self.assertRaises(LinkDoesntExistException):
            self.t_util.delete_connection(p1, p2)

        link = self.t_util.create_connection(p1, p2)
        link_deleted = self.t_util.delete_connection(p1, p2)
        self.assertEqual(link, link_deleted)
        with self.assertRaises(LinkDoesntExistException):
            self.t_util.delete_connection(p1, p2)
