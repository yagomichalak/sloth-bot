import aiomysql
import asyncio

loop = asyncio.get_event_loop()


async def the_data_base():
    db = await aiomysql.connect(host='us-cdbr-iron-east-04.cleardb.net',
                                user='b538834d791963',
                                password='23cbe0c7',
                                db='heroku_e2ddae4f4191b3e', loop=loop)

    mycursor = await db.cursor()
    return mycursor, db


async def create_class_announcement():
    mycursor, db = await the_data_base()
    await mycursor.execute('CREATE TABLE class_announcement (id bigint, class_id bigint)')
    await mycursor.close()


async def add_class_announcement(id: int, class_id: int):
    mycursor, db = await the_data_base()
    await mycursor.execute(f"INSERT INTO class_announcement (id, class_id) VALUES (%s, %s)", (id, class_id))
    await db.commit()
    await mycursor.close()


async def show_class_announcements():
    mycursor, db = await the_data_base()
    await mycursor.execute('SELECT * FROM class_announcement')
    announcements = await mycursor.fetchall()
    await mycursor.close()
    return announcements


async def remove_announcement(class_id: int):
    mycursor, db = await the_data_base()
    await mycursor.execute(f'DELETE FROM class_announcement WHERE class_id = {class_id}')
    await db.commit()
    await mycursor.close()


async def drop_class_announcement():
    mycursor, db = await the_data_base()
    await mycursor.execute('DROP TABLE class_announcement')
    await db.commit()
    await mycursor.close()


async def remove_all_class_announcements():
    mycursor, db = await the_data_base()
    announs = await show_class_announcements()
    for ann in announs:
        await mycursor.execute(f'DELETE FROM class_announcement WHERE class_id = {ann[1]}')
        await db.commit()
    await mycursor.close()


async def create_table():
    mycursor, db = await the_data_base()
    await mycursor.execute(
        'CREATE TABLE Teachers (id int NOT NULL, language VARCHAR(30) NOT NULL, teacher VARCHAR(30) NOT NULL, day VARCHAR(30) NOT NULL, time VARCHAR(30) NOT NULL, type VARCHAR(30), forr VARCHAR(30))')


async def create_table_cid():
    mycursor, db = await the_data_base()
    await mycursor.execute('CREATE TABLE CID (channel_id bigint, message_id bigint)')


async def create_table_event():
    mycursor, db = await the_data_base()
    await mycursor.execute('CREATE TABLE Events (id int, event VARCHAR(30), day VARCHAR(30), time VARCHAR(30))')


async def add_teacher_class(id: int, language: str, teacher: str, day: str, time: str, type: str, forr: str):
    mycursor, db = await the_data_base()
    await mycursor.execute(
        f"INSERT INTO Teachers (id, language, teacher, day, time, type, forr) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (id, language, teacher, day, time, type, forr))
    await db.commit()
    await mycursor.close()


async def remove_teacher_class(id: int):
    mycursor, db = await the_data_base()
    await mycursor.execute(f'DELETE FROM Teachers WHERE id = {id}')
    await db.commit()
    teachers = await show_teachers()
    count = 0
    for teacher in teachers:
        count += 1
        await mycursor.execute(f"UPDATE Teachers SET id = {count} WHERE id = {teacher[0]}")
        await db.commit()
    await mycursor.close()


async def edit_teacher_class_language(id: int, language: str):
    mycursor, db = await the_data_base()
    await mycursor.execute(f"UPDATE Teachers SET language = '{language}' WHERE id = {id}")
    await db.commit()
    await mycursor.close()


async def edit_teacher_class_name(id: int, name: str):
    mycursor, db = await the_data_base()
    await mycursor.execute(f"UPDATE Teachers SET teacher = '{name}' WHERE id = {id}")
    await db.commit()
    await mycursor.close()


async def edit_teacher_class_day(id: int, day: str):
    mycursor, db = await the_data_base()
    await mycursor.execute(f"UPDATE Teachers SET day = '{day}' WHERE id = {id}")
    await db.commit()
    await mycursor.close()


async def edit_teacher_class_time(id: int, time: str):
    mycursor, db = await the_data_base()
    await mycursor.execute(f"UPDATE Teachers SET time = '{time}' WHERE id = {id}")
    await db.commit()
    await mycursor.close()


async def edit_teacher_class_type(id: int, type: str):
    mycursor, db = await the_data_base()
    await mycursor.execute(f"UPDATE Teachers SET type = '{type}' WHERE id = {id}")
    await db.commit()
    await mycursor.close()


async def edit_teacher_class_forr(id: int, forr: str):
    mycursor, db = await the_data_base()
    await mycursor.execute(f"UPDATE Teachers SET forr = '{forr}' WHERE id = {id}")
    await db.commit()
    await mycursor.close()


async def show_teachers():
    mycursor, db = await the_data_base()
    await mycursor.execute('SELECT * FROM Teachers ORDER BY id')
    teachers = await mycursor.fetchall()
    await mycursor.close()
    return teachers


async def drop_table():
    mycursor, db = await the_data_base()
    await mycursor.execute('DROP TABLE Teachers')
    await db.commit()
    await mycursor.close()


async def add_cid_id(channel_id: int, message_id: int):
    mycursor, db = await the_data_base()
    config = await show_config()
    if len(config) > 0:
        await mycursor.execute(
            f"UPDATE CID SET channel_id = {channel_id}, message_id = {message_id} WHERE message_id = message_id")
        await db.commit()
        await mycursor.close()
    else:
        await mycursor.execute(f"INSERT INTO CID VALUES ({channel_id}, {message_id})")
        await db.commit()
        await mycursor.close()


async def remove_cid_id():
    mycursor, db = await the_data_base()
    await mycursor.execute(f"DELETE FROM CID WHERE channel_id = channel_id")
    await db.commit()
    await mycursor.close()


async def show_config():
    mycursor, db = await the_data_base()
    await mycursor.execute('SELECT * FROM CID')
    ids = await mycursor.fetchall()
    await mycursor.close()
    return ids


async def drop_table_cid():
    mycursor, db = await the_data_base()
    mycursor.execute("DROP TABLE CID")
    await db.commit()
    await mycursor.close()


async def add_the_event(id: int, event: str, day: str, time: str):
    mycursor, db = await the_data_base()
    await mycursor.execute(f"INSERT INTO Events (id, event, day, time) VALUES (%s, %s, %s, %s)", (id, event, day, time))
    await db.commit()
    await mycursor.close()


async def show_events():
    mycursor, db = await the_data_base()
    await mycursor.execute('SELECT * FROM Events ORDER BY id')
    events = await mycursor.fetchall()
    await mycursor.close()
    return events


async def remove_the_event(id: int):
    mycursor, db = await the_data_base()
    await mycursor.execute(f'DELETE FROM Events WHERE id = {id}')
    await db.commit()
    events = await show_events()
    count = 0
    for event in events:
        count += 1
        await mycursor.execute(f"UPDATE Events SET id = {count} WHERE id = {event[0]}")
        await db.commit()
    await mycursor.close()


async def edit_event_name(id: int, name: str):
    mycursor, db = await the_data_base()
    await mycursor.execute(f"UPDATE Events SET event = '{name}' WHERE id = {id}")
    await db.commit()
    await mycursor.close()


async def edit_event_day(id: int, day: str):
    mycursor, db = await the_data_base()
    await mycursor.execute(f"UPDATE Events SET day = '{day}' WHERE id = {id}")
    await db.commit()
    await mycursor.close()


async def edit_event_time(id: int, time: str):
    mycursor, db = await the_data_base()
    await mycursor.execute(f"UPDATE Events SET time = '{time}' WHERE id = {id}")
    await db.commit()
    await mycursor.close()


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
        clr = (199, 21, 133)

    return clr


