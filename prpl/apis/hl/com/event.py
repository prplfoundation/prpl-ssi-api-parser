
class Event:
    """HL-API event wrapper.

    Example:
        # Import module.
        from prpl.apis.hl.com import Event as HLAPIEvent

        # Create new instance.
        api_event = HLAPIEvent(
            '0',
            'USER_ACCOUNTS_ADDED',
            'Raised when a new account is added.',
            '{"Header":{"Code":1,"Name":"USER_ACCOUNTS_ADDED"},"Body":{"AccountId":"User.Accounts.2"}}')

    """

    def __init__(self, code, name, description, sample):
        """Creates a new HL-API event.

        Args:
            code (int): Code of the event.
            name (str): Name of the event.
            description (str): Description of the event.
            sample (str): Event sample in JSON format.

        """

        self.code = code
        self.name = name
        self.description = description
        self.sample = sample

    def __str__(self):
        """Converts object to human-readable string.

        Returns:
            str: Human-readable representation of HL-API event.

        """

        return '{} - {}'.format(self.code, self.name)
