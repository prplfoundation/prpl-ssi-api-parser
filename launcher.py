
import logging

from prpl.apis.hl.spec.parser import ExcelReader as HLAPIParser
from prpl.apis.hl.factory import ObjectFactory as HLAPIObjectFactory
from prpl.apis.hl.spec.builder import WordWriter as HLAPIWordWriter
from prpl.apis.hl.spec.builder import JSONSchemaWriter as HLAPIJSONSSchemaWriter

class Launcher:
    """HL-API Parser orchestrator.

    Implements the logic of the parsings the HL-API and converting into a different format.

    """

    def __init__(self, spec):
        """Initializes the parser.

        By default it enables logging to both console and file.

        Args:
            spec (str): File name of the specification file to be parsed.

        """

        self.specification_file = spec
        self.raw_change_log = None
        self.raw_procedures = None
        self.raw_fields = None
        self.raw_response_codes = None
        self.raw_events = None
        self.raw_instances = None
        self.api = None

        # Set logging format and level.
        log_level = logging.DEBUG
        log_format = '[%(asctime)s] (%(name)s) <%(levelname)s>: %(message)s'

        # Setup file logger.
        logging.basicConfig(level=log_level,
                            format=log_format,
                            filename='parser.log',
                            filemode='w')

        # Add console handler with same configuration.
        console = logging.StreamHandler()
        console.setLevel(log_level)

        formatter = logging.Formatter(log_format)
        console.setFormatter(formatter)

        # logging.getLogger().addHandler(console)

    def _parse_excel(self):
        """Parses the Excel HL-API specification file.

        It reads all Excel sheets and converts into list of dictionaries.

        """

        logger = logging.getLogger('ExcelReader')

        # Load specification.
        logger.info('Excel - Parsing started.\n')
        parser = HLAPIParser(self.specification_file)

        # Parse change-log.
        logger.info('ChangeLog - Parsing started.')
        self.raw_change_log = parser.get_change_log()
        logger.info('ChangeLog - Parsing finished with {} versions discovered.\n'.format(len(self.raw_change_log)))

        # Parse objects & methods.
        logger.info('Objects - Parsing started.')
        self.raw_procedures = parser.get_procedures()
        logger.info('Objects - Parsing finished with {} procedures discovered.\n'.format(len(self.raw_procedures)))

        # Parse Parameters.
        logger.info('Parameters - Parsing started.')
        self.raw_parameters = parser.get_parameters()
        logger.info('Parameters - Parsing finished with {} fields discovered.\n'.format(len(self.raw_parameters)))

        # Parse Data Types
        logger.info('Data Types - Parsing started.')
        self.raw_data_types = parser.get_data_types()
        logger.info('Data Types - Parsing finished with {} fields discovered.\n'.format(len(self.raw_data_types)))

        # Parse events.
        logger.info('Events - Parsing started.')
        self.raw_events = parser.get_events()
        logger.info('Events - Parsing finished with {} events.\n'.format(len(self.raw_events)))

        # Parse ToC (instances).
        logger.info('ToC - Parsing started.')
        self.raw_instances = parser.get_instances()
        logger.info('ToC - Parsing finished with {} instances.\n'.format(len(self.raw_instances)))

        # Parse Response Codes.
        logger.info('Response Codes - Parsing started.')
        self.raw_response_codes = parser.get_response_codes()
        logger.info('Response Codes - Parsing finished with {} response codes.\n'.format(len(self.raw_response_codes)))

        logger.info('Excel - Parsing finished.\n')

    def _build_objects(self):
        """Builds HL-API objects.

        It converts and links raw-data read from Excel file into HL-API objects.

        """

        logger = logging.getLogger('ObjectFactory')

        # Build objects.
        logger.info('Building API objects.\n')
        factory = HLAPIObjectFactory(self.raw_procedures,
                                     self.raw_parameters,
                                     self.raw_data_types,
                                     self.raw_events,
                                     self.raw_instances,
                                     self.raw_response_codes,
                                     self.raw_change_log)

        self.api = factory.get_api()
        logger.info('Finished building API {}.\n'.format(self.api))

    def _build_word_report(self):
        """Generates a HL-API Specification document in MS Word format."""

        logger = logging.getLogger('WordWriter')

        # Build objects.
        logger.info('Word - Started building file.\n')
        writer = HLAPIWordWriter(self.api,
                                 'specs/generated/prpl HL-API ({}).docx'.format(self.api.get_version()))
        writer.build()
        logger.info('Word - Finished building file.')

    def _build_json_schema(self):
        """Generates a HL-API Specification as a list of JSON Schema files."""

        logger = logging.getLogger('JSONSchemaWriter')

        # Build objects.
        logger.info('JSON Schema - Started building files. {}\n'.format(self.api.get_version()))
        folder = 'specs/generated/json/v{}/'.format(self.api.get_version())
        writer = HLAPIJSONSSchemaWriter(self.api, folder)
        writer.build()
        logger.info('Word - Finished building file.')

    def run(self):
        """HL-API main function."""

        self._parse_excel()
        print("done parsing")
        self._build_objects()
        print("done building {}".format(self.api.get_version()))

        # self._build_word_report()
        # TODO
        self._build_json_schema()


if __name__ == '__main__':
    l = Launcher('specs/input/04 prpl HL-API (3.8.2.7) [Release Candidate].xlsx')
    l.run()
