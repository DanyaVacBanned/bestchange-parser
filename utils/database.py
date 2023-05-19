import sqlite3

class Model:

    def __init__(self, db_file) -> None:
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    
    def create_table(self):
        with self.connection:
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name VARCHAR (100),
                task_time datetime);
                """
                )
            self.connection.commit()

    
           
            
class TasksManager(Model):
    def create_task(self,task_name, task_time):
        with self.connection:
            self.cursor.execute(
                """
                INSERT INTO tasks (task_name, task_time) VALUES (?, ?)
                """, (task_name, task_time,)
                )
            self.connection.commit()

    def get_tasks(self, with_datetime = False):
        with self.connection:
            if with_datetime:
                data = self.cursor.execute(
                """
                SELECT task_name, task_time FROM tasks
                """
                ).fetchall()
                return [f"{val[0]} {val[1]}" for val in data]
            else:
                data = self.cursor.execute(
                    """
                    SELECT task_name FROM tasks
                    """
                    ).fetchall()
            return [val[0] for val in data]
           
    def get_task_by_name(self, task_name):
        with self.connection:
            data = self.cursor.execute(
            """
            SELECT task_name, task_time FROM tasks
            WHERE task_name = ?
            """, (task_name,)
            ).fetchone()

        return data
    
    def delete_task_by_name(self, task_name):
        with self.connection:
            self.cursor.execute(
                """
                DELETE FROM tasks WHERE task_name = ?
                """, (task_name,)
                )
    def delete_all_data(self):
        with self.connection:
            self.cursor.execute(
            """
            DELETE FROM tasks
            """
         )

        


db = Model('db.sqlite3')
db.create_table()