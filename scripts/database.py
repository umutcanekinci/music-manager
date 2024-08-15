#-# Import Packages #-#
from sqlite3 import connect
from os import path, makedirs

#-# Database Class #-#
class Database():

    def __init__(self, name) -> None:

        self.name = name
    
    def Connect(self) -> bool:
        
        try:
        
            if not path.exists('databases/'):

                makedirs('databases/')

            self.connection = connect(("databases/" + self.name + ".db")) 

        except Exception as error:
            
            print("==> Failed to connect to database!", error)

            return False
        
        else:

            return True
        
    def GetCursor(self) -> None:

        return self.connection.cursor()
    
    def Execute(self, sql, *paramaters) -> None:
        
        try:
            
            return self.GetCursor().execute(sql, paramaters)
            
        except Exception as error:

            print("An error occured during execute sql code:", error)
            
            return 

    def Commit(self) -> None:

        self.connection.commit()

    def Disconnect(self) -> None:

        self.connection.close()