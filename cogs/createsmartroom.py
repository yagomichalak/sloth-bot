import discord
from discord.ext import commands
from extra.smartrooms.rooms import BasicRoom, PremiumRoom, GalaxyRoom, SmartRoom
from extra.smartrooms.database_commands import SmartRoomDatabase

from extra import utils

class CreateSnartRoom(SmartRoomDatabase):

	def __init__(self, client: commands.Cog) -> None:
		self.client = client
		# self.db: SmartRoomDatabase = SmartRoomDatabase()


	@commands.command()
	async def create_room(self, ctx) -> None:
		""" Test command for creating rooms. """

		author: discord.Member = ctx.author
		guild: discord.Guild = ctx.guild

		cat: discord.CategoryChannel = discord.utils.get(guild.categories, id=777886759957823522)
		vc: discord.VoiceChannel = await guild.create_voice_channel(name=str(ctx.author), category=cat)

		current_ts: int = await utils.get_timestamp()

		try:
			await self.insert_smartroom(author.id, 'basic', vc.id, current_ts)
		except Exception as e:
			print(e)
			await ctx.reply("**An error occurred!**")
		else:
			await ctx.reply(f"Created VC {vc.mention}")


	@commands.command()
	async def get_room(self, ctx, room_id: int = None) -> None:
		""" Test command for getting rooms. """

		author: discord.Member = ctx.author

		if not room_id: return

		
		smart_room: SmartRoom = await self.get_smartroom(
			user_id=author.id, vc_id=room_id
		)

		print('dsauhdsahu', type(smart_room))


def setup(client: commands.Bot) -> None:
	""" Cog's setup function. """

	client.add_cog(CreateSnartRoom(client))