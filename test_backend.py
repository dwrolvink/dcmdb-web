from backend.app import App
app = App()

# Import scripts
import backend.scripts.reset_database 

# Reset database
app.print.begin_step("Removing and recreating database")
backend.scripts.reset_database.run(app)
app.print.end_step("Done.")

app.process_input("backend/data/input.stid")
#app.print_object_tree("computer/srv-001")
#print(repr(app.get("dep_location")))

ots = app.get_all_object_types()
for ot in ots:
    print(repr(ot))
