# removes current database, and creates a new fresh one
def run(app):
    # delete current database
    app.db.remove_database_file()

    # create tables
    # lists
    query1 = "CREATE TABLE lists (id integer primary key autoincrement, " \
            "name text UNIQUE, type text, value text); \n"
    

    # object_types
    query2 = ("CREATE TABLE object_types " 
            "(id integer primary key autoincrement, handle text UNIQUE, name text, " \
            "description text, value_limit text); \n")

    # objects
    query3 = ("CREATE TABLE objects " 
            "(id integer primary key autoincrement, type int, " \
            "handle text UNIQUE, value text, properties text, members text);")
    
    app.db.run((query1, query2, query3))
