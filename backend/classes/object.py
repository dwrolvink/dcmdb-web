
class ObjectInstanceManager():
    def __init__(self, app):
        self.app = app
        self.print = app.print

    # Create new ObjectInstance (no relationships)
    def new(self, object_type, value):
        self.print.begin_step("Starting object creation of %s of type %s" % 
                              (value, object_type))

        def fail():
            self.print.end_step("Object creation failed", failure=True)
            return False
        
        # Type accepts both object_type ids, and their respective names
        # If a name is given, convert it to an id
        # then test if result is OK
        type_id = self.app.convert_to_object_type_id(object_type)
        if type_id == False:
            return fail()
        type_handle = self.app.get_object_type_handle(type_id)

        if type_handle == False:
            self.print.error("object type with id %s was not found." % type_id)
            return fail()
        elif type_handle != object_type:
            self.print.print("Type id %s was converted to %s" 
                              % (type_id, type_handle))
        # Test if the type/value combination is unique
        # For example, there should be only one computer/srv-001,
        # and only one location/amsterdam
        obj = self.get_object(object_type, value)
        if obj != False:
            self.print.error("Object "+type_handle+"/"+value+" already exists")
            return fail()

        # Create object
        query = "INSERT INTO objects (type, value, properties, members) "
        query += "VALUES('%s', '%s', '', '')" % (type_id, value)
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
        object_type, value = url.split("/")
        return self.get_object(object_type, value)

    def get_id(self, object_type, value):
        # object_type can be _name or _id, make sure to get the id
        object_type_id = self.app.convert_to_object_type_id(object_type)
        if object_type_id == False:
            return False

        # value (object name) has to be set
        if value == False:
            return False
        
        # Get object id
        query = "SELECT id FROM objects " \
                "WHERE type = '%s' AND value = '%s'" % (object_type_id, value)  

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

    def get_object(self, object_type, value):
        obj_id = self.get_id(object_type, value)
        return self.get_object_by_id(obj_id)

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
        
        # Add member to parent, and parent to member
        r1 = parent.add_member(member.id)
        r2 = member.add_property(parent.id)

        if r1 != r2: # one succeeded, other didn't
            self.print.error("Database is now corrupt :)")
            return fail()
        elif r1 and r2: # both succeeded
            self.print.end_step("Relationship set succesfully.")
            return True
        else: # both failed
            return fail()    
                          

class ObjectInstance():
    def __init__(self, app, row):
        self.app = app
        self.print = app.print

        self.id = row[0]
        self.object_type_id = row[1]
        self.value = row[2]
        self.properties = row[3]
        self.members = row[4]
        self.object_type_handle = self.app.get_object_type_handle(self.object_type_id)
        self.url = self.object_type_handle + "/" + self.value

    def add_member(self, member_id):
        # test if property is already set
        if str(member_id) in self.members:
            self.print.print("Member is already set. Skipping.", verbosity=2)
            return True        

        # Compose new member list
        members = self.members + str(member_id) + ", "

        # Execute
        query = """UPDATE objects
                SET members = '%s'
                WHERE id == %i;""" % (members, self.id)

        self.print.debug(query)

        # Return true (= success) if query succeeded
        return self.app.db.run(query)


    def add_property(self, property_id):
        # test if property is already set
        if str(property_id) in self.properties:
            self.print.print("Property is already set. Skipping.", verbosity=2)
            return True

        # Compose new property list
        properties = self.properties + str(property_id) + ", "

        # execute
        query = """UPDATE objects
                SET properties = '%s'
                WHERE id == %i;""" % (properties, self.id)

        self.print.debug(query)

        # Return true (=success) if query succeeded
        return self.app.db.run(query)      


    