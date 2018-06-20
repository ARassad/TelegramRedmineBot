from enum import Enum
import time
import redminerequests as rq


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
            return "Невозможно авторизироваться заданым ключем"
        except:
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

        try:
            rq.create_time_entries(self.api_key, self.issue_id, spenthours, text)
        except:
            return "Ошибка соединения во время создания временной отметки"

        self.status = UserState.free

        return "Временная отметка создана\n" \
               "Вы потратили {}".format(spenthours)

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
            return "Задача {} стоит на паузе уже {} часов вы работали над ней {} часов".format(self.issue_id,
                            round((time.time() - self.issue_pause_start_time)/(60*60), 2),
                            round((self.issue_pause_start_time - self.issue_start_time - self.pause_summary) / (60 * 60), 2))
        return "Неизвестное состояние"


if __name__ == '__main__':

    u = User("ebf5ba42b3ba39611660f4b9456c952cfbd7273b")
    u.begin_time_entries(24876)
    print(u.current_issue_info())

    pass