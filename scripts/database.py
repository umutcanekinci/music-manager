#-# Import Packages #-#
import sqlite3
import sys
from os import path, makedirs

#-# Database Class #-#
class Database():

    def __init__(self, name):

        self.name = name
    
    def Connect(self) -> bool:
        
        try:
        
            if not path.exists('databases/'):

                makedirs('databases/')

            self.connection = sqlite3.connect(("databases/" + self.name + ".db")) 

        except Exception as error:
            
            print("==> Failed to connect to database!", error)

            return False
        
        else:

            return True
        
    def GetCursor(self):

        return self.connection.cursor()
    
    def Execute(self, sql):
        
        try:
            
            return self.GetCursor().execute(sql)
            
        except Exception as error:

            print("An error occured during execute sql code:", error)
            
            return sys.exit()

    def Commit(self):

        self.connection.commit()

    def Disconnect(self):

        self.connection.close()
