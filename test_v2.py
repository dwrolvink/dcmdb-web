from backend.app import App
"""
    Deletes the database, and creates a new empty one.
    Then it fills the database with data from the input file.
"""

# CONFIG
# ----------------------------------------------
input_file = "backend/data/input.stid"


# INIT
# ----------------------------------------------
app = App()


# Import scripts
import backend.scripts.reset_database 


# CREATE EMPTY DATABASE
# ----------------------------------------------
app.print.begin_step("Removing and recreating database")
backend.scripts.reset_database.run(app)
app.print.end_step("Done.")

# # LOAD IN DATA
# # ----------------------------------------------
# app.process_input("backend/data/input.stid")

# # ERROR SUMMARY
# # ----------------------------------------------
# app.print.debug("Completed with errors (if any):" \
#                  "\n-------------------------------")
# app.print.dump_errors()

rcd = app.RecordClassDefinition(app)
rcd.handle = "computer"
rcd.name = "Computer"
rcd.description = "Can be either a server or a desktop."
rcd.accepts = "bleh, bla"
rcd.create()

rd = app.RecordDefinition(app)
rd.class_id = rcd.id
rd.handle = "srv001"
rd.create()

rc = app.get_record_class(rcd.id)
rc.print()

rec = app.get_record(rd.id)
rec.print()