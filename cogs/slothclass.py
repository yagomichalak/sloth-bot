import discord
from discord.ext import commands
from mysqldb import the_database
from typing import Union, List, Any
from extra.customerrors import MissingRequiredSlothClass

class SlothClass(commands.Cog):
	""" A category for the Sloth Class system. """

	def __init__(self, client) -> None:
		""" Class initializing method. """

		self.client = client

	@commands.Cog.listener()
	async def on_ready(self) -> None:
		""" Tells when the cog is ready to use. """

		print("SlothClass cog is online")


	@commands.command(aliases=['sloth_class'])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def sloth_classes(self, ctx) -> None:

		mycursor, db = await the_database()
		await mycursor.execute("""
		    SELECT sloth_class, COUNT(sloth_class) FROM UserCurrency 
		    WHERE sloth_class != 'default'
		    GROUP BY sloth_class
		    """)

		sloth_classes = await mycursor.fetchall()
		await mycursor.close()
		sloth_classes = [f"[Class]: {sc[0]:<10} | [Count]: {sc[1]}\n" for sc in sloth_classes]
		embed = discord.Embed(
		    title="__Sloth Classes__",
		    description=f"```ini\n{''.join(sloth_classes)}```",
		    color=ctx.author.color,
		    timestamp=ctx.message.created_at,
		    url='https://thelanguagesloth.com/profile/slothclass'
		)

		await ctx.send(embed=embed)

	def user_is_class(command_class):
		""" Checks whether the user has the required Sloth Class to run the command. 
		:param command_class: The Sloth Class required to run that command. """

		async def get_user_sloth_class(user_id: int) -> Union[str, bool]:
			""" Gets the user Sloth Class from the database.
			:param user_id: The ID of the user to get the Sloth Class. """

			mycursor, db = await the_database()
			await mycursor.execute("SELECT sloth_class FROM UserCurrency WHERE user_id = %s", (user_id,))
			user_sloth_class = await mycursor.fetchone()		
			await mycursor.close()
			if user_sloth_class:
				return user_sloth_class[0]
			else:
				return None

		async def real_check(ctx):
			""" Perfoms the real check. """

			user_sloth_class = await get_user_sloth_class(ctx.author.id)
			if user_sloth_class and user_sloth_class.lower() == command_class:
				return True
			raise MissingRequiredSlothClass(required_class=command_class, error_message="You don't have the required Sloth Class to run this command!")
		return commands.check(real_check)

	@commands.command()
	@user_is_class('warrior')
	async def claw_attack(self, ctx) -> None:
		""" A command for Warriors. """

		return await ctx.send("**Command not ready yet!**")


	@commands.command()
	@user_is_class('metamorph')
	async def transmutation(self, ctx) -> None:
		""" A command for Metamorphs. """

		return await ctx.send("**Command not ready yet!**")

	@commands.command()
	@user_is_class('agares')
	async def magical_armor(self, ctx) -> None:
		""" A command for Agares. """

		return await ctx.send("**Command not ready yet!**")

	@commands.command()
	@user_is_class('cybersloth')
	async def energy_boost(self, ctx) -> None:
		""" A command for Cybersloths. """

		return await ctx.send("**Command not ready yet!**")

	@commands.command()
	@user_is_class('merchant')
	async def open_shop(self, ctx) -> None:
		""" A command for Merchants. """

		return await ctx.send("**Command not ready yet!**")

	@commands.command()
	@user_is_class('seraph')
	async def divine_protection(self, ctx) -> None:
		""" A command for Seraphs. """

		return await ctx.send("**Command not ready yet!**")

	@commands.command()
	@user_is_class('prawler')
	async def steal(self, ctx) -> None:
		""" A command for Prawlers. """

		return await ctx.send("**Command not ready yet!**")

	@commands.command()
	@user_is_class('munk')
	async def soul_search(self, ctx) -> None:
		""" A command for Munks. """

		return await ctx.send("**Command not ready yet!**")


def setup(client) -> None:
	""" Cog's setup function. """

	client.add_cog(SlothClass(client))