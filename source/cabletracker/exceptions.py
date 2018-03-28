class ModelException(Exception):
    message = None

    def __str__(self):
        return self.message


class PortBadNameException(ModelException):
    message = "Port name must start with 'PP', 'FP', or 'RR'."


class SamePortException(ModelException):
    message = "The given Ports are the same."


class PortFullException(ModelException):
    def __init__(self, port):
        self.message = "'{}' is already full.".format(port.name)


class LinkExistsException(ModelException):
    def __init__(self, port_a, port_b):
        self.message = "A link already exists between ports '{}' and '{}'.".format(port_a.name, port_b.name)


class LinkDoesntExistException(ModelException):
    def __init__(self, port_a, port_b):
        self.message = "No link between '{}' and '{}' exists.".format(port_a.name, port_b.name)
