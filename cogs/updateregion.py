import discord
from discord.ext import commands, tasks
from mysqldb2 import *
from extra.native_regions import language_regions

server_id = 459195345419763713
bot_and_commands_channel_id = 562019654017744904

class UpdateRegion(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("UpdateRegion cog is online!")
        self.change_region.start()

    @tasks.loop(minutes=60)
    async def change_region(self):
        guild = self.client.get_guild(server_id)
        for member in guild.members:
            if str(member.status).title() == 'Online':
                # top_role = member.roles[1].name
                for role in member.roles:
                    try:
                        region = language_regions[role.name]
                    except KeyError:
                        pass
                    else:
                        if region:
                            await self.store_in_db(role.name, region)

        top_online_role = await self.get_top_online_role()
        await self.reset_table_roleregion()
        top_region = top_online_role[0][0]
        old_region = guild.region
        await guild.edit(region=top_region)
        channel = discord.utils.get(guild.channels, id=bot_and_commands_channel_id)
        if str(old_region) != str(top_region):
            await channel.send(f"**Region changed from `{old_region}` to `{top_region}`**")
        else:
            await channel.send(f"**Region remained the same; `{old_region}`**")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def create_table_roleregion(self, ctx):
        await ctx.message.delete()
        mycursor, db = await the_data_base5()
        await mycursor.execute("CREATE TABLE RoleRegion (role VARCHAR(30), region VARCHAR(20))")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table __RoleRegion__ created!**", delete_after=3)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def drop_table_roleregion(self, ctx):
        await ctx.message.delete()
        mycursor, db = await the_data_base5()
        await mycursor.execute("DROP TABLE RoleRegion")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table __RoleRegion__ dropped!**", delete_after=3)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reset_table_roleregion(self, ctx=None):
        if ctx:
            await ctx.message.delete()
        mycursor, db = await the_data_base5()
        await mycursor.execute("DELETE FROM RoleRegion")
        await db.commit()
        await mycursor.close()
        if ctx:
            return await ctx.send("**Table __RoleRegion__ reset!**", delete_after=3)

    async def store_in_db(self, top_role: str, region: str):
        mycursor, db = await the_data_base5()
        await mycursor.execute("INSERT INTO RoleRegion (role, region) VALUES (%s, %s)", (top_role, region))
        await db.commit()
        await mycursor.close()

    async def get_top_online_role(self):
        mycursor, db = await the_data_base5()
        await mycursor.execute("SELECT region, count(*) FROM RoleRegion GROUP BY region ORDER BY count(*) DESC")
        the_roles = await mycursor.fetchall()
        await mycursor.close()
        return the_roles

def setup(client):
    client.add_cog(UpdateRegion(client))
