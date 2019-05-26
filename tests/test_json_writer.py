import unittest2
import os
import json
from re import sub, compile

from prpl.apis.hl.spec.builder import JSONSchemaWriter as HLAPISpecWriter
from prpl.apis.hl.com import API as HLAPI
from prpl.apis.hl.com import ResponseCode as HLAPIResponseCode
from prpl.apis.hl.com import Version as HLAPIVersion
from prpl.apis.hl.com import Object as HLAPIObject
from prpl.apis.hl.com import Procedure as HLAPIProcedure
from prpl.apis.hl.com import Event as HLAPIEvent

import logging

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s'))
log = logging.getLogger(__name__)
log.addHandler(stream_handler)
log.setLevel(logging.INFO)


class TestJSONSchemaWriter(unittest2.TestCase):
    """Tests the 'prpl.apis.hl.spec.builder.JSONSchemaWriter' component."""

    def setUp(self):
        """Test environment setup."""

        # Setup a HL-API Version.
        self.api_version = HLAPIVersion('3.5', '2018-04-13')
        self.api_version.change_list.append((1, 'Added new "foo" object.'))

        # Setup a HL-API Response Code.
        self.api_response_code = HLAPIResponseCode(
            'OK',
            'A well-formed call was performed and successfully processed.',
            '{"Header":{"Code":0,"Name":"OK"},"Body":{"Id":0,"Name":"Guest"}}',
            '')

        # Setup a HL-API Object.
        self.api_object = HLAPIObject(1, 'User.Accounts.{AccountId}', 'User Account')

        # Setup a HL-API Procedure.
        self.api_procedure = HLAPIProcedure(
            'Set',
            'Modifies the account.',
            '{"Name":"Admin"}',
            '{"Header":{"Code":0,"Name":"OK"}}')

        self.api_object.procedures.append(self.api_procedure)

        # Setup a HL-API Event.
        self.api_event = HLAPIEvent(
            '0',
            'USER_ACCOUNTS_ADDED',
            'Raised when a new account is added.',
            '{"Header":{"Code":1,"Name":"USER_ACCOUNTS_ADDED"},"Body":{"AccountId":"User.Accounts.2"}}')

        self.api_object.events.append(self.api_event)

        # Create list of objects.
        self.api_objects = [self.api_object]

        # Create list of response codes.
        self.api_response_codes = [self.api_response_code]

        # Create list of version.
        self.api_versions = [self.api_version]

        # Setup an API.
        self.api = HLAPI(self.api_objects, self.api_response_codes, self.api_versions)

        # Setup the JSONWriter.
        self.test_folder = 'tests/test-json/'
        self.spec_writer = HLAPISpecWriter(self.api, self.test_folder)
        self.spec_writer.build()

        # load api json
        f = open("{}/{}".format(self.test_folder, "api.json"), "r")
        try:
<<<<<<< HEAD
          self.api_json = json.loads(f.read())
        except:
          pass
=======
            self.api_json = json.loads(f.read())
        except:
            pass
>>>>>>> 27d437c0b1338327cf8a0d023c524938b0d4485d
        f.close()

        # load User.Accounts.json
        f = open("{}/{}".format(self.test_folder, "User.Accounts.json"), "r")
        try:
          self.user_accounts_json = json.loads(f.read())
        except:
          pass
        f.close()

    def tearDown(self):
        """Test environment teardown."""

        # os.remove(self.test_folder)
        # os.remove(self.api_json)
        pass

    def test__get_api_file(self):
        """Test if we can actually parse the api.json file"""

        self.assertIsNotNone(self.api_json)

    def test__check_version(self):
        """Tests if the JSONSchemaWrite got the right API version."""

        # check we have exaclty one version
        self.assertEqual(len(self.api_json["versions"]), 1)

        # check that one version is 3.5
        self.assertIn(self.api_version.number, self.api_json["versions"])
        
        # check we have date field
        self.assertIn("date", self.api_json["versions"][self.api_version.number])

        # check the date is correct
        self.assertEqual(self.api_json["versions"][self.api_version.number]["date"], self.api_version.date)

        # check we have changes list
        self.assertIn("changes", self.api_json["versions"][self.api_version.number])

        # check we have exactly one change in changes
        self.assertEqual(len(self.api_json["versions"][self.api_version.number]["changes"]), 1)

        # check the change version number is 1
        self.assertEqual(self.api_json["versions"][self.api_version.number]["changes"][0][0],
                         self.api_version.change_list[0][0])

        # check the change message is correct
        self.assertEqual(self.api_json["versions"][self.api_version.number]["changes"][0][1],
                         self.api_version.change_list[0][1])

    def test__check_paths(self):
        """Tests if the JSONSchemaWrite set the right paths."""

        name = sub('\.\{[^.]*\}$', '', self.api_object.name)

        # check we have exaclty one path
        self.assertEqual(len(self.api_json["paths"]), 1)

        # check that one version is 3.5
        self.assertIn(name, self.api_json["paths"])
        
        # check we have date field
        self.assertIn("$ref", self.api_json["paths"][name])

        # check the date is correct
        self.assertEqual(self.api_json["paths"][name]["$ref"], '{}.json#/paths'.format(name))
        
    def test__check_components(self):
        """Tests if the JSONSchemaWrite set the right schema."""
        
        #   get object's name
        name = sub('\.\{[^.]*\}$','', self.api_object.name)
        
        # check we have exaclty one path
        self.assertEqual(len(self.api_json["components"]["schemas"]), 3)

        # check that one version is 3.5
        self.assertIn(name, self.api_json["components"]["schemas"])
        
        # check we have date field
        self.assertIn("$ref", self.api_json["components"]["schemas"][name])

        # check the date is correct
        self.assertEqual(self.api_json["components"]["schemas"][name]["$ref"],
                         '{}.json#/components/schemas/{}'.format(name, name))

    def test__get_user_accounts_file(self):
        """Test if we can actually parse the api.json file"""

        self.assertIsNotNone(self.user_accounts_json)

    def test__check_user_paths(self):
        """Tests if the JSONSchemaWrite set the right paths in the User.Accounts file."""

        # check we have the right number of paths
        self.assertEqual(len(self.user_accounts_json["paths"]), len(self.api_object.procedures))

        for p in self.api_object.procedures:

            method_name = "{}.{}".format(self.api_object.name, p.name)

            # check that one version is 3.5
            self.assertIn(method_name, self.user_accounts_json["paths"])

            # check we have the operationId field
            self.assertIn("operationId", self.user_accounts_json["paths"][method_name])

            # check the operationId is correct
            self.assertEqual(self.user_accounts_json["paths"][method_name]["operationId"], method_name)

            # check we have the summary field
            self.assertIn("summary", self.user_accounts_json["paths"][method_name])

            # check the summary is correct
            self.assertEqual(self.user_accounts_json["paths"][method_name]["summary"], p.description)

            # check we have exactly one tag
            self.assertEqual(len(self.user_accounts_json["paths"][method_name]["tags"]), 1)

            # check the tag is correct
            self.assertEqual(self.user_accounts_json["paths"][method_name]["tags"][0], self.api_object.name)

            # check we have the right number of response codes
            self.assertEqual(
                len(self.user_accounts_json["paths"][method_name]["responses"]),
                len(self.api.response_codes)
            )

            # check that we have the right values for each response code
            for r in self.api.response_codes:
                # check we have the response code
                self.assertIn(r.name, self.user_accounts_json["paths"][method_name]["responses"])

                # check we have the right value in the description field
                self.assertEqual(self.user_accounts_json["paths"][method_name]["responses"][r.name]["description"],
                                 r.description)

                # check we have the right value in the example field
                self.assertEqual(
                    json.loads(self.user_accounts_json["paths"][method_name]["responses"][r.name]["content"][
                                   "application/json"]["example"]),
                    json.loads(p.sample_response)
                )

                # check we have the right value in the raised_by field
                self.assertEqual(self.user_accounts_json["paths"][method_name]["responses"][r.name]["raised_by"],
                                 r.raised_by)

                # check we have the right number of schema properties
                self.assertEqual(
                    len(self.user_accounts_json["paths"][method_name]["responses"][r.name]["content"][
                            "application/json"]["schema"]["allOf"][1]["properties"]["Body"]["properties"]),
                    len(p.fields)
                )

                # TODO: iterate through fields and check we have all data

            #### check request body
            # check we have the right number of schema properties
            self.assertEqual(
                len(self.user_accounts_json["paths"][method_name]["requestBody"]["content"]["application/json"][
                        "schema"]["properties"]),
                len(p.fields)
            )

            # TODO: iterate over requestBody properties

            # check response example
            self.assertEqual(json.loads(
                self.user_accounts_json["paths"][method_name]["requestBody"]["content"]["application/json"]["example"]),
                             json.loads(p.sample_request))

            ##### check parameters
            params_re = compile('\{(.*?)\}')
            params_matches = params_re.findall(self.api_object.name)

            for p in params_matches:
                # check if we can find it in the path parameters
                all_param_names = [x["name"] for x in self.user_accounts_json["paths"][method_name]["parameters"]]
                self.assertIn(p, all_param_names)

    def test__check_user_components(self):
        """Tests if the JSONSchemaWrite set the right paths in the User.Accounts file."""

        # get object's name
        name = sub('\.\{[^.]*\}$', '', self.api_object.name)

        # check if we have a component with the object's name
        self.assertIn(name, self.user_accounts_json["components"]["schemas"])

        # check if the description is correct
        self.assertEqual("{} Object".format(name),
                         self.user_accounts_json["components"]["schemas"][name]["description"])

        # check if the id is correct
        self.assertEqual("{}".format(name), self.user_accounts_json["components"]["schemas"][name]["id"])

        # check if the layer is correct
        self.assertEqual(self.api_object.layer, self.user_accounts_json["components"]["schemas"][name]["layer"])

        # TODO: check fields

        # check if we have the right number of events
        self.assertEqual(
          len(self.user_accounts_json["components"]["schemas"][name]["events"]), 
          len(self.api_object.events)
        )

        # iterate through events
        for e in self.api_object.events:
          # check if the event is present
          self.assertIn(e.name, self.user_accounts_json["components"]["schemas"][name]["events"].keys())
          
          # check if the example is correct
          self.assertEqual(json.loads(e.sample), json.loads(self.user_accounts_json["components"]["schemas"][name]["events"][e.name]["content"]["application/json"]["example"]))
          
          # check if the description is correct
          self.assertEqual(e.description, self.user_accounts_json["components"]["schemas"][name]["events"][e.name]["description"]) 
          
          # check if the code is correct
          self.assertEqual(e.code, self.user_accounts_json["components"]["schemas"][name]["events"][e.name]["code"])

    def test__build(self):
        """Tests the 'JSONSchemaWriter.build' method ability to generate the right json files in a folder structure."""

        # check that we have the output folder
        os.path.isdir(self.test_folder)

        # check we have exactly two output files
        file_count = len(
            [name for name in os.listdir(self.test_folder) if os.path.isfile(os.path.join(self.test_folder, name))])
        self.assertEqual(file_count, 2)

        # check we have the api.json file
        os.path.isfile("{}/{}".format(self.test_folder, "api.json"))

        # check we have the User.Accounts.json file
        os.path.isfile("{}/{}".format(self.test_folder, "User.Accounts.json"))

if __name__ == '__main__':
    unittest2.main()
