
class ResponseCode:
    """HL-API response code wrapper.

    Example:
        # Import module.
        from prpl.apis.hl.com import ResponseCode as HLAPIResponseCode

        # Create new instance.
        api_response_code = HLAPIResponseCode(
            '0',
            'OK',
            'A well-formed call was performed and successfully processed.',
            '{"Header":{"Code":0,"Name":"OK"},"Body":{"Id":0,"Name":"Guest"}}')

    """

    def __init__(self, name, description, sample):
        """Creates a new HL-API event.

        Args:
            code (int): Return code unique identifier.
            name (str): Return code name.
            description (str): Return code description.
            sample (str): Return code sample, in JSON format.

        """

        # self.code = code
        self.name = name
        self.description = description
        self.sample = sample

    def __str__(self):
        """Converts object to human-readable string.

        Returns:
            str: Human-readable representation of HL-API response code.

        """

        return '{} - {}'.format(self.name)

