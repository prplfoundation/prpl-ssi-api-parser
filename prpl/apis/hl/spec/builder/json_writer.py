
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
        try:
          shutil.rmtree(self.folder)
        except Exception as e:
            self.logger.debug("ran into an exception removing old files")

        self.logger.debug('File - Finished removing files "{}".'.format(self.folder))

        # create new folder
        os.makedirs(self.folder)

        # load template into object
        f = open(self.template, "r")
        self.json_api_object = json.loads(f.read())
        f.close()

####################################################################
################################ SCHEMAS
####################################################################

    def makeBaseSchema(self, name, api_object):
      desc = name + " Object"
      res = {
        "description": desc, 
        "id": name,
        "type": "object",
        "required": [],
        "properties": {},
        "events": {},
        "example": {},
        "layer": api_object.layer
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
      mainObject = f.name[:f.name.index(".")]
      newProperty = f.name[f.name.index(".")+1:]
      if mainObject not in res["properties"]:
        
        res["properties"][mainObject] = {
          "type": "object",
          "properties": {},
          "required": []
        }

      ## CULPRIT
      newF = copy.deepcopy(f)
      newF.name = newProperty

      
      if "." in newF.name:
        self.getNestedProperty(newF, res["properties"][mainObject])  
      else:
        self.getSimpleProperty(newF, res["properties"][mainObject])

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

          for f in p.parameters:
            
            if "." in f.name:
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
        
        f = open(fname, 'r')
        obj_dict = json.loads(f.read())
        f.close()

        schemas = obj_dict["components"]["schemas"]
        
      except Exception as e:
        
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

      return res

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

          # try:
          r_sample = json.dumps(json.loads(r.sample))
          # except:
            # r_sample = ""

          self.jsonResponses[r.name] = {
            "content":{
              "application/json": {
                "example": r_sample,
                "schema": {
                  "$ref": "#/components/schemas/Error"
                }
              }
            },
            "raised_by": r.raised_by,
            "description": r.description
          }

      return self.jsonResponses


    def makeRequestBody(self, obj, pr, object):

      if pr.name not in ["Delete", "Get"]:

        try:
          s_request = json.dumps(json.loads(pr.sample_request))
        except:
          s_request = ""
        
        ref = "#/components/schemas/" + re.sub('\.\{[^.]*\}$','', object.name)

        if pr.name == "List":
          ref = "#/components/schemas/ListRequest"

        schema = self.makeSchemaFromProcedureParameters(pr, True)

        res = {
                "content":{
                  "application/json": {
                    "schema": schema,
                    "example": s_request
                  }
                }
              }

        # res = {
        #         "content":{
        #           "application/json": {
        #             "schema": {
        #               "$ref": ref
        #             },
        #             "example": s_request
        #           }
        #         }
        #       }

        obj["requestBody"] = res


    def makeSchemaFromProcedureParameters(self, procedure, collect_request_parameters):
      schema = {"properties":{}, "required": []}

      for f in procedure.parameters:
        if (collect_request_parameters and f.is_input) or (not collect_request_parameters and f.is_output):
          if "." in f.name:
            self.getNestedProperty(f, schema)
            
          else:
            self.getSimpleProperty(f, schema)

      return schema

    def makePathsFromObject(self, api_object):
      res = {}
      for pr in api_object.procedures:
        
        try:
          s_response = json.dumps(json.loads(pr.sample_response))
        except:
          s_response = ""

        schema = self.makeSchemaFromProcedureParameters(pr, False)

        obj = {
          "operationId": api_object.name + "." + pr.name,
          "summary": pr.description,
          "tags": [api_object.name],
          "responses": {
            "99": {
              "content": {
                "application/json":{
                  "example": s_response,
                  "schema": schema
                }
              }, 
              "description": "A well-formed call was performed to a valid object with valid arguments."
            }
          }
        }

        self.makeRequestBody(obj, pr, api_object)

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
        if "{" in api_object.name:
          obj["parameters"] = []
          params_re = re.compile('\{(.*?)\}')
          params_matches = params_re.findall(api_object.name)

          for p in params_matches:
            new_param = copy.deepcopy(PATH_PARAMETER_TEMPLATE)
            new_param["name"] = p
            new_param["description"] = "ID of a(n) {}".format(p.replace("Id", ""))
            if new_param["type"] == "integer":
              new_param["schema"] = json.loads(json.dumps(INTEGER_PARAMETER_SCHEMA))
            obj["parameters"].append(new_param)

        res[api_object.name + "." + pr.name] = obj

      return res

    def getPaths(self, name, idx, obj):

      if not name in self.json_api_object["paths"]:
        self.json_api_object["paths"][name] = {}

      return self.makePathsFromObject(obj)


####################################################################
################################ PATHS EOF
####################################################################

####################################################################
################################ INSTANCES
####################################################################

    def getInstances(self, obj):
      res = {}

      for ins in obj.instances:
        res[ins.name] = {
          'description': ins.description
        }

      return res

####################################################################
################################ INSTANCES EOF
####################################################################

####################################################################
################################ VERSIONS
####################################################################

    def addVersions(self):

      self.json_api_object["versions"] = {}

      for v in self.api.versions:
        
        self.json_api_object["versions"][v.number] = {
          'date': v.date,
          'changes': v.change_list
        }


####################################################################
################################ VERSIONS EOF
####################################################################

    def writeFile(self, name, obj):
      filepath = "{}{}.json".format(self.folder, name)

      f = open(filepath, "w")
      f.write(json.dumps(obj, indent=2))
      f.close()

    def createFilesAndPopulateObject(self):

      for idx, obj in enumerate(self.api.objects):

        name = re.sub('\.\{[^.]*\}$','', obj.name)
        f_name = "{}{}.json".format(self.folder, name)

        ## check if we already have a file of that name
        if os.path.isfile(f_name):
          f = open(f_name, "r")
          out = json.loads(f.read())
          f.close()
        else:
          ## if not, load template
          out = json.loads(self.objectTemplateString)

        ## add schemas
        ## TODO: this changes the field.name
        out["components"]["schemas"][name] = self.getSchema(name, idx, obj)

        ## add paths

        if out["paths"] == None:
          out["paths"] = self.getPaths(name, idx, obj)
        else:
          out["paths"] = {**out["paths"], **self.getPaths(name, idx, obj)}
        
        if len(obj.instances) > 0:
          out["instances"] = self.getInstances(obj)

        self.json_api_object["paths"][name]["$ref"] = "{}.json#/paths".format(name)
        self.json_api_object["components"]["schemas"].update({name:{"$ref": "{}.json#/components/schemas/{}".format(name, name)}})
        self.writeFile(name, out)

      self.addVersions()

    def writeOut(self):
      self.writeFile("api", self.json_api_object)

    def build(self):

      ## populate API object
      self.createFilesAndPopulateObject()

      ## write file
      self.writeOut()

# 