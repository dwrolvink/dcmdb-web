import re
from pprint import pprint

class Command():
    def __init__(self, app):
        self.app = app
        self.print = app.print

        self.line = 0
        self.action = ""            # new_class, new_object
        self.record_type = "normal" # normal, linked-object      

        self.record_class_definition = self.app.RecordClassDefinition(self.app)
        self.record_definition = self.app.RecordDefinition(self.app)

        self.udvs = []       # [(class_handle, value)]
        self.properties = [] # [rec_url]


    def execute(self):
        if self.action == "new_class":
            rcid = self.record_class_definition.create()

        elif self.action == "new_record":
            rid = self.create_record()

        # Reset object
        self.__init__(self.app)
            

    def create_record(self):
        # Create record
        rid = self.record_definition.create()

        # Get record
        record = self.app.get_record(rid)

        # Set properties
        for p in self.properties:
            self.print.begin_step("Adding {} as a property to {}".format(p, record.url))

            # Get property_id
            property_id = self.app.get_record_id_by_short_url(p)
            if property_id == False:
                self.app.fail("Couldn't find {}.".format(p))
                self.print.end_step("Adding property {} failed.".format(p), failure=True, blockend=True)
                continue

            # Add property
            record.add_property(property_id)
            self.print.end_step("Done.", blockend=True)

        # Set UDV's
        for udv in self.udvs:
            # Create record
            class_handle = udv[0]
            value = udv[1]
            record.add_valued_property(class_handle, value)




class Processor():
    def __init__(self, app):
        self.app = app
        self.print = app.print

        self.command = Command(self.app)
        self.command_list = []


    def process_input(self, input_file):
        """ Go line by line through the input file, and parse the lines, and
            execute.
        """

        self.print.begin_step("Processing input from {}".format(input_file), bar=True)

        # Get root, for imports (if we have any)
        root = input_file.rsplit("/", 1)[0]

        with open(input_file) as f:
            # Load in all the lines and remove all whitespace before and after
            lines = [line.strip() for line in f]

            # Loop lines
            i = -1
            for line in lines:
                # Count what line we're on
                i += 1

                # skip empty lines / comments
                if line == "":
                    continue
                if line[0] == "#":
                    continue

                if line[0] == '>':
                    # Line started with '>', this is an import
                    line = line.replace("> ", "")
                    self.process_input(root+"/"+line)
                    continue

                if line[0] == '+':
                    # Line started with '+', this is a new command
                    # previous command has ended, execute it
                    if self.command.action != "":
                        self.command.execute()
                    # parse new command
                    self.parse_command_line(line)
                    self.command.line = i
                else:
                    # Line did not start with '+', this line is an attribute
                    self.parse_attributes(line)

            # EOF
            self.command.execute()
        
        self.print.end_step("Reached end of {}".format(input_file), blockend=True, bar=True)

        return

    def parse_command_line(self, line):

        # PARSE LINE HEADING
        # ------------------------------------

        # The use of '+' is to start a new command, this information
        # has already been used in process_input(), it can be removed now
        line = line.replace('+ ', '')
        
        # Test if the [data_type] prefix is present
        # If it is not present, this command line codes for a new record
        # otherwise it codes for a new class
        result = re.search(r"\[([^\]]*)\]", line)
        if result is None:
            self.command.action = "new_record"
        else:
            self.command.action = "new_class"
            self.command.record_class_definition.type = result.group(1)

        # remove [data_type] from line
        result = re.search(r"(\[[^\]]*\])", line)
        if result is not None:
            bracket_box = result.group(1)
            line = line.replace(bracket_box, '')
            line = line.strip()

        # Now we are left with the url of the object to be created
        url = line

        if self.command.action == "new_record":
            self.command.record_definition.url = url
            # Check if url is well formed:
            # - class_handle/object_handle
            # - class_handle/object_handle/prop_handle
            args = line.split("/")
            if len(args) < 2 or len(args) > 3:
                return self.app.fail("URL '{}' is malformed.".format(line))
                
            # Define new normal record
            if len(args) == 2:
                self.command.record_type = "object"
                self.command.record_definition.class_handle = args[0]
                self.command.record_definition.handle = args[1]

            if len(args) == 3:
                # Get rc to check if it's a linked-object or alias
                class_handle = args[2]
                rc_id = self.app.get_record_class_id(class_handle)
                if rc_id == False:
                    return self.app.fail("Couldn't retrieve class {}".format(class_handle))
                rc = self.app.get_record_class(rc_id)

                # alias
                if rc.type == "alias":
                    self.command.record_type = "alias"
                    self.command.record_definition.class_handle = args[2]
                    self.command.record_definition.alias_dst_url = "class/"+args[0]+"/"+args[1] 

                # linked-object
                elif rc.type == "linked-object":
                    self.command.record_type = "linked-object"
                    self.command.record_definition.class_handle = args[2]
                    self.command.record_definition.target_url = "class/"+args[0]+"/"+args[1]                                                        

        elif self.command.action == "new_class":
            self.command.record_class_definition.handle = line.strip()
            self.command.record_class_definition.url = url

    def parse_attributes(self, line):
        # LINK OBJECTS TO OBJECT
        # department/hr or -> department/hr
        if ": " not in line: 

            # -> denotes an alias. Aliases can only have one property
            if line[0:2] == "->":
                line = line.replace('->', '')
                line = line.strip()
                self.command.record_definition.alias_src_url = line
                return

            # an object is being linked, add it's url (the line) to the list
            self.command.properties.append(line)
            return
        
        # SET VALUE
        # "attribute: value"
        else:                
            attribute, value = line.split(": ")

        attribute = attribute.strip()
        value = value.strip()

        # BUILT-IN VALUES
        if attribute == 'label':
            self.command.record_definition.label = value    
        elif attribute == 'value':
            self.command.record_definition.value = value     

        elif attribute == 'name':
            self.command.record_class_definition.name = value
        elif attribute == 'description':
            self.command.record_class_definition.description = value
        elif attribute == 'value_limit':
            self.command.record_class_definition.value_limit = value
        elif attribute == 'unit':
            self.command.record_class_definition.unit = value
        elif attribute == 'prefix':
            self.command.record_class_definition.value_prefix = value            
        elif attribute == 'applies_to':
            self.command.record_class_definition.applies_to = value   
        elif attribute == 'accepts':
            self.command.record_class_definition.accepts = value                                                

        # USER-DEFINED VALUES
        else:
            self.command.udvs.append((attribute, value))

        return        
