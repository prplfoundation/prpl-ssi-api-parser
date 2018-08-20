
import logging
import os
import shutil
import re
from collections import OrderedDict
import json
import copy

PATH_PARAMETER_TEMPLATE = {
      "in": "path",
      "name": "",
      "type": "integer",
      "required": True,
      "description": ""
    }

class JSONSchemaWriter:
    """JSONSchema specification writer for prpl HL-API.

    """

    def __init__(self, api, folder):
        """Initializes the specification writer.

        Args:
            api (prpl.apis.hl.com.api): API to be parsed.
            folder (str): Target folder to place the specification files.

        """

        self.api = api
        self.folder = folder

        # Init logger.
        self.logger = logging.getLogger('JSONSchemaWriter')

        # Load template styles.
        
        # Remove old folder.
        self.logger.debug('File - Removing previous files "{}".'.format(self.folder))
        # try:
        shutil.rmtree(self.folder)
        # except Exception as e:
            # self.logger.debug("ran into an exception removing old files")

        self.logger.debug('File - Finished removing files "{}".'.format(self.folder))

        # create new folder
        os.mkdir(self.folder)

    def makeResponseCodesFromAPI(self):
      res = {}

      for r in self.api.response_codes:

        try:
          r_sample = json.dumps(json.loads(r.sample))
        except:
          r_sample = ""

        res[r.name] = {
          "sample": r_sample,
          "description": r.description,
          "code": r.code
        }

      return res

    def makeEventsFromObject(self, object):
      res = {}

      for ev in object.events:
        res[ev.name] = {
          "sample": json.dumps(json.loads(ev.sample)),
          "description": ev.description,
          "code": ev.code
        }

      return res

    def getInitialProperty(self, f):
      
      res = {
        "type": f.type,
        "description": f.description,
        "format": f.format,
        "default_value": f.default_value,
        "possible_values": f.possible_values
      }

      if "," in f.possible_values or "or" in f.possible_values:

        possible_values_regex = re.compile("^(.*?)(?:,|\sor\s)(\S+)$")
        params = possible_values_regex.match(f.possible_values.replace('"',''))
        # values = possible_values_regex.findall(f.possible_values.replace('"',''))
        if params:
          if len(params.groups()) > 0:
            res["enum"] = list(params.groups())

      ## initial writable settings
      if f.is_input and not f.is_output:
        res["writeOnly"] = True
      elif f.is_output and not f.is_input:
        res["readOnly"] = True

      return res

    def getNestedProperty(self, f, res):
      mainObject = f.name.split(".")[0]
      newProperty = f.name.split(".")[1]

      if mainObject not in res["properties"]:
        res["properties"][mainObject] = {
          "type": "object",
          "properties": {},
          "required": []
        }

      newF = f
      newF.name = newProperty

      self.getSimpleProperty(f, res["properties"][mainObject])


    def getSimpleProperty(self, f, res):
      ## check if we have a simple property
      if not(f.name in res["properties"].keys()):
        ## initial writable settings
        res["properties"][f.name] = self.getInitialProperty(f)
      else:
        ## update readable settings
        if "writeOnly" in res["properties"][f.name] and f.is_output:
          del res["properties"][f.name]["writeOnly"]
        elif "readOnly" in res["properties"][f.name] and f.is_input:
          del res["properties"][f.name]["readOnly"]
      
      if f.is_required and f.name not in res["required"]:
        res["required"].append(f.name)


    def makePropertiesFromObject(self, object, properties):
      res = {"required":[], "properties":properties}

      # print(res["properties"])

      for p in object.procedures:

        if p.name != "List":

          for f in p.fields:

            if f.name.count(".") > 0:
              self.getNestedProperty(f, res)
            else:
              self.getSimpleProperty(f, res)

      return res
    
    def makeLinksFromObject(self, object):
      res = {}
      # object.fields = []

      for pr in object.procedures:
        
        try:
          s_response = json.dumps(json.loads(pr.sample_response))
        except:
          s_response = ""

        try:
          s_request = json.dumps(json.loads(pr.sample_request))
        except:
          s_request = ""

        obj = {
          "title": pr.name + " " + object.name,
          "rel": "instances",
          "href": object.name,
          "description": pr.description,
          "sample": s_response,
          "request": s_request,
          "schema": {},
          "targetSchema": {
            "type": "object",
            "properties": {
              "List": {
                "type": "array",
                "items": {"rel": "self"}
              }
            }
          }
        }

        if pr.name == "List":
          obj["schema"] = {
            "type": "object",
            "properties": {
              "offset": {
                "type": "integer",
                "description": "Which object index to start with",
                "example": 45,
                "default": 0
              },
              "limit": {
                "type": "integer",
                "description": "How many objects to return",
                "min": 1,
                "max": 200,
                "default": 20
              }
            }
          }

        ## check if we are a sub object path
        #self.logger.debug(object.name)
        if "{" in object.name:
          obj["parameters"] = []
          #self.logger.debug("found a sub object {}".format(object.name))
          params_re = re.compile('\{(.*?)\}')
          params_matches = params_re.findall(object.name)

          for p in params_matches:
            new_param = copy.deepcopy(PATH_PARAMETER_TEMPLATE)
            new_param["name"] = p
            new_param["description"] = "ID of a(n) {}".format(p.replace("Id", ""))
            obj["parameters"].append(new_param)

          #self.logger.debug(params)


        # for f in pr.fields:
        #   object.fields.append(f)

        res[pr.name] = obj

      return res

    def makeBaseObject(self, name, object):
      desc = name + " Object"
      res = {
        "links": {}, 
        "title": name, 
        "description": desc, 
        "$schema": "http://json-schema.org/draft-04/schema#",
        "id": name,
        "type": "object",
        "required": [],
        "properties": {},
        "X-events": {},
        "X-response_codes": {}
      }
      return res 
    
    def makeObjects(self):
      objects = {}

      for idx, obj in enumerate(self.api.objects):
        ## get the name of the root object instead of the path
        name = re.sub('\.\{[^.]*\}$','', obj.name)

        ## create the base object if it doesn't exist yet
        if not name in objects.keys():
          objects[name] = self.makeBaseObject(name, obj)

        objects[name]["links"] = {**objects[name]["links"], **self.makeLinksFromObject(obj)}

        ## extract properties and required properties while merging with existing properties
        properties_and_required = self.makePropertiesFromObject(obj, objects[name]["properties"])

        ## store properties
        objects[name]["properties"] = properties_and_required["properties"]
        
        ## merge with already required properties
        objects[name]["required"] = objects[name]["required"] + properties_and_required["required"]

        objects[name]["X-events"] = {**objects[name]["X-events"], **self.makeEventsFromObject(obj)}

        objects[name]["X-response_codes"] = {**objects[name]["X-response_codes"], **self.makeResponseCodesFromAPI()}

      return objects

    def makeObjectFiles(self):
      objects = self.makeObjects()

      for o in objects:
        # print(o)
        # print(objects[o])
        filepath = "{}{}.json".format(self.folder, objects[o]["title"])

        f = open(filepath, "w")
        f.write(json.dumps(objects, indent=2))
        f.close()


    def build(self):
        """Generates json schema files specification for the HL-API.

        {
          
        }


        """

        ## create objects
        ## 'events', 'instances', 'layer', 'name', 'procedures', 'resource'
        # Iterate through each object.
        
        self.makeObjectFiles()
