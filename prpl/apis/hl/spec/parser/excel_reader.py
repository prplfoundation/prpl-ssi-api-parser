
from openpyxl import load_workbook
import os
import logging


class ExcelReader:
    """Excel Parser for prpl HL-API.

    It reads every sheet, namely 'Change-Log', 'Objects', 'Fields', 'Events', 'Response Codes' and 'ToC',
    ands returns its contents as a list of dictionaries, which can then be converted to Python objects
    with the aid of 'prpl.apis.hl.factory.ObjectFactory'.

    Example:
        # Import module.
        from prpl.apis.hl.spec.parser import ExcelReader as HLAPIParser

        # Loads parser with the specification.
        parser = HLAPIParser('specs/hl-api.xlsx')

        # Parse change-log.
        change_log = parser.get_change_log()

        # Parse objects and procedures.
        procedures = parser.get_procedures()

        # Parse fields.
        fields = parser.get_fields()

        # Parse return codes.
        response_codes = parser.get_response_codes()

        # Parse events.
        events = parser.get_events()

    """

    def __init__(self, spec):
        """Initializes the ExcelReader parser.

        Args:
            spec (str): Relative path to Excel specification file.

        """

        self.spec_path = '{}/{}'.format(os.getcwd(), spec)

        self.logger = logging.getLogger('ExcelReader')

    def _parse_sheet(self, name):
        """Parses de specified Excel sheet and returns its contents as a list of dictionaries.

        Args:
            name (str): Name of the Excel sheet to be parsed.

        Returns:
            list<dict>: Array of dictionaries with cell contents. The keys are the header names.

        """

        # Open work book.
        work_book = load_workbook(self.spec_path, data_only=True, read_only=True)

        # Init return array.
        entries = []

        # Open specified sheet.
        sheet = work_book[name]

        # Start reading at A2.
        cell = ['A', '1']

        # Read headers.
        headers = []

        # Iterate trough each column.
        while True:
            h = sheet[''.join(cell)].value

            # Stop reading once and empty cell is found.
            if h is None:
                break

            headers.append(h)

            # Jump to next column.
            cell[0] = chr(ord(cell[0]) + 1)

        # Read body.
        cell = ['A', '2']

        # Loop through each row.
        while True:
            entry = []

            # Loop through each column.
            for h in headers:
                value = sheet[''.join(cell)].value

                # Empty cell found, stop parsing.
                if value is None:
                    break

                entry.append(value)

                # Jump to next column.
                cell[0] = chr(ord(cell[0]) + 1)
            else:
                # Append procedure as dictionary.
                p = dict(zip(headers, entry))
                entries.append(p)
                self.logger.debug('{} - Parsed entry {}.'.format(name, p))

                # Continue to next line/entry.
                cell = ['A', str(int(cell[1]) + 1)]
                continue

            # Empty cell was found, assume end of specification.
            break

        # Close workbook.
        work_book.close()

        # Return found procedures.
        return entries

    def get_change_log(self):
        """Parses the 'Change-Log' Excel sheet and returns a list of HL-API versions and changes.

        Returns:
            list<dict>: Array of identified change-log versions.

        """

        # Open work book.
        work_book = load_workbook(self.spec_path, data_only=True, read_only=True)

        # Init return array.
        change_log = []

        # Open sheet.
        sheet = work_book['Change-Log']

        # Start reading at B2.
        cell = ['B', '2']

        # Iterate trough each row until two empty lines are found.
        while True:
            # Read Version Header.
            header = sheet[''.join(cell)].value

            # Quit if no more versions are available.
            if header is None:
                break

            # Parse header.
            tokens = header.split(' ')
            api_version = {'Number': tokens[1], 'Date': tokens[2][1:-1], 'Changes': []}

            # Read Version Body (Change-List).
            cell[1] = str(int(cell[1]) + 1)
            while True:
                # Parse change number.
                change_number = sheet[''.join(cell)].value

                # Quit if no more changes are available.
                if change_number is None:
                    self.logger.debug('ChangeLog - Found version "{}" ({}) with {} changes.'.format(
                        api_version['Number'],
                        api_version['Date'],
                        len(api_version['Changes'])))

                    # Skip the blank line for the next version.
                    cell[1] = str(int(cell[1]) + 1)
                    break

                # Parse change.
                cell[0] = 'C'
                change_description = sheet[''.join(cell)].value
                api_version['Changes'].append((change_number, change_description))

                # Iterate to next cell.
                cell = ['B', str(int(cell[1]) + 1)]

            change_log.append(api_version)
            self.logger.debug('ChangeLog - Parsed entry {}.'.format(api_version))

        # Close work book.
        work_book.close()

        # Return change-log.
        return change_log

    def get_procedures(self):
        """Parses the 'Object' Excel sheet and returns a list of HL-API objects and procedures.

        Returns:
            list<dict>: Array of API objects and procedures.

        """

        return self._parse_sheet('Objects')

    def get_fields(self):
        """Parses the 'Fields' Excel sheet and returns as list of HL-API fields.

        Returns:
            list<dict>: Array of API fields.

        """

        return self._parse_sheet('Fields')

    def get_response_codes(self):
        """Parses the 'Response Codes' Excel sheet and returns as list of HL-API return codes.

         Returns:
             list<dict>: Array of API return codes.

        """

        return self._parse_sheet('Response Codes')

    def get_events(self):
        """Parses the 'Events' Excel sheet and returns a list of HL-API events.

         Returns:
             list<dict>: Array of API events.

        """

        return self._parse_sheet('Events')

    def get_instances(self):
        """Parses the 'ToC' Excel sheet and returns a list of HL-API object instances.

         Returns:
             list<dict>: Array of API instances.

        """

        return self._parse_sheet('ToC')
