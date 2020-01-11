from .config import config 

from .application.printer import Printer
from .application.input_processor import Processor
from .application.sqlite_engine import DatabaseEngine

from .classes.object import ObjectInstanceManager
from .classes.object_type import ObjectTypeManager

class App():
    def __init__(self):
        # load other objects into app
        self.config = config
        self.print = Printer(app=self)
        self.db = DatabaseEngine(db_url=self.config["database_file"], app=self)

        self.object_instance = ObjectInstanceManager(app=self)
        self.object_type = ObjectTypeManager(app=self)

    # ObjectInstance
    def create_object(self, type, value):
        return self.object_instance.new(type, value)

    def get_object_id(self, object_type, value):
        return self.object_instance.get_id(object_type, value)     

    def get_object_by_url(self, url):
        return self.object_instance.get_object_by_url(url)  

    def get_object_by_id(self, obj_id):
        return self.object_instance.get_object_by_id(obj_id)      

    def get_object_instance(self, object_type, value):
        return self.object_instance.get_object(object_type, value)           

    # ObjectType
    def create_object_type(self, handle, name="", description="", value_limit=""):
        return self.object_type.new(handle, name, description, value_limit)    

    def get_object_type_id(self, type_handle):
        return self.object_type.get_id(type_handle)      

    def get_object_type_handle(self, object_type_id):
        return self.object_type.get_handle(object_type_id)                   

    def convert_to_object_type_id(self, object_type):
        return self.object_type.convert_to_object_type_id(object_type)

    # General
    def get_id(self, url):
        self.get(url, req="id")

    def get(self, url, req="object"):
        if url == "" or url == False:
            self.print.error("app.get_id(): url was empty or false.")
            return False

        # Split url. If one part is found, get the object_type.
        # If two parts are found, get the object instance.
        # computer         <-- object_type
        # computer/srv-01  <-- object_instance

        parts = url.split("/")
        if len(parts) == 1:
            if req == "object":
                return self.object_type.get_object(parts[0])
            else:
                return self.get_object_type_id(parts[0])

        elif len(parts) == 2:
            if req == "object":
                return self.object_instance.get_object(parts[0], parts[1])
            else:
                return self.object_instance.get_id(parts[0], parts[1])
        else:
            self.print.error("app.get_id(): url %s is invalid." % url)
            return False


    def add_property(self, property, to):
        return self.object_instance.add_property(property_url=property, member_url=to)

    def csl_to_list(self, csl):
        l = csl.split(", ")
        return list(filter(None, l))

    def print_object_tree(self, object_url, level=0):
        obj = self.get(object_url)

        if obj == False:
            self.print.error("Object %s not found" % object_url)
            return False

        message = "  "*level + "- " + obj.url
        print(message)

        if obj.properties != "":
            properties = self.csl_to_list(obj.properties)
            for p in properties:
                prop = self.get_object_by_id(p)
                self.print_object_tree(prop.url, level=level+1)

        return True

    def process_input(self, input_file):
        processor = Processor(app=self)
        processor.process_input(input_file)


 



