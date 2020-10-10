import discord
from discord.ext import commands


class Embeds(commands.Cog):
    '''
    A cog related to embedded messages.
    '''

    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Embeds cog is ready.')

    # Sends an embedded message
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def embed(self, ctx):
        '''
        (ADM) Sends an embedded message.
        '''
        await ctx.message.delete()
        if len(ctx.message.content.split()) < 2:
            return await ctx.send('You must inform all parameters!')

        msg = ctx.message.content.split('!embed', 1)
        embed = discord.Embed(description=msg[1], colour=discord.Colour.dark_green())
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def embed_jacob(self, ctx):
        '''
        (ADM) Sends Jacob's moderator card.
        '''
        await ctx.message.delete()
        embed = discord.Embed(description="**Staff Card**", colour=5833416, timestamp=ctx.message.created_at)
        embed.add_field(name="👤 Username : Jacob#7638",
                        value="Hi, I'm Jacob and my DM's are always open if you need anything at all (at ALL)",
                        inline=False)
        embed.add_field(name="👮‍Moderator",
                        value="My main task is to ensure that people who violate any rules put in place in this server be penalized and make sure the server is a safe, healthy environment.",
                        inline=False)
        embed.add_field(name="👅 Languages", value="➖", inline=True)
        embed.add_field(name="➖", value=":flag_us:**English** 🔹🔹🔹", inline=True)
        embed.add_field(name="➖", value=":flag_es:**Spanish** 🔹", inline=True)
        embed.set_footer(text='Cosmos',
                         icon_url='https://cdn.discordapp.com/avatars/423829836537135108/da15dea5017edf5567e531fc6b97f935.jpg?size=2048')
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/avatars/328194044587147278/a_a635379c73404bd2894ca268e28328a7.gif')
        embed.set_author(name='The Language Sloth', url='https://discordapp.com',
                         icon_url='https://cdn.discordapp.com/attachments/562019489642709022/676564604087697439/ezgif.com-gif-maker_1.gif')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def embed_rules(self, ctx):
        '''
        (ADM) Sends an embedded message containing all rules in it.
        '''
        await ctx.message.delete()
        embed = discord.Embed(title="Discord’s Terms of Service and Community Guidelines",
                              description="Rules Of The Server", url='https://discordapp.com/guidelines',
                              colour=1406210,
                              timestamp=ctx.message.created_at)
        embed.add_field(name="#1 No NSFW",
                        value="Do not post or talk about NSFW content in text or voice chat. This server is a safe for work",
                        inline=False)
        embed.add_field(name="#2 Respect at all times.", value="Be respectful of all members, especially Staff.",
                        inline=False)
        embed.add_field(name="#3 Avoid Controversy",
                        value="Avoid topics such as: Politics,Religion,Self-Harm or anything considered controversial anywhere in the server except in the **Debate Club**",
                        inline=False)
        embed.add_field(name="#4 No Advertising",
                        value="Do not advertise your server or other communities without express consent from an Owner of this server.",
                        inline=False)
        embed.add_field(name="#5 No Doxing", value="Do not share others' personal information without their consent.",
                        inline=False)
        embed.add_field(name="#6 No Spamming",
                        value="Do not flood or spam the text chat. Do not staff members repeatedly without a reason.",
                        inline=False)
        embed.add_field(name="#7 No Earrape",
                        value="No ear rape or mic spam. If you have a loud background, go on push-to-talk or mute.",
                        inline=False)
        embed.add_field(name="#8 Resolve your own disputes",
                        value="Try to settle disputes personally. You may mute or block a user. If you cannot resolve the issue, contact staff in <#729454413290143774>",
                        inline=False)
        embed.add_field(name="#9 Do not impersonate others", value="Do not impersonate users or member of the staff",
                        inline=False)
        embed.add_field(name="#10 No Begging",
                        value="No asking to be granted roles/moderator roles, you may apply by accessing the link in <#562019353583681536> but begging the staff repeatedly and irritatingly will result in warnings or even ban.",
                        inline=False)
        embed.add_field(name="<:zzSloth:686237376510689327>", value="Have fun!", inline=True)
        embed.add_field(name="<:zzSloth:686237376510689327>", value="Check our lessons!", inline=True)
        embed.set_footer(text='Cosmos',
                         icon_url='https://cdn.discordapp.com/avatars/423829836537135108/da15dea5017edf5567e531fc6b97f935.jpg?size=2048')
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/562019489642709022/676564604087697439/ezgif.com-gif-maker_1.gif')
        embed.set_author(name='The Language Sloth', url='https://discordapp.com',
                         icon_url='https://cdn.discordapp.com/attachments/562019489642709022/676564604087697439/ezgif.com-gif-maker_1.gif')
        await ctx.send(
            content="Hello, **The Language Sloth** is a public Discord server for people all across the globe to meet ,learn languages and exchange cultures. here are our rules of conduct.",
            embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def embed_join_us(self, ctx):
        '''
        (ADM) Sends the join-us embedded message.
        '''
        await ctx.message.delete()
        embed = discord.Embed(title="Join our Staff!",
                              description="```We depend on people like you to keep this community running, and any help is welcome. if you feel like you would like to contribute apply to any of the positions below: ```",
                              url='https://docs.google.com/forms/d/1H-rzl9AKgfH1WuKN7nYAW-xJx411Q4-HxfPXuPUFQXs',
                              colour=2788104, timestamp=ctx.message.created_at)
        embed.add_field(name=":police_officer: Become a Moderator",
                        value='Would you like to help us by mediating conflicts in the voice channels and becoming an official part of our staff? [Click here to apply](https://docs.google.com/forms/d/e/1FAIpQLSfFXh7GrwftdDro6iqtuw9W4-G2dZfhqvCcEB1jQacQMdNJtA/viewform)',
                        inline=False)
        embed.add_field(name=":man_teacher: Become a Teacher",
                        value="Do you want to teach on our server? Since this community is made by people like you, we are always looking for people to join our ranks ! Teach your native language here ! [Click here to apply](https://docs.google.com/forms/d/1H-rzl9AKgfH1WuKN7nYAW-xJx411Q4-HxfPXuPUFQXs)",
                        inline=False)
        embed.add_field(name="All positions are unsalaried, for professional enquiry please get in touch.",
                        value="```Other available positions !```", inline=False)
        embed.add_field(name=":musical_note:  Karaoke Night Organizer",
                        value="We are looking for someone to take over the **Karaoke Night** event, A 40 minute per week event that would unite people in a voice chat to sing karaoke.You would have to organize and screenshare karaoke songs on a given day of the week. To anyone interested in this position please contact <@423829836537135108> privately.",
                        inline=False)
        embed.add_field(name=":speaking_head: Moderator in the Debate Club",
                        value="We are searching for someone willing to moderate debates impartially once a week, Must have command of the English language and over 16 years old.",
                        inline=False)
        embed.add_field(name="Apply now!", value="Or Later?", inline=True)
        embed.add_field(name="Apply Tomorrow!", value="Or after tomorrow?", inline=True)
        embed.set_footer(text='Cosmos',
                         icon_url='https://cdn.discordapp.com/avatars/423829836537135108/da15dea5017edf5567e531fc6b97f935.jpg?size=2048')
        embed.set_thumbnail(url='https://i.imgur.com/bFfenC9.png')
        embed.set_image(url='https://cdn.discordapp.com/attachments/668049600871006208/689196815509094403/unnamed.png')
        embed.set_author(name='The Language Sloth', url='https://discordapp.com',
                         icon_url='https://cdn.discordapp.com/attachments/562019489642709022/676564701399744512/jungle_2.gif')
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Embeds(client))
