from pprint import pprint
from collections import OrderedDict
import inspect

class AttributeDataClass():
    def print(self):
        attrs = vars(self)
        pprint(attrs)

    def set_attr(self, name, value, list=True):
        if hasattr(self, name) == False:
            setattr(self, name, [value])
        else:
            setattr(self, name, getattr(self, name) + [value])

            
class Record():
    def __init__(self, app, record_id):
        self.app = app

        if record_id == 0:
            print(inspect.stack()[1][3])

        query = "SELECT * FROM records WHERE id = {}".format(record_id)   
        row = self.app.db.fetch_one(query)


        self.id = row[0]
        self.class_id = row[1]
        self.handle = row[2]
        self.label = row[3]
        self.value = row[4]     

        self.target_id = row[5]
        self.alias_src_id = row[6]
        self.alias_dst_id = row[7]

        self.record_class = self.app.get_record_class(self.class_id)
        self.class_name = self.record_class.name
        self.class_type = self.record_class.type
        self.class_handle = self.record_class.handle
        self.unit = self.record_class.unit

        # Properties
        self.property_table = False
        self.property_list = False
        self.member_table_save = False
        self.member_list_save = False
        self.custom_attribute_list = False

        self.target_obj = False

        # alias
        self.alias_src = False
        self.alias_dst = False

        if self.alias_src_id:
            self.alias_src = self.app.get_record(self.alias_src_id)
        if self.alias_dst_id:
            self.alias_dst = self.app.get_record(self.alias_dst_id)                    
        
        # URL
        self.url = self.set_url()




    """
            API REPRESENTATION
    """


    def definition(self):

        """ Create a simple object that can be parsed by JSON """

        rc = self.record_class

        # Output
        defObj = OrderedDict()

        # Set values
        defObj['id'] = self.id
        defObj['label'] = self.label 
        defObj['url'] = self.url
        if self.handle:
            defObj['handle'] = self.handle

        defObj['value'] = self.value

        if self.target:
            defObj['target'] = (self.target.id, self.target.label)

        defObj['class'] = rc.signature()

        defObj['properties'] = {}
        for property in self.list:

            value_list = property[1]
            property_name = property[0]

            if type(value_list[0]) == Record:
                defObj['properties'][property_name] = []

                for r in value_list:
                    if r.value != "":
                        defObj['properties'][property_name].append({'value':r.value, 'unit':r.unit})
                    else:
                        defObj['properties'][property_name].append(r.signature())
                    

        defObj['parents'] = [r.signature() for r in self.properties()]
        defObj['members']    = [r.signature() for r in self.members()]

        
            
        return defObj

    def signature(self):
        """ this is how this record is represented in the definitions of 
            other records """
        return {
                    'id':self.id, 
                    'url':self.url, 
                    'label':self.label, 
                    'value':self.value
                }




    """
            GETTTERS / SETTERS
    """

    @property
    def target(self): 
        if self.target_obj:
            return self.target_obj

        if self.target_id:
            self.target_obj = self.app.get_record(self.target_id)    

        return self.target_obj

    @property
    def type(self):
        return self.class_type    

    @property
    def table(self):
        self.get_property_table()
        return self.property_table

    

    def properties(self):
        # Get all records
        query = "SELECT parent_id FROM relationships WHERE object_id = {}".format(self.id) 
        return self.app.get_object_list(query, Record)   

    def members(self):
        query = "SELECT object_id FROM relationships WHERE parent_id = {}".format(self.id)   
        return self.app.get_object_list(query, Record) 



    @property
    def list(self):

        """
        Gets all properties (from self.properties() and values like self.id
        and returns it as a list. See get_property_table() for more information.
        """

        # Only do this work once
        if self.property_list != False:
            return self.property_list
        
        # Compile a list of all the attributes in the self.table object
        prop_list = [   a for a in dir(self.table) 
                        if not a.startswith('__') 
                        and not callable(getattr(self.table, a))
                    ]

        # Make a tupled list (property_name, value)
        prop_value_list = []
        for prop in prop_list:
            prop_value_list.append((prop, getattr(self.table, prop)))

        self.property_list = prop_value_list
        return self.property_list

    @property
    def custom_attributes(self):

        """
        This creates a subset of self.list, leaving out the self-set variables.
        This is mostly useful for view functions. For internal functions, consider
        self.properties() instead.
        """
        if self.custom_attribute_list != False:
            return self.custom_attribute_list
 
        noncustom = ['id', 'type', 'label', 'url', 'value', 
                        'target', 'alias_src', 'alias_dst']

        self.custom_attribute_list = [p for p in self.list 
                                        if p[0] not in noncustom]
        return self.custom_attribute_list        

    def get_property_table(self):

        """
        Creates an Object that has all the properties of this object as
        attributes. This consolidates child
        relationships (like "telephone number"), with selfset properties, like
        label and id, into one simple structure.
        """

        if self.property_table != False:
            return

        pd = AttributeDataClass()

        # Simple general attributes
        pd.set_attr('id', self.id, list=False) 
        pd.set_attr('type', self.type, list=False) 
        pd.set_attr('label', self.label, list=False) 
        pd.set_attr('url', self.url, list=False) 
        pd.set_attr('value', self.value, list=False) 
  
        # Simple common attributes
        if self.target_obj:
            pd.set_attr('target', self.target_obj, list=False)
        if self.alias_src:
            pd.set_attr('alias_src', self.alias_src, list=False)  
        if self.alias_dst:
            pd.set_attr('alias_dst', self.alias_dst, list=False)         

        # Listed custom attributes
        for p in self.properties():
            pd.set_attr(p.record_class.handle, p)                           
    
        self.property_table = pd
        


    @property
    def member_list(self):
        if self.member_list_save != False:
            return self.member_list_save
        
        member_list = [   a for a in dir(self.member_table) 
                        if not a.startswith('__') 
                        and not callable(getattr(self.member_table, a))
                    ]

        member_value_list = []
        for member in member_list:
            member_value_list.append((member, getattr(self.member_table, member)))

        self.member_list_save = member_value_list
        return self.member_list_save



    @property
    def member_table(self):
        return self.get_member_table()        

    def get_member_table(self):
        if self.member_table_save != False:
            return self.member_table_save

        pd = AttributeDataClass()
        members = self.get_members()
       
        # Listed custom attributes
        for p in members:
            if p.record_class.type == 'object':
                pd.set_attr(p.record_class.handle, p)
            else:
                pd.set_attr(p.record_class.handle, p)
               
        self.member_table_save = pd

        return self.member_table_save


    def set_url(self):
        rc = self.record_class
        url = ""

        # Get url for the appended case
        if self.record_class.appended == True:
            # alias
            if self.alias_dst:
                return self.alias_dst.url + "/" + rc.handle + "/" + str(self.id)
            # linked-object
            elif self.target:
                return self.target.url + "/" + rc.handle + "/" + str(self.id)
        
        # Non-appended
        if self.handle:
            return (self.record_class.url + "/" + self.handle)
        
        return (self.record_class.url + "/" + str(self.id))

    def add_valued_property(self, class_handle, value):
        # Create record
        rec = self.app.RecordDefinition(self.app)
        rec.class_handle = class_handle
        rec.value = value
        rec.url = self.url + "/" + class_handle
        rec.create()

        # Set udv as property
        self.add_property(rec.id)        

    def add_member(self, member_id):
        member = self.app.get_record(member_id)
        return member.add_property(self.id)

    def add_property(self, record_id):
        
        # Test if record is already set as property
        query = "SELECT * FROM relationships " \
                "WHERE object_id = {} AND parent_id = {}" \
                .format(self.id, record_id)

        result = self.app.db.fetch_one(query) 
        if result == False or result is not None:
            self.app.print.error("Property is already set.")
            return False

        # Test if this property is a member of this object
        query = "SELECT * FROM relationships " \
                "WHERE object_id = {} AND parent_id = {}" \
                .format(record_id, self.id)     

        result = self.app.db.fetch_one(query) 
        if result == False or result is not None:
            self.app.print.error("Property is already a member.")
            return False            

        # Test if we're trying to set an object to itself
        if self.id == record_id:
            self.app.print.error("Can't set object as property of itself.")
            return False

        # execute
        query = "INSERT INTO relationships (object_id, parent_id) "
        query += "VALUES('%s', '%s')" % (self.id, record_id)

        # Set target value of added object if applicable
        rec = self.app.get_record(record_id)
        if rec.record_class.type == "value":
            rec.set_target(self.id)

        # Return true (=success) if query succeeded
        return self.app.db.run(query)   
        
    def set_target(self, record_id):
        query = "UPDATE records SET target_id = {} WHERE id = {};" \
                .format(record_id, self.id)
        return self.app.db.run(query) 

    def print(self):
        msg = (
                "\n"
                "{2} \n"               
                "  - id:           {0} \n"
                "  - handle:       {1} \n"                 
                "  - url:          {2} \n"
                "  - class_type:   {3} \n"      
                "  - label:        {4} \n"                
                "  - value:        {5} \n"                              
                "  - class_id:     {6} \n"
                "  - class_handle  {7} \n"
              )

        msg = msg.format(   self.id, 
                            self.handle, 
                            self.url, 
                            self.class_type,
                            self.label,
                            self.value,
                            self.class_id, 
                            self.class_handle
                        )       
        print(msg)

    def __repr__(self):  
        if self.record_class.type == "value":
            return ("<"+self.record_class.handle + ' [' + self.value + ', ' + self.record_class.unit + '] ' + "({})".format(self.id) + ">")
        return "<"+self.url + " ({})".format(self.id) + ">"


class RecordDefinition():
    """ Allows one to easily define a new record, then check/process 
        the input, and finally write the record to the database. 
    """

    def __init__(self, app):
        self.app = app
        self.print = app.print

        self.class_id     = 0
        self.class_handle = ""
        self.handle       = ""
        self.label        = ""
        self.value        = ""  

        # linked-object
        self.target_id = 0
        self.target_url = ""

        # alias
        self.alias_src_id = 0
        self.alias_dst_id = 0
        self.alias_src_url = ""
        self.alias_dst_url = ""       

        self.record_class = False  # Set by self.precreate_check()
        

        self.url = ""


    def create(self):
        def fail_create():
            self.app.end_step("Record creation failed", failure=True)
            return False

        self.app.begin_step ("Starting record creation {}.".format(self.url))

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

        # Create Record
        record_id = self.write_to_database()
        if record_id != False:
            self.app.end_step("Record creation succeeded (id:{})".format(self.id), blockend=True)
            return record_id
        else:
            return fail_create() 
                    

    def precreate_check(self):
        """ Checks all prerequisites prior to creation """

        # Check if we set a class for this record
        if self.class_id == 0 and self.class_handle == "":
            return self.app.fail("You need to set either class_id or class_handle.")


        # Get record_class
        if self.class_id == 0:
            class_id = self.app.get_record_class_id(self.class_handle)
            self.class_id = class_id
        rc = self.app.get_record_class(self.class_id)
        self.record_class = rc

        # Check if we got a value back for rc
        if rc == False:
            return self.app.fail("Couldn't retrieve record_type.")

        # Print value to terminal if type=value
        if rc.type == "value":
            self.print.print("+ Value will be set to {}.".format(self.value), 2)
        # Check if we need target set
        if rc.type == 'linked-object':
            if self.target_id == 0 and self.target_url == "":
                return self.app.fail("You need to set either target_id "
                                     "or target_url for linked-objects.")     

        # Check if we need alias_src set
        # Check if we need alias_dst set
        if rc.type in ['alias']:
            if self.alias_src_id == 0 and self.alias_src_url == "":
                return self.app.fail("You need to set either alias_src_id "
                                     "or alias_src_url for alias objects.")              
            if self.alias_dst_id == 0 and self.alias_dst_url == "":
                return self.app.fail("You need to set either alias_dst_id "
                                     "or alias_dst_url for alias objects.")                   
        
        # Check if we need a handle
        if rc.type == 'object':
            # We need a handle, is it set?
            if self.handle == "":
                return self.app.fail("A record of type object needs a handle.")
            # We need a handle, is it unique?
            result = self.app.get('class/' + rc.handle + "/" + self.handle)
            if result != False:
                return self.app.fail("Handle is already in use.")

        # Check to see if the object that we're appending to exists
        if rc.type == 'linked-object':
            if self.target_id == 0:
                self.target_id = self.app.get(self.target_url).id 
            if self.target_id == False:
                return self.app.fail("Couldn't retrieve parent object.")

        # Check to see if the object that we're setting as property exists
        if rc.type in ['alias']:
            if self.alias_src_id == 0:
                self.alias_src_id = self.app.get(self.alias_src_url).id 
            if self.alias_src_id== False:
                return self.app.fail("Couldn't retrieve alias src object.")

            if self.alias_dst_id == 0:
                self.alias_dst_id = self.app.get(self.alias_dst_url).id 
            if self.alias_dst_id== False:
                return self.app.fail("Couldn't retrieve alias dst object.")                

        return True

    def fill_in_auto_values(self):
        """ Fills in missing values with sensible values """

        # Fill in label if it is empty
        if self.label == "":
            # If handle is set, use that as label
            if self.handle != "":
                self.label = self.handle
            # If handle is not set, this must be a record of type=text
            # use the record_class handle as label
            elif self.record_class.type in ["value", "linked-object", "alias"]:
                self.label = self.record_class.handle
            else:
                return self.app.fail("Handle is not set, and class type is not value or linked-object")

        # Fill in class_id if it isn't set
        if self.class_id == 0:
            self.class_id = self.app.record_manager.get_id(self.class_handle)
        
        return True

    def write_to_database(self):
        # CREATE RECORD
        # -------------------------
        # Compile query
        query = "INSERT INTO records (class_id, handle, label, value, target_id, alias_src_id, alias_dst_id) " \
                "VALUES('{}', '{}', '{}', '{}', {}, {}, {})" \
                .format(self.class_id, self.handle, self.label, self.value,
                        self.target_id, self.alias_src_id, self.alias_dst_id)

        # Run query & get id
        r = self.app.db.run(query)
        row_id = self.app.db.cursor.lastrowid

        # Check if error occurred
        if r == False:
            return False

        self.id = row_id

        # LINK OBJECT
        # -------------------------
        if self.record_class.type == "linked-object":
            query = "INSERT INTO relationships (object_id, parent_id) " \
                    "VALUES ({}, {});".format(self.target_id, self.id)

            if self.app.db.run(query) == False:
                return False

        # ALIAS
        # -------------------------
        if self.record_class.type == "alias":

            rec = self.app.get_record(self.alias_dst_id)

            self.print.begin_step("Setting {} as a property of {}." \
                                  .format(self.url, rec.url))

            # link alias to destination object (where the property shows up)
            query = "INSERT INTO relationships (object_id, parent_id) " \
                    "VALUES ({}, {});".format(self.alias_dst_id, self.id)

            if self.app.db.run(query) == False:
                return False

            query = "INSERT INTO relationships (object_id, parent_id) " \
                    "VALUES ({}, {});".format(self.id, self.alias_src_id)

            if self.app.db.run(query) == False:
                self.app.end_step("Couldn't set relationship.")
                return False

        self.app.end_step("Done.")
        return self.id





    