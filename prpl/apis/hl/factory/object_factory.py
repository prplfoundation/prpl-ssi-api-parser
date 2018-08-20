
from operator import itemgetter
import logging

from prpl.apis.hl.com import Object as HLAPIObject
from prpl.apis.hl.com import Procedure as HLAPIProcedure
from prpl.apis.hl.com import Field as HLAPIField
from prpl.apis.hl.com import Event as HLAPIEvent
from prpl.apis.hl.com import Instance as HLAPIInstance
from prpl.apis.hl.com import ResponseCode as HLAPIResponseCode
from prpl.apis.hl.com import Version as HLAPIVersion
from prpl.apis.hl.com import API as HLAPI


class ObjectFactory:
    """Generates HL-API Python objects.

    Wraps up raw data dictionaries fetched from the 'prpl.apis.hl.spec.parser.ExcelReader' into HL-API Python objects,
    which can then be used by other components such as the 'WordWriter' or 'JSONSchemaWriter'.

    Example:
        # Use ExcelReader to parse the specification file.
        from prpl.apis.hl.spec.parser import ExcelReader as HLAPIParser

        SPECIFICATION_FILE = "specs/test_api.xlsx"
        parser = HLAPIParser(SPECIFICATION_FILE)

        procedures = parser.get_procedures()
        fields = parser.get_fields()
        events = parser.get_events()
        instances = parser.get_instances()

        # Import Object Factory.
        from prpl.apis.hl.factory import ObjectFactory as HLAPIObjectFactory

        # Link objects.
        factory = HLAPIObjectFactory(procedures, fields, events, instances)
        objects = factory.get_objects()

    """

    def __init__(self, procedures, fields, events, instances, response_codes, change_log):
        """Initializes the HL-API Object factory.

        Args:
            procedures (list<dict>): Array of raw procedures to be parsed and linked.
            fields (list<dict>): Array of raw fields to be parsed and linked.
            events (list<dict>): Array of raw events to be parsed and linked.
            instances (list<dict>): Array of object instances to be parsed and linked.
            response_codes (list<dict>): Array of response codes to be parsed.
            change_log (list<dict>): Array of changes.

        """

        self.procedures = sorted(procedures, key=itemgetter('Layer', 'Object', 'Procedure'))
        self.fields = sorted(fields, key=itemgetter('Layer', 'Object', 'Procedure', 'Field'))
        self.events = sorted(events, key=itemgetter('Layer', 'Object', 'Code'))
        self.instances = sorted(instances, key=itemgetter('Layer', 'Object', 'Instance'))
        self.response_codes = sorted(response_codes, key=itemgetter('Code'))
        self.change_log = change_log
        self.objects = []

        self.logger = logging.getLogger('ObjectFactory')

    def _get_fields(self, object_name, procedure_name):
        """Generates a list of HL-API Fields based on the specified object and procedure names.

        For optimal performance, this method assumes that 'self.fields' is sorted by object name (ascending).
        Once a field which does not match the object and procedure name is found it returns without processing
        all entries.

        Args:
            object_name (str): Lookup object name.
            procedure_name (str): Lookup procedure name.

        Returns:
            list<prpl.apis.hl.com.Field>: List of fields which matched the specified object and procedure names.

        """

        # Init fields array.
        fields = []

        # Iterate though each field.
        while len(self.fields) > 0:
            f = self.fields[0]

            # If current object matches the field object link it.
            if object_name == f['Object'] and procedure_name == f['Procedure']:
                # Split "Rights" field into "input" and "output" booleans.
                rights = f['Rights']

                # Parse input.
                is_input = False
                if 'W' in rights:
                    is_input = True

                # Parse output.
                is_output = False
                if 'R' in rights:
                    is_output = True

                # Convert required field to boolean.
                is_required = None
                if f['Required'] == 'Optional':
                    is_required = False
                elif f['Required'] == 'Required':
                    is_required = True
                elif is_input is True:
                    # Raise event in case and input field is detected without the required flag.
                    raise Exception('Detected input field without required flag descriptor (object="{}",'
                                    'procedure="{}", field="{}".'.format(f['Object'], f['Procedure'], f['Field']))

                # Create new API Field.
                api_field = HLAPIField(
                    f['Field'],
                    f['Description'],
                    f['Type'],
                    is_input,
                    is_required,
                    f['Default Value'],
                    is_output,
                    f['Possible Values'],
                    f['Format'],
                    f['Notes'])

                # Link field to procedure.
                fields.append(api_field)
                self.logger.debug('Fields - Added field "{}" ({}).'.format(api_field.name, api_field.type))

                # Delete the already parsed field from list to speed up the following lookup process.
                del self.fields[0]
            else:
                # Exit loop to continue on to the next object.
                break

        return fields

    def _get_events(self, object_name):
        """Generates a list of HL-API Events based on the specified object names.

        For optimal performance, this method assumes that 'self.events' is sorted by object name (ascending).
        Once an event which does not match the object name is found it returns without processing all entries.

        Args:
            object_name (str): Lookup object name.

        Returns:
            list<prpl.apis.hl.com.Event>: List of events which matched the specified object name.

        """

        # Init events array.
        events = []

        # Iterate through each event.
        while len(self.events) > 0:
            e = self.events[0]

            # If the current object matches the event object, link it.
            if object_name == e['Object']:
                api_event = HLAPIEvent(e['Code'], e['Name'], e['Description'], e['Sample'])
                events.append(api_event)
                self.logger.debug('Events - Added event "{}".'.format(api_event.name))

                # Delete the already parsed event from list to speed up the following lookup process.
                del self.events[0]
            else:
                # Exit loop to continue on to the next object.
                break

        # Returns events.
        return events

    def _get_instances(self, object_name):
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
        while len(self.instances) > 0:
            toc = self.instances[0]

            # If the current object matches the instance object, link it.
            if object_name == toc['Object']:
                api_instance = HLAPIInstance(toc['Instance'], toc['Description'])
                instances.append(api_instance)
                self.logger.debug('Instances - Added instance "{}".'.format(api_instance.name))

                # Delete the already parsed instances from list to speed up the following lookup process.
                del self.instances[0]
            else:
                # Exit loop to continue on to the next object.
                break

        # Return instances.
        return instances

    def _get_objects(self):
        """Generates a list of HL-API Objects.

        Returns:
            list<prpl.apis.hl.com.Object>: List of parsed objects.

        """

        self.objects = []

        # Iterate through each procedure.
        while len(self.procedures) > 0:
            p = self.procedures[0]

            object_name = p['Object']

            # If the object differs from the last parsed, crease a new instance.
            if len(self.objects) == 0 or object_name != self.objects[-1].name:
                    # Create new API Object.
                    api_object = HLAPIObject(p['Layer'], p['Object'], p['Resource'])

                    # Append to list.
                    self.objects.append(api_object)
                    self.logger.debug('Objects - Created object "{}"'.format(object_name))

                    # Parse events and append.
                    api_object.events += self._get_events(object_name)

                    # Parse instances and append.
                    api_object.instances += self._get_instances(object_name)

            # Create new procedure.
            api_procedure = HLAPIProcedure(p['Procedure'], p['Description'], p['Arguments'], p['Sample'])

            # Link it to object.
            api_object.procedures.append(api_procedure)
            self.logger.debug('Procedures - Added procedure "{}".'.format(api_procedure.name))

            # Parse fields and append.
            api_procedure.fields += self._get_fields(object_name, api_procedure.name)

            # Delete the already parsed procedure from list to speed up the following lookup process.
            del self.procedures[0]

        self.logger.debug('Objects - All objects and procedures have been successfully linked.')

        # Validate if all fields have been parsed.
        if len(self.fields) > 0:
            raise Exception('Field "{}" on object "{}" procedure "{}" could not be linked. '
                            'Please review the spec for errors.'.format(self.fields[0]['Field'],
                                                                        self.fields[0]['Object'],
                                                                        self.fields[0]['Procedure']))

        self.logger.debug('Fields - All fields have been successfully linked.')

        # Validate if all events have been parsed.
        if len(self.events) > 0:
            raise Exception('Event "{}" on object "{}" could not be linked. '
                            'Please review the spec for errors.'.format(self.events[0]['Name'],
                                                                        self.events[0]['Object']))

        self.logger.debug('Events - All events have been successfully linked.')

        # Validate if all instances have been parsed.
        if len(self.instances) > 0:
            raise Exception('Instance "{}" on object "{}" could not be linked. '
                            'Please review the spec for errors.'.format(self.instances[0]['Instance'],
                                                                        self.instances[0]['Object']))

        self.logger.debug('Instances - All instances have been successfully linked.')

        # Return list of linked objects.
        return self.objects

    def _get_response_codes(self):
        """Generates a list of HL-API ResponseCodes.

        Returns:
            list<prpl.apis.hl.com.ResponseCode>: List of response codes.

        """

        # Init response codes array.
        codes = []

        # Iterate through each response code.
        while len(self.response_codes) > 0:
            rc = self.response_codes[0]

            # Create new response code object instance and append.
            api_code = HLAPIResponseCode(rc['Code'], rc['Name'], rc['Description'], rc['Sample'])
            codes.append(api_code)
            self.logger.debug('Response Codes - Created response code "{}" ({}).'.format(api_code.code, api_code.name))

            # Delete parsed response code.
            del self.response_codes[0]

        self.logger.debug('Response Codes - All response codes have been successfully linked.')

        # Return list of parsed response codes.
        return codes

    def _get_change_log(self):
        """Generates a list of HL-API Versions.

        Returns:
            list<prpl.apis.hl.com.Version>: List of versions.

        """

        versions_list = []
        while len(self.change_log) > 0:
            version = self.change_log[0]
            v = HLAPIVersion(version['Number'], version['Date'])
            v.change_list = version['Changes']
            versions_list.append(v)
            self.logger.debug('ChangeLog - Added version "{} ({})" with {} changes.'.format(v.number,
                                                                           v.date,
                                                                           len(v.change_list)))
            del self.change_log[0]

        return versions_list

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
