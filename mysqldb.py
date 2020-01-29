import sqlite3

conn = sqlite3.connect('calendar.db')

c = conn.cursor()

def create_table():
    with conn:
        c.execute('CREATE TABLE Teachers (id INTEGER, language TEXT, teacher TEXT, day TEXT, time TEXT, type TEXT)')


def add_teacher_class(id: int, language: str, teacher: str, day: str, time: str, type: str):
    with conn:
        c.execute(f'''INSERT INTO Teachers VALUES ({id}, "{language}", "{teacher}", "{day}", "{time}", "{type}")''')
    

def remove_teacher_class(id: int):
    with conn:
        c.execute(f'DELETE FROM Teachers WHERE id = {id}')
        teachers = show_teachers()
        count = 0
        for teacher in teachers:
            count += 1
            c.execute(f"UPDATE Teachers SET id = {count} WHERE id = {teacher[0]}")


def edit_teacher_class_language(id: int, language: str):
    with conn:
        c.execute(f"UPDATE Teachers SET language = '{language}' WHERE id = {id}")
        

def edit_teacher_class_name(id: int, name: str):
    with conn:
        c.execute(f"UPDATE Teachers SET teacher = '{name}' WHERE id = {id}")
    
    
def edit_teacher_class_day(id: int, day: str):
    with conn:
        c.execute(f"UPDATE Teachers SET day = '{day}' WHERE id = {id}")


def edit_teacher_class_time(id: int, time: str):
    with conn:
        c.execute(f"UPDATE Teachers SET time = '{time}' WHERE id = {id}")


def edit_teacher_class_type(id: int, type: str):
    with conn:
        c.execute(f"UPDATE Teachers SET type = '{type}' WHERE id = {id}")


def show_teachers():
    with conn:
        c.execute('SELECT * FROM Teachers')
        return c.fetchall()


def drop_table():
    c.execute('DROP TABLE Teachers')

