#z!eval
from mysqldb import the_database

async def convert_everyone() -> None:
    mycursor, db = await the_database()
    await mycursor.excute("""
    SELECT user_id, sloth_class, change_class_ts,
    protected, has_potion, hacked,
    knocked_out, skills_used, knife_sharpness_stack,
    wired, tribe, frogged
    """)

    users = await mycursor.fetchall()

    await mycursor.execute("""
    INSERT INTO SlothProfile (
        
    )
    """)