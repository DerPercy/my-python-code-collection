import json 

class SchemaType():
    type_def :str
    is_list:bool
    def __init__(self, payload:dict) -> None:
        self.type_def = "None"
        self.is_list = False
        self.parse_payload(payload)

    def parse_payload(self,payload:dict):
        if payload.get("kind",None) in ["LIST"]:
            self.is_list =True
        if payload.get("kind",None) in ["OBJECT","INPUT_OBJECT"]:
            self.type_def = payload["name"]
            return
        if payload.get("ofType",None) != None:
            self.parse_payload(payload.get("ofType",None))

    def has_type_def(self) -> bool:
        if self.type_def == "None":
            return False
        if self.type_def == 'Float':
            return False
        if self.type_def == 'String':
            return False
        return True

    def get_type_def(self,for_request:bool) -> str:
        if self.type_def == 'Float':
            return ""
        if self.type_def == 'String':
            return ""
        result = self.type_def
        if for_request == False:
            # response: add list if needed
            if self.is_list == True:
                result = "list["+result+"]"
        return result

class SchemaArgument():
    arg_name:str
    arg_type:SchemaType
    def __init__(self, arg_name:str, arg_type: SchemaType) -> None:
        self.arg_name = arg_name
        self.arg_type = arg_type
    def to_method_arg_format(self,for_request:bool):
        if self.arg_type != None and self.arg_type.has_type_def() == True:
            return self.arg_name+":'"+self.arg_type.get_type_def(for_request)+"'"
        return self.arg_name
      
class SchemaMethod():
    method_name:str
    return_type:SchemaType
    arguments:list[SchemaArgument]
    def __init__(self, method_name:str,schema_object:'SchemaObject') -> None:
        self.method_name = method_name
        self.arguments = []
    def set_return_type(self,return_type:SchemaType) -> None:
        self.return_type = return_type
    def add_argument(self,argument:SchemaArgument) -> None:
        self.arguments.append(argument)
    def get_method_name(self) -> str:
        m_name = self.method_name
        if m_name == "from":
            m_name = "_from"
        return m_name
    def get_method_type_declaration(self,for_request:bool, splitter:str = " -> ", ):
        ret_class_name = ""
        if self.return_type != None and self.return_type.has_type_def() == True :
            ret_class_name = splitter + "'" + self.return_type.get_type_def(for_request) + "'"
        return ret_class_name
    def to_file(self):
        m_name = self.get_method_name()
        ret_class_name = self.get_method_type_declaration(True)
        # Arguments
        args = ""
        for arg in self.arguments:
            args += ","+arg.to_method_arg_format(True)
        lines = []
        lines.append("\n    def "+m_name+"(self"+ args +",_param_name:str = '"+m_name+"')" + ret_class_name+ ":")
        if self.return_type != None and self.return_type.has_type_def() == True :
            lines.append("\n        param_list = []")
            for arg in self.arguments:
                lines.append("\n        param_list.append((\""+arg.arg_name+"\","+arg.arg_name+"))")
            #lines.append("\n        self._parameter_list = param_list")    
            lines.append("\n        inst = "+self.return_type.get_type_def(True)+"(self,param_list)")
            lines.append("\n        self._add_to_query(\""+m_name+"\",_param_name,inst)")
            lines.append("\n        self.value_"+ m_name +" = inst")
            #lines.append("\n        self['"+ m_name +"'] = inst")
            lines.append("\n        return inst")    
        else:
            lines.append("\n        inst = None")
            lines.append("\n        self._add_to_query(\""+m_name+"\",_param_name)")
            lines.append("\n        pass")
        lines.append("\n")
        return lines

class SchemaObject():
    class_name:str
    methods: list[SchemaMethod]
    constructor_args: list[SchemaArgument]
    def __init__(self, class_name:str) -> None:
        self.class_name = class_name
        self.methods = []
        self.constructor_args = []

    def add_method(self, method:SchemaMethod):
        self.methods.append(method)
    def add_constructor_arg(self, arg:SchemaArgument):
        self.constructor_args.append(arg)

    def get_required_class_names(self) -> list[str]:
        """
        Get required class names
        """
        list_class_names = []
        # 1. Return values of methods
        for meth in self.methods:
            if meth.return_type != None:
                list_class_names.append(meth.return_type.get_type_def(True))
        return list_class_names
    # Abstract methods
    def on_class_name_after(self,lines:list[str]) -> None:
        pass
    def on_init_method(self,lines:list[str]) -> None:
        lines.append("\n        pass")
    def on_get_class_parent(self) -> str:
        return ""
    def render_methods(self) -> bool:
        return True
    
    # To file rendering
    def to_file(self):
        lines = []
        lines.append("\nclass "+self.class_name+"("+self.on_get_class_parent()+"):")
        self.on_class_name_after(lines)
        if len(self.constructor_args) > 0:
            args = ""
            for arg in self.constructor_args:
                args += ","+arg.to_method_arg_format(True)+" = None"
        
            lines.append("\n    def __init__(self"+args+"):")
            self.on_init_method(lines)
            
        if self.render_methods() == True:
            for method in self.methods:
                lines.extend(method.to_file())
        lines.append("\n")
        return lines

class SchemaObjectObject(SchemaObject):
    def on_class_name_after(self, lines: list[str]) -> None:
        super().on_class_name_after(lines)
        for method in self.methods:
            lines.append("\n    value_"+method.get_method_name()+method.get_method_type_declaration(False,":")+" = None") # Add Methodname as variable to
    def on_get_class_parent(self) -> str:
        return "GraphQLObject"

class SchemaObjectInputObject(SchemaObject):
    def on_init_method(self, lines: list[str]) -> None:
        if len(self.constructor_args) > 0:
            for arg in self.constructor_args:
                lines.append("\n        self._add_parameter('"+ arg.arg_name+"',"+ arg.arg_name +")")    
        else:
            return super().on_init_method(lines)
    def render_methods(self) -> bool:
        return False
    def on_get_class_parent(self) -> str:
        return "GraphQLInputObject"


class SchemaEnum():
    pass

class SchemaFile():
    classes:list[SchemaObject]
    enums:list[SchemaEnum]

    def __init__(self) -> None:
        self.classes = []
        self.enums = []
    def add_class(self,schema_object:SchemaObject):
        self.classes.append(schema_object)
    def add_enum(self,schema_enum:SchemaEnum):
        self.enums.append(schema_enum)
    
    def render_class(self,class_name:str, class_list: list[str]) -> list[str]:
        file_lines = []
        if class_name in class_list:
            class_list.remove(class_name)
            for class_obj in self.classes:
                if class_name == class_obj.class_name:
                    for req_class_name in class_obj.get_required_class_names():
                        file_lines.extend(self.render_class(req_class_name,class_list))
                    #print("Now rendering class "+class_name)
                    file_lines.extend(class_obj.to_file())
                    
            #return file_lines
        else:
            pass
            #return file_lines
        return file_lines
        
    def to_file(self):
        code = """

class GraphQLInputObject():
    _parameter_list = []
    def __init__(self):
        self._parameter_list = []
    def _add_parameter(self,name:str,value):
        if value != None:
            self._parameter_list.append((name,value))
    def __str__(self):
        result = "{"
        sep = ""
        for param in self._parameter_list:
            result = result + sep + param[0] + ": " + GraphQLInputObject.to_string(param[1])
            sep = ","
        result = result + "}" 
        return result
    def to_string(value):
        if value == None:
            return None
        val = ""
        if isinstance(value,GraphQLInputObject):
            val = str(value)
        elif isinstance(value,int):
            val = str(value)
        else:
            val = "\\"" + str(value) + "\\""
        return val

class GraphQLResultObject():
    pass
class GraphQLObject():
    _parent = None
    _children = None
    _parameter_list = None
    def __init__(self,parent:'GraphQLObject' = None,parameter_list = []):
        self._parent = parent
        self._children = []
        self._parameter_list = parameter_list
    def __getitem__(self, x):
        return self
    def _add_to_query(self,name:str, param_name:str, sub_obj:'GraphQLObject' = None) -> None:
        self._children.append((name,sub_obj,param_name))
    def _create_parameter_code(self) -> str:
        result = ""
        if len(self._parameter_list) > 0:
            result = result + "("
            for param in self._parameter_list:
                val = GraphQLInputObject.to_string(param[1])
                if val != None:
                    result = result + param[0] +": "+ val
            result = result + ")"     
        return result

    def _create_query_code(self, check_parent:bool = True) -> str:
        if check_parent == True and self._parent != None:
            return self._parent._create_query_code(True)
        result = ""    
        for child in self._children:
            result = result + "\\n" + child[2]+": "+ child[0]
            if child[1] != None:
                result = result + child[1]._create_parameter_code() + "{" + child[1]._create_query_code(False) + "\\n}"
            
        return result
    
    def _fill_response(self, json_payload, check_parent:bool = True):
        def get_value(data):
            if isinstance(data,list):
                #print("is list")
                result = []
                for entry in data:
                    result.append(get_value(entry))
                return result
            if isinstance(data,dict):
                #print("is dictionary")
                result = GraphQLResultObject()
                for key in data.keys():
                    setattr(result,"value_"+key,get_value(data[key]))
                    #result["value_"+key] = get_value(data[key])
                return result
            else:
                return data
        for key in json_payload.keys():
            setattr(self, "value_"+key, get_value(json_payload[key]))
            print("Set key "+key+" in "+str(self))
            #print(get_value(json_payload[key]))
"""
        lines = []
        lines.append("\nfrom enum import Enum")
        lines.append("\n")
        lines.append("\n"+code)
        lines.append("\n")
        render_classes = []

        for schema_object in self.classes:
            render_classes.append(schema_object.class_name)
            #lines.extend(schema_object.to_file())
        while len(render_classes) > 0:
            lines.extend(self.render_class(render_classes[0],render_classes))
        return lines


schema_file = SchemaFile()
with open('schema.json', 'r') as f:
    data = json.load(f)

    #print(data["data"]["__schema"]["queryType"])

    for type_entity in data["data"]["__schema"]["types"]:
        if type_entity["kind"] in ["OBJECT","INTERFACE","INPUT_OBJECT"]:
            if type_entity["kind"] in ["OBJECT"]:
                obj = SchemaObjectObject(class_name=type_entity["name"])
            elif type_entity["kind"] in ["INPUT_OBJECT"]:
                obj = SchemaObjectInputObject(class_name=type_entity["name"])
            else:
                obj = SchemaObject(class_name=type_entity["name"])
            # parse subtypes
            fields = type_entity["fields"]
            if fields == None:
                fields = type_entity["inputFields"]
                # inputFields => constructor imports
                for constructor_params in fields:
                    cons_arg = SchemaArgument(constructor_params["name"],SchemaType(constructor_params["type"]))
                    obj.add_constructor_arg(cons_arg)

            for children in fields:
                method = SchemaMethod(method_name=children["name"],schema_object=obj)
                obj.add_method(method)
                # Arguments
                if children.get("args") != None:
                    for arg in children["args"]:
                        method.add_argument(SchemaArgument(arg["name"],SchemaType(arg["type"])))
                # get return value
                if children["type"] != None:
                    schema_type = SchemaType(children["type"])
                    method.set_return_type(schema_type)
                #try:
                #    if children["type"].get("ofType",{}).get("kind",None) == "OBJECT":
                #        method.set_return_class(children["type"]["ofType"]["name"])
                #except AttributeError:
                #    pass
                ## get return value (2nd way)
                #try:
                #    if children["type"].get("kind",None) == "OBJECT":
                #        method.set_return_class(children["type"]["name"])
                #except AttributeError:
                #    pass
               # 
                # Return list
                #try:
                #    if children["type"].get("ofType",{}).get("kind",None) == "LIST":
                #        method.set_return_list_class(children["type"]["ofType"]["ofType"]["ofType"]["name"])
                #except AttributeError:
                #    pass
                #except TypeError:
                #    pass
                
            #print( type_entity["name"] ) 
            schema_file.add_class(obj)
        if type_entity["kind"] == "ENUM":
            pass
with open('schema.py', 'w') as f:
    f.writelines(schema_file.to_file())