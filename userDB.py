import pyodbc
import user as u

class UserDB:

    def __init__(self, server, database, driver, username=None, password=None):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.driver = driver

        self.cursor, self.cnxn = self.__connect_database()

    def __connect_database(self):

        if self.username is not None and self.password is not None:
            connection_string = 'DRIVER={};PORT=1433;SERVER={};PORT=1443;DATABASE={};UID={};PWD={}'\
                .format(self.driver, self.server, self.database, self.username, self.password)
        else:
            connection_string = 'DRIVER={};PORT=1433;SERVER={};PORT=1443;DATABASE={};Trusted_Connection=yes;'\
                .format(self.driver, self.server,self.database)

        cnxn = pyodbc.connect(connection_string, autocommit=True)
        cursor = cnxn.cursor()
        return cursor, cnxn

    def save_user(self, user: u.User):
        self.cursor.execute("INSERT INTO [User]([user_id],[status],[api_key],[issue_id],[issue_start_time]"
                            ",[issue_pause_start_time],[pause_summary])"
                            "VALUES({}, {}, {}, {}, {}, {}, {})"
                            .format(user.user_id, user.status.value, user.api_key, user.issue_id,
                                                          user.issue_start_time,
                                                          user.issue_pause_start_time, user.pause_summary))

    def update_user(self, user: u.User):
        self.cursor.execute("UPDATE [User] SET status={}, api_key='{}', issue_id={}, "
                            "issue_start_time={}, issue_pause_start_time={}, pause_summary={}"
                            " Where user_id = {}".format(user.status.value, user.api_key, user.issue_id, user.issue_start_time,
                                                          user.issue_pause_start_time, user.pause_summary, user.user_id))

    def get_user(self, user_id):
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

        return user
