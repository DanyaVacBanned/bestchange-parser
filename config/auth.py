import os

from dotenv import load_dotenv

load_dotenv()

token = os.getenv('token')
admin_id = int(os.getenv('admin_id'))
developer_id = int(os.getenv('developer_id'))