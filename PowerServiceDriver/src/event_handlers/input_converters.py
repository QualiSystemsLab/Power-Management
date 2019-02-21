

class ActionDetails:
    def __init__(self, action_details):
        """
        input will look like this:
        Username|!Domain|!Admin|!DomainAdmin|!ExternalUser|!ViewOnly
        admin|!Global|!True|!True|!False|!False
        :param str action_details: action details as received from the server
        """
        lines = action_details.split('\n')
        details = lines[1].split('|!')
        self.user = details[0]
        self.domain = details[1]
        self.isDomainAdmin = bool(details[2])
        self.isExternalUser = bool(details[3])
        self.isViewOnly = bool(details[4])


class ServiceDetails:
    def __init__(self, service_details):
        """
        input will look like this:
        [Alias|!OldAlias|!Family|!Model] #optional line when there is only one service
        ServiceExtensibilityTemplate|!|!Extenisbility Services|!ServiceExtensibilityTemplate
        :param str service_details: service details as received from the server
        """
        lines = service_details.split('\n')
        if lines.count > 1:
            details = lines[1].split('|!')
        else:
            details = service_details.split('|!')
        self.alias = details[0]
        self.oldalias = details[1]
        self.family = details[2]
        self.model = details[3]


class ServicesDetails:
    def __init__(self, services_details):
        """
        input will look like this:
        Alias|!OldAlias|!Family|!Model
        ServiceExtensibilityTemplate|!|!Extenisbility Services|!ServiceExtensibilityTemplate
        :param str services_details: service details as received from the server
        """
        lines = services_details.split('\n')
        curline = 1
        self.services = []
        """:type : list[ServiceDetails]"""
        while curline < len(lines):
            if len(lines[curline].strip()) > 0:
                self.services.append(ServiceDetails(lines[curline]))
            curline += 1


class ResourceDetails:
    def __init__(self, resource_details):
        """
        input will look like this:
        Port1|!My Device\Port1|!Device Family|!Device Model|!1|!False
        :param str resource_details: resource details as received from the server
        """
        details = resource_details.split('|!')
        self.name = details[0]
        self.fullname = details[1].replace('\\', '/')
        self.family = details[2]
        self.model = details[3]
        self.address = details[4]
        self.isShared = bool(details[5])


class ResourcesDetails:
    def __init__(self, resources_details):
        """
        input will look like this:
        Name|!FullName|!Family|!Model|!Address|!Shared
        Port1|!My Device\Port1|!Device Family|!Device Model|!1|!False
        :param str resources_details: resources details as received from the server
        """
        lines = resources_details.split('\n')
        curline = 1
        self.resources = []
        """:type : list[ResourceDetails]"""
        while curline < len(lines):
            if len(lines[curline].strip()) > 0:
                self.resources.append(ResourceDetails(lines[curline]))
            curline += 1


class ConnectionDetails:
    def __init__(self, connection_details):
        """
        input will look like this:
        PC3/Port4|!PC4/Port4|!|!bi
        :param str connection_details: connection details as received from the server
        """
        details = connection_details.split('|!')
        self.source = details[0]
        self.target = details[1]
        self.alias = details[2]
        self.direction = details[3]


class ConnectionsDetails:
    def __init__(self, connections_details):
        """
        input will look like this:
        SourceName|!TargetName|!Alias|!Direction
        PC3/Port4|!PC4/Port4|!|!bi
        :param str connections_details: connection details as received from the server
        """
        lines = connections_details.split('\n')
        curline = 1
        rcount = 0
        self.connections = []
        """:type : list[ConnectionDetails]"""
        while curline < len(lines):
            if len(lines[curline].strip()) > 0:
                self.connections[rcount] = ConnectionDetails(lines[curline])
                rcount += 1
            curline += 1


class AttributeDetails:
    def __init__(self, attribute_details):
        """
        input will look like this:
        ExtensionServiceTemplate|!Auto Add To Reservation|!False
        :param str attribute_details: attribute details as received from the server
        """
        details = attribute_details.split('|!')
        self.name = details[0]
        self.attribute_name = details[1]
        self.attribute_value = details[2]


class AttributesDetails:
    def __init__(self, attributes_details):
        """
        input will look like this:
        Name,AttributeName,AttributeValue
        ExtensionServiceTemplate|!Auto Add To Reservation|!False
        :param str attributes_details: attributes details as received from the server
        """
        lines = attributes_details.split('\n')
        curline = 1
        rcount = 0
        self.attributes = []
        """:type : list[AttributeDetails]"""
        while curline < len(lines):
            if len(lines[curline].strip()) > 0:
                self.attributes[rcount] = AttributeDetails(lines[curline])
                rcount += 1
            curline += 1

