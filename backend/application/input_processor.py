import re

class Command():
    def __init__(self, app):
        self.app = app
        self.print = app.print

        self.line = 0
        self.action = ""

        self.type_handle = ""
        self.type_name = ""
        self.type_description = ""
        self.type_value_limit = ""
        self.type_data_type = ""
        self.type_unit = ""

        self.object_handle = ""
        self.object_value = ""
        self.object_type = ""
        self.object_property_handles = ""
        self.ud_values = []  # user-defined values. [(type_handle, value), ...]

    def execute(self):
        # CREATE TYPE
        # -------------------------------------------------------------
        if self.action == "new_type":

            # Create udv object type if data_type is "value"
            if self.type_data_type == "value":
                self.app.udv.new(self.type_handle,
                                 self.type_name,
                                 self.type_description,
                                 self.type_value_limit,
                                 self.type_data_type,                                            
                                 self.type_unit)
            else:
                # Create general object type
                self.app.create_type(self.type_handle, 
                                        self.type_name, 
                                        self.type_description, 
                                        self.type_value_limit,
                                        self.type_data_type,
                                        self.type_unit)

        # CREATE OBJECT
        # -------------------------------------------------------------
        elif self.action == "new_object":
            # Create object
            obj_id = self.app.create_object(self.object_type, 
                                            self.object_handle,
                                            self.object_value)
            obj_url = self.object_type + "/" + self.object_handle

            # Link properties
            if self.object_property_handles != "":
                property_handles = self.app.csl_to_list(self.object_property_handles)
                for ph in property_handles:
                    self.app.add_property(ph, obj_url)

            # set user-defined values
            for udv in self.ud_values:
                type_handle = udv[0]
                value = udv[1]
                self.app.udv.set_ud_value(obj_url, type_handle, value)

           
class Processor():
    def __init__(self, app):
        self.app = app
        self.print = app.print

    def process_input(self, input_file):
        # Globals
        command = Command(self.app)
        command_list = []
    
        def parse_command_line(line):
            # Input line example:
            # + [object] department/hr

            # PARSE LINE HEADING
            # ------------------------------------

            line = line.replace('+ ', '')
            # [object] department/hr

            # Get the value in between [] (the data type)
            result = re.search(r"\[([^\]]*)\]", line)
            if result is None:
                data_type = 'object'
            else:
                data_type = result.group(1)

            # remove [{{ data_type }}]
            result = re.search(r"(\[[^\]]*\])", line)
            if result is not None:
                bracket_box = result.group(1)
                line = line.replace(bracket_box, '')
            # department/hr

            # PARSE OBJECT
            # ------------------------------------
            # department/hr
            if '/' in line:
                command.action = "new_object"
                args = line.split("/")
                command.object_type = args[0]
                command.object_handle = args[1]

            # PARSE TYPE
            # ------------------------------------
            # + department
            else:
                command.action = "new_type"
                command.type_handle = line.strip()
                command.type_data_type = data_type

        def parse_attributes(line):
            # LINK OBJECTS TO OBJECT
            # department/hr
            if ": " not in line: 
                # an object is being linked, add it's url (the line) to the list
                command.object_property_handles += (line + ", ")
                return
            
            # SET VALUE
            # "attribute: value"
            else:                
                attribute, value = line.split(": ")

            attribute = attribute.strip()
            value = value.strip()

            # BUILT-IN VALUES
            if attribute == 'name':
                command.type_name = value
            if attribute == 'value':
                command.object_value = value
            elif attribute == 'description':
                command.type_description = value
            elif attribute == 'value_limit':
                command.type_value_limit = value
            elif attribute == 'unit':
                command.type_unit = value

            # USER-DEFINED VALUES
            else:
                command.ud_values.append((attribute, value))

            return

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

                if line[0] == '+':
                    # Line started with '+', this is a new command
                    # previous command has ended, execute it
                    if command.action != "":
                        command.execute()
                        command = Command(self.app)
                    # parse new command
                    parse_command_line(line)
                    command.line = i
                else:
                    # Line did not start with '+', this line is an attribute
                    parse_attributes(line)

            # EOF
            command.execute()
        
        return
