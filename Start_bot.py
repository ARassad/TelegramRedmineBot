from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
import telegram as tel
import userDB as udb
import usercontainer as uc
import re
import config
import logging


Set_Api_Key_RE = "^/({})\s+(\S+)\s*$"
Begin_Time_Entries_RE = "^/({})\s+(\d+)\s*$"
End_Time_Entries_RE = "^/({})\s+(.{{1,255}})$"
Pause_Time_Entries_RE = "^/({})\s*$"
Continue_Time_Entries_RE = "^/({})\s*$"
Current_Issue_Info_RE = "^/({})\s*$"
Get_User_State_RE = "^/({})\s*$"
Feedback_RE = "^/({})\s+(.+)\s*$"
Commands_List_RE = "^/({})\s*$"
Drop_Issue_RE = "^/({})\s*$"
Create_Time_Entries_RE = "^/({})\s+(\d+)\s+(\d+\.\d+?)\s+(.{{1,255}})$"


class RedmineBot:

    commands_description_string = ""

    def __init__(self):
        logging.basicConfig(filename=config.LOG_FILE, level=logging.INFO)

        self.UserDb = udb.UserDB(config.CONNECTION_STRING)
        self.UserContainer = uc.UserContainer(self.UserDb)

        self.commands = RedmineBot.commands_with_re()
        RedmineBot.commands_description_string = RedmineBot.create_commands_description()

        self.updater = Updater(token=config.BOT_TOKEN, request_kwargs=RedmineBot.get_proxy_settings())
        self.dispatcher = self.updater.dispatcher
        handler = MessageHandler(Filters.command | Filters.text, self.process)
        self.dispatcher.add_handler(handler)

    def start(self):
        logging.info("Start")
        self.updater.start_polling()

    def process(self, bot: tel.Bot, update: tel.Update):
        user = self.UserContainer.get_user(update.effective_user.id)
        message = "Команда не распознана"
        logging.info("From ({} : {}) message  : {}"
                     .format(update.effective_user.id, update.effective_user.first_name, update.message.text))

        try:
            for command in self.commands:
                if re.match(command[0], update.message.text, re.MULTILINE | re.DOTALL):
                    matcher = re.search(command[0], update.message.text, re.MULTILINE | re.DOTALL)
                    message = command[1](user, matcher)
                    break

            self.send_message(bot, update, message)
            self.UserContainer.update_user_to_bd(user.user_id)

        except Exception:
            logging.exception("Exception")
            self.send_message(bot, update, "Во время выполнения команды произошла ошибка")

    @staticmethod
    def send_message(bot: tel.Bot, update: tel.Update, message):
        bot.send_message(update.message.chat.id, message)
        logging.info("Send to ({} : {}) message  : {}"
                     .format(update.effective_user.id, update.effective_user.first_name, message))

    @staticmethod
    def save_feedback(message):
        with open(config.FEEDBACK_FILE, "a", encoding="utf8") as f:
            f.write(message)
        return "Спасибо за отзыв"

    @staticmethod
    def commands_to_string(commands: list):
        return "".join([c + "|" for c in commands])[:-1]

    @staticmethod
    def commands_with_re():
        commands = list()
        c_to_s = RedmineBot.commands_to_string
        commands.append((Set_Api_Key_RE.format(c_to_s(config.SET_API_KEY_COMMANDS)),
                         lambda user, matcher: user.set_api_key(matcher.group(2))))
        commands.append((Begin_Time_Entries_RE.format(c_to_s(config.BEGIN_TIME_ENTRIES_COMMANDS)),
                         lambda user, matcher: user.begin_time_entries(matcher.group(2))))
        commands.append((End_Time_Entries_RE.format(c_to_s(config.END_TIME_ENTRIES_COMMANDS)),
                         lambda user, matcher: user.end_time_entries(matcher.group(2))))
        commands.append((Pause_Time_Entries_RE.format(c_to_s(config.PAUSE_TIME_ENTRIES_COMMANDS)),
                         lambda user, matcher: user.pause_time_entries()))
        commands.append((Continue_Time_Entries_RE.format(c_to_s(config.CONTINUE_TIME_ENTRIES_COMMANDS)),
                         lambda user, matcher: user.continue_time_entries()))
        commands.append((Current_Issue_Info_RE.format(c_to_s(config.CURRENT_ISSUE_INFO_COMMANDS)),
                         lambda user, matcher: user.current_issue_info()))
        commands.append((Get_User_State_RE.format(c_to_s(config.GET_USER_STATE_COMMANDS)),
                         lambda user, matcher: user.get_user_state()))
        commands.append((Feedback_RE.format(c_to_s(config.FEEDBACK_COMMANDS)),
                         lambda user, matcher: RedmineBot.save_feedback("From {} : {} \n"
                                                                        .format(user.user_id, matcher.group(2)))))
        commands.append((Commands_List_RE.format(c_to_s(config.COMMANDS_LIST_COMMANDS)),
                         lambda user, matcher: RedmineBot.get_commands_string()))
        commands.append((Drop_Issue_RE.format(c_to_s(config.DROP_ISSUE_COMMANDS)),
                         lambda user, matcher: user.drop_current_issue()))
        commands.append((Create_Time_Entries_RE.format(c_to_s(config.CREATE_TIME_ENTRIES)),
                         lambda user, matcher: user.create_issue_time_entries(matcher.group(2),
                                                                              matcher.group(3), matcher.group(4))))
        return commands

    @staticmethod
    def get_commands_string():
        return RedmineBot.commands_description_string

    @staticmethod
    def create_commands_description():
        commands_descript = list()
        commands_descript.append("/{} <ключ> - установка api-key для доступа к редмайну.\n"
                                 .format(RedmineBot.commands_to_string(config.SET_API_KEY_COMMANDS)))
        commands_descript.append("/{} <id задачи> - начало отсчета времени по задаче.\n"
                                 .format(RedmineBot.commands_to_string(config.BEGIN_TIME_ENTRIES_COMMANDS)))
        commands_descript.append("/{} <комментарий до 255 символов> - окончание отсчета работы над задачей и создание временной отметки в редмайне.\n"
                                 .format(RedmineBot.commands_to_string(config.END_TIME_ENTRIES_COMMANDS)))
        commands_descript.append("/{} - пауза.\n"
                                 .format(RedmineBot.commands_to_string(config.PAUSE_TIME_ENTRIES_COMMANDS)))
        commands_descript.append("/{} - снятие с паузы.\n"
                                 .format(RedmineBot.commands_to_string(config.CONTINUE_TIME_ENTRIES_COMMANDS)))
        commands_descript.append("/{} - информация о текущей задаче из редмайна.\n"
                                 .format(RedmineBot.commands_to_string(config.CURRENT_ISSUE_INFO_COMMANDS)))
        commands_descript.append("/{} - информация о выполнении задачи.\n"
                                 .format(RedmineBot.commands_to_string(config.GET_USER_STATE_COMMANDS)))
        commands_descript.append("/{} <текст> - пожелания для новых фич и тд.\n"
                                 .format(RedmineBot.commands_to_string(config.FEEDBACK_COMMANDS)))
        commands_descript.append("/{} - список команд для бота.\n"
                                 .format(RedmineBot.commands_to_string(config.COMMANDS_LIST_COMMANDS)))
        commands_descript.append("/{} - сброс текущей задачи.\n"
                                 .format(RedmineBot.commands_to_string(config.DROP_ISSUE_COMMANDS)))
        commands_descript.append("/{} <id задачи> <время> <комментарий> - создание временной отметки в редмайне.\n"
                                 .format(RedmineBot.commands_to_string(config.CREATE_TIME_ENTRIES)))
        return "".join(commands_descript)

    @staticmethod
    def get_proxy_settings():
        proxy_settings = None

        if config.PROXY_URL is not None and len(config.PROXY_URL) > 0:
            proxy_settings = {"proxy_url": config.PROXY_URL}
            if config.PROXY_PASSWORD is not None and len(config.PROXY_PASSWORD) > 0 and \
                    config.PROXY_USERNAME is not None and len(config.PROXY_USERNAME):
                proxy_settings["urllib3_proxy_kwargs"] = {
                    "username": config.PROXY_USERNAME,
                    "password": config.PROXY_PASSWORD
                }
        return proxy_settings


if __name__ == "__main__":
    bot = RedmineBot()
    bot.start()
