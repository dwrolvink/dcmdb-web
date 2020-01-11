# call:
# python main.py {{ db_name }}

import sys
from app import App

# Collect commandline args
# ---------------------------------------------------------------------
table_name = 'test'
if (len(sys.argv) > 1):
    table_name = sys.argv[1]

# Init
# ---------------------------------------------------------------------
# Create App
app = App()

# Import scripts
import scripts.reset_database


# Toggles
# ---------------------------------------------------------------------
if table_name == '_cleanse':
    app.print.begin_step("Removing and recreating database")
    scripts.reset_database.run(app)
    app.print.end_step("Done.")
    exit()

