
# UDV extends the normal object type (see type.py)

class UDVManager():
    def __init__(self, app):
        self.app = app
        self.print = app.print

   
    def new(self, handle, name="", description="", value_limit="", data_type="", unit=""):
        self.print.begin_step("Starting creation of new UDV %s " % 
                              (handle))

        def fail():
            self.print.end_step("UDV creation failed", failure=True)
            return False
        
        # Create new table for this UDV
        self.print.begin_step("Starting creation of UDV table")
        result = self.create_value_table(handle)

        if result == False:
            self.print.end_step("UDV table creation failed", failure=True)
            return fail()
        
        self.print.end_step("UDV table created succesfully")

        # Create new Type
        result = self.app.create_type(handle, name, description, value_limit,
                                      data_type, unit)
        if result == False:
            return fail()

        self.print.end_step("UDV created succesfully")

        return True
           

    def create_value_table(self, type_handle):
        table_name = "value_" + type_handle
        query = "CREATE TABLE {} (id integer primary key autoincrement, " \
                 "parent_id integer, value text);".format(table_name)  
        self.app.print.debug(query)
        return self.app.db.run(query)

    def get_set_udv_values(self, type_handle):
        # Select all objects that have set values for this value_type
        query = "SELECT object_id FROM udvs WHERE udv = '{}'".format(type_handle)
        result = self.app.db.fetch_all(query)

        # For each object, make a tuple (obj, [val1, val2, ...])
        # and put this in a list
        objects = []
        for row in result:
            obj_id = row[0]

            # Get udv values + make tuple
            obj = self.app.get_object_by_id(obj_id)
            values = obj.get_udvs_of_type(type_handle)
            tup = (obj, values)

            # Append to list
            objects.append(tup)
        
        return objects

    def set_ud_value(self, obj_url, type_handle, value):
        def fail():
            self.print.end_step("Failed to set UDV.", failure=True)
            return False

        self.print.begin_step("Setting UDV {} with value {} " \
                              "on object {}".format(type_handle, value, obj_url))        

        # Check if udv type exists
        query = "SELECT * FROM types WHERE handle = '{}'".format(type_handle)
        r = self.app.db.fetch_one(query)  

        if r is None:
            self.app.print.error("Could not set UDV {} to {} because " \
                                 "the type seems to not exist yet." \
                                 .format(type_handle, obj_url))
            return fail()

        # Get/set some data to be used later
        table_name = "value_"+type_handle
        obj = self.app.get_object_by_url(obj_url)

        # See if this UDV is already set to the object
        # This will allow the object to only query UDV's that are linked
        # in this way.
        query = "SELECT udv FROM udvs WHERE object_id = {} AND udv = '{}'" \
                .format(obj.id, type_handle)
        r = self.app.db.fetch_one(query)  
        
        if r is None:
            # not yet set, so set it now
            query = "INSERT INTO udvs (object_id, udv) " \
                    "VALUES('{}', '{}')".format(obj.id, type_handle)
            self.print.debug(query)
            r = self.app.db.run(query) 

            if r == False:
                return fail()
            
        # Add value to the UDV table
        query = "INSERT INTO {} (parent_id, value) ".format(table_name)
        query += "VALUES('{}', '{}')".format(obj.id, value)

        self.app.print.debug(query) 
        r = self.app.db.run(query) 

        if r == False:
            return fail()

        self.print.end_step("UDV set succesfully")
        return True
    