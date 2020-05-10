import discord
from discord.ext import commands
from random import randint, choice
from cogs.slothcurrency import SlothCurrency
from datetime import datetime
import aiohttp


class Misc(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Misc cog is online!")


    @commands.command()
    async def dice(self, ctx):
        '''Rolls a certain number of dice'''
        await ctx.message.delete()
        em = discord.Embed(color=ctx.author.color, title=f":game_die: **YOU GOT:** `{randint(1, 6)}` :game_die:",
                           timestamp=ctx.message.created_at)
        em.set_footer(text=f"Dice rolled by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command(aliases=['8ball'])
    async def eightball(self, ctx, *, question: str = None):
        '''Ask the 8 ball a question'''
        await ctx.message.delete()
        if not question:
            return await ctx.send("**Inform a question!**", delete_after=3)
        elif not question.endswith('?'):
            return await ctx.send('**Please ask a question.**', delete_after=3)

        responses = ["It is certain", "It is decidedly so", "Without a doubt", "Yes definitely",
                     "You may rely on it", "As I see it, yes", "Most likely", "Outlook good",
                     "Yes", "Signs point to yes", "Reply hazy try again", "Ask again later",
                     "Better not tell you now", "Cannot predict now", "Concentrate and ask again",
                     "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good",
                     "Very doubtful"]

        num = randint(0, len(responses) - 1)
        if num < 10:
            em = discord.Embed(color=discord.Color.green())
        elif num < 15:
            em = discord.Embed(color=discord.Color(value=0xffff00))
        else:
            em = discord.Embed(color=discord.Color.red())

        response = responses[num]

        em.title = f"🎱**{question}**"
        em.description = response
        await ctx.send(embed=em)

    @commands.command(aliases=['coin'])
    async def flipcoin(self, ctx):
        '''Flips a coin'''
        await ctx.message.delete()
        choices = ['You got Heads', 'You got Tails']
        em = discord.Embed(color=ctx.author.color, title='Coinflip:', description=choice(choices),
                           timestamp=ctx.message.created_at)
        em.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)

    @commands.command(aliases=['lotto'])
    async def lottery(self, ctx, g1=None, g2=None, g3=None):
        '''
        Enter the lottery and see if you win!
        :param g1: Guess 1.
        :param g2: Guess 2.
        :param g3: Guess 3.
        '''
        await ctx.message.delete()
        if not g1:
            self.client.get_command('lottery').reset_cooldown(ctx)
            return await ctx.send("**You informed 0 guesses, 3 guesses are needed!**", delete_after=3)
        elif not g2:
            self.client.get_command('lottery').reset_cooldown(ctx)
            return await ctx.send("**You informed 1 guess, 3 guesses are needed!**", delete_after=3)
        elif not g3:
            self.client.get_command('lottery').reset_cooldown(ctx)
            return await ctx.send("**You informed 2 guesses, 3 guesses are needed!**", delete_after=3)

        try:
            g1 = int(g1)
            g2 = int(g2)
            g3 = int(g3)
        except ValueError:
            await self.client.get_command('lottery').reset_cooldown(ctx)
            return await ctx.send("**All guesses must be integers!**", delete_after=3)

        for n in [g1, g2, g3]:
            if not int(n) > 0 and int(n) <= 5:
                await self.client.get_command('lottery').reset_cooldown(ctx)
                return await ctx.send(f"**Each number must be between 1-5!**", delete_after=3)

        # Check if user is not on cooldown
        user_secs = await SlothCurrency.get_user_currency(ctx, ctx.author.id)
        epoch = datetime.utcfromtimestamp(0)
        the_time = (datetime.utcnow() - epoch).total_seconds()
        if not user_secs:
            await SlothCurrency.insert_user_currency(ctx, ctx.author.id, the_time - 61)
            user_secs = await SlothCurrency.get_user_currency(ctx, ctx.author.id)

        if user_secs[0][6]:
            sub_time = the_time - user_secs[0][6]
            if sub_time >= 1200:
                await SlothCurrency.update_user_lotto_ts(ctx, ctx.author.id, the_time)
            else:
                m, s = divmod(1200 - int(sub_time), 60)
                h, m = divmod(m, 60)
                if h > 0:
                    return await ctx.send(f"**You're on cooldown, try again in {h:d} hours, {m:02d} minutes and {s:02d} seconds.**", delete_after=5)
                elif m > 0:
                    return await ctx.send(
                        f"**You're on cooldown, try again in {m:02d} minutes and {s:02d} seconds.**",
                        delete_after=5)
                else:
                    return await ctx.send(
                        f"**You're on cooldown, try again in {s:02d} seconds.**",
                        delete_after=5)
        else:
            await SlothCurrency.update_user_lotto_ts(ctx, ctx.author.id, the_time)

        author = ctx.author
        numbers = []
        for x in range(3):
            numbers.append(randint(1, 5))

        string_numbers = [str(i) for i in numbers]
        if g1 == numbers[0] and g2 == numbers[1] and g3 == numbers[2]:
            await ctx.send(f'**{author.mention} You won! Congratulations on winning the lottery with the numbers ({g1}, {g2},{g3})!🍃+100łł!**')
            if not await SlothCurrency.get_user_currency(ctx, ctx.author.id):

                await SlothCurrency.insert_user_currency(ctx, ctx.author.id, the_time - 61)
            await SlothCurrency.update_user_money(ctx, ctx.author.id, 100)

        else:
            await ctx.send(
                f"**{author.mention}, better luck next time... You guessed {g1}, {g2}, {g3}...\nThe numbers were:** `{', '.join(string_numbers)}`")


    @commands.command(aliases=['number'])
    async def numberfact(self, ctx, number: int = None):
        '''Get a fact about a number.'''
        if not number:
            await ctx.send(f'**Usage: `{ctx.prefix}numberfact <number>`**', delete_after=3)
            return
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'http://numbersapi.com/{number}?json') as resp:
                    file = await resp.json()
                    fact = file['text']
                    await ctx.send(f"**Did you know?**\n*{fact}*")
        except KeyError:
            await ctx.send("**No facts are available for that number.**", delete_after=3)


def setup(client):
    client.add_cog(Misc(client))
