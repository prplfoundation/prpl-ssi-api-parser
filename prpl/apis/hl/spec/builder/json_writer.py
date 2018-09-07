
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

INTEGER_PARAMETER_SCHEMA = {
  "type": "integer",
  "format": "int32",
  "default": 20,
  "example": {
    "Limit": 10
  }
}

class JSONSchemaWriter:
    """JSONSchema specification writer for prpl HL-API.

    """

    def __init__(self, api, folder, template='specs/templates/prpl.json', object_template='specs/templates/object.json'):
        """Initializes the specification writer.

        Args:
            api (prpl.apis.hl.com.api): API to be parsed.
            folder (str): Target folder to place the specification files.

        """

        self.api = api
        self.folder = folder
        self.template = template
        
        f = open(object_template, "r")
        self.objectTemplateString = f.read()
        f.close()

        self.jsonResponses = None
        self.objects_and_paths = {}

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


    def loadBlankJSONAPIObjectFromTemplate(self):
        f = open(self.template, "r")
        self.json_api_object = json.loads(f.read())

####################################################################
################################ SCHEMAS
####################################################################

    def makeBaseSchema(self, name, object):
      desc = name + " Object"
      res = {
        "description": desc, 
        "id": name,
        "type": "object",
        "required": [],
        "properties": {},
        "events": {},
        "example": {}
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

    def makePropertiesFromSchema(self, object, properties):
      res = {"required":[], "properties":properties}

      for p in object.procedures:

        if p.name != "List":

          for f in p.fields:

            if f.name.count(".") > 0:
              self.getNestedProperty(f, res)
            else:
              self.getSimpleProperty(f, res)

      return res

    def makeEventsFromSchema(self, obj):
      res = {}

      for ev in obj.events:
        res[ev.code] = {
          "content": {
            "application/json":{
              "example": json.dumps(json.loads(ev.sample)),
            }
          },
          "description": ev.description,
          "code": ev.name
        }

      return res

    # def addSchemas(self, idx, obj):
    #   """
    #     generates schema entries
    #   """

    #   #for idx, obj in enumerate(self.api.objects):

    #   schemas = self.json_api_object["components"]["schemas"]

    #   ## get the name of the root object instead of the path
    #   name = re.sub('\.\{[^.]*\}$','', obj.name)

    #   if not name in schemas.keys():
    #     schemas[name] = self.makeBaseSchema(name, obj)   

    #   ## extract properties and required properties while merging with existing properties
    #   properties_and_required = self.makePropertiesFromSchema(obj, schemas[name]["properties"])

    #   ## store properties
    #   schemas[name]["properties"] = properties_and_required["properties"]

    #   ## merge with already required properties
    #   schemas[name]["required"] = schemas[name]["required"] + properties_and_required["required"]

    #   ## create events list
    #   schemas[name]["events"] = {**schemas[name]["events"], **self.makeEventsFromSchema(obj)}

    #   self.json_api_object["components"]["schemas"] = schemas


    def getSchema(self, name, idx, obj):

      # schemas = self.json_api_object["components"]["schemas"] 

      ## get the name of the root object instead of the path
      # name = re.sub('\.\{[^.]*\}$','', obj.name)

      ## check if we already have a file

      try:
        fname = "{}{}.json".format(self.folder, name)
        # print("looking for {}".format(fname))
        f = open(fname, 'r')
        obj_dict = json.loads(f.read())
        f.close()

        schemas = obj_dict["components"]["schemas"]
        # print("found existing schema {}".format(schemas))
      except Exception as e:
        # print("didn't find it {}".format(e))
        schemas = json.loads(self.objectTemplateString)

      if not name in schemas.keys():
        res = self.makeBaseSchema(name, obj)   
      else:
        res = schemas[name]

      ## extract properties and required properties while merging with existing properties
      properties_and_required = self.makePropertiesFromSchema(obj, res["properties"])

      ## store properties
      res["properties"] = properties_and_required["properties"]

      ## merge with already required properties
      res["required"] = res["required"] + properties_and_required["required"]

      ## create events list
      res["events"] = {**res["events"], **self.makeEventsFromSchema(obj)}

      # print(res["events"])

      return res

    # self.json_api_object["components"]["schemas"] = schemas
     

      # if not name in self.json_api_object["paths"]:
      #     self.json_api_object["paths"][name] = {}

      # return self.makePathsFromObject(obj)

####################################################################
################################ SCHEMAS EOF
####################################################################

####################################################################
################################ PATHS 
####################################################################

    def getResponses(self):

      if not(self.jsonResponses):
        self.jsonResponses = {}
        
        for r in self.api.response_codes:

          try:
            r_sample = json.dumps(json.loads(r.sample))
          except:
            r_sample = ""

          self.jsonResponses[r.name] = {
            "content":{
              "application/json": {
                "example": r_sample,
                "schema": {
                  "$ref": "#/components/schemas/Error"
                }
              }
            },
            "description": r.description,
          }

      return self.jsonResponses

    def makePathsFromObject(self, object):
      res = {}

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
          "operationId": pr.name + object.name,
          "summary": pr.description,
          "tags": [object.name],
          "requestBody": {
            "content":{
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ListRequest"
                },
                "example": s_request
              }
            }
          },
          "responses": {
            "99": {
              "content": {
                "application/json":{
                  "example": s_response,
                  "schema": {
                    "$ref": "#/components/schemas/" + re.sub('\.\{[^.]*\}$','', object.name)
                  }
                }
              }, 
              "description": "A well-formed call was performed to a valid object with valid arguments."
            }
          }
        }

        obj["responses"].update(self.getResponses())

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
        if "{" in object.name:
          obj["parameters"] = []
          params_re = re.compile('\{(.*?)\}')
          params_matches = params_re.findall(object.name)

          for p in params_matches:
            new_param = copy.deepcopy(PATH_PARAMETER_TEMPLATE)
            new_param["name"] = p
            new_param["description"] = "ID of a(n) {}".format(p.replace("Id", ""))
            if new_param["type"] == "integer":
              new_param["schema"] = json.loads(json.dumps(INTEGER_PARAMETER_SCHEMA))
            obj["parameters"].append(new_param)

        ## write procedure to out object
        res[pr.name] = obj

      return res

    # def addPaths(self, idx, obj):
    #     """
    #       adds paths to API object
    #     """

    #     name = re.sub('\.\{[^.]*\}$','', obj.name)

    #     if not name in self.json_api_object["paths"]:
    #       self.json_api_object["paths"][name] = {}

    #     self.json_api_object["paths"][name].update(self.makePathsFromObject(obj))

    def getPaths(self, name, idx, obj):

      if not name in self.json_api_object["paths"]:
          self.json_api_object["paths"][name] = {}

      return self.makePathsFromObject(obj)


####################################################################
################################ PATHS EOF
####################################################################

    # def populate(self):
    #   for idx, obj in enumerate(self.api.objects):

    #     ## add schemas
    #     self.addSchemas(idx, obj)

    #     ## add paths
    #     self.addPaths(idx, obj)

    def writeFile(self, name, obj):
      filepath = "{}{}.json".format(self.folder, name)

      f = open(filepath, "w")
      f.write(json.dumps(obj, indent=2))
      f.close()

    def createFilesAndPopulateObject(self):
      for idx, obj in enumerate(self.api.objects):
        out = json.loads(self.objectTemplateString)
        # out = {"paths":{}, "schema": {}}

        name = re.sub('\.\{[^.]*\}$','', obj.name)

        ## add schemas
        out["components"]["schemas"][name] = self.getSchema(name, idx, obj)
        print("{} {}".format(name, out["components"]["schemas"][name]["events"]))

        ## add paths
        out["paths"] = self.getPaths(name, idx, obj)
        self.json_api_object["paths"][name]["$ref"] = "{}.json#/paths".format(name)
        self.json_api_object["components"]["schemas"].update({name:{"$ref": "{}.json#/components/schemas/{}".format(name, name)}})
        self.writeFile(name, out)

    def writeOut(self):
      self.writeFile("api", self.json_api_object)
      # filepath = "{}{}.json".format(self.folder, "api")

      # f = open(filepath, "w")
      # f.write(json.dumps(self.json_api_object, indent=2))
      # f.close()

    def build(self):

        ## get template
        self.loadBlankJSONAPIObjectFromTemplate()

        ## populate API object
        self.createFilesAndPopulateObject()

        ## write file
        self.writeOut()

