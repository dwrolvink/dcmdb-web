# removes current database, and creates a new fresh one
def run(app):
    # delete current database
    app.db.remove_database_file()

    # create tables
    # lists
    query1 = "CREATE TABLE lists (id integer primary key autoincrement, " \
            "name text UNIQUE, type text, value text); \n"
    

    # object_types
    query2 = ("CREATE TABLE classes " 
            "(id integer primary key autoincrement, handle text UNIQUE, name text, " \
            "type text, description text, appended integer, unit text, value_prefix, "\
            "value_limit text, applies_to text, accepts text);")
   

    # objects
    query3 = ("CREATE TABLE records " 
            "(id integer primary key autoincrement, class_id int, " \
            "handle text, label text, value text, target_id int, " \
            "alias_src_id int, alias_dst_id int);")

    # relationships
    query4 = ("CREATE TABLE relationships " 
            "(id integer primary key autoincrement, object_id integer, parent_id integer);")  
    
    # User-defined values
    query5 = ("CREATE TABLE udvs " 
            "(id integer primary key autoincrement, object_id integer, udv text);")      
    app.db.run((query1, query2, query3, query4, query5))
