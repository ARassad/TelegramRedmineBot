from enum import Enum
import time
import redminerequests as rq
import logging
import dbprovider as db
import datetime

class UserState(Enum):
    unregister = 1
    inprogress = 2
    pause = 3
    free = 4


class User:
    def __init__(self, user_id, api_key="null", status=UserState.free,
                 issue_id=0, issue_start_time=0, issue_pause_start_time=0, pause_summary=0):
        self.status = status
        self.user_id = user_id

        self.api_key = api_key
        self.api_key_valid = False
        self.set_api_key(api_key)

        self.issue_id = issue_id
        self.issue_start_time = issue_start_time
        self.issue_pause_start_time = issue_pause_start_time
        self.pause_summary = pause_summary

    def set_api_key(self, key):
        self.api_key_valid = False

        try:
            rq.get_user_info(key)
            self.api_key_valid = True
        except rq.NetworkUnauthorizedError:
            return "Невозможно авторизироваться заданным ключом"
        except:
            logging.exception("Exception : set_api_key")
            return "Ошибка при доступе к редмайну. Не получилось проверить ключ"

        self.api_key = key
        return "Ключ успешно назначен"

    def begin_time_entries(self, issue_id):
        if not self.api_key_valid:
            return "Не установлен ключ для доступа к редмайну"
        elif self.status == UserState.inprogress or self.status == UserState.pause:
            return "Вы уже работаете над задачей {}. " \
                   "Отслеживать можно только одну задачу одновременно. Завершите текущую задачу".format(self.issue_id)

        self.issue_id = int(issue_id)
        self.issue_start_time = time.time()
        self.pause_summary = 0
        self.issue_pause_start_time = 0
        self.status = UserState.inprogress

        return "Вы начали работу над задачей!"

    def end_time_entries(self, text):
        if not self.api_key_valid:
            return "Не установлен ключ для доступа к редмайну"
        elif self.status == UserState.free:
            return "Вы не работаете над задачей"
        elif self.status == UserState.pause:
            self.continue_time_entries()

        spenttime = time.time() - self.issue_start_time - self.pause_summary
        spenthours = round(spenttime / (60 * 60), 2)

        request_result = False
        result_message = ""
        try:
            rq.create_time_entries(self.api_key, self.issue_id, spenthours, text)
            request_result = True
        except rq.NetworkUnauthorizedError:
            logging.exception("Не получилось авторизоваться user_id : {}".format(self.user_id))
            result_message = "Не получилось авторизоваться в редмайне. Попробуйте обновить api_key."
        except rq.CannotCreateTimeEntries:
            logging.exception("Не получилось создать отметку в редмайне user_id : {}".format(self.user_id))
            result_message = "Не получилось создать отметку в редмайне."
        finally:
            db.save_tiem_entrie_db(self.user_id, self.issue_id, spenthours, text, datetime.datetime.now(), request_result)
            self.status = UserState.free

        result_message += "{}\nВы потратили {} часов".format("Временная отметка создана." if request_result
                                                             else "Отметка будет автоматически создана после получения доступа к редмайну.",
                                                             spenthours)
        return result_message

    def pause_time_entries(self):
        if not self.api_key_valid:
            return "Не установлен ключ для доступа к редмайну"
        elif self.status == UserState.free:
            return "Вы не работаете над задачей"
        elif self.status == UserState.pause:
            return "Задача уже стоит на паузе"

        self.issue_pause_start_time = time.time()
        self.status = UserState.pause

        return "Задача поставлена на паузу"

    def continue_time_entries(self):
        if not self.api_key_valid:
            return "Не установлен ключ для доступа к редмайну"
        elif self.status == UserState.free:
            return "Вы не работаете над задачей"
        elif self.status == UserState.inprogress:
            return "Задача не стоит на паузе"

        self.pause_summary += time.time() - self.issue_pause_start_time
        self.issue_pause_start_time = 0
        self.status = UserState.inprogress

        return "Задача снята с паузы"

    def current_issue_info(self):
        if not self.api_key_valid:
            return "Не установлен ключ для доступа к редмайну"
        elif self.status == UserState.free:
            return "Вы не работаете над задачей"

        try:
            issue = rq.get_issues(self.issue_id, self.api_key)["issue"]
        except:
            logging.exception("Exception : current_issue_info")
            return "Не удалось связаться с редмайном"

        mes = "Название проекта : {}\n" \
              "Название задачи : {}\n" \
              "Статус : {}\n" \
              "Автор : {}\n" \
              "Назначено на : {}\n" \
              "Описание : {}\n" \
              .format(issue["project"]["name"], issue["subject"], issue["status"]["name"], issue["author"]["name"],
                      issue["assigned_to"]["name"], str(issue["description"]))

        return mes

    def get_user_state(self):
        if not self.api_key_valid:
            return "Не установлен ключ для доступа к редмайну"
        elif self.status == UserState.free:
            return "Вы не работаете над задачей"
        elif self.status == UserState.inprogress:
            return "Вы работаете над задачей {} уже {} часов"\
                .format(self.issue_id, round((time.time() - self.issue_start_time - self.pause_summary) / (60*60), 2))
        elif self.status == UserState.pause:
            return "Задача {} стоит на паузе уже {} часов\nВы работали над ней {} часов".format(self.issue_id,
                        round((time.time() - self.issue_pause_start_time)/(60*60), 2),
                        round((self.issue_pause_start_time - self.issue_start_time - self.pause_summary) / (60 * 60), 2))
        return "Неизвестное состояние"

    def drop_current_issue(self):
        if not self.api_key_valid:
            return "Не установлен ключ для доступа к редмайну!"
        elif self.status == UserState.free:
            return "Вы не работаете над задачей"

        self.status = UserState.free

        return "Задача сброшена"

    def create_issue_time_entries(self, issue_id, hours, message):
        if not self.api_key_valid:
            return "Не установлен ключ для доступа к редмайну"

        try:
            rq.create_time_entries(self.api_key, issue_id, float(hours), message)
        except:
            logging.exception("Exception : create_issue_time_entries")
            return "Ошибка во время создания временной отметки"

        return "Временная отметка создана"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.status == other.status and self.user_id == other.user_id and self.api_key == other.api_key and\
                   self.api_key_valid == other.api_key_valid and self.issue_id == other.issue_id and \
                   self.issue_start_time == other.issue_start_time and \
                   self.issue_pause_start_time == other.issue_pause_start_time and\
                   self.pause_summary == other.pause_summary
        return False
