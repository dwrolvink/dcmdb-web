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

# LOAD IN DATA
# ----------------------------------------------
app.process_input("backend/data/input.stid")

# ERROR SUMMARY
# ----------------------------------------------
if len(app.print.error_list):
    app.print.debug("Completed with errors:" \
                    "\n-------------------------------")
    app.print.dump_errors()



