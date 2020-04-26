import discord
from discord.ext import commands
import wikipedia, os
from chatbot import Chat, register_call

chat_room_id = 703968197988188170
template_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"../chatbotTemplate","chatbottemplate.template")
chat=Chat(template_file_path)

@register_call("whoIs")
def who_is(query, session_id="general"):
    try:
        return wikipedia.summary(query)
    except Exception:
        for new_query in wikipedia.search(query):
            try:
                return wikipedia.summary(new_query)
            except Exception:
                pass
    return "I don't know about " + query

class ChatterSloth(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("The bot is ready!")


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.channel.id == chat_room_id:
            if message.content[3:].startswith(str(self.client.user.mention)[2:]):
                if len(message.content.split()) < 2:
                    return await message.channel.send('**?**')

                msg = message.content.split(f'{self.client.user.mention[2:]}', 1)
                msg = msg[1].strip()
                await self.chatbot(message.channel, msg)
            else:
                await message.delete()


    async def chatbot(self, channel, message):
        result = chat.respond(message)
        if (len(result) <= 2048):
            embed = discord.Embed(title=f"{self.client.user} says:", description=result, colour=discord.Colour.green())
            await channel.send(embed=embed)
        else:
            embedList = []
            n = 2048
            embedList = [result[i:i + n] for i in range(0, len(result), n)]
            for num, item in enumerate(embedList, start=1):
                if (num == 1):
                    embed = discord.Embed(title=f"{self.client.user} says:", description=item, colour=discord.Colour.green())
                    embed.set_footer(text="Page {}".format(num))
                    await channel.send(embed=embed)
                else:
                    embed = discord.Embed(description=item, colour=discord.Colour.green())
                    embed.set_footer(text="Page {}".format(num))
                    await channel.send(embed=embed)

def setup(client):
    client.add_cog(ChatterSloth(client))
