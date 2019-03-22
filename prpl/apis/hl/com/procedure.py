
class Procedure:
    """HL-API procedure wrapper.

    Example:
        # Import module.
        from prpl.apis.hl.com import Procedure as HLAPIProcedure

        # Create new instance.
        api_procedure = HLAPIProcedure(
            'Set',
            'Modifies the account.',
            '{"Name":"Admin"}',
            '{"Header":{"Code":0,"Name":"OK"}}')

        # Append field.
        from prpl.apis.hl.com import Field as HLAPIField

        api_field = HLAPIField(
            'Password',
            'Account password.',
            'String',
            True,
            False,
            'the currently configured value',
            False,
            'True or False.',
            None,
            'Default value is the currently configured value. Possible values are True or False.')

        api_procedure.fields.append(api_field)

    """

    def __init__(self, name, description, sample_request, sample_response):
        """Creates a new HL-API procedure.

        Args:
            name (str): Name of the procedure.
            description (str): Description of the procedure.
            sample_request (str): Sample request body (i.e.: arguments) in JSON format.
            sample_response (str): Sample response body in JSON format.

        """

        self.name = name
        self.description = description
        self.sample_request = sample_request
        self.sample_response = sample_response
        self.parameters = []

    def __str__(self):
        """Converts object to human-readable string.

        Returns:
            str: Human-readable representation of HL-API procedure.

        """

        return self.name
