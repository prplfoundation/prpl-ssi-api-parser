
import logging
import re

from prpl.apis.hl.com import Object as HLAPIObject
from prpl.apis.hl.com import Procedure as HLAPIProcedure
from prpl.apis.hl.com import Field as HLAPIField
from prpl.apis.hl.com import Event as HLAPIEvent
from prpl.apis.hl.com import Instance as HLAPIInstance
from prpl.apis.hl.com import ResponseCode as HLAPIResponseCode
from prpl.apis.hl.com import Version as HLAPIVersion
from prpl.apis.hl.com import API as HLAPI


class JSONObjectFactory:
    """Generates HL-API Python objects.

    Wraps up raw data dictionaries fetched from the 'prpl.apis.hl.spec.parser.JSONReader' into HL-API Python objects,
    which can then be used by other components such as the 'WordWriter' or 'JSONSchemaWriter'.

    Example:
        # Use JSONReader to parse the specification folder.
        

    """

    def __init__(self, api_json, object_schemas):
        """Initializes the HL-API Object factory.

        Args:
            procedures (list<dict>): Array of raw procedures to be parsed and linked.
            fields (list<dict>): Array of raw fields to be parsed and linked.
            events (list<dict>): Array of raw events to be parsed and linked.
            instances (list<dict>): Array of object instances to be parsed and linked.
            response_codes (list<dict>): Array of response codes to be parsed.
            change_log (list<dict>): Array of changes.

        """

        self.api_json = api_json
        self.object_schemas = object_schemas

        self.logger = logging.getLogger('JSONObjectFactory')

    def _get_change_log(self):
        # iterate over versions in API file and create HL API Objects

        versions_list = []
        for version, value in self.api_json["versions"].items():
            v = HLAPIVersion(version, self.api_json["versions"][version]['date'])
            v.change_list = self.api_json["versions"][version]['changes']
            versions_list.append(v)
            self.logger.debug('ChangeLog - Added version "{} ({})" with {} changes.'.format(v.number,
                                                                           v.date,
                                                                           len(v.change_list)))

        return versions_list

    def _get_response_codes(self):

        """Generates a list of HL-API ResponseCodes.

        Returns:
            list<prpl.apis.hl.com.ResponseCode>: List of response codes.

        """

        # Init response codes array.
        codes = []

        # extract response codes from first API object
        name = list(self.object_schemas.keys())[0]

        path_name = list(self.object_schemas[name]["paths"].keys())[0]
        responses = self.object_schemas[name]["paths"][path_name]["responses"]

        # Iterate through each response code.
        for response_name, response in responses.items():
            if response_name != "99":

                # Create new response code object instance and append.
                api_code = HLAPIResponseCode(response_name, response['description'], response['content']['application/json']['example'], response['raised_by'])
                codes.append(api_code)
                self.logger.debug('Response Codes - Created response code "{}".'.format(api_code.name))

        self.logger.debug('Response Codes - All response codes have been successfully linked.')

        # Return list of parsed response codes.
        return codes

    def _get_instances(self, instance_entries):
        """Generates a list of HL-API Instances based on the specified object names.

        For optimal performance, this method assumes that 'self.instances' is sorted by object name (ascending).
        Once an event which does not match the object name is found it returns without processing all entries.

        Args:
            object_name (str): Lookup object name.

        Returns:
            list<prpl.apis.hl.com.Instance>: List of instances which matched the specified object name.

        """

        # Init events array.
        instances = []

        # Iterate through each instance.
        for instance_name, values in instance_entries.items():

            api_instance = HLAPIInstance(instance_name, values['description'])
            instances.append(api_instance)
            self.logger.debug('Instances - Added instance "{}".'.format(api_instance.name))


        # Return instances.
        return instances

    def _get_events(self, object_schema, object_name):
        """Generates a list of HL-API Events based on the object's schema.

        For optimal performance, this method assumes that 'self.events' is sorted by object name (ascending).
        Once an event which does not match the object name is found it returns without processing all entries.

        Args:
            object_schmema (dict): dictionary holding the object's json schema.

        Returns:
            list<prpl.apis.hl.com.Event>: List of events which matched the specified object name.

        """

        # Init events array.
        events = []

        # Iterate through each event.
        for code, e in object_schema["events"].items():

            prefix = "{}_".format(object_name.upper().replace(".", "_"))
            name = "{}".format(e['code'].replace(prefix, ""))
            api_event = HLAPIEvent(code, name, e['description'], e["content"]["application/json"]['example'])
            events.append(api_event)
            self.logger.debug('Events - Added event "{}".'.format(api_event.name))


        # Returns events.
        return events

    def _get_field(self, fields, property_name, property_values, is_input, is_output, required_list):

        # check if we are dealing with a nested object
        if property_values["type"] == "object":

            # if so, iterate through sub objects
            for sp_name in list(property_values["properties"].keys()):
                
                # create new name
                combined_name = "{}.{}".format(property_name, sp_name)

                # recursively call this function
                self._get_field(fields, combined_name, property_values["properties"][sp_name], is_input, is_output, property_values["required"])
        else:
            # otherwise, proceed to add new field

            # check if property is required
            if property_name in required_list:
                is_required = True
            else:
                is_required = False

            # create text properties
            description = property_values["description"] if "description" in property_values else ""
            default_value = property_values["default_value"] if "default_value" in property_values else ""
            possible_values = property_values["possible_values"] if "possible_values" in property_values else ""
            field_format = property_values["format"] if "format" in property_values else ""
            notes = ""

            # create notes property
            if default_value != "" and default_value != "-":
                notes = notes + "Default value is \"{}\". ".format(property_values['default_value'])
            if possible_values != "" and possible_values != "-":
                notes = notes + "Possible value are \"{}\". ".format(property_values['possible_values'])
            if field_format != "" and field_format != "-":
                notes = notes + "Format is {}. ".format(property_values['format'])
            if notes == "":
                notes = "-"

            # Create new API Field.
            api_field = HLAPIField(
                property_name,
                description,
                property_values['type'],
                is_input,
                is_required,
                default_value,
                is_output,
                possible_values,
                field_format,
                notes)

            # set new field to object
            fields[property_name] = api_field


    def _get_fields(self, procedure_name, path_schema):
        """Generates a list of HL-API Fields based on the specified object and procedure names.

        For optimal performance, this method assumes that 'self.fields' is sorted by object name (ascending).
        Once a field which does not match the object and procedure name is found it returns without processing
        all entries.

        Args:
            procedure_name (str): procedure name.
            path_schema (str): JSON schema for the procedure.

        Returns:
            list<prpl.apis.hl.com.Field>: List of fields which matched the specified object and procedure names.

        """

        # Init fields dictionary.
        fields = {}

        # check if we have a request body and add fields from schema
        if "requestBody" in path_schema.keys():

            # iterate over each property and add accordingly
            for property_name, property_values in path_schema["requestBody"]["content"]["application/json"]["schema"]["properties"].items():
            
                ## for easier reading this is initialized up here
                is_input = True
                is_output = False

                self._get_field(fields, property_name, property_values, is_input, is_output, path_schema["requestBody"]["content"]["application/json"]["schema"]["required"])
        # check response with code 99 and add fields from schema
        # iterate over each property and add accordingly
        for property_name, property_values in path_schema["responses"]["99"]["content"]["application/json"]["schema"]["properties"].items():

            ## for easier reading this is initialized up here
            is_input = False
            is_output = True

            ## check if we already have an input parameter with the same name
            ## if not, create a completely new field
            if not property_name in fields.keys():
                self._get_field(fields, property_name, property_values, is_input, is_output, path_schema["responses"]["99"]["content"]["application/json"]["schema"]["required"])
            else:
                ## if yes, update existing field 
                ## set field to also be an output field
                fields[property_name].is_output = True

                ## check required, if it is true, set it on the existing property
                if property_name in path_schema["responses"]["99"]["content"]["application/json"]["schema"]["required"]:
                    fields[property_name].is_required = True


        return fields

    def _get_objects(self):
        """Generates a list of HL-API Objects.

        Returns:
            list<prpl.apis.hl.com.Object>: List of parsed objects.

        """

        objects = []

        # Iterate through each procedure.
        for object_name, object_schema in self.object_schemas.items():

            schema = object_schema["components"]["schemas"][object_name]

            procedure = list(object_schema["paths"].keys())[0]
            # Create new API Object.

            resource = re.sub(r'\{.+?\}\s?', "", object_schema["paths"][procedure]["tags"][0].replace("."," "))
            api_object = HLAPIObject(schema["layer"], object_name, resource)

            # Append to list.
            objects.append(api_object)
            self.logger.debug('Objects - Created object "{}"'.format(object_name))

            # Parse events and append.
            api_object.events += self._get_events(schema, object_name)

            # Parse instances and append.
            if "instances" in object_schema.keys():
                api_object.instances += self._get_instances(object_schema["instances"])

            for procedure_name, p in object_schema["paths"].items():

                p_name = procedure_name.split(".")[-1]
                # collect info about procedure
                
                if not "requestBody" in p:
                    request_example = "-"
                else:
                    request_example = p["requestBody"]["content"]["application/json"]["example"]

                if not "responses" in p:
                    response_example = "-"
                else:
                    response_example = p["responses"]["99"]["content"]["application/json"]["example"]

                # Create new procedure.    
                api_procedure = HLAPIProcedure(p_name, p['summary'], request_example, response_example)

                # Link it to object.
                api_object.procedures.append(api_procedure)
                self.logger.debug('Procedures - Added procedure "{}" to "{}".'.format(api_procedure.name, object_name))

                # Parse fields and append.
                api_procedure.fields = self._get_fields(p_name, p)

        return objects

    def get_api(self):
        """Generates a HL-API instance from raw dictionaries.

        Returns:
            prpl.apis.hl.com.API: API object with list of linked objects, release notes and response codes.

        """

        api_versions = self._get_change_log()

        api_response_codes = self._get_response_codes()

        api_objects = self._get_objects()

        api = HLAPI(api_objects, api_response_codes, api_versions)

        return api
