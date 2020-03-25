import discord
from discord.ext import commands
from mysqldb import *

announce_channel = 689918515129352213


class NClassManagement(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print('NClassManagement cog is ready!')

    # Add classes
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def nclass(self, ctx, teacher: discord.Member, language, day, time, *desc: str):
        await ctx.message.delete()
        if len(desc) == 0:
            desc = 'Unspecified'
        else:
            desc = ' '.join(desc)

        embed = discord.Embed(title='Upcoming Class',
                              description=f":bust_in_silhouette: **Teacher:** {teacher.mention}\n:tongue: **Language:** {language.title()}\n:high_brightness: **Day:** {day.title()}\n:timer: **Time:** {time.upper()}\n:scroll: **Class Description:** {desc}\n`RSVP with ✅`",
                              colour=discord.Colour.green(), timestamp=ctx.message.created_at)
        embed.set_thumbnail(url=teacher.avatar_url)
        the_channel = discord.utils.get(ctx.guild.channels, id=announce_channel)
        the_class = await the_channel.send(content=":busts_in_silhouette: **Attendees:**```->```", embed=embed)
        await the_class.add_reaction('✅')
        await add_class_announcement(teacher.id, the_class.id)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def show_announ(self, ctx):
        await ctx.message.delete()
        announcements = await show_class_announcements()
        if len(announcements) > 0:
            embed = discord.Embed(title="Class Announcements:", description="__Available class announcements__",
                                  colour=discord.Colour.green(), timestamp=ctx.message.created_at)
            for ann in announcements:
                embed.add_field(name=f"Teacher id: {ann[0]}", value=f"Class id: {ann[1]}", inline=False)
        else:
            embed = discord.Embed(title="Class Announcements:", description="__No classes available!__",
                                  colour=discord.Colour.green(), timestamp=ctx.message.created_at)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def del_announ(self, ctx, class_id: int = None):
        await ctx.message.delete()
        if not class_id:
            return await ctx.send("**Inform the class id!**")

        announcements = await show_class_announcements()
        for announ in announcements:
            if announ[1] == class_id:
                await remove_announcement(announ[1])
                return await ctx.send(f"**Class announcement: `{class_id}` removed!**")
        else:
            await ctx.send("**Class announcement not found!**")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def delall_announs(self, ctx):
        await ctx.message.delete()
        await remove_all_class_announcements()
        return await ctx.send("**All class announcements deleted!**")


def setup(client):
    client.add_cog(NClassManagement(client))
