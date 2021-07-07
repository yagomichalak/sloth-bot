#z!eval
from mysqldb import the_database

async def convert_everyone() -> None:
    mycursor, db = await the_database()

    # Get columns from 
    await mycursor.excute("""
    SELECT user_id, sloth_class, skills_used,
    tribe, change_class_ts, has_potion,
    knife_sharpness_stack, 0, hacked,
    protected, knocked_out, wired,
    frogged FROM UserCurrency""")

    users = await mycursor.fetchall()

    await mycursor.execute("INSERT INTO SlothProfile VALUES %s", users)
    await db.commit()

    print('Success!')


if __name__ == '__main__':
    convert_everyone()
