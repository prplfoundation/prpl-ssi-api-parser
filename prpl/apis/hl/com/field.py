
class Field:
    """HL-API field wrapper.

    Example:
        # Import module.
        from prpl.apis.hl.com import Field as HLAPIField

        # Create new instance.
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

    """

    def __init__(self, name, description, type, is_input, is_required, default_value, is_output, possible_values,
                 format, notes):
        """Creates a new HL-API field.

        Args:
            name (str): Name of the field.
            description (str): Description of the field.
            type (str): Field type, typically 'String', 'Boolean', 'Integer', 'Float' or 'List'.
            is_input (bool): Is argument flag. When set to 'True' the field is part of the requested body.
            is_required (bool): Is required flag. When set to 'True' the field is mandatory (non-optional).
            default_value (str): Value to assume when the field is not specified. Only applicable to optional fields.
            is_output (bool): Is output flag. When set to 'True' the field is part of the response body.
            possible_values (str): List of possible field values (input/output).
            format (str): Format of the field (e.g.: time-stamp format or field units).
            notes (str): Field notes.
                Usually a human-readable concatenation of the 'default_value', 'possible_values' and 'format' fields.

        """

        self.name = name
        self.description = description
        self.type = type
        self.is_input = is_input
        self.is_required = is_required
        self.default_value = default_value
        self.is_output = is_output
        self.possible_values = possible_values
        self.format = format
        self.notes = notes

    def __str__(self):
        """Converts object to human-readable string.

        Returns:
            str: Human-readable representation of HL-API field.

        """

        return self.name
