from .config import config 

from .application.printer import Printer
from .application.input_processor import Processor
from .application.sqlite_engine import DatabaseEngine

from .classes.object import ObjectManager
from .classes.type import TypeManager
from .classes.udv import UDVManager

class App():
    def __init__(self):
        # load other objects into app
        self.config = config
        self.print = Printer(app=self)
        self.db = DatabaseEngine(db_url=self.config["database_file"], app=self)

        self.object = ObjectManager(app=self)
        self.type   = TypeManager(app=self)
        self.udv    = UDVManager(app=self)

    # ObjectInstance
    def create_object(self, type, handle, value):
        return self.object.new(type, handle, value)

    def get_object_id(self, type, handle):
        return self.object.get_id(type, handle)     

    def get_object_by_url(self, url):
        return self.object.get_object_by_url(url)  

    # int -> ObjectInstance | False
    def get_object_by_id(self, obj_id):
        return self.object.get_object_by_id(obj_id)      

    def get_object(self, type, handle):
        return self.object.get_object(type, handle)     

    def get_all_objects_of_type(self, type):
        obj_list = self.object.get_all_of_type(type)
        obj_list.sort(key = lambda x: x.value)
        return obj_list           

    # ObjectType
    def create_type(self, handle, name="", description="", value_limit="", data_type="object", unit=""):
        return self.type.new(handle, name, description, value_limit, data_type, unit)    

    def get_type_id(self, type_handle):
        return self.type.get_id(type_handle)      

    def get_type_by_id(self, type_id):
        return self.type.get_object_by_id(type_id)

    def get_type_by_handle(self, type_handle):
        return self.type.get_object_by_handle(type_handle)

    def get_type_handle(self, type_id):
        return self.type.get_handle(type_id)      

    def get_all_types(self):
        ot_list = self.type.get_all()  
        ot_list.sort(key = lambda x: x.name)
        return ot_list           

    def convert_to_type_id(self, type):
        return self.type.convert_to_type_id(type)
       

    # General
    def get_id(self, url):
        self.get(url, req="id")

    def get(self, url, req="object"):
        if url == "" or url == False:
            self.print.error("app.get_id(): url was empty or false.")
            return False

        # Split url. If one part is found, get the type.
        # If two parts are found, get the object.
        # computer         <-- type
        # computer/srv-01  <-- object

        parts = url.split("/")
        if len(parts) == 1:
            if req == "object":
                return self.type.get_object(parts[0])
            else:
                return self.get_type_id(parts[0])

        elif len(parts) == 2:
            if req == "object":
                return self.object.get_object(parts[0], parts[1])
            else:
                return self.object.get_id(parts[0], parts[1])
        else:
            self.print.error("app.get_id(): url %s is invalid." % url)
            return False


    def add_property(self, property, to):
        return self.object.add_property(property_url=property, member_url=to)

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


 



