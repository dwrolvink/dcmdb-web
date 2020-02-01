from .config import config 
import inspect
from pprint import pprint

from .application.printer import Printer
from .application.input_processor import Processor
from .application.sqlite_engine import DatabaseEngine

from .classes.record import Record, RecordDefinition
from .classes.record_class import RecordClass, RecordClassDefinition

class App():
    def __init__(self):
        # Init config
        self.config = config
        
        # Init Printer
        self.print = Printer(app=self)
        self.begin_step = self.print.begin_step
        self.end_step = self.print.end_step
        self.debug = self.print.debug
        self.error = self.print.error

        # Init Database helper class
        self.db = DatabaseEngine(db_url=self.config["database_file"], app=self)

        # Load types into context so they are accessible without imports
        self.Record = Record
        self.RecordDefinition = RecordDefinition
        self.RecordClass = RecordClass
        self.RecordClassDefinition = RecordClassDefinition        

    def get_record_class(self, class_id):
        query = "SELECT * FROM classes WHERE id = {}".format(class_id)   
        row = self.db.fetch_one(query)

        if row is None or row is False:
            return False

        return RecordClass(self, class_id)

    def get_all_record_classes(self):
        query = "SELECT * FROM classes"
        return self.get_object_list(query, RecordClass)      

    def exists_record(self, record_id):
        query = "SELECT * FROM records WHERE id = {}".format(record_id)   
        row = self.db.fetch_one(query)
        if row is None or row is False:
            return False      
        elif row[0] == record_id:
            return True
        return False

    def get_record(self, record_id):
        if self.exists_record(record_id):
            return Record(self, record_id)    
        return False

    def get_all_records(self):
        query = "SELECT * FROM records"  
        rows = self.db.fetch_all(query)

        if rows is None or rows is False:
            return False      

        output = []
        for row in rows:
            output.append(Record(self, row[0]))

        return output        

    def get_records(self, class_handle):
        rc = self.get(class_handle)
        return rc.records()    

    gr = get_record
    grs = get_records
    grc = get_record_class

    def get_record_class_id(self, class_handle):
        query = "SELECT id FROM classes WHERE handle = '{}';".format(class_handle)
        row = self.db.fetch_one(query)
        if row:
            return row[0]
        return False

    def get_record_id(self, class_handle, record_handle):
        class_id = self.get_record_class_id(class_handle)
        query = "SELECT id FROM records WHERE handle = '{}' AND class_id = {};" \
                .format(record_handle, class_id)

        row = self.db.fetch_one(query)
        if row:
            return row[0]  
        return False

    def get_record_id_by_url(self, short_url):
        class_handle, record_handle = short_url.split("/")
        return self.get_record_id(class_handle, record_handle)        
        
    def fail(self, error_message):
        """ Easy way to signal errors and quit functions. """

        # Get the name of the function that just had an error (the caller):
        func = inspect.stack()[1][3]

        # Write error 
        self.error(func + "(): " + error_message)

        # Return false so that we can say: return self.fail("big oof")
        return False

    def get_object_list(self, query, ObjectClass):
        """
            Returns a list of ObjectClass, based on the results of the query.
            Query needs to select id as first column.
            The ObjectClass needs to accept only App and object_id.
            Objectclass is expected to init itself using its object_id.
            If no rows are found, an empty list is returned.
        """

        # Query database
        query_result = self.db.fetch_all(query)


        # Compile list
        object_list = []
        for row in query_result:
            # Get object_id
            obj_id = row[0]
            # Create object
            obj = ObjectClass(self, obj_id)
            # Add to list
            object_list.append(obj)

        # Return list
        return object_list

    def get(self, url):
        """
            ch --> return list of records of class=ch
                rh --> return record of class=ch, and handle=rh (rec1)
                id --> return record with id=id (rec1)
                    ch2 --> return list of records where parent=rec1, and class=ch2
                        rh2 --> return record of class=ch, and handle=rh (rec1)
            
            rinse and repeat
        """

        # Pre-execution checks on url
        # -------------------------------------------------------------
        # Test for empty url
        if url == "":
            return self.fail("URL is empty.")

        # Remove class/ prefix if present
        url = url.replace("class/","")

        # Split url into segment list
        segments = url.split("/")
        segments = list(filter(None, segments)) # remove empty members

        # Test for mode
        if len(segments) == 1:
            mode = "get_class"
        elif len(segments) % 2 == 0:
            mode = "get_record"
        elif len(segments) % 3 == 0:
            mode = "get_children"

        if mode == "get_class":
            rc_id = self.get_record_class_id(segments[0])
            return RecordClass(self, rc_id)
            
        if mode == "get_record":
            rec_id = self.get_record_id(segments[-2], segments[-1])
            return self.get_record(rec_id)

        if mode == "get_children":
            rec_id = self.get_record_id(segments[-3], segments[-2])
            rec = self.get_record(rec_id)

            class_handle = segments[-1]
            properties = rec.properties()
            return [a for a in properties if a.record_class.handle == class_handle ]

 
        # Shouldn't end up here
        return self.fail("Unexpected fall-through")

    def csl_to_list(self, csl):
        """ Converts a string like "a, b" to a list like ['a', 'b'] """
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


 



