#z!eval
from mysqldb import the_database

async def convert_everyone() -> None:
    mycursor, db = await the_database()

    placeholders = ['%s'] * 13
    sql_template = """
    INSERT IGNORE INTO SlothProfiles VALUES ({placeholders})
    """
    sql = sql_template.format(placeholders=','.join(placeholders))

    # Get columns from 
    await mycursor.execute("""
    SELECT user_id, sloth_class, skills_used,
    tribe, change_class_ts, has_potion,
    knife_sharpness_stack, 0, hacked,
    protected, knocked_out, wired,
    frogged FROM UserCurrency""")

    users = await mycursor.fetchall()
    # return await ctx.send(users)
    await mycursor.executemany(sql, users)
    await db.commit()

    await ctx.send('Success!')

await convert_everyone()

if __name__ == '__main__':
    await convert_everyone()
