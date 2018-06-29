import pyodbc
import user as u


class UserDB:

    def __init__(self, connection_string):
        self.connection_string = connection_string

        self.cursor, self.cnxn = self.__connect_database()

    def __connect_database(self):
        cnxn = pyodbc.connect(self.connection_string, autocommit=True)
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
