
import unittest2

from prpl.apis.hl.factory import ObjectFactory as HLAPIObjectFactory


class TestObjectFactory(unittest2.TestCase):
    """Tests the 'prpl.apis.hl.factory.ObjectFactory' component."""

    def setUp(self):
        """Test environment setup."""

        pass

    def tearDown(self):
        """Test environment teardown."""

        pass

    def test__get_fields(self):
        """Tests the 'ObjectFactory._get_fields' method ability to return the fields associated with the
        specified object procedure.

        """

        # Setup dummy fields.
        field0 = {
            'Layer': 1,
            'Object': 'User.Accounts',
            'Method': 'Add',
            'Parameter': 'Description',
            'Resource': 'User Account',
            'Description': 'User Account description.',
            'Type': 'String',
            'Rights': 'W',
            'Required': 'Optional',
            'Default Value': 'null',
            'Possible Values': '"null" or any string with length from 1 up to 64 chars',
            'Format': '-',
            'Notes': 'Default Value is "null". Possible values are "null" or any string with length '
                     'from 1 up to 64 chars. '
        }

        field1 = {
            'Layer': 1,
            'Object': 'User.Accounts',
            'Method': 'Add',
            'Parameter': 'Enabled',
            'Resource': 'User Account',
            'Description': 'User Account administrative status.',
            'Type': 'Boolean',
            'Rights': 'W',
            'Required': 'Optional',
            'Default Value': 'true',
            'Possible Values': '"true" or "false"',
            'Format': '-',
            'Notes': 'Default Value is "true". Possible values are "true" or "false". '
        }

        field2 = {
            'Layer': 4,
            'Object': 'System.Buttons',
            'Method': 'List',
            'Parameter': 'Offset',
            'Resource': 'Button',
            'Description': 'Button list start offset.',
            'Type': 'Integer',
            'Rights': 'RW',
            'Required': 'Optional',
            'Default Value': '0',
            'Possible Values': '"0" to fetch all entries or positive integer',
            'Format': '-',
            'Notes': 'Default Value is "0". Possible values are "0" to fetch all entries or positive integer. '
        }

        # Init factory.
        fields_list = [field0, field1, field2]
        factory = HLAPIObjectFactory([], fields_list, [], [], [], [])

        # Parse fields for an invalid object.
        api_fields = factory._get_fields('Invalid.Object', 'Add')

        # Validate that no fields are found.
        self.assertEqual(len(api_fields), 0)

        # Parse fields for an invalid method.
        api_fields = factory._get_fields('System.Accounts', 'Unknown')

        # Validate that no fields are found.
        self.assertEqual(len(api_fields), 0)

        # Parse fields for 'User.Accounts' Add method.
        api_fields = factory._get_fields('User.Accounts', 'Add')

        # Validate that 2 fields are found.
        self.assertEqual(len(api_fields), 2)

        self.assertEqual(api_fields[0].name, 'Description')
        self.assertEqual(api_fields[0].description, 'User Account description.')
        self.assertEqual(api_fields[0].type, 'String')
        self.assertEqual(api_fields[0].is_input, True)
        self.assertEqual(api_fields[0].is_required, False)
        self.assertEqual(api_fields[0].default_value, 'null')
        self.assertEqual(api_fields[0].is_output, False)
        self.assertEqual(api_fields[0].possible_values, '"null" or any string with length from 1 up to 64 chars')
        self.assertEqual(api_fields[0].format, '-')
        self.assertEqual(api_fields[0].notes, 'Default Value is "null". Possible values are "null" or any string '
                                              'with length from 1 up to 64 chars. ')

        self.assertEqual(api_fields[1].name, 'Enabled')

        # Parse fields for 'System.Buttons' List method.
        api_fields = factory._get_fields('System.Buttons', 'List')

        # Validate that 1 field is found.
        self.assertEqual(len(api_fields), 1)

        self.assertEqual(api_fields[0].name, 'Offset')
        self.assertEqual(api_fields[0].is_input, True)
        self.assertEqual(api_fields[0].is_output, True)

        # Validate that all fields have been parsed.
        self.assertEqual(len(factory.fields), 0)

    def test__get_events(self):
        """Tests the 'ObjectFactory._get_events' method ability to return the events associated with for
        the specified object.

        """

        # Setup 'dummy' events.
        event0 = {
            'Layer': 1,
            'Object': 'User.Accounts',
            'Resource': 'User Account',
            'Code': 1,
            'Prefix': 'USER_ACCOUNTS_',
            'Event': 'ADDED',
            'Name': 'USER_ACCOUNTS_ADDED',
            'Parameters': '{\n  "AccountId": "User.Accounts.2"\n}',
            'Sample': '{\n  "Header": {\n    "Code": 1,\n    "Name": "USER_ACCOUNTS_ADDED"\n  },\n  '
                      '"Body": {\n    "AccountId": "User.Accounts.2"\n  }\n}',
            'Description': 'Raised when a new User Account is added.'
        }

        event1 = {
            'Layer': 1,
            'Object': 'User.Accounts', 'Resource': 'User Account',
            'Code': 2,
            'Prefix': 'USER_ACCOUNTS_',
            'Event': 'DELETED',
            'Name': 'USER_ACCOUNTS_DELETED',
            'Parameters': '{\n  "AccountId": "User.Accounts.2"\n}',
            'Sample': '{\n  "Header": {\n    "Code": 2,\n    "Name": "USER_ACCOUNTS_DELETED"\n  },\n  '
                      '"Body": {\n    "AccountId": "User.Accounts.2"\n  }\n}',
            'Description': 'Raised when an existing User Account is deleted.'}

        event2 = {
            'Layer': 4,
            'Object': 'System.Buttons',
            'Resource': 'Button',
            'Code': 1,
            'Prefix': 'SYSTEM_BUTTONS_',
            'Event': 'CLICKED',
            'Name': 'SYSTEM_BUTTONS_CLICKED',
            'Parameters': '{\n  "ButtonId": "System.Buttons.0"\n}',
            'Sample': '{\n  "Header": {\n    "Code": 1,\n    "Name": "SYSTEM_BUTTONS_CLICKED"\n  },\n  '
                      '"Body": {\n    "ButtonId": "System.Buttons.0"\n  }\n}',
            'Description': 'Raised when a Button is clicked.'
        }

        # Init factory.
        events_list = [event0, event1, event2]
        factory = HLAPIObjectFactory([], [], events_list, [], [], [])

        # Parse events for first object.
        api_events = factory._get_events('User.Accounts')

        # Validate first object events.
        self.assertEqual(len(api_events), 2)
        self.assertEqual(api_events[0].code, 1)
        self.assertEqual(api_events[0].name, 'USER_ACCOUNTS_ADDED')
        self.assertEqual(api_events[0].description, 'Raised when a new User Account is added.')
        self.assertEqual(api_events[0].sample,
                         '{\n  "Header": {\n    "Code": 1,\n    "Name": "USER_ACCOUNTS_ADDED"\n  },\n  '
                         '"Body": {\n    "AccountId": "User.Accounts.2"\n  }\n}')

        self.assertEqual(api_events[-1].name, 'USER_ACCOUNTS_DELETED')

        # Parse events for invalid object.
        api_events = factory._get_events('Invalid.Object')

        # Validate no events were returned.
        self.assertEqual(len(api_events), 0)

        # Parse events for last object.
        api_events = factory._get_events('System.Buttons')

        # Validate one event was found.
        self.assertEqual(len(api_events), 1)
        self.assertEqual(api_events[0].name, 'SYSTEM_BUTTONS_CLICKED')

        # Validate all events have been successfully parsed.
        self.assertEqual(len(factory.events), 0)

    def test__get_instances(self):
        """Tests the 'ObjectFactory._get_instances' method ability to return the instances associated with for
        the specified object.

        """

        # Setup dummy instances.
        instance0 = {
            'Layer': 4,
            'Object': 'System.Buttons.{ButtonId}',
            'Instance': 'Wi-Fi',
            'Description': 'Physical Wi-Fi button.'
        }

        instance1 = {
            'Layer': 4,
            'Object': 'System.Buttons.{ButtonId}',
            'Instance': 'WPS',
            'Description': 'Physical WPS button.'
        }

        # Init factory.
        instances_list = [instance0, instance1]
        factory = HLAPIObjectFactory([], [], [], instances_list, [], [])

        # Parse instances for invalid object.
        api_instances = factory._get_instances('Invalid.Object')

        # Validate no instances were found.
        self.assertEqual(len(api_instances), 0)

        # Parse instance for a valid object.
        api_instances = factory._get_instances('System.Buttons.{ButtonId}')

        # Validate found instance for valid object.
        self.assertEqual(len(api_instances), 2)

        self.assertEqual(api_instances[0].name, 'WPS')
        self.assertEqual(api_instances[0].description, 'Physical WPS button.')

        self.assertEqual(api_instances[1].name, 'Wi-Fi')

        # Validate that all instance have been parsed.
        self.assertEqual(len(factory.instances), 0)

    def test__get_objects(self):
        """Tests the 'ObjectFactory._get_objects' method ability to return all objects."""

        # Setup dummy procedures and objects.
        procedure0 = {
            'Layer': 1,
            'Object': 'User.Accounts',
            'Method': 'Add',
            'Request Body (Sample)':
                '{\n  "Id": "Admin",\n  "Enabled": true,\n  "Name": "Administrator",\n  '
                '"Password": "prplFoundation",\n  "Description": "Home-Gateway administrator.",\n  '
                '"RoleId": "User.Roles.Root"\n}',
            'Response Body (Parameters)': '{ \n  "Id": "Admin"\n}',
            'Response Body (Sample)':
                '{\n  "Header": {\n    "Name": "OK"\n  },\n  '
                '"Body": {\n    "Id": "Admin"\n  }\n}',
            'Resource': 'User Account',
            'Description': 'Adds a new User Account.'
        }

        procedure1 = {
            'Layer': 1,
            'Object': 'User.Accounts',
            'Method': 'List',
            'Request Body (Sample)': '{\n  "Limit": 10,\n  "Offset": 0\n}',
            'Response Body (Parameters)':
                '{\n  "List": [\n    {\n      "Id": "Admin",\n      "Enabled": true,\n      '
                '"Name": "Administrator",\n      "Hash": {\n        '
                '"Fingerprint": "21232f297a57a5a743894a0e4a801fc3",\n        "Type": "MD5"\n      },\n      '
                '"Description": "Home-Gateway administrator.",\n      "RoleId": "User.Roles.Root"\n    }\n  ]'
                ',\n  "Limit": 10,\n  "Offset": 0\n}',
            'Response Body (Sample)':
                '{\n  "Header": {\n    "Name": "OK"\n  },\n  "Body": {\n    "List": [\n      '
                '{\n        "Id": "Admin",\n        "Enabled": true,\n        "Name": "Administrator",\n        '
                '"Hash": {\n          "Fingerprint": "21232f297a57a5a743894a0e4a801fc3",\n          '
                '"Type": "MD5"\n        },\n        "Description": "Home-Gateway administrator.",\n        '
                '"RoleId": "User.Roles.Root"\n      }\n    ],\n    "Limit": 10,\n    "Offset": 0\n  }\n}',
            'Resource': 'User Account',
            'Description': 'Retrieves a list of User Accounts.'
        }

        procedure2 = {
            'Layer': 4,
            'Object': 'System.Buttons.{ButtonId}',
            'Method': 'Set',
            'Request Body (Sample)':
                '{\n  "Id": "0",\n  "Name": "Wi-Fi",\n  "Enabled": true,\n  "Actions": {\n    '
                '"Click": {\n      "Object": "Interfaces.Physical.Network.LAN.Wi-Fi.Radios.24GHz",\n      '
                '"Method": "Set",\n      "Arguments": "{\\"Enabled\\":false}"\n    },\n    '
                '"Press": {\n      "Object": "Services.Local.Wi-Fi.WPS.Pairing",\n      '
                '"Method": "Start",\n      "Arguments": "{}"\n    }\n  }\n}',
            'Response Body (Parameters)': '-',
            'Response Body (Sample)': '{\n  "Header": {\n    "Name": "OK"\n  }\n}',
            'Resource': 'Button',
            'Description': 'Modifies the status and configuration parameters of the (specified) Button.'
        }

        # Init factory.
        procedure_list = [procedure0, procedure1, procedure2]
        factory = HLAPIObjectFactory(procedure_list, [], [], [], [], [])
        api_objects = factory._get_objects()

        # Validate 2 objects were found.
        self.assertEqual(len(api_objects), 2)

        # Validate 'User.Accounts' object.
        self.assertEqual(api_objects[0].layer, 1)
        self.assertEqual(api_objects[0].name, 'User.Accounts')
        self.assertEqual(api_objects[0].resource, 'User Account')
        self.assertEqual(len(api_objects[0].procedures), 2)
        self.assertEqual(api_objects[0].procedures[0].name, 'Add')
        self.assertEqual(api_objects[0].procedures[0].description, 'Adds a new User Account.')
        self.assertEqual(api_objects[0].procedures[0].sample_request,
                         '{\n'
                         '  "Id": "Admin",\n'
                         '  "Enabled": true,\n'
                         '  "Name": "Administrator",\n'
                         '  "Password": "prplFoundation",\n'
                         '  "Description": "Home-Gateway administrator.",\n'
                         '  "RoleId": "User.Roles.Root"\n'
                         '}')
        self.assertEqual(api_objects[0].procedures[0].sample_response,
                         '{\n'
                         '  "Header": {\n'
                         '    "Name": "OK"\n'
                         '  },\n'
                         '  "Body": {\n'
                         '    "Id": "Admin"\n'
                         '  }\n'
                         '}')

        self.assertEqual(len(api_objects[0].procedures[0].fields), 0)

        self.assertEqual(api_objects[0].procedures[1].name, 'List')

        self.assertEqual(len(api_objects[0].events), 0)
        self.assertEqual(len(api_objects[0].instances), 0)

        # Validate 'System.Buttons.{ButtonId}' object.
        self.assertEqual(api_objects[1].name, 'System.Buttons.{ButtonId}')
        self.assertEqual(api_objects[1].procedures[0].name, 'Set')

        # Validate all procedures have been parsed.
        self.assertEqual(len(factory.procedures), 0)

    def test__get_response_codes(self):
        """Tests the 'ObjectFactory._get_response_codes' method ability to return all response codes."""

        # Setup dummy codes.
        code0 = {
            'Name': 'OK',
            'Sample': '{\n  "Header": {\n    "Code": 0,\n    "Name": "OK"\n  },\n  '
                      '"Body": {\n    "Id": 0,\n    "Name": "Guest"\n  }\n}',
            'Description': 'A well-formed call was performed to a valid object with valid arguments.'
        }

        code1 = {
            'Name': 'INVALID_ARGUMENT',
            'Sample': '{\n  "Header": {\n    "Code": 1,\n    "Name": "INVALID_ARGUMENT"\n  }\n}',
            'Description': 'A call to an existing object and command was performed, but invalid arguments were '
                           'provided (unknown argument or data type).'
        }

        # Init factory.
        code_list = [code0, code1]
        factory = HLAPIObjectFactory([], [], [], [], code_list, [])

        # Parse response codes.
        api_codes = factory._get_response_codes()

        # Validate codes.
        self.assertEqual(len(api_codes), 2)
        self.assertEqual(api_codes[0].name, 'OK')
        self.assertEqual(api_codes[0].description,
                         'A well-formed call was performed to a valid object with valid arguments.')
        self.assertEqual(api_codes[0].sample, '{\n  "Header": {\n    "Code": 0,\n    "Name": "OK"\n  },\n  '
                                              '"Body": {\n    "Id": 0,\n    "Name": "Guest"\n  }\n}')

        self.assertEqual(api_codes[1].name, 'INVALID_ARGUMENT')

        # Validate all codes have been parsed.
        self.assertEqual(len(factory.response_codes), 0)

    def test__get_change_log(self):
        """Tests the 'ObjectFactory._get_change_log' method ability to return all changes."""

        # Setup dummy versions.
        change0 = {
            'Number': '3.5.2',
            'Date': '2018-04-25',
            'Changes': [
                (1, 'Updated ToC with MobileApp User.Roles instance Ids.'),
                (2, 'Removed extra spaces between each API version on the Change-Log sheet in order to'
                'make it parseable.'),
                (3, 'Included "Layer" column on the "ToC" field for sorting purposes.')
            ]
        }

        change1 = {
            'Number': '3.5.1',
            'Date': '2018-04-17',
            'Changes': [
                (1, 'Some fields flag as "Required" no longer have a "Default Value". '
                    'This is only applicable to optional fields.'),
                (2, 'The "System.Firmware.Images" object has been updated to support "Add"ing a new '
                    'Firmware from the Filesystem.\n- Possible values for the "Source.Protocol" field '
                    'have been updated to "HTTP", "HTTPS", "FTP", "FS" (look internaly on the File System).\n'
                    '- Field "Source.Port" is now optional with the following default values: 80 (HTTP), '
                    '443 (HTTPS), 21 (FTP) and Not Applicable (FS).')]
            }

        # Init factory.
        change_list = [change0, change1]
        factory = HLAPIObjectFactory([], [], [], [], [], change_list)

        # Parse response codes.
        api_versions = factory._get_change_log()

        # Validate number of identified entries.
        self.assertEqual(len(api_versions), 2)

        # Validate first entry.
        self.assertEqual(api_versions[0].number, '3.5.2')
        self.assertEqual(api_versions[0].date, '2018-04-25')
        self.assertEqual(len(api_versions[0].change_list), 3)

        self.assertEqual(api_versions[0].change_list[0][0], 1)
        self.assertEqual(api_versions[0].change_list[0][1], 'Updated ToC with MobileApp User.Roles instance Ids.')

        self.assertEqual(api_versions[0].change_list[-1][0], 3)
        self.assertEqual(api_versions[0].change_list[-1][1],
                         'Included "Layer" column on the "ToC" field for sorting purposes.')

        # Validate last entry.
        self.assertEqual(api_versions[-1].number, '3.5.1')
        self.assertEqual(api_versions[-1].date, '2018-04-17')
        self.assertEqual(len(api_versions[-1].change_list), 2)

        # Validate all entries have been parsed.
        self.assertEqual(len(factory.change_log), 0)

    def test_get_api(self):
        """Tests the 'ObjectFactory.get_api' method."""

        # Setup dummy data.
        changes = [{
            'Number': '3.5.2',
            'Date': '2018-04-25',
            'Changes': [
                (1, 'Updated ToC with MobileApp User.Roles instance Ids.'),
                (2, 'Removed extra spaces between each API version on the Change-Log sheet in order to'
                'make it parseable.'),
                (3, 'Included "Layer" column on the "ToC" field for sorting purposes.')
            ]
        }]

        procedures = [{
            'Layer': 4,
            'Object': 'System.Buttons.{ButtonId}',
            'Method': 'Add',
            'Request Body (Sample)':
                '{\n  "Id": "0",\n  "Name": "Wi-Fi",\n  "Enabled": true,\n  "Actions": {\n    '
                '"Click": {\n      "Object": "Interfaces.Physical.Network.LAN.Wi-Fi.Radios.24GHz",\n      '
                '"Method": "Set",\n      "Arguments": "{\\"Enabled\\":false}"\n    },\n    '
                '"Press": {\n      "Object": "Services.Local.Wi-Fi.WPS.Pairing",\n      '
                '"Method": "Start",\n      "Arguments": "{}"\n    }\n  }\n}',
            'Response Body (Parameters)': '-',
            'Response Body (Sample)': '{\n  "Header": {\n    "Code": 0,\n    "Name": "OK"\n  }\n}',
            'Resource': 'Button',
            'Description': 'Modifies the status and configuration parameters of the (specified) Button.'
        }]

        codes = [{
            'Name': 'OK',
            'Sample': '{\n  "Header": {\n    "Code": 0,\n    "Name": "OK"\n  },\n  '
                      '"Body": {\n    "Id": 0,\n    "Name": "Guest"\n  }\n}',
            'Description': 'A well-formed call was performed to a valid object with valid arguments.'
        }]

        fields = [{
            'Layer': 1,
            'Object': 'System.Buttons.{ButtonId}',
            'Method': 'Add',
            'Parameter': 'Description',
            'Resource': 'System Button',
            'Description': 'System button description.',
            'Type': 'String',
            'Rights': 'W',
            'Required': 'Optional',
            'Default Value': 'null',
            'Possible Values': '"null" or any string with length from 1 up to 64 chars',
            'Format': '-',
            'Notes': 'Default Value is "null". Possible values are "null" or any string with length '
                     'from 1 up to 64 chars. '
        }]

        events = [{
            'Layer': 4,
            'Object': 'System.Buttons.{ButtonId}',
            'Resource': 'Button',
            'Code': 1,
            'Prefix': 'SYSTEM_BUTTONS_',
            'Event': 'CLICKED',
            'Name': 'SYSTEM_BUTTONS_CLICKED',
            'Parameters': '{\n  "ButtonId": "System.Buttons.0"\n}',
            'Sample': '{\n  "Header": {\n    "Code": 1,\n    "Name": "SYSTEM_BUTTONS_CLICKED"\n  },\n  '
                      '"Body": {\n    "ButtonId": "System.Buttons.0"\n  }\n}',
            'Description': 'Raised when a Button is clicked.'
        }]

        instances = [{
            'Layer': 4,
            'Object': 'System.Buttons.{ButtonId}',
            'Instance': 'Wi-Fi',
            'Description': 'Physical Wi-Fi button.'
        }]

        # Init factory.
        factory = HLAPIObjectFactory(procedures, fields, events, instances, codes, changes)
        api = factory.get_api()

        # Validate creation of API.
        self.assertEqual(len(api.versions), 1)
        self.assertEqual(len(api.objects), 1)
        self.assertEqual(len(api.objects[0].procedures), 1)
        self.assertEqual(len(api.objects[0].events), 1)
        self.assertEqual(len(api.objects[0].instances), 1)
        self.assertEqual(len(api.response_codes), 1)

        # Validate everything has been parsed.
        self.assertEqual(len(factory.procedures), 0)
        self.assertEqual(len(factory.fields), 0)
        self.assertEqual(len(factory.events), 0)
        self.assertEqual(len(factory.instances), 0)
        self.assertEqual(len(factory.response_codes), 0)
        self.assertEqual(len(factory.change_log), 0)

if __name__ == '__main__':
    unittest2.main()
