class Printer():
    def __init__(self, app):
        self.app = app
        self.step_index = 0

        self.padding_prefix = "  "
        self.begin_prefix = "> "
        self.fail_prefix = "# "
        self.end_prefix  = "+ "
        self.prefix = ""

        self.error_list = []

    # Printing is done with two concepts: steps, and verbosity.
    # Desired verbosity level can be set in the app config.
    # Errors are always level 1, step messages are level 2, and the rest
    # is level 3. If verbosity level 0 is given in the settings, nothing
    # will be printed, even if this level is passed into a print function.
    # 
    # Steps can be begun and ended, all the messages in between will be
    # shifted to the right by the padding prefix. This allows logical blocks of
    # messages to be formed.
    #
    # Using self.print() directly will be level 3 by default.

    def begin_step(self, message, bar=False):
        verbosity = 2 # step messages are always level 2
        
        if bar == False:
            self.prefix = self.begin_prefix

        self.print(message, verbosity)

        if bar:
            self.print( "-" * (len(message)) )

        self.step_index += 1

    def end_step(self, message, failure=False, blockend=False, bar=False):
        verbosity = 2 # step messages are always level 2
        self.step_index -= 1

        if bar:
            self.print( "-" * (len(message)) )
        else:
            self.prefix = self.end_prefix
        
        if failure:
            self.prefix = self.fail_prefix
            self.error_list.append(message)
        
        self.print(message, verbosity)

        if blockend:
            self.blockspacer(verbosity)

    def blockspacer(self, verbosity):
        self.print("", verbosity)
        
    def error(self, message):
        verbosity = 1 # errors are always level 1
        message = "ERROR: " + message 
        self.error_list.append(message)
        self.print(message, verbosity)

    def tip(self, message):
        verbosity = 1 # errors are always level 1
        message = "TIP: " + message 
        self.print(message, verbosity)        

    def debug(self, message):
        verbosity = 3
        self.print(message, verbosity)

    def dump_errors(self):
        for e in self.error_list:
            self.print(e)
        self.error_list = []
        
    def print(self, message, verbosity=3):
        if self.app.config["verbosity"] == 0:
            return
        if verbosity > self.app.config["verbosity"]:
            return
        prefix = (self.padding_prefix * self.step_index) + self.prefix
        m = prefix + message
        print(m)
        self.prefix = ""
        return