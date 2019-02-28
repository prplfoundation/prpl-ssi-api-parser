
from operator import attrgetter


class API:
    """HL-API wrapper.

    Example:
        # Import module.
        from prpl.apis.hl.com import API as HLAPI

        # Create list of objects.
        api_objects = []

        # Create list of response codes.
        api_response_codes = []

        # Create list of version.
        api_versions = []

        # Create API.
        api = HLAPI(api_objects, api_response_codes, api_versions)

    """

    def __init__(self, objects, response_codes, versions):
        """Creates a new HL-API.

        Args:
            objects (list<prpl.apis.hl.com.Object>): List of objects part of the API.
            response_codes (list<prpl.apis.hl.com.ResponseCode>): List of response codes part of the API.
            versions (list<prpl.apis.hl.com.Version>): List of API versions change-log.

        """

        self.objects = objects
        self.response_codes = response_codes
        self.versions = sorted(versions, key=attrgetter('number'), reverse=True)

    def __str__(self):
        """Converts API to human-readable string.

        Returns:
            str: Human-readable representation of HL-API.

        """

        return 'v{} ({} objects)'.format(self.get_version(), len(self.objects))

    def get_version(self):
        """Returns the API version number.

        Returns:
            str: Current API version.

        """

        return self.versions[0].number
