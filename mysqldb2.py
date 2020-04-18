import aiomysql
import asyncio

loop = asyncio.get_event_loop()

#mysql://bf6ed027290645:fcec7f15@us-cdbr-iron-east-01.cleardb.net/heroku_7b5f278b70b0f56?reconnect=true

async def the_data_base2():
    db = await aiomysql.connect(host='us-cdbr-iron-east-01.cleardb.net',
                                user='bf6ed027290645',
                                password='fcec7f15',
                                db='heroku_7b5f278b70b0f56', loop=loop)

    mycursor = await db.cursor()
    return mycursor, db


loop2 = asyncio.get_event_loop()

#mysql://b0df23b6f3cd0c:4feaafce@us-cdbr-iron-east-01.cleardb.net/heroku_6452134eab38dfc?reconnect=true

async def the_data_base3():
    db = await aiomysql.connect(host='us-cdbr-iron-east-01.cleardb.net',
                                user='b0df23b6f3cd0c',
                                password='4feaafce',
                                db='heroku_6452134eab38dfc', loop=loop2)

    mycursor = await db.cursor()
    return mycursor, db
