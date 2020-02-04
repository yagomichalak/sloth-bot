import mysql.connector

# mysql://b538834d791963:23cbe0c7@us-cdbr-iron-east-04.cleardb.net/heroku_e2ddae4f4191b3e?reconnect=true

db = mysql.connector.connect(
    host='us-cdbr-iron-east-04.cleardb.net',
    user='b538834d791963',
    passwd='23cbe0c7',
    database='heroku_e2ddae4f4191b3e'
)

mycursor = db.cursor()

def create_table():
    mycursor.execute('CREATE TABLE Teachers (id int NOT NULL, language VARCHAR(30) NOT NULL, teacher VARCHAR(30) NOT NULL, day VARCHAR(30) NOT NULL, time VARCHAR(30) NOT NULL, type VARCHAR(30), forr VARCHAR(30))')


def create_table_cid():
    mycursor.execute('CREATE TABLE CID (channel_id bigint, message_id bigint)')


def create_table_event():
    mycursor.execute('CREATE TABLE Events (id int, event VARCHAR(30), day VARCHAR(30), time VARCHAR(30))')


def add_teacher_class(id: int, language: str, teacher: str, day: str, time: str, type: str, forr: str):
    mycursor.execute(f"INSERT INTO Teachers (id, language, teacher, day, time, type, forr) VALUES (%s, %s, %s, %s, %s, %s, %s)", (id, language, teacher, day, time, type, forr))
    db.commit()
    

def remove_teacher_class(id: int):
        mycursor.execute(f'DELETE FROM Teachers WHERE id = {id}')
        db.commit()
        teachers = show_teachers()
        count = 0
        for teacher in teachers:
            count += 1
            mycursor.execute(f"UPDATE Teachers SET id = {count} WHERE id = {teacher[0]}")
            db.commit()


def edit_teacher_class_language(id: int, language: str):
    mycursor.execute(f"UPDATE Teachers SET language = '{language}' WHERE id = {id}")
    db.commit()
        

def edit_teacher_class_name(id: int, name: str):
    mycursor.execute(f"UPDATE Teachers SET teacher = '{name}' WHERE id = {id}")
    db.commit()
    
    
def edit_teacher_class_day(id: int, day: str):
    mycursor.execute(f"UPDATE Teachers SET day = '{day}' WHERE id = {id}")
    db.commit()


def edit_teacher_class_time(id: int, time: str):
    mycursor.execute(f"UPDATE Teachers SET time = '{time}' WHERE id = {id}")
    db.commit()


def edit_teacher_class_type(id: int, type: str):
    mycursor.execute(f"UPDATE Teachers SET type = '{type}' WHERE id = {id}")
    db.commit()


def edit_teacher_class_forr(id: int, forr: str):
    mycursor.execute(f"UPDATE Teachers SET forr = '{forr}' WHERE id = {id}")
    db.commit()


def show_teachers():
    mycursor.execute('SELECT * FROM Teachers ORDER BY id')
    teachers = []
    for x in mycursor:
        teachers.append(x)
    return teachers


def drop_table():
    mycursor.execute('DROP TABLE Teachers')


def add_cid_id(channel_id: int, message_id: int):
    if len(show_config()) > 0:
        mycursor.execute(f"UPDATE CID SET channel_id = {channel_id}, message_id = {message_id} WHERE message_id = message_id")
        db.commit()
    else:
        mycursor.execute(f"INSERT INTO CID VALUES ({channel_id}, {message_id})")
        db.commit()


def remove_cid_id():
    mycursor.execute(f"DELETE FROM CID WHERE channel_id = channel_id")
    db.commit()


def show_config():
    mycursor.execute('SELECT * FROM CID')
    ids = []
    for x in mycursor:
        ids.append(x)
    return ids


def drop_table_cid():
    mycursor.execute("DROP TABLE CID")


def add_the_event(id: int, event: str, day: str, time: str):
    mycursor.execute(f"INSERT INTO Events (id, event, day, time) VALUES (%s, %s, %s, %s)", (id, event, day, time))
    db.commit()


def show_events():
    mycursor.execute('SELECT * FROM Events ORDER BY id')
    events = []
    for x in mycursor:
        events.append(x)
    return events


def remove_the_event(id: int):
    mycursor.execute(f'DELETE FROM Events WHERE id = {id}')
    db.commit()
    events = show_events()
    count = 0
    for event in events:
        count += 1
        mycursor.execute(f"UPDATE Events SET id = {count} WHERE id = {event[0]}")
        db.commit()


def edit_event_name(id: int, name: str):
    mycursor.execute(f"UPDATE Events SET event = '{name}' WHERE id = {id}")
    db.commit()


def edit_event_day(id: int, day: str):
    mycursor.execute(f"UPDATE Events SET day = '{day}' WHERE id = {id}")
    db.commit()


def edit_event_time(id: int, time: str):
    mycursor.execute(f"UPDATE Events SET time = '{time}' WHERE id = {id}")
    db.commit()


def check_x(something):
    x = 0
    if len(something) == 7:
        if something[3] == 'Monday':
            x = 335
        elif something[3] == 'Tuesday':
            x = 550
        elif something[3] == 'Wednesday':
            x = 760
        elif something[3] == 'Thursday':
            x = 970
        elif something[3] == 'Friday':
            x = 1180
        elif something[3] == 'Saturday':
            x = 1400
        elif something[3] == 'Sunday':
            x = 1590

    if len(something) == 4:
        if something[2] == 'Monday':
            x = 335
        elif something[2] == 'Tuesday':
            x = 550
        elif something[2] == 'Wednesday':
            x = 760
        elif something[2] == 'Thursday':
            x = 970
        elif something[2] == 'Friday':
            x = 1180
        elif something[2] == 'Saturday':
            x = 1390
        elif something[2] == 'Sunday':
            x = 1590
    return x


def check_y(something):
    y = 0
    if len(something) == 7:
        if something[4] == '1AM':
            y = 360
        elif something[4] == '3AM':
            y = 430
        elif something[4] == '12PM':
            y = 500
        elif something[4] == '4PM':
            y = 570
        elif something[4] == '5PM':
            y = 635
        elif something[4] == '6PM':
            y = 705
        elif something[4] == '7PM':
            y = 780
        elif something[4] == '8PM':
            y = 850
        elif something[4] == '9PM':
            y = 920
        elif something[4] == '10PM':
            y = 995

    elif len(something) == 4:
        if something[3] == '1AM':
            y = 360
        elif something[3] == '3AM':
            y = 430
        elif something[3] == '12PM':
            y = 500
        elif something[3] == '4PM':
            y = 570
        elif something[3] == '5PM':
            y = 635
        elif something[3] == '6PM':
            y = 705
        elif something[3] == '7PM':
            y = 780
        elif something[3] == '8PM':
            y = 850
        elif something[3] == '9PM':
            y = 920
        elif something[3] == '10PM':
            y = 995

    return y


def check_clr(something):
    clr = (0, 255, 0)

    if len(something) == 7:
        if something[5] == 'Grammar':
            clr = (0, 0, 0)
        elif something[5] == 'Pronunciation':
            clr = (0, 153, 153)
        elif something[5] == 'Both':
            clr = (255, 0, 0)

    elif len(something) == 4:
        clr = (199,21,133)

    return clr

#create_table()
#drop_table_cid()
#create_table_cid()
#create_table_event()