
import logging


# TODO: make dynamic
# readers
from prpl.apis.hl.spec.parser import ExcelReader as HLAPIExcelParser
from prpl.apis.hl.spec.parser import JSONReader as HLAPIJSONParser

# TODO: make dynamic
# writers
from prpl.apis.hl.spec.builder import WordWriter as HLAPIWordWriter
from prpl.apis.hl.spec.builder import ExcelWriter as HLAPIExcelWriter
from prpl.apis.hl.spec.builder import \
    JSONSchemaWriter as HLAPIJSONSSchemaWriter


class Launcher:
    """HL-API Parser orchestrator.

    Implements the logic of the parsings the HL-API and
    converting into a different format.

    """

    def __init__(self, spec, input_format="xls", output_format="json"):
        """Initializes the parser.

        By default it enables logging to both console and file.

        Args:
            spec (str): File name of the specification file to be parsed.

        """

        self.specification_file = spec
        self.api = None
        self.input_format = input_format
        self.output_format = output_format

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

    def _parse_from_excel(self):
        """Fills the api object with input from an Excel HL-API specification file.

        It reads all Excel sheets and converts into list of dictionaries.

        """

        logger = logging.getLogger('ExcelReader')

        # Load specification.
        logger.info('Excel - Parsing started.\n')
        parser = HLAPIExcelParser(self.specification_file)
        self.api = parser.parse()

    def _parse_from_json(self):
        """Fills the api object with input from an Excel HL-API specification file.

        It reads all Excel sheets and converts into list of dictionaries.

        """

        logger = logging.getLogger('JSONReader')

        # Load specification.
        logger.info('JSON - Parsing started.\n')
        parser = HLAPIJSONParser(self.specification_file)
        self.api = parser.parse()

    def _build_word_report(self):
        """Generates a HL-API Specification document in MS Word format."""

        logger = logging.getLogger('WordWriter')

        # Build objects.
        logger.info('Word - Started building file.\n')
        writer = HLAPIWordWriter(
                                self.api,
                                'specs/generated/prpl HL-API ({}).docx'
                                .format(self.api.get_version())
                                )
        writer.build()
        logger.info('Word - Finished building file.')

    def _build_json_schema(self):
        """Generates a HL-API Specification as a list of JSON Schema files."""

        logger = logging.getLogger('JSONSchemaWriter')

        # Build objects.
        logger.info(
            'JSON Schema - Started building files. {}\n'
            .format(self.api.get_version())
        )
        folder = 'specs/generated/json/v{}/'.format(self.api.get_version())
        writer = HLAPIJSONSSchemaWriter(self.api, folder)
        writer.build()
        logger.info('Word - Finished building file.')

    def _build_excel_file(self):
        """Generates a HL-API Specification document in MS Word format."""

        logger = logging.getLogger('ExcelWriter')

        # Build objects.
        logger.info('Excel - Started building file.\n')
        writer = HLAPIExcelWriter(self.api,
                                  'specs/generated/')
        writer.build()
        logger.info('Excel - Finished building file.')

    def run(self):
        """HL-API main function."""

        logger = logging.getLogger('Launcher')

        # perform input type specific parsing
        if self.input_format == "xls":
            self._parse_from_excel()
        elif self.input_format == "json":
            self._parse_from_json()

        if self.api is None:
            raise Exception("Error, no API parsed")

        logger.info('Finished building API {}.\n'.format(self.api))
        print("done parsing")

        if self.output_format == "json":
            self._build_json_schema()
        elif self.output_format == "word":
            self._build_word_report()
        elif self.output_format == "xls":
            self._build_excel_file()


if __name__ == '__main__':
    # l = Launcher(
    #     'specs/input/3.8.2.7RC.xlsx'
    # )
    l = Launcher(
            'specs/generated/json/v3.8.2.7',
            input_format="json",
            output_format="xls"
            )
    l.run()
