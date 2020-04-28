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
