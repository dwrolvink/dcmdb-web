
class TypeManager():
    def __init__(self, app):
        self.app = app
        self.print = app.print

    def new(self, handle, name="", description="", value_limit="", data_type="", unit=""):
        def fail():
            self.print.end_step("Type creation failed", failure=True)
            return False 

        if name == "":
            self.print.begin_step("Starting type creation of %s" % handle)
        else:
            self.print.begin_step("Starting type creation of %s (%s)" % 
                                    (handle, name))

        # Test if object already exists
        obj = self.get_id(handle)
        if obj != False:
            self.print.error("Object type "+handle+" already exists")
            return fail()        
      
        # Execute
        query = "INSERT INTO types (handle, name, description, value_limit, data_type, unit) "
        query += "VALUES('%s', '%s', '%s', '%s', '%s', '%s');" % (
                    handle, name, description, value_limit, data_type, unit)
        self.print.debug(query)

        r = self.app.db.run(query)
        row_id = self.app.db.cursor.lastrowid

        if r == False:
            return fail()     

        self.print.end_step("type %s created (id: %i)" % (handle, row_id))

        return row_id

    def get_all(self):
        query = "SELECT * FROM types;"
        fetch_result = self.app.db.fetch_all(query)

        # objects not found
        if fetch_result is None:
            return False

        # Convert to ObjectType
        ot_list = []
        for row in fetch_result:
            ot_list.append(ObjectType(app=self.app, row=row))
        return ot_list
    
    def get_id(self, type_handle):
        """returns False if no object is found, otherwise str(int)"""

        query = "SELECT id FROM types WHERE handle = '%s';" % type_handle
        r = self.app.db.fetch_one(query)

        # object type not found
        if r is None:
            return False

        # object type is found, return first element of tuple
        return str(r[0])     

    def get_object_by_id(self, obj_id):
        query = "SELECT * FROM types " \
                "WHERE id = '%s'" % obj_id
        fetch_result = self.app.db.fetch_one(query)

        # object not found
        if fetch_result is None:
            return False

        # object is found, create ObjectInstance, and return that
        obj = ObjectType(app=self.app, row=fetch_result)
        return obj

    def get_object_by_handle(self, handle):
        obj_id = self.get_id(handle)
        return self.get_object_by_id(obj_id)
        
    def get_handle(self, type_id):
        query = "SELECT handle FROM types WHERE id = '%s';" % type_id
        r = self.app.db.fetch_one(query)

        # object type not found
        if r is None:
            return False

        # object type is found, return first element of tuple
        return r[0]           

    # in: either type_handle or type_id, out: type_id
    def convert_to_type_id(self, _type):
        type_id = 0
        type_handle = ""

        # check if given type is an id / get type_id
        if type(_type) == int:
            type_id = _type
        elif _type.isdigit() == False:
            type_handle = _type
        else:
            type_id = _type

        # Get object id, if handle is found
        if type_handle != "":
            type_id = self.get_id(type_handle)

        # id could not be found
        if type_id == False:
            self.print.error("convert_to_type_id(): inserted type was either empty, "
                  "or given type (%s) could not be found" % _type)
            return False       

        return type_id                 

class ObjectType():
    def __init__(self, app, row):
        self.app = app
        self.print = app.print

        self.id = row[0]
        self.handle = row[1]
        self.name = row[2]
        self.description = row[3]
        self.value_limit = row[4]
        self.data_type = row[5]
        self.unit = row[6]
        self.url = self.handle

        if self.name == "":
            self.name = self.handle

    def __repr__(self):    
        return ("\n<class ObjectType> \n" \
              " handle: %s \n"
              " name: %s \n" \
              " description: \"%s\" \n" \
              " value_limit: \"%s\" \n" \
              " unit: \"%s\" \n" \
              " data_type: \"%s\"\n</class>\n" %
              (self.handle, self.name, self.description, 
              self.value_limit, self.unit, self.data_type))    