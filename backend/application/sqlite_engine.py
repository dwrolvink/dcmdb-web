import sqlite3
import os

class DatabaseEngine():
    def __init__(self, db_url, app):
        self.app = app
        self.print = app.print
        self.cursor = False
        self.connection = False
        self.url = db_url

    def connect(self):
        if self.connection == False:
            self.connection = sqlite3.connect(self.url)
            self.cursor = self.connection.cursor()

    def commit(self):
        self.connection.commit()


    def close_connection(self):
        self.connection.close()
        self.connection = False

    def remove_database_file(self):
        if os.path.exists(self.url):
            os.remove(self.url)        

    # use for create, update, delete
    # returns boolean denoting success of operation
    def run(self, query):

        try:
            self.connect()
            #self.print.debug("Connected to database")

            if type(query)==str:
                self.cursor.execute(query)
            else:
                for q in query:
                    self.cursor.execute(q)

            self.commit()
            self.cursor.close()

        except sqlite3.IntegrityError as error:
            self.app.fail("Failed to execute query: " + str(error))
            self.print.tip("Does the object already exist?")
            return False

        except sqlite3.Error as error:
            self.app.fail(str(error))
            self.print.debug(query)

        finally:
            if (self.connection):
                self.close_connection()
                #self.print.debug("The Sqlite connection is closed")

        return True

        

    # use when you expect one row from the database
    # returns row
    def fetch_one(self, query):
        self.connect()
        qr = self.cursor.execute(query)
        result = self.cursor.fetchone()
        self.commit()
        self.close_connection()
        return result  

    # use when you expect more than one row
    # returns list of rows
    def fetch_all(self, query):      
        self.connect()
        qr = self.cursor.execute(query)
        result = self.cursor.fetchall()
        self.commit()
        self.close_connection()
        return result             