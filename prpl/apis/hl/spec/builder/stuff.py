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