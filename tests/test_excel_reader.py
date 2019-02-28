
import unittest2

from prpl.apis.hl.spec.parser import ExcelReader as HLAPIParser


class TestExcelReader(unittest2.TestCase):
    """Tests the 'prpl.apis.hl.spec.parser.ExcelReader' component."""

    def setUp(self):
        """Test environment setup."""

        self.parser = HLAPIParser('tests/test-api.xlsx')

    def tearDown(self):
        """Test environment teardown."""

        pass

    def test_get_change_log(self):
        """Tests the 'ExcelReader.get_change_log' method ability to fetch and parse all entries."""

        # Parse change-log.
        change_log = self.parser.get_change_log()

        # Validate number of parsed versions.
        self.assertEqual(len(change_log), 2)

        # Validate version number.
        self.assertEqual(change_log[0]['Number'], '3.5.2')

        # Validate version date.
        self.assertEqual(change_log[1]['Date'], '2018-04-17')

        # Validate number of changes.
        self.assertEqual(len(change_log[0]['Changes']), 3)
        self.assertEqual(len(change_log[1]['Changes']), 2)

        # Validate change contents.
        self.assertEqual(change_log[0]['Changes'][0][0], 1)
        self.assertEqual(change_log[0]['Changes'][0][1], 'Updated ToC with MobileApp User.Roles instance Ids.')

        self.assertEqual(change_log[1]['Changes'][1][0], 2)
        self.assertEqual(change_log[1]['Changes'][1][1],
                         'The "System.Firmware.Images" object has been updated to support "Add"ing a new Firmware '
                         'from the Filesystem.\n'
                         '- Possible values for the "Source.Protocol" field have been updated to "HTTP", "HTTPS", '
                         '"FTP", "FS" (look internaly on the File System).\n'
                         '- Field "Source.Port" is now optional with the following default values: 80 (HTTP), '
                         '443 (HTTPS), 21 (FTP) and Not Applicable (FS).')

    def test_get_procedure(self):
        """Tests the 'ExcelReader.get_procedure' method ability to fetch and parse all entries."""

        # Parse procedures.
        procedures = self.parser.get_procedures()

        # Validate number of procedures.
        self.assertEqual(len(procedures), 9)

        # Validate layer column and 1st row.
        self.assertEqual(procedures[0]['Layer'], 1)

        # Validate object column and 2nd row.
        self.assertEqual(procedures[1]['Object'], 'User.Accounts')

        # Validate procedure column and 3rd row.
        self.assertEqual(procedures[2]['Method'], 'Delete')

        # Validate arguments column and 4th row.
        self.assertEqual(procedures[3]['Request Body (Sample)'], '-')

        # Validate sample column and 5th row.
        self.assertEqual(procedures[4]['Response Body (Sample)'],
                         '{\n'
                         '  "Header": {\n'
                         '    "Name": "OK"\n'
                         '  }\n'
                         '}')

        # Validate description column and last row.
        self.assertEqual(procedures[8]['Description'],
                         'Modifies the status and configuration parameters of the specified Button.')

    def test_get_fields(self):
        """Tests the 'ExcelReader.get_fields' method ability to fetch and parse all entries."""

        fields = self.parser.get_fields()

        # Validate number of fields.
        self.assertEqual(len(fields), 56)

        # Validate layer column and 1st row.
        self.assertEqual(fields[0]['Layer'], 1)

        # Validate object column and 2nd row.
        self.assertEqual(fields[1]['Object'], 'User.Accounts')

        # Validate procedure column and 3rd row.
        self.assertEqual(fields[2]['Method'], 'Add')

        # Validate field column and 4th row.
        self.assertEqual(fields[3]['Parameter'], 'Hash.Salt')

        # Validate description column and 5th row.
        self.assertEqual(fields[4]['Description'], 'User Account password hash type.')

        # Validate type column and 6th row.
        self.assertEqual(fields[5]['Type'], 'String')

        # Validate rights column and 7th row.
        self.assertEqual(fields[6]['Rights'], 'W')

        # Validate required column and 8th row.
        self.assertEqual(fields[7]['Required'], 'Optional')

        # Validate default value column and 9th row.
        self.assertEqual(fields[8]['Default Value'], '-')

        # Validate possible values column and 10th row.
        self.assertEqual(fields[9]['Possible Values'], 'valid "User.Accounts.Roles.{RoleId}" object')

        # Validate format column and 11th row.
        self.assertEqual(fields[10]['Format'], '-')

        # Validate notes column and last row.
        self.assertEqual(fields[-1]['Notes'],
                         'Default Value is "the existing configuration". Possible values are any string with '
                         'length from 1 up to 64 chars. ')

    def test_get_response_codes(self):
        """Tests the 'ExcelReader.get_response_codes' method ability to fetch and parse all entries."""

        # Parse response codes.
        response_codes = self.parser.get_response_codes()

        # Validate number of response codes.
        self.assertEqual(len(response_codes), 12)

        # Validate code column and 1st row.
        self.assertEqual(response_codes[0]['Name'], 'OK')

        # Validate name column and 2nd row.
        self.assertEqual(response_codes[1]['Name'], 'OBJECT_NOT_FOUND')

        # Validate sample column and 3rd row.
        self.assertEqual(response_codes[2]['Sample'],
                         '{\n'
                         '  "Header": {\n'
                         '    "Name": "METHOD_NOT_FOUND",\n'
                         '    "Description": "Unable to process the request because \'Set\' is not a valid method"\n'
                         '  }\n'
                         '}')

        # Validate description column and last row.
        self.assertEqual(response_codes[9]['Description'],
                         'A well-formed request was performed however, the client did not meet the security '
                         'conditions required to access the protected resource, therefore it is not possible '
                         'to process the request.')

    def test_get_events(self):
        """Tests the 'ExcelReader.get_events' method ability to fetch and parse all entries."""

        # Parse events.
        events = self.parser.get_events()

        # Validate number of events.
        self.assertEqual(len(events), 5)

        # Validate layer column and 1st row.
        self.assertEqual(events[0]['Layer'], 1)

        # Validate object column and 2nd row.
        self.assertEqual(events[1]['Object'], 'User.Accounts')

        # Validate code column and 3rd row.
        self.assertEqual(events[2]['Code'], 3)

        # Validate code column and 3rd row.
        self.assertEqual(events[3]['Name'], 'SYSTEM_BUTTONS_CLICKED')

        # Validate description column and 4th row.
        self.assertEqual(events[3]['Description'], 'Raised when a Button is clicked.')

        # Validate sample column and last row.
        self.assertEqual(events[4]['Sample'],
                         '{\n'
                         '  "Header": {\n'
                         '    "Code": 2,\n'
                         '    "Name": "SYSTEM_BUTTONS_PRESSED"\n'
                         '  },\n'
                         '  "Body": {\n'
                         '    "ButtonId": "System.Buttons.0"\n'
                         '  }\n'
                         '}')

    def test_get_instances(self):
        """Tests the 'ExcelReader.get_instances' method ability to fetch and parse all entries."""

        # Parse instances.
        instances = self.parser.get_instances()

        # Validate number of instances.
        self.assertEqual(len(instances), 2)

        # Validate layer column and 1st row.
        self.assertEqual(instances[0]['Layer'], 4)

        # Validate object column and last row.
        self.assertEqual(instances[1]['Object'], 'System.Buttons.{ButtonId}')

        # Validate instance column and 1st row.
        self.assertEqual(instances[0]['Instance'], 'Wi-Fi')

        # Validate description column and last row.
        self.assertEqual(instances[1]['Description'], 'Physical WPS button.')

if __name__ == '__main__':
    unittest2.main()
