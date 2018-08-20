
class Instance:
    """HL-API Object instance wrapper.

    Example:
        # Import module.
        from prpl.apis.hl.com import Instance as HLAPIInstance

        # Create new instance.
        api_instance = HLAPIInstance('WUI:Admin', 'Web-GUI administrator account.')

    """

    def __init__(self, name, description):
        """Creates a new HL-API object instance.

        Args:
            name (str): Name of the object instance.
            description (str): Description of the object instance.

        """

        self.name = name
        self.description = description

    def __str__(self):
        """Converts object to human-readable string.

        Returns:
            str: Human-readable representation of HL-API object instance.

        """

        return self.name
