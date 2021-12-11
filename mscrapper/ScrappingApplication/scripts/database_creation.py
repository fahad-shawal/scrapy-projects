import sqlite3

from sqlite3 import Error


class DataBase:
    DB_PATH = '../database/movies.db'
    QUARIES = [
        ('Movies', """CREATE TABLE IF NOT EXISTS movies_tbl (
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    name text,
                                    hash text,
                                    pdf_path text);"""
        ),
    ]

    def connect(self):
        """ create a database connection to a SQLite database """

        try:
            conn = sqlite3.connect(self.DB_PATH)
            print ("Connected Successfully With Database!")
        except Error as e:
            print ("There is an error in creating Database File")
            print(e)
        
        return conn

    def create_tables(self, conn):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        for tbl_name, query in self.QUARIES:
            try:
                c = conn.cursor()
                c.execute(query)
                print(f"{tbl_name} Table is created!")
            except Error as e:
                print(f"Unabele to create {tbl_name} Table due to {e}")

    def runner(self):
        conn = self.connect()
        self.create_tables(conn)
        conn.close()


if __name__ == '__main__':
    db = DataBase()
    db.runner()
    