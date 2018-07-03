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

CONNECTION_STRING = "" // строка подключения к бд
BOT_TOKEN = "exampleexampleexampleexample"
REDMINE_URL = "https://redmine.yourcompany.com/"
LOG_FILE = ""
FEEDBACK_FILE = ""