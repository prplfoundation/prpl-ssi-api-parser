
import os
import json
import logging

from prpl.apis.hl.factory import JSONObjectFactory


class JSONReader:
    """JSON Parser for prpl HL-API.

    It reads all objects with help of 'prpl.apis.hl.factory.JSONObjectFactory'.

    Example:
        # Import module.
        from prpl.apis.hl.spec.parser import JSONReader as HLAPIJsonParser

    """

    def _getFileContents(self, path):
        f = open(path, "r")
        res = f.read()
        f.close()
        return res

    def __init__(self, spec):
        """Initializes the ExcelReader parser.

        Args:
            spec (str): Relative path to Excel specification file.

        """

        self.api_json = None
        self.object_schemas = None

        self.spec_path = '{}/{}'.format(os.getcwd(), spec)

        self.logger = logging.getLogger('JSONReader')


    def _build_objects(self):
        """Builds HL-API objects.

        It converts and links raw-data read from JSON folder into HL-API objects.

        """

        logger = logging.getLogger('JSONObjectFactory')

        # Build objects.
        logger.info('Building API objects.\n')
        factory = JSONObjectFactory(self.api_json,
                                     self.object_schemas)

        return factory.get_api()
    
    def _parse_objects(self):
        res = {}

        ## parse all object files referenced in api json
        ## by iterating over paths
        for name in self.api_json["paths"]:
            file_name = "{}/{}".format(self.spec_path, self.api_json["paths"][name]['$ref'].replace("#/paths", ""))
            obj_schema = json.loads(self._getFileContents(file_name))
            res[name] = obj_schema

        return res

    def parse(self):
        """Parses the Excel HL-API specification file.

        It reads all Excel sheets and converts into list of dictionaries.

        """
        logger = logging.getLogger('JSONReader')

        self.api_json = json.loads(self._getFileContents("{}/api.json".format(self.spec_path)))

        self.object_schemas = self._parse_objects()

        logger.info('Excel - Parsing finished.\n')

        return self._build_objects()

