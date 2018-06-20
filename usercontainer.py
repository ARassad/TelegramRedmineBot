import user as u
import pyodbc
import userDB as udb


class UserContainer:

    def __init__(self, user_db: udb.UserDB, soft_max_users=50):
        self.users = []
        self.userDB = user_db
        self.soft_max_users = soft_max_users

    def get_user(self, user_id):

        if len(self.users) > self.soft_max_users:
            self.remove_unused_users()

        user = [us for us in self.users if us.user_id == user_id]
        if len(user) == 0:
            user = self.userDB.get_user(user_id)

            if user is None:
                user = u.User(user_id)
                self.userDB.save_user(user)

            self.users.append(user)
        else:
            user = user[0]

        return user

    def update_user_to_bd(self, user_id):
        user = [us for us in self.users if us.user_id == user_id]
        if len(user) != 0:
            self.userDB.update_user(user[0])

    def remove_unused_users(self):
        unused_users = [us for us in self.users if us.status == u.UserState.free or us.status == u.UserState.unregister]
        for us in unused_users:
            self.users.remove(us)
