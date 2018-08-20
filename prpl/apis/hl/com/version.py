
class Version:
    """HL-API version wrapper.

    Example:
        # Import module.
        from prpl.apis.hl.com import Version as HLAPIVersion

        # Create new instance.
        api_version = HLAPIVersion('3.5', '2018-04-13')

        # Append change.
        api_version.change_list.append((1, 'Added new "foo" object.'))

    """

    def __init__(self, number, date):
        """Creates a new HL-API version.

        Args:
            number (str): API version number.
            date (str): API release date.

        """

        self.number = number
        self.date = date
        self.change_list = []

    def __str__(self):
        """Converts object to human-readable string.

        Returns:
            str: Human-readable representation of HL-API version.

        """

        return '{} ({})'.format(self.number, self.date)

    def get_changes(self):
        """Converts list of changes to a string.

        Returns:
            str: List of changes as a single string.

        """

        changes = list(map(lambda x: '{}. {}'.format(x[0], x[1]), self.change_list))
        return '\n'.join(changes)
