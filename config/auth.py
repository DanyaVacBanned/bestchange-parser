import os

from dotenv import load_dotenv

load_dotenv()

token = os.getenv('token')
admin_id = int(os.getenv('admin_id'))
second_admin_id = int(os.getenv('second_admin_id'))
developer_id = int(os.getenv('developer_id'))