class Command():
    def __init__(self, app):
        self.app = app
        self.print = app.print

        self.line = 0
        self.action = ""
        self.ot_handle = ""
        self.ot_name = ""
        self.ot_description = ""
        self.ot_value_limit = ""
        self.oi_value = ""
        self.oi_object_type = ""
        self.oi_property_handles = ""

    def execute(self):
        if self.action == "new_object_type":
            # Create object type
            self.app.create_object_type(self.ot_handle, 
                                        self.ot_name, 
                                        self.ot_description, 
                                        self.ot_value_limit)
        elif self.action == "new_object_instance":
            # Create object instance
            obj_id = self.app.create_object(self.oi_object_type, self.oi_value)
            obj_url = self.oi_object_type + "/" + self.oi_value

            # Link properties
            if self.oi_property_handles != "":
                property_handles = self.app.csl_to_list(self.oi_property_handles)
                for ph in property_handles:
                    self.app.add_property(ph, obj_url)

           
class Processor():
    def __init__(self, app):
        self.app = app
        self.print = app.print

    def process_input(self, input_file):
        # Globals
        command = Command(self.app)
        command_list = []
    
        def parse_command_line(line):
            line = line.replace('+ ', '')

            # + department/hr
            if '/' in line:
                command.action = "new_object_instance"
                args = line.split("/")
                command.oi_object_type = args[0]
                command.oi_value = args[1]
            # + department
            else:
                command.action = "new_object_type"
                command.ot_handle = line

        def parse_attributes(line):
            if ": " not in line: # department/hr
                command.oi_property_handles += (line + ", ")
                return
            else:                # "attribute: value"
                attribute, value = line.split(": ")

            if attribute == 'name':
                command.ot_name = value
            elif attribute == 'description':
                command.ot_description = value
            elif attribute == 'value_limit':
                command.ot_value_limit = value

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
