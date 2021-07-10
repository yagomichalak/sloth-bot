#z!eval
from mysqldb import the_database

async def convert_everyone() -> None:
    mycursor, db = await the_database()


    # Get columns from 
    await mycursor.execute("""
    SELECT UC.user_id, sloth_class, skills_used,
    UT.tribe_name, change_class_ts, has_potion,
    knife_sharpness_stack, 0, hacked,
    protected, knocked_out, wired,
    frogged, UC.user_id 
    FROM UserCurrency UC
    LEFT JOIN UserTribe UT
    ON UC.tribe = UT.tribe_name
    """)
    users = await mycursor.fetchall()
    # return await ctx.send(users)

    sql = """
    INSERT IGNORE INTO TribeMember (owner_id, tribe_name, member_id, tribe_role)
    SELECT UT.user_id, tribe_name, UC.user_id, 'Member'
    FROM UserCurrency UC
    LEFT JOIN UserTribe UT
    ON UC.tribe = UT.tribe_name
    """
    await mycursor.executemany(sql)



    placeholders = ['%s'] * 14
    sql_template2 = """
    INSERT IGNORE INTO SlothProfile VALUES ({placeholders})
    """
    sql2 = sql_template2.format(placeholders=','.join(placeholders))
    await mycursor.executemany(sql2, users)



    await db.commit()

    await ctx.send('Success!')

await convert_everyone()

if __name__ == '__main__':
    await convert_everyone()
