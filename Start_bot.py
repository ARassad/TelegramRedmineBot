from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
import telegram as tel
import userDB as udb
import usercontainer as uc
import re
import config
import logging

logging.basicConfig(filename=config.LOG_FILE, level=logging.DEBUG)
UserDb = udb.UserDB(config.SERVER, config.DATABASE, config.DRIVER, config.USERNAME, config.PASSWORD)
UserContainer = uc.UserContainer(UserDb)

Set_Api_Key_RE = "^/(set_api_key|api_key|api|key|akey|ak|k)\s+(\S+)\s*$"
Begin_Time_Entries_RE = "^/(begin_time_entries|bte|start_time)\s+(\d+)\s*$"
End_Time_Entries_RE = "^/(end_time_entries|ete)\s+(.{1,255})$"
Pause_Time_Entries_RE = "^/(pause_time_entries|pte|p|pause)\s*$"
Continue_Time_Entries_RE = "^/(continue_time_entries|cte|c|cont|continue)\s*$"
Current_Issue_Info_RE = "^/(current_issue_info|cii|info|issue)\s*$"
Get_User_State_RE = "^/(get_user_state|state)\s*$"
Feedback = "^/(feedback)\s+(.+)\s*$"


def process(bot: tel.Bot, update: tel.Update):
    user = UserContainer.get_user(update.effective_user.id)
    message = "Команда не распознана"
    logging.info("From ({} : {}) message  : {}"
                 .format(update.effective_user.id, update.effective_user.first_name, update.message.text))

    try:
        if re.match(Set_Api_Key_RE, update.message.text):
            matcher = re.search(Set_Api_Key_RE, update.message.text)
            message = user.set_api_key(matcher.group(2))
            UserContainer.update_user_to_bd(user.user_id)

        elif re.match(Begin_Time_Entries_RE, update.message.text):
            matcher = re.search(Begin_Time_Entries_RE, update.message.text)
            message = user.begin_time_entries(matcher.group(2))
            UserContainer.update_user_to_bd(user.user_id)

        elif re.match(End_Time_Entries_RE, update.message.text):
            matcher = re.search(End_Time_Entries_RE, update.message.text)
            message = user.end_time_entries(matcher.group(2))
            UserContainer.update_user_to_bd(user.user_id)

        elif re.match(Pause_Time_Entries_RE, update.message.text):
            message = user.pause_time_entries()
            UserContainer.update_user_to_bd(user.user_id)

        elif re.match(Continue_Time_Entries_RE, update.message.text):
            message = user.continue_time_entries()
            UserContainer.update_user_to_bd(user.user_id)

        elif re.match(Current_Issue_Info_RE, update.message.text):
            message = user.current_issue_info()

        elif re.match(Get_User_State_RE, update.message.text):
            message = user.get_user_state()

        elif re.match(Feedback, update.message.text):
            matcher = re.search(Feedback, update.message.text)
            save_feedback("From {} : {} : \n {} \n"
                          .format(update.effective_user.first_name, update.effective_user.id, matcher.group(2)))
            message = "Спасибо за отзыв"

        send_message(bot, update, message)

    except Exception:
        logging.exception("Exception")
        send_message(bot, update, "Во время выполнения команды произошла ошибка")


def send_message(bot: tel.Bot, update: tel.Update, message):
    bot.send_message(update.message.chat.id, message)
    logging.info("Send to ({} : {}) message  : {}"
                 .format(update.effective_user.id, update.effective_user.first_name, message))


def save_feedback(message):
    file = open(config.FEEDBACK_FILE, "a")
    file.write(message)
    file.close()


if __name__ == "__main__":
    token = config.BOT_TOKEN
    updater = Updater(token=token)
    dispatcher = updater.dispatcher
    handler = MessageHandler(Filters.command | Filters.text, process)
    dispatcher.add_handler(handler)

    logging.info("Start")
    updater.start_polling()
