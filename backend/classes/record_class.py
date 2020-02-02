class RecordClass():
    def __init__(self, app, class_id):
        self.app = app

        query = "SELECT * FROM classes WHERE id = {}".format(class_id)        
        row = self.app.db.fetch_one(query)

        self.id = row[0]
        self.handle = row[1]
        self.name = row[2]
        self.type = row[3]
        self.description = row[4]
        self.appended = row[5]
        self.unit = row[6]
        self.value_prefix = row[7]
        self.value_limit = row[8]
        self.applies_to = self.app.csl_to_list(row[9])
        self.accepts = self.app.csl_to_list(row[10])

        # Set applies_to_all flag if applies_to == '*'
        self.applies_to_all = False
        if '*' in self.applies_to:
            self.applies_to_all = True
            self.applies_to.remove('*')

        # Set url
        self.url = 'class/' + self.handle

    def definition(self, load_records=False):
        rcObj = {}
        rcObj['id']     = self.id
        rcObj['handle'] = self.handle
        rcObj['name']   = self.name
        rcObj['type']   = self.type
        rcObj['unit']   = self.unit

        if load_records:
            rcObj['records'] = [r.definition() for r in self.records()]

        # List all classes that records of this class accepts as properties
        accept_list = self.accepts_objects()
        if accept_list:
            rcObj['accepts'] = [(rc.id, rc.name) for rc in accept_list]       

        return rcObj 

    def signature(self):
        return  {
                    'id' : self.id,
                    'url': self.handle,
                    'name': self.name,
                    'type': self.type
                }

    def accepts_objects(self):
        rc_list = []
        for rch in self.accepts:
            rc_list.append(self.app.get(rch))
        return rc_list

    def records(self):
        query = "SELECT * FROM records WHERE class_id = {};" \
                .format(self.id)

        return self.app.get_object_list(query, self.app.Record)   

    def print(self):
        print(self.__repr__())

    def __repr__(self):  

        appended = "False"
        if self.appended:
            appended = "True"

        msg = (
                "\n"
                "[{5}] {0} \n" 
                "  - id:           {6} \n"
                "  - handle:       {0} \n" 
                "  - name:         {1} \n" 
                "  - type:         {5} \n"                
                "  - description:  {2} \n" 
                "  - appended:     {7} \n"
                "  - unit:         {4} \n" 
                "  - value_prefix: {8} \n" 
                "  - value_limit:  {3} \n" 
                "  - applies_to:   {9} \n" 
                "  - accepts:      {10} "
               )

        msg = msg.format(   self.handle, 
                            self.name, 
                            self.description, 
                            self.value_limit, 
                            self.unit, 
                            self.type,
                            self.id,
                            appended,
                            self.value_prefix,
                            self.applies_to,
                            self.accepts
                        )       
        return msg    







class RecordClassDefinition():
    def __init__(self, app):
        self.app = app

        self.id = 0
        self.handle = ""
        self.name = ""
        self.type = "object"
        self.description = ""
        self.appended = False
        self.unit = ""
        self.value_prefix = ""
        self.value_limit = ""
        self.applies_to = ""
        self.accepts = ""   

        self.url = ""

    def create(self):
        def fail_create():
            self.app.end_step("RecordClass creation failed. {}".format(self.url), 
                              failure=True, blockend=True
                             )
            return False

        self.app.begin_step ("Starting record_class creation {}.".format(self.url))

        # Check if input is sufficient for record creation / correct
        self.app.begin_step ("Checking input.")        

        if self.precreate_check () == False:
            self.app.end_step ("Check failed.", failure=True)   
            return fail_create()

        self.app.end_step ("Input OK.")   
        
        # Fill in missing values, with logical alternatives
        self.app.begin_step ("Filling in missing values.")        

        if self.fill_in_auto_values () == False:
            self.app.end_step ("An error occurred.", failure=True)   
            return fail_create()

        self.app.end_step ("Finished.")   

        # Create RecordClass
        class_id = self.write_to_database()
        if class_id != False:
            self.app.end_step("RecordClass creation succeeded", blockend=True)
            self.id = class_id
            return True
        else:
            return fail_create()          

    def precreate_check(self):
        """ Checks all prerequisites prior to creation """

        # Check if handle is set
        if self.handle == "":
            return self.app.fail("Handle has not been set.")

        # Check that url is unique
        if self.app.get_record_class_id(self.handle) != False:
            return self.app.fail("Class '{}' already exists.".format(self.handle))
                          
        return True

    def fill_in_auto_values(self):
        """ Fills in missing values with sensible values """ 

        if self.name == "":
            self.name = self.handle.capitalize()

        if self.type in ['linked-object', 'value', 'alias']:
            self.appended = True
        
        return True

    def write_to_database(self):
        # Compile query
        query = "INSERT INTO classes "\
                "(handle, name, type, description, appended, " \
                "unit, value_prefix, value_limit, applies_to, "\
                "accepts) " \
                "VALUES ('{}', '{}', '{}', '{}', {}, '{}', '{}', '{}', '{}', '{}');" \
                .format(self.handle, self.name, self.type, self.description,
                 int(self.appended), self.unit, self.value_prefix, self.value_limit,
                 self.applies_to, self.accepts)
                 
        # Run query & get id
        r = self.app.db.run(query)
        row_id = self.app.db.cursor.lastrowid

        # Check if error occurred
        if r == False:
            return False

        return row_id