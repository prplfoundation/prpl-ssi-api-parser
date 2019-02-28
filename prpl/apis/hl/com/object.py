
class Object:
    """HL-API Object wrapper.

    Example:
        # Import module.
        from prpl.apis.hl.com import Object as HLAPIObject

        # Create new instance.
        api_object = HLAPIObject(1, 'User.Accounts.{AccountId}', 'User Account').

        # Append procedure.
        from prpl.apis.hl.com import Procedure as HLAPIProcedure

        api_procedure = HLAPIProcedure(
            'Set',
            'Modifies the account.',
            '{"Name":"Admin"}',
            '{"Header":{"Code":0,"Name":"OK"}}')

        api_object.procedures.append(api_procedure)

        # Append event.
        from prpl.apis.hl.com import Event as HLAPIEvent

        api_event = HLAPIEvent(
            'USER_ACCOUNTS_ADDED',
            'Raised when a new account is added.',
            '{"Header":{"Code":1,"Name":"USER_ACCOUNTS_ADDED"},"Body":{"AccountId":"User.Accounts.2"}}')

        api_object.events.append(api_event)

        # Append instance.
        from prpl.apis.hl.com import Instance as HLAPIInstance

        api_instance = HLAPIInstance('WUI:Admin', 'Web-GUI administrator account.')

        api_object.instances.append(api_instance)

    """

    def __init__(self, layer, name, resource):
        """Creates a new HL-API object.

        Args:
            layer (int): Layer of the object, used for sorting purposes.
                Typically, '1' (User), '2' (Services), '3' (Interfaces) and '4' (System).
            name (str): Name of the object.
            resource (str): Resource which the object represents (Human-friendly name).

        """

        self.layer = layer
        self.name = name
        self.resource = resource
        self.procedures = []
        self.events = []
        self.instances = []

    def __str__(self):
        """Converts object to human-readable string.

        Returns:
            str: Human-readable representation of HL-API object.

        """

        return self.name
