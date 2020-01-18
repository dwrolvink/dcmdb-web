
class ObjectManager():
    def __init__(self, app):
        self.app = app
        self.print = app.print

    # Create new ObjectInstance (no relationships)
    def new(self, object_type, handle, value=""):
        self.print.begin_step("Starting object creation of %s of type %s" % 
                              (handle, object_type))

        def fail():
            self.print.end_step("Object creation failed", failure=True)
            return False
        
        # Type accepts both type ids, and their respective names
        # If a name is given, convert it to an id
        # then test if result is OK
        type_id = self.app.convert_to_type_id(object_type)
        if type_id == False:
            return fail()
        type_handle = self.app.get_type_handle(type_id)

        if type_handle == False:
            self.print.error("object type with id %s was not found." % type_id)
            return fail()
        elif type_handle != object_type:
            self.print.print("Type id %s was converted to %s" 
                              % (type_id, type_handle))
        # Test if the type/handle combination is unique
        # For example, there should be only one computer/srv-001,
        # and only one location/amsterdam
        obj = self.get_object(object_type, handle)
        if obj != False:
            self.print.error("Object "+type_handle+"/"+handle+" already exists")
            return fail()

        # Create object
        query = "INSERT INTO objects (type, handle, value) "
        query += "VALUES('%s', '%s', '%s')" % (type_id, handle, value)
        r = self.app.db.run(query)
        row_id = self.app.db.cursor.lastrowid

        if r == False:
            return fail()     

        obj = self.get_object_by_id(row_id)
        
        self.print.end_step("Object "+obj.url+" created (id: %i)"
                            % row_id)      

        return row_id
           
    # GET OBJECT 
    # -----------------------------------------------------------------
    def get_object_by_url(self, url):
        type, handle = url.split("/")
        return self.get_object(type, handle)

    def get_id(self, type, handle):
        # type can be _name or _id, make sure to get the id
        type_id = self.app.convert_to_type_id(type)
        if type_id == False:
            return False

        # handle (object name) has to be set
        if handle == False:
            return False
        
        # Get object id
        query = "SELECT id FROM objects " \
                "WHERE type = '%s' AND handle = '%s'" % (type_id, handle)  

        fetch_result = self.app.db.fetch_one(query)

        # object not found
        if fetch_result is None:
            return False

        # object is found, return id
        return str(fetch_result[0])  

    def get_object_by_id(self, obj_id):
        query = "SELECT * FROM objects " \
                "WHERE id = '%s'" % obj_id
        fetch_result = self.app.db.fetch_one(query)

        # object not found
        if fetch_result is None:
            return False

        # object is found, create ObjectInstance, and return that
        obj = ObjectInstance(app=self.app, row=fetch_result)
        return obj

    def get_object(self, type, handle):
        obj_id = self.get_id(type, handle)
        return self.get_object_by_id(obj_id)

    def get_all_of_type(self, type_handle):
        # Convert type handle to id
        type_id = self.app.get_type_id(type_handle)

        # Get all objects of that type
        query = ("SELECT * FROM objects WHERE type = '%s';" %
                type_id)
        fetch_result = self.app.db.fetch_all(query)

        # objects not found
        if fetch_result is None:
            return False

        # Convert to ObjectType
        obj_list = []
        for row in fetch_result:
            obj_list.append(ObjectInstance(app=self.app, row=row))
        return obj_list    

    def add_property(self, property_url, member_url):
        def fail():
            self.print.end_step("Failed to create relationship.", failure=True)
            return False

        self.print.begin_step("Setting %s as a property of %s." % 
                             (property_url, member_url))

        # Get objects
        parent = self.get_object_by_url(property_url)
        member = self.get_object_by_url(member_url)

        if parent == False:
            self.print.error("Could not find %s" % property_url)
            return fail()
        elif member == False:
            self.print.error("Could not find %s" % member_url)
            return fail()
        
        # Add parent to member
        r = member.add_property(parent.id)

        if r: 
            self.print.end_step("Relationship set succesfully.")
            return True
        else: 
            return fail()    
                          

class ObjectInstance():
    def __init__(self, app, row):
        self.app = app
        self.print = app.print

        self.id = row[0]
        self.type_id = row[1]
        self.handle = row[2]
        self.value = row[3]

        self.members = []
        self.properties = []
        self.udvs = self.get_udvs()

        if self.value == "":
            self.value = self.handle

        # Get object type values
        self.type = self.app.get_type_by_id(self.type_id)
        self.type_handle = self.type.handle
        self.type_name = self.type.name

        # Compile object url
        self.url = self.type_handle + "/" + self.handle


    def add_property(self, property_id):
        """# test if property is already set
        if str(property_id) in self.properties:
            self.print.print("Property is already set. Skipping.", verbosity=2)
            return True """

        # Test if property is already set
        query = "SELECT * FROM relationships " \
                "WHERE object_id = {} AND parent_id = {}" \
                .format(self.id, property_id)

        result = self.app.db.fetch_one(query) 

        if result == False or result is not None:
            self.app.print.error("Property is already set.")
            return False

        # Test if this property is a member of this object
        query = "SELECT * FROM relationships " \
                "WHERE object_id = {} AND parent_id = {}" \
                .format(property_id, self.id)     

        result = self.app.db.fetch_one(query) 

        if result == False or result is not None:
            self.app.print.error("Property is already a member.")
            return False            

        # Test if we're trying to set an object to itself
        if self.id == property_id:
            self.app.print.error("Can't set object as property of itself.")
            return False

        # execute
        query = "INSERT INTO relationships (object_id, parent_id) "
        query += "VALUES('%s', '%s')" % (self.id, property_id)

        self.print.debug(query)

        # Return true (=success) if query succeeded
        return self.app.db.run(query)   

    def get_properties(self):
        # Get objects
        query = "SELECT parent_id FROM relationships WHERE object_id = {}".format(self.id)   
        res = self.app.db.fetch_all(query)
        properties = []
        for p in res:
            properties.append(self.app.get_object_by_id(p[0]))

        return properties

    def get_udvs(self):
        """ Return a tuple list with the udv type and the value:
            [(type_obj, val1), (type_obj, val2), ...]
        """

        # Get all udv types
        query = "SELECT udv FROM udvs WHERE object_id = {}".format(self.id)
        udvs = self.app.db.fetch_all(query)
        
        if udvs is None:
            return []

        # OUT
        udv_return = []

        # Loop over each udv and find the values associated to this object
        for udv in udvs:
            udv_type = udv[0]
            
            # Get type object so we can return that for each value
            otype = self.app.get_type_by_handle(udv_type)
            
            # All the values of this udv type are in a separate table
            # Get the values
            table_name = "value_"+udv_type 
            query = "SELECT value FROM {} WHERE parent_id = {}".format(table_name, self.id)
            self.print.debug(query)
            values = self.app.db.fetch_all(query)

            # Add each value to the output list
            for value in values:
                udv_return.append((otype, value[0]))
        
        return udv_return

    def get_udvs_of_type(self, type_handle):
        """ Return a list of values of the given udv type: [val1, val2, ...] """
        output = []
        for udv in self.udvs:
            if udv[0].handle == type_handle:
                output.append(udv[1])
        return output

    def get_members(self):
        query = "SELECT object_id FROM relationships WHERE parent_id = {}".format(self.id)  
        res = self.app.db.fetch_all(query)
        
        members = []
        for p in res:
            if p[0] != self.id:
                members.append(p[0])
        
        return members        






    