import pyodbc
import user as u
import logging


__current_DBProvider = None


def get_dbprovider(connection_string):
    global __current_DBProvider
    if __current_DBProvider is not None:
        logging.ERROR("Cannot create more then one DBProvider")
        raise NotImplementedError
    __current_DBProvider = DBProvider(connection_string)
    return __current_DBProvider


def save_tiem_entrie_db(user_id, issue_id, hours, comment, date_time, sended):
    global __current_DBProvider
    __current_DBProvider.save_time_entries(user_id, issue_id, hours, comment, date_time, sended)


class DBProvider:

    def __init__(self, connection_string):
        self.connection_string = connection_string

        self.cursor, self.cnxn = self.__connect_database()
        self.__create_databases()

    def __connect_database(self):
        try:
            cnxn = pyodbc.connect(self.connection_string, autocommit=True)
            cursor = cnxn.cursor()
        except Exception as e:
            logging.exception("Cannot connect to databases")
            raise e
        return cursor, cnxn

    def __create_databases(self):
        try:
            self.cursor.execute(DBProvider.__create_tables_request)
        except Exception as e:
            logging.exception("Cannot create tables")
            raise e

    def save_user(self, user: u.User):
        try:
            self.cursor.execute("INSERT INTO [User]([user_id],[status],[api_key],[issue_id],[issue_start_time]"
                                ",[issue_pause_start_time],[pause_summary])"
                                "VALUES({}, {}, {}, {}, {}, {}, {})"
                                .format(user.user_id, user.status.value, user.api_key, user.issue_id,
                                                              user.issue_start_time,
                                                              user.issue_pause_start_time, user.pause_summary))
        except Exception as e:
            logging.exception("Cannot save user")
            raise e

    def update_user(self, user: u.User):
        try:
            self.cursor.execute("UPDATE [User] SET status={}, api_key='{}', issue_id={}, "
                                "issue_start_time={}, issue_pause_start_time={}, pause_summary={}"
                                " Where user_id = {}".format(user.status.value, user.api_key, user.issue_id, user.issue_start_time,
                                                              user.issue_pause_start_time, user.pause_summary, user.user_id))
        except Exception as e:
            logging.exception("Cannot update user")
            raise e

    def get_user(self, user_id):
        try:
            self.cursor.execute("SELECT * FROM [User] WHERE user_id = {}".format(user_id))
            responce = self.cursor.fetchone()

            if responce is None:
                return None

            user = u.User(user_id=responce[0],
                          status=u.UserState(responce[1]),
                          api_key=responce[2],
                          issue_id=responce[3],
                          issue_start_time=responce[4],
                          issue_pause_start_time=responce[5],
                          pause_summary=responce[6])
        except Exception as e:
            logging.exception("Cannot get user")
            raise e
        return user

    def save_time_entries(self, user_id, issue_id, hours, comment, date_time, sended):
        try:
            self.cursor.execute("""
                INSERT INTO dbo.[TimeEntrie] ([user_id], [issue_id], [hours], [comment], [date_time], [sended])
                VALUES ({}, {}, {}, {}, {}, {})
            """.format(user_id, issue_id, hours, comment, date_time, sended))
        except Exception as e:
            logging.exception("Cannot save time entries")
            raise e

    __create_tables_request = """
            IF NOT EXISTS (SELECT * FROM SYSOBJECTS WHERE NAME='User' AND xtype='U')
              CREATE TABLE dbo.[User] 
                (user_id int PRIMARY KEY NOT NULL,  
                status int NOT NULL,  
                api_key varchar(255) NULL,  
                issue_id int NOT NULL,
                issue_start_time float NOT NULL,
                issue_pause_start_time float NOT NULL,
                pause_summary float NOT NULL)  
              GO
              
            IF NOT EXISTS (SELECT * FROM SYSOBJECTS WHERE NAME='TimeEntrie' AND xtype='U')
              CREATE TABLE dbo.TimeEntrie  
                (time_entrie_id int PRIMARY KEY NOT NULL IDENTITY(1,1),  
                user_id int NOT NULL,
                issue_id int NOT NULL,
                hours float NOT NULL,
                comment varchar(255) NULL,
                date_time datetime NOT NULL,
                sended bit NOT NULL)  
              GO
        """
