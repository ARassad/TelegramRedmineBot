��� ������ ���� ������ ���� ������� ���� ������ 
� �������� User: 
	user_id : int
	status : int 
	api_key : varchar(255) : nullable
	issue_id : int
	issue_start_time : float
	issue_pause_start_time : float
	pause_summary : float

����� � ���������� ���� ������ ���� ������ ���� config.py ���������� ��������� ����������
SERVER = "EXAMPLE"
DATABASE = "EXAMPLE"
DRIVER = "{ODBC Driver 13 for SQL Server}"
USERNAME = "EXAMPLE"
PASSWORD = "EXAMPLE"
BOT_TOKEN = "exampleexampleexampleexample"
REDMINE_URL = "https://redmine.yourcompany.com/"

������� 																				������ 
��������� ����� �������� /(set_api_key|api_key|api|key|akey|ak|k) (����)  			/ak 647268476138562876582
������ ������ ��� ������� /(begin_time_entries|bte|start_time) (�������� ������)  	/bte 21444
����� ������ ��� ������� /(end_time_entries|ete) (����������) 						/ete ��� ������
����� /(pause_time_entries|pte|p|pause)												/pause
������ ����� /(continue_time_entries|cte|c|cont|continue)							/c
���������� �� ������� ������ = /(current_issue_info|cii|info|issue)					/info
���������� �� �������� ������� ����� /(get_user_state|state)						/state