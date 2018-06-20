Для работы бота должна быть создана база данных 
С таблицей User: 
	user_id : int
	status : int 
	api_key : varchar(255) : nullable
	issue_id : int
	issue_start_time : float
	issue_pause_start_time : float
	pause_summary : float

Также в директории бота должен быть создан файл config.py содержащий следующие переменные
SERVER = "EXAMPLE"
DATABASE = "EXAMPLE"
DRIVER = "{ODBC Driver 13 for SQL Server}"
USERNAME = "EXAMPLE"
PASSWORD = "EXAMPLE"
BOT_TOKEN = "exampleexampleexampleexample"
REDMINE_URL = "https://redmine.yourcompany.com/"

Команды 																				Пример 
установка ключа редмайна /(set_api_key|api_key|api|key|akey|ak|k) (ключ)  			/ak 647268476138562876582
начало работы над задачей /(begin_time_entries|bte|start_time) (айдишник задачи)  	/bte 21444
конец работы над задачей /(end_time_entries|ete) (коментарий) 						/ete Все сделал
пауза /(pause_time_entries|pte|p|pause)												/pause
снятие паузы /(continue_time_entries|cte|c|cont|continue)							/c
информация по текущей задаче = /(current_issue_info|cii|info|issue)					/info
информация по текущему статусу юзера /(get_user_state|state)						/state