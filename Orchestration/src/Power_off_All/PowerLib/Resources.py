from cloudshell.api.cloudshell_api import ReservedResourceInfo


class ResourceDetails(object):
    def __init__(self, resource_details):
        """
        input will look like this:
        Port1|!My Device\Port1|!Device Family|!Device Model|!1|!False
        :param str resource_details: resource details as received from the server
        """
        details = resource_details.strip('\r').split('|!')
        self.name = details[0]
        self.fullname = details[1].replace('\\', '/')
        self.family = details[2]
        self.model = details[3]
        self.address = details[4]
        self.isShared = details[5] == 'True'
        self.subresource = True if '/' in self.fullname else False

    @classmethod
    def create_from_ReservedResourceInfo(cls, resource):
        """

        :param ReservedResourceInfo resource:
        :return:
        """
        self = cls.__new__(cls)
        self.name = resource.Name
        if resource.FolderFullPath == '':
            self.fullname = resource.Name
        else:
            self.fullname = resource.FolderFullPath + '/' + resource.Name
        self.family = resource.ResourceFamilyName
        self.model = resource.ResourceModelName
        self.address = resource.FullAddress
        self.isShared = resource.Shared
        self.subresource = True if '/' in resource.FullAddress else False
        return self


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

    @classmethod
    def create_from_ReservedResourceInfo_dict(cls, resources):
        """

        :param Dict[str, ReservedResourceInfo] resources:
        :return:
        """
        resources_out = []
        for (key, reserved_resource_info) in resources.iteritems():
            resources_out.append(ResourceDetails.create_from_ReservedResourceInfo(reserved_resource_info))
        return resources_out
