import discord
from discord.app.commands import slash_command, message_command, user_command, Option, OptionChoice
from discord.ext import commands, menus
import asyncio
from gtts import gTTS

from googletrans import Translator
import inspect
import io
import textwrap
import traceback
import collections
from contextlib import redirect_stdout
import os
from treelib import Tree
import json

from datetime import datetime
import pytz
from pytz import timezone
from mysqldb import the_database

from extra.slothclasses.player import Player
from extra.menu import InroleLooping, InchannelLooping
from extra.prompt.menu import Confirm
from extra.useful_variables import patreon_roles
from extra import utils

from extra.view import SoundBoardView, BasicUserCheckView
from extra.select import SoundBoardSelect

from extra.tool.stealthstatus import StealthStatusTable

guild_ids = [int(os.getenv('SERVER_ID'))]

from typing import List, Optional, Union

mod_role_id = int(os.getenv('MOD_ROLE_ID'))
senior_mod_role_id: int = int(os.getenv('SENIOR_MOD_ROLE_ID'))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID'))
owner_role_id = int(os.getenv('OWNER_ROLE_ID'))
analyst_debugger_role_id: int = int(os.getenv('ANALYST_DEBUGGER_ROLE_ID'))
in_a_vc_role_id: int = int(os.getenv('IN_A_VC_ROLE_ID'))


allowed_roles = [owner_role_id, admin_role_id, mod_role_id, *patreon_roles.keys(), int(os.getenv('SLOTH_LOVERS_ROLE_ID'))]
teacher_role_id = int(os.getenv('TEACHER_ROLE_ID'))
patreon_channel_id = int(os.getenv('PATREONS_CHANNEL_ID'))

popular_lang_cat_id = int(os.getenv('LANGUAGES_CHANNEL_ID'))
more_popular_lang_cat_id = int(os.getenv('MORE_LANGUAGES_CHANNEL_ID'))
smart_room_cat_id = int(os.getenv('CREATE_SMART_ROOM_CAT_ID'))

dynamic_vc_id: int = int(os.getenv('CREATE_DYNAMIC_ROOM_VC_ID'))
dynamic_channels_cat_id = int(os.getenv('CREATE_DYNAMIC_ROOM_CAT_ID'))
tool_cogs: List[commands.Cog] = [
	StealthStatusTable
]

class Tools(*tool_cogs):
	""" Some useful tool commands. """

	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		print('Tools cog is ready!')

	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after) -> None:
		""" Removes the 'in a VC' role from people who are in the stealth mode,
		upon joining VCs. """

		if after.channel:
			role = member.get_role(in_a_vc_role_id)
			if not role:
				return

			stealth_status = await self.get_stealth_status(member.id)
			if not stealth_status or not stealth_status[1]:
				return

			await member.remove_roles(role)

	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		""" Removes the 'in a VC' role from people who are in the stealth mode,
		upon getting roles. """

		if not after.guild:
			return

		roles = before.roles
		roles2 = after.roles
		if len(roles2) < len(roles):
			return

		new_role = None

		for r2 in roles2:
			if r2 not in roles:
				new_role = r2
				break

		if new_role:
			role = after.get_role(in_a_vc_role_id)
			if not role:
				return

			stealth_status = await self.get_stealth_status(after.id)
			if not stealth_status or not stealth_status[1]:
				return

			try:
				await after.remove_roles(role)
			except:
				pass


	@commands.Cog.listener()
	async def on_message(self, message) -> None:
		""" Reacts to messages sent in Lesson Announcement channels. """
		
		if not message.guild:
			return

		channel = message.channel

		announcement_channels: List[int] = [
			576793212304228352, 801514509424525363, 799394160096444456,
			761303171833790464, 784499538366824488, 760958206683643975, 
			852918933786066984, 860637056682426388, 890621139297128548,
			872477233179152414, 871785544361840690, 870437619522236427
		]

		if channel.id in announcement_channels:
			try:
				await message.add_reaction('✅')
			except:
				pass

	@commands.command(aliases=["in_role"])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def inrole(self, ctx, roles: commands.Greedy[discord.Role] = None) -> None:
		""" Shows everyone who has that role in the server.
		:param roles: The set of roles you want to check. """

		member = ctx.author

		if not roles:
			return await ctx.send(f"**Please, inform at least one role, {member.mention}!**")

		roles: List[discord.Role] = list(set(roles))
		
		members = [
			m.mention for m in ctx.guild.members
			if (m_inter := set(m.roles).intersection(set(roles))) and len(m_inter) == len(roles)
		]

		if members:
			additional = {
				'roles': roles
			}
			pages = menus.MenuPages(source=InroleLooping(members, **additional), clear_reactions_after=True)
			await pages.start(ctx)
		else:
			return await ctx.send(f"**No one has this role, {member.mention}!**")

	@commands.command(aliases=["in_channel"])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def inchannel(self, ctx, channel: Union[discord.TextChannel, discord.VoiceChannel] = None) -> None:
		""" Shows everyone who has permissions in a particular channel.
		:param roles: The set of roles you want to check. """

		member = ctx.author
		if not channel:
			channel = ctx.channel
		
		members = [ow.mention for ow in channel.overwrites.keys() if isinstance(ow, discord.Member)]
		if not members:
			return await ctx.send(f"**No one has permissions in this channel, {member.mention}!**")

		# embed = discord.Embed(description=', '.join(members))
		# await ctx.send(embed=embed)

		if members:
			additional = {
				'channel': channel
			}
			pages = menus.MenuPages(source=InchannelLooping(members, **additional), clear_reactions_after=True)
			await pages.start(ctx)
		else:
			return await ctx.send(f"**No one has this role, {member.mention}!**")

	@commands.command(aliases=["ping_inrole", "pir"])
	@commands.cooldown(1, 5, commands.BucketType.user)
	@utils.is_allowed(allowed_roles)
	async def ping_intersection_role(self, ctx, roles: commands.Greedy[discord.Role] = None) -> None:
		""" Shows everyone who have that role in the server.
		:param roles: The set of roles you want to check. """

		member = ctx.author

		await ctx.message.delete()

		if not roles:
			return await ctx.send(f"**Please, inform at least one role, {member.mention}!**")

		roles: List[discord.Role] = list(set(roles))
		
		members = [
			m for m in ctx.guild.members
			if (m_inter := set(m.roles).intersection(set(roles))) and len(m_inter) == len(roles)
		]

		if members:
			# create role
			temp_role = await ctx.guild.create_role(name="temporary role")

			# send disclaimer message
			tmp_message = await ctx.send(f"Wait! this command may take several minutes...")

			# add role to members
			for member in members:
				await member.add_roles(temp_role)

			# delete disclaimer message
			tmp_message.delete()

			# send ping
			tmp_message = await ctx.send(f"{temp_role.mention}")

			# remove message and role
			await tmp_message.delete()
			await temp_role.delete()
		else:
			return await ctx.send(f"**No one has this role, {member.mention}!**")


	# Countsdown from a given number
	@commands.command()
	@utils.is_allowed([senior_mod_role_id], throw_exc=True)
	async def count(self, ctx, amount=0):
		""" (ADM) Countsdown by a given number
		:param amount: The start point. """

		await ctx.message.delete()
		if amount > 0:
			msg = await ctx.send(f'**{amount}**')
			await asyncio.sleep(1)
			for x in range(int(amount) - 1, -1, -1):
				await msg.edit(content=f'**{x}**')
				await asyncio.sleep(1)
			await msg.edit(content='**Done!**')
		else:
			await ctx.send('Invalid parameters!')

	# Bot leaves
	@commands.command()
	@utils.is_allowed([mod_role_id, admin_role_id, owner_role_id], throw_exc=True)
	async def leave(self, ctx):
		""" (MOD) Makes the bot leave the voice channel. """

		guild = ctx.message.guild
		voice_client = guild.voice_client
		user_voice = ctx.message.author.voice

		if voice_client:
			if user_voice.channel == voice_client.channel:
				await voice_client.disconnect()
				await ctx.send('**Disconnected!**')
			else:
				await ctx.send("**You're not in the bot's voice channel!**")
		else:
			await ctx.send("**I'm not even in a channel, lol!**")

	@commands.command(aliases=['talk'])
	@commands.cooldown(1, 5, type=commands.BucketType.guild)
	@utils.is_allowed([*allowed_roles, analyst_debugger_role_id], throw_exc=True)
	@Player.poisoned()
	async def tts(self, ctx, language: str = None, *, message: str = None):
		'''
		(BOOSTER) Reproduces a Text-to-Speech message in the voice channel.
		:param language: The language of the message.
		:param message: The message to reproduce.
		'''
		await ctx.message.delete()
		if not language:
			return await ctx.send("**Please, inform a language!**", delete_after=5)
		elif not message:
			return await ctx.send("**Please, inform a message!**", delete_after=5)

		voice = ctx.message.author.voice
		voice_client = ctx.message.guild.voice_client

		# Checks if the user is in a voice channel
		if voice is None:
			return await ctx.send("**You're not in a voice channel**")
		voice_client: discord.VoiceClient = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

		# Checks if the bot is in a voice channel
		if not voice_client:
			await voice.channel.connect()
			voice_client: discord.VoiceClient = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

		# Checks if the bot is in the same voice channel that the user
		if voice.channel == voice_client.channel:
			# Plays the song
			if not voice_client.is_playing():
				tts = gTTS(text=message, lang=language)
				tts.save(f'tts/audio.mp3')
				audio_source = discord.FFmpegPCMAudio('tts/audio.mp3')
				voice_client.play(audio_source, after=lambda e: print('finished playing the tts!'))
		else:
			await ctx.send("**The bot is in a different voice channel!**")

	@commands.command(name="translate", aliases=["tr"])
	@Player.poisoned()
	async def _tr_command(self, ctx, language: str = None, *, message: str = None) -> None:
		""" Translates a message into another language.
		:param language: The language to translate the message to.
		:param message: The message to translate.
		:return: A translated message. """

		await ctx.message.delete()
		if not language:
			return await ctx.send("**Please, inform a language!**", delete_after=5)
		elif not message:
			return await ctx.send("**Please, inform a message to translate!**", delete_after=5)

		await self._tr_callback(ctx, language, message, True)


	@message_command(name="Translate", guild_ids=guild_ids)
	@Player.poisoned()
	async def _tr_slash(self, ctx, message: discord.Message) -> None:
		""" Translates a message into another language. """

		await ctx.defer(ephemeral=True)
		language: str = 'en'    
		await self._tr_callback(ctx, language, message.content)


	async def _tr_callback(self, ctx, language: str = None, message: str = None, show_src: bool = False) -> None:
		""" Translates a message into another language.
		:param language: The language to translate the message to.
		:param message: The message to translate.
		:param show_src: Whether to show the source message. """

		answer: discord.PartialMessageable = None
		if isinstance(ctx, commands.Context):
			answer = ctx.send
		else:
			answer = ctx.respond

		trans = Translator(service_urls=['translate.googleapis.com'])
		current_time = await utils.get_time_now()
		try:
			translation = trans.translate(f'{message}', dest=f'{language}')
		except ValueError:
			return await answer("**Invalid parameter for 'language'!**", delete_after=5)

		embed = discord.Embed(title="__Sloth Translator__", color=ctx.author.color, timestamp=current_time)

		if show_src:
			embed.add_field(name=f"__{translation.src}:__", value=f"```{message}```", inline=False)
		embed.add_field(name=f"__{translation.dest}:__", value=f"```{translation.text}```", inline=False)

		embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
		embed.set_footer(text=f"{translation.src} -> {translation.dest}")
		await answer(embed=embed)

	@commands.command()
	@Player.poisoned()
	async def ping(self, ctx):
		""" Show the latency. """

		await ctx.send(f"**:ping_pong: Pong! {round(self.client.latency * 1000)}ms.**")

	@commands.command()
	@Player.poisoned()
	async def math(self, ctx, v1=None, oper: str = None, v2=None):
		'''
		Calculates something.
		:param v1: The value 1.
		:param oper: The operation/operator.
		:param v2: The value 2.
		'''
		await ctx.message.delete()
		if not v1:
			return await ctx.send("**Inform the values to calculate!**", delete_after=3)
		elif not oper:
			return await ctx.send("**Inform the operator to calculate!**", delete_after=3)
		elif not v2:
			return await ctx.send("**Inform the second value to calculate!**", delete_after=3)

		try:
			v1 = float(v1)
			v2 = float(v2)
		except ValueError:
			return await ctx.send("**Invalid value parameter!**", delete_after=3)

		operators = {'+': (lambda x, y: x + y), "plus": (lambda x, y: x + y), '-': (lambda x, y: x - y),
					 "minus": (lambda x, y: x - y),
					 '*': (lambda x, y: x * y), "times": (lambda x, y: x * y), "x": (lambda x, y: x * y),
					 '/': (lambda x, y: x / y),
					 '//': (lambda x, y: x // y), "%": (lambda x, y: x % y), }
		if not oper.lower() in operators.keys():
			return await ctx.send("**Invalid operator!**", delete_after=3)

		embed = discord.Embed(title="__Math__",
							  description=f"`{v1}` **{oper}** `{v2}` **=** `{operators[oper](v1, v2)}`",
							  colour=ctx.author.color, timestamp=ctx.message.created_at)
		embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar)
		return await ctx.send(embed=embed)

	@commands.command()
	@commands.is_owner()
	async def eval(self, ctx, *, body=None):
		'''
		(ADM) Executes a given command from Python onto Discord.
		:param body: The body of the command.
		'''
		await ctx.message.delete()
		if not body:
			return await ctx.send("**Please, inform the code body!**")

		"""Evaluates python code"""
		env = {
			'ctx': ctx,
			'client': self.client,
			'channel': ctx.channel,
			'author': ctx.author,
			'guild': ctx.guild,
			'message': ctx.message,
			'source': inspect.getsource
		}

		def cleanup_code(content):
			"""Automatically removes code blocks from the code."""
			# remove ```py\n```
			if content.startswith('```') and content.endswith('```'):
				return '\n'.join(content.split('\n')[1:-1])

			# remove `foo`
			return content.strip('` \n')

		def get_syntax_error(e):
			if e.text is None:
				return f'```py\n{e.__class__.__name__}: {e}\n```'
			return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

		env.update(globals())

		body = cleanup_code(body)
		stdout = io.StringIO()
		err = out = None

		to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

		def paginate(text: str):
			'''Simple generator that paginates text.'''
			last = 0
			pages = []
			for curr in range(0, len(text)):
				if curr % 1980 == 0:
					pages.append(text[last:curr])
					last = curr
					appd_index = curr
			if appd_index != len(text)-1:
				pages.append(text[last:curr])
			return list(filter(lambda a: a != '', pages))

		try:
			exec(to_compile, env)
		except Exception as e:
			err = await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
			return await ctx.message.add_reaction('\u2049')

		func = env['func']
		try:
			with redirect_stdout(stdout):
				ret = await func()
		except Exception as e:
			value = stdout.getvalue()
			err = await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
		else:
			value = stdout.getvalue()
			if ret is None:
				if value:
					try:

						out = await ctx.send(f'```py\n{value}\n```')
					except:
						paginated_text = paginate(value)
						for page in paginated_text:
							if page == paginated_text[-1]:
								out = await ctx.send(f'```py\n{page}\n```')
								break
							await ctx.send(f'```py\n{page}\n```')
			else:
				try:
					out = await ctx.send(f'```py\n{value}{ret}\n```')
				except:
					paginated_text = paginate(f"{value}{ret}")
					for page in paginated_text:
						if page == paginated_text[-1]:
							out = await ctx.send(f'```py\n{page}\n```')
							break
						await ctx.send(f'```py\n{page}\n```')

		if out:
			await ctx.message.add_reaction('\u2705')  # tick
		elif err:
			await ctx.message.add_reaction('\u2049')  # x
		else:
			await ctx.message.add_reaction('\u2705')

	@commands.command(aliases=['mivc'])
	@commands.cooldown(1, 5, commands.BucketType.user)
	@Player.poisoned()
	async def member_in_vc(self, ctx, vc: Optional[discord.VoiceChannel] = None) -> None:
		""" Tells how many users are in the voice channel.
		:param vc: The Voice Channel to check. [Optional][Default = all vcs] """

		if vc:
			await ctx.send(f"**`{len(vc.members)}` members are in the {vc.mention} vc atm!**")
		else:
			vcs = ctx.guild.voice_channels
			all_members = [m.name for vc in vcs for m in vc.members]
			await ctx.send(f"**`{len(all_members)}` members are in a vc atm!**")

	@commands.command(aliases=['stalk', 'voice_channel'])
	@utils.is_allowed([*allowed_roles, analyst_debugger_role_id], throw_exc=True)
	async def vc(self, ctx) -> None:
		""" Tells where the given member is at (voice channel).
		:param member: The member you are looking for. """

		author: discord.Member = ctx.author

		members = await utils.get_mentions(ctx.message)

		if not members:
			members = [author]

		members_in_vc: List[str] = []

		for member in members:
			member_state = member.voice
			if channel := member_state and member_state.channel:
				members_in_vc.append(f"{member.mention} **-** {channel.mention}")
			else:
				members_in_vc.append(f"{member.mention} is not in a VC!")


		if len(members_in_vc) > 1:
			embed = discord.Embed(
				title="__Members' VCs__",
				description='\n'.join(members_in_vc),
				color=author.color,
				timestamp=ctx.message.created_at
			)
			embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)
			await ctx.send(embed=embed)
		else:
			await ctx.send(members_in_vc[0])

	@commands.command(aliases=['mag'], hidden=True)
	@commands.cooldown(1, 300, commands.BucketType.guild)
	@commands.has_permissions(administrator=True)
	async def magnet(self, ctx) -> None:
		""" Magnets all users who are in the voice channel into a single channel. """

		vcs = ctx.guild.voice_channels
		all_members = [m for vc in vcs for m in vc.members]

		# Checks user's channel state
		user_state = ctx.author.voice
		if not user_state:
			self.client.get_command('magnet').reset_cooldown(ctx)
			return await ctx.send("**You are not in a vc!**")

		confirm = await Confirm(f"{ctx.author.mention}, you sure you want to magnet everyone into `{user_state.channel}`?").prompt(ctx)
		if not confirm:
			self.client.get_command('magnet').reset_cooldown(ctx)
			return await ctx.send("**Not doing it, then!**")

		# Resolves bot's channel state
		bot_state = ctx.author.guild.voice_client

		try:
			if bot_state and bot_state.channel and bot_state.channel != user_state.channel:
				await bot_state.disconnect()
				await bot_state.move_to(user_state.channel)
			elif not bot_state:
				voicechannel = discord.utils.get(ctx.author.guild.channels, id=user_state.channel.id)
				vc = await voicechannel.connect()

			await asyncio.sleep(2)
			voice_client: discord.VoiceClient = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

			# Plays / and they don't stop commin' /
			if voice_client and not voice_client.is_playing():
				audio_source = discord.FFmpegPCMAudio('best_audio.mp3')
				voice_client.play(audio_source, after=lambda e: print("Finished trolling people!"))
			else:
				pass

		except Exception as e:
			print(e)
			return await ctx.send("**Something went wrong, I'll stop here!**")

		else:
			# Moves all members who are in the voice channel to the context channel.
			magneted_members = 0
			for member in all_members:
				try:
					await member.move_to(user_state.channel)
				except:
					pass
				else:
					magneted_members += 1
			else:
				await ctx.send(f"**They stopped comming, but we've gathered `{magneted_members}/{len(all_members)}` members!**")

	@commands.command(aliases=['mv', 'drag'])
	@utils.is_allowed([mod_role_id, admin_role_id, owner_role_id, analyst_debugger_role_id])
	async def move(self, ctx) -> None:
		""" Moves 1 or more people to a voice channel.
		Ps¹: If no channel is provided, the channel you are in will be used.
		Ps²: The voice channel can be in the following formats: <#id>, id, name.
		Ps³: The members can be in the following formats: <@id>, id, name, nick, display_name. """

		member = ctx.author
		channels = await utils.get_voice_channel_mentions(message=ctx.message)

		members = await utils.get_mentions(message=ctx.message)

		moved = not_moved = 0
		voice = voice.channel if (voice := member.voice) else None

		if not channels and not voice:
			return await ctx.send(f"**No channels were provided, and you are not in a channel either, {member.mention}!**")

		channels.append(voice)

		if not members:
			return await ctx.send(f"**No members were provided, {member.mention}!**")

		for m in members:
			try:
				await m.move_to(channels[0])
			except Exception as e:
				not_moved += 1
			else:
				moved += 1

		text = []
		if moved:
			text.append(f"**`{moved}` {'people were' if moved > 1 else 'person was'} moved to `{channels[0]}`!**")
		if not_moved:
			text.append(f"**`{not_moved}` {'people were' if moved > 1 else 'person was'} not moved!**")
		await ctx.send(' '.join(text))

	@commands.command(aliases=['tp', 'beam'])
	@utils.is_allowed([senior_mod_role_id], throw_exc=True)
	async def teleport(self, ctx, vc_1: discord.VoiceChannel = None, vc_2: discord.VoiceChannel = None) -> None:
		""" Teleports all members in a given voice channel to another one.
		:param vc_1: The origin vc.
		:param vc_2: The target vc. """

		member = ctx.author

		voice = voice.channel if (voice := member.voice) else None

		if not vc_1 and not vc_2:
			return await ctx.send(f"**Inform the voice channels, {member.mention}!**")

		if vc_1 and not vc_2:
			if not voice:
				return await ctx.send(f"**You provided just 1 VC, and you're not in one, so we can't make a target VC, {member.mention}!**")
			vc_1, vc_2 = voice, vc_1

		moved = not_moved = 0

		members = [m for m in vc_1.members]
		if not members:
			return await ctx.send(f"**No members found to move!**")

		for m in members:
			try:
				await m.move_to(vc_2)
			except:
				not_moved += 1
			else:
				moved += 1

		text = []
		if moved:
			text.append(f"**`{moved}` {'people were' if moved > 1 else 'person was'} moved from `{vc_1}` to `{vc_2}`!**")
		if not_moved:
			text.append(f"**`{not_moved}` {'people were' if moved > 1 else 'person was'} not moved!**")
		await ctx.send(' '.join(text))

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.user)
	@Player.poisoned()
	async def time(self, ctx: commands.Context, time: str = None, my_timezone: str = None) -> None:
		""" Tells the time in a given timezone, and compares to the CET one.
		:param time: The time you want to check. Ex: 7pm
		:param my_timezone: The time zone to convert """

		member = ctx.author
		default_timezone = timezone('Etc/GMT')

		user_timezone = await self.select_user_timezone(member.id)

		if not time:
			if user_timezone:
				time_now = datetime.now(timezone(user_timezone[1])).strftime(f"%H:%M {user_timezone[1]}")
			else:
				time_now = datetime.now(default_timezone).strftime(f"%H:%M {default_timezone}")

			return await ctx.send(f"**Now it's `{time_now}`, {member.mention}**")

		if not my_timezone:
			if not user_timezone:
				return await ctx.send(f"**Please, inform a `my_timezone`, {member.mention}!**")
			my_timezone = user_timezone[1]

		if my_timezone not in (timezones := pytz.all_timezones):
			return await ctx.send(f"**Please, inform a valid timezone, {member.mention}!**\n`(Type z!timezones to get a full list with the timezones in your DM's)`")

		# Given info (time and timezone)
		given_timezone = my_timezone.title()

		# Format given time
		given_date = datetime.strptime(time, '%H:%M')
		# print(f"Given date: {given_date.strftime('%H:%M')}")

		# Convert given date to given timezone
		time_now_here = await utils.get_time_now('Brazil/East')
		time_now_here = time_now_here.replace(hour=given_date.hour, minute=given_date.minute)
		time_now_there = await utils.get_time_now()
		converted_time = time_now_here.astimezone(default_timezone)

		datetime_text = f"**`{time_now_here.strftime('%H:%M')} ({given_timezone})` = `{converted_time.strftime('%H:%M')} ({default_timezone})`**"
		await ctx.send(datetime_text)

	@commands.command()
	@commands.cooldown(1, 300, commands.BucketType.user)
	async def timezones(self, ctx) -> None:
		""" Sends a full list with the timezones into the user's DM's.
		(Cooldown) = 5 minutes. """

		member = ctx.author

		timezones = pytz.all_timezones
		timezone_text = ', '.join(timezones)
		try:
			await Tools.send_big_message(title="Timezones:", channel=member, message=timezone_text, color=discord.Color.green())
		except Exception as e:
			ctx.command.reset_cooldown(ctx)
			await ctx.send(f"**I couldn't do it for some reason, make sure your DM's are open, {member.mention}!**")
		else:
			await ctx.send(f"**List sent into your DM's, {member.mention}!**")

	@staticmethod
	async def send_big_message(title, channel, message, color):
		""" Sends a big message to a given channel. """

		if (len(message) <= 2048):
			embed = discord.Embed(title=title, description=message, color=discord.Colour.green())
			await channel.send(embed=embed)
		else:
			embedList = []
			n = 2048
			embedList = [message[i:i + n] for i in range(0, len(message), n)]
			for num, item in enumerate(embedList, start=1):
				if (num == 1):
					embed = discord.Embed(title=title, description=item, color=discord.Colour.green())
					embed.set_footer(text=num)
					await channel.send(embed=embed)
				else:
					embed = discord.Embed(description=item, color=discord.Colour.green())
					embed.set_footer(text=num)
					await channel.send(embed=embed)

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def settimezone(self, ctx, my_timezone: str = None) -> None:
		""" Sets the timezone.
		:param my_timezone: Your timezone.
		Ps: Use z!timezones to get a full list with the timezones in your DM's. """

		member = ctx.author

		if not my_timezone:
			return await ctx.send(f"**Please, inform a timezone, {member.mention}!**")

		my_timezone = my_timezone.title()
		if my_timezone not in pytz.all_timezones:
			return await ctx.send(f"**Please, inform a valid timezone, {member.mention}!**")

		if user_timezone := await self.select_user_timezone(member.id):
			await self.update_user_timezone(member.id, my_timezone)
			await ctx.send(f"**Updated timezone from `{user_timezone[1]}` to `{my_timezone}`, {member.mention}!**")
		else:
			await self.insert_user_timezone(member.id, my_timezone)
			await ctx.send(f"**Set timezone to `{my_timezone}`, {member.mention}!**")

	# Database (CRUD)

	async def insert_user_timezone(self, user_id: int, my_timezone: str) -> None:
		""" Inserts a timezone for a user.
		:param user_id: The ID of the user to insert.
		:param my_timezone: The user's timezone. """

		mycursor, db = await the_database()
		await mycursor.execute("INSERT INTO UserTimezones (user_id, my_timezone) VALUES (%s, %s)", (user_id, my_timezone))
		await db.commit()
		await mycursor.close()

	async def select_user_timezone(self, user_id: int) -> None:
		""" Gets the user's timezone.
		:param user_id: The ID of the user to get. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM UserTimezones WHERE user_id = %s", (user_id,))
		user_timezone = await mycursor.fetchone()
		await mycursor.close()
		return user_timezone

	async def update_user_timezone(self, user_id: int, my_timezone: str) -> None:
		""" Updates the user's timezone.
		:param user_id: The ID of the user to update.
		:param my_timezone: The user's new timezone. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE UserTimezones SET my_timezone = %s WHERE user_id = %s", (my_timezone, user_id))
		await db.commit()
		await mycursor.close()

	async def delete_user_timezone(self, user_id: int) -> None:
		""" Deletes the user's timezone.
		:param user_id: The ID of the user to delete. """

		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM UserTimezones WHERE user_id = %s", (user_id,))
		await db.commit()
		await mycursor.close()

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def create_table_user_timezones(self, ctx) -> None:
		""" (ADM) Creates the UserTimezones table. """

		if await self.check_table_user_timezones():
			return await ctx.send("**Table __UserTimezones__ already exists!**")

		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute("CREATE TABLE UserTimezones (user_id BIGINT NOT NULL, my_timezone VARCHAR(50) NOT NULL)")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table __UserTimezones__ created!**", delete_after=3)

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def drop_table_user_timezones(self, ctx) -> None:
		""" (ADM) Creates the UserTimezones table """
		if not await self.check_table_user_timezones():
			return await ctx.send("**Table __UserTimezones__ doesn't exist!**")
		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute("DROP TABLE UserTimezones")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table __UserTimezones__ dropped!**", delete_after=3)

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def reset_table_user_timezones(self, ctx) -> None:
		""" (ADM) Creates the UserTimezones table """

		if not await self.check_table_user_timezones():
			return await ctx.send("**Table __UserTimezones__ doesn't exist yet!**")

		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM UserTimezones")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table __UserTimezones__ reset!**", delete_after=3)

	async def check_table_user_timezones(self) -> bool:
		""" Checks if the UserTimezones table exists """

		mycursor, db = await the_database()
		await mycursor.execute("SHOW TABLE STATUS LIKE 'UserTimezones'")
		table_info = await mycursor.fetchall()
		await mycursor.close()

		if len(table_info) == 0:
			return False

		else:
			return True


	@commands.command(aliases=['show_tree', 'file_tree', 'showtree', 'filetree', 'sft'])
	@commands.has_permissions(administrator=True)
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def show_file_tree(self, ctx, path: str = None) -> None:
		""" Shows the file tree.
		:param path: The path (Optional). """

		if not path:
			path = './'

		path = path.replace('../', '')

		if not os.path.isdir(path):
			return await ctx.send(f"**Invalid path, {ctx.author.mention}!**")

		tree = Tree()

		ignore_files = ['venv', '__pycache__', '.git', '.gitignore']

		tree.create_node('Root' if path == './' else path, 'root')

		for file in os.listdir(path):
			if file in ignore_files:
				continue

			if os.path.isdir(file):
				tree.create_node(file, file, parent='root')
				for subfile in (directory := os.listdir(f'./{file}')):
					if subfile in ignore_files:
						continue
					tree.create_node(subfile, subfile, parent=file)

			else:
				tree.create_node(file, file, parent='root')


		# the_tree = tree.show(line_type="ascii-em")

		# embed = discord.Embed(description=tree)

		# await ctx.send(embed=embed)
		await Tools.send_big_message('File Tree', ctx.channel, str(tree), discord.Color.green())

	@commands.command(aliases=["eli", "elj", "elijaaah"])
	async def elijah(self, ctx) -> None:
		""" A command for telling something about Elijah. """

		await ctx.send("**\"You have a really nice voice\"**")

	@commands.command()
	@utils.is_allowed([owner_role_id, admin_role_id, mod_role_id])
	async def cosmos(self, ctx) -> None:
		""" A command for pinging Cosmos, the stealthy little guy. """

		cosmos_id = int(os.getenv('COSMOS_ID'))
		cosmos = discord.utils.get(ctx.guild.members, id=cosmos_id)
		await ctx.send(cosmos.mention)

	@commands.command()
	@utils.is_allowed([owner_role_id, admin_role_id, mod_role_id])
	async def muffin(self, ctx) -> None:
		""" A command for pinging Muffin, the rich Lux lass. """

		muffin_id = int(os.getenv('MUFFIN_ID'))
		muffin = discord.utils.get(ctx.guild.members, id=muffin_id)
		await ctx.send(muffin.mention)

	@commands.command()
	@utils.is_allowed([owner_role_id, admin_role_id, mod_role_id])
	async def prisca(self, ctx) -> None:
		""" A command for pinging Prisca, the photoshop Turk. """

		prisca_id = int(os.getenv('PRISCA_ID'))
		prisca = discord.utils.get(ctx.guild.members, id=prisca_id)
		await ctx.send(prisca.mention)

	@commands.command(aliases=['gui'])
	@utils.is_allowed([owner_role_id, admin_role_id, mod_role_id])
	async def guibot(self, ctx) -> None:
		""" A command for pinging GuiBot, the lawyer and demoter guy. """

		guibot_id = int(os.getenv('GUIBOT_ID'))
		guibot = discord.utils.get(ctx.guild.members, id=guibot_id)
		await ctx.send(guibot.mention)

	@commands.command(aliases=['musicbot', 'music_bot', 'musicbots', 'music', 'mb'])
	@commands.cooldown(1, 10, commands.BucketType.user)
	@Player.poisoned()
	async def music_bots(self, ctx) -> None:
		""" Shows a list with all music bots available in the server. """

		music_bot_role = discord.utils.get(ctx.guild.roles, id=int(os.getenv('MUSIC_BOT_ROLE_ID')))
		music_bots = [mb for mb in ctx.guild.members if music_bot_role in mb.roles]
		music_bots = [f"{mb.mention} ❌" if mb.voice and mb.voice.channel else f"{mb.mention} ✅" for mb in music_bots]

		embed = discord.Embed(
			title="__Available Music Bots:__",
			description=f"✅ = Available | ❌ = Being used\n\n{', '.join(music_bots)}",
			color=ctx.author.color,
			timestamp=ctx.message.created_at
		)
		await ctx.send(embed=embed)


	@commands.command(aliases=["pd"])
	@commands.has_permissions(administrator=True)
	async def payday(self, ctx) -> None:
		""" Pays all Patreon members when run. (Generally run on the 6th) """

		SlothCurrency = self.client.get_cog('SlothCurrency')

		members = collections.defaultdict(list)

		people_count: int = 0
		# Loops through each Patreon role and gets a list containing members that have them
		async with ctx.typing():
			for member in ctx.guild.members:
				for role_id in patreon_roles:  # dict.keys
					if discord.utils.get(member.roles, id=role_id):
						members[role_id].append(member)

			for role_id, role_members in members.items():
				values = patreon_roles[role_id]
				users = list((values[3], m.id) for m in role_members)

				people_count += len(role_members)
				# Give them money
				await SlothCurrency.update_user_many_money(users)

				channel = discord.utils.get(ctx.guild.text_channels, id=patreon_channel_id)
				m_mentions = ', '.join([m.mention for m in role_members])
				embed = discord.Embed(
					title=f"__Payday__",
					description=f"The members below were paid off according to their <@&{role_id}> role!\n\n{m_mentions}",
					color=discord.Color.green()
				)
				embed.add_field(name="Reward", value=f"You all just got your monthly **{values[3]}łł** :leaves:")
				await channel.send(content=f"<@&{role_id}>", embed=embed)

			await ctx.send(f"**{people_count} Patreons were paid!**")

	@commands.command(alises=['count_channel', 'countchannel'])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def channels(self, ctx) -> None:
		""" Counts how many channels there are in the server. """

		await ctx.reply(f"**We currently have `{len(ctx.guild.channels)}` channels!**")

	@commands.slash_command(name="timestamp", guild_ids=guild_ids)
	async def _timestamp(self, ctx, 
			hour: Option(int, name="hour", description="Hour of time in 24 hour format.", required=False),
			minute: Option(int, name="minute", description="Minute of time.", required=False),
			day: Option(int, name="day", description="Day of date.", required=False),
			month: Option(int, name="month", description="Month of date.", required=False),
			year: Option(int, name="year", description="Year of date.", required=False)) -> None:
		""" Gets a timestamp for a specific date and time. - Output will format according to your timezone. """

		await ctx.defer()
		current_date = await utils.get_time_now()

		if hour: current_date = current_date.replace(hour=hour)
		if minute: current_date = current_date.replace(minute=minute)
		if day: current_date = current_date.replace(day=day)
		if month: current_date = current_date.replace(month=month)
		if year: current_date = current_date.replace(year=year)

		embed = discord.Embed(
			title="__Timestamp Created__",
			description=f"Requested date: `{current_date.strftime('%m/%d/%Y %H:%M')}` (**GMT**)",
			color=ctx.author.color
		)
		timestamp = int(current_date.timestamp())
		embed.add_field(name="Output", value=f"<t:{timestamp}>")
		embed.add_field(name="Copyable", value=f"\<t:{timestamp}>")

		await ctx.respond(embed=embed, ephemeral=True)

	@commands.slash_command(name="mention", guild_ids=guild_ids)
	@utils.is_allowed([mod_role_id, admin_role_id, owner_role_id])
	async def _mention(self, ctx, 
		member: Option(str, name="member", description="The Staff member to mention/ping.", required=True,
			choices=[
				OptionChoice(name="Cosmos", value=os.getenv('COSMOS_ID')), OptionChoice(name="Alex", value=os.getenv('ALEX_ID')),
				OptionChoice(name="DNK", value=os.getenv('DNK_ID')), OptionChoice(name="Muffin", value=os.getenv('MUFFIN_ID')),
				OptionChoice(name="Prisca", value=os.getenv('PRISCA_ID')), OptionChoice(name="GuiBot", value=os.getenv('GUIBOT_ID'))
			]
		)) -> None:
		""" (ADMIN) Used to mention staff members. """

		if staff_member := discord.utils.get(ctx.guild.members, id=int(member)):
			await ctx.respond(staff_member.mention)
		else:
			await ctx.respond("**For some reason I couldn't ping them =\ **")

	@commands.command(aliases=['sound', 'board', 'sound_board'])
	@utils.is_allowed([mod_role_id, admin_role_id, owner_role_id], throw_exc=True)
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def soundboard(self, ctx) -> None:
		""" Sends a soundboard into the channel. """

		author = ctx.author

		author_state = author.voice
		if not (vc := author_state and author_state.channel):
			ctx.command.reset_cooldown(ctx)
			return await ctx.send(f"**You're not in a VC!**")

		embed = discord.Embed(
			title="__Soundboard__",
			description="Click any of the buttons below to play different sounds in the Voice Channel.",
			color=author.color,
			timestamp=ctx.message.created_at
		)
		embed.add_field(name="Info:", value=f"Soundboard is bound to the {vc.mention} `Voice Channel`.")
		embed.set_footer(text=f"Started by {author}", icon_url=author.display_avatar)
		view: discord.ui.View = BasicUserCheckView(author)
		select: discord.ui.Select = SoundBoardSelect(ctx, self.client, sb_view=SoundBoardView, settings=[
			['General', 'sounds'], ['General 2', 'sounds2'], ['General 3', 'sounds3'], ['Cosmos', 'cosmos'],
			['DNK', 'dnk'], ['Other', 'other']
		])
		view.add_item(select)
		await ctx.send(embed=embed, view=view)


	@slash_command(name="poll", guild_ids=guild_ids)
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def _poll(self, ctx, 
		description: Option(str, description="The description of the poll."),
		title: Option(str, description="The title of the poll.", required=False, default="Poll"), 
		role: Option(discord.Role, description="The role to tag in the poll.", required=False)) -> None:
		""" Makes a poll.
		:param title: The title of the poll.
		:param description: The description of the poll. """

		await ctx.defer()

		member = ctx.author
		current_time = await utils.get_time_now()

		embed = discord.Embed(
			title=f"__{title}__",
			description=description,
			color=member.color,
			timestamp=current_time
		)

		if role:
			msg = await ctx.respond(content=role.mention, embed=embed)
		else:
			msg = await ctx.respond(embed=embed)
		await msg.add_reaction('<:yessloth:912068622841708594>')
		await msg.add_reaction('<:nosloth:912066953160556575>')

	@user_command(name="Follow", guild_ids=guild_ids)
	@utils.is_allowed([owner_role_id, admin_role_id, mod_role_id])
	async def _follow(self, ctx, user: discord.Member) -> None:
		""" Follows a user by moving yourself to the Voice Channel they are in. """

		author = ctx.author
		user_vc = user.voice
		if not user_vc or not user_vc.channel:
			return await ctx.respond(f"**{user} is not in a VC, {author.mention}!**")

		author_vc = author.voice
		if not author_vc or not author_vc.channel:
			return await ctx.respond(f"**You're not in a VC, I cannot move you to there, {author.mention}!**")

		try:
			await author.move_to(user_vc.channel)
		except:
			await ctx.respond(f"**For some reason I couldn't move you to there, {author.mention}!**")
		else:
			await ctx.respond(f"**You got moved to {user_vc.channel.mention}!**")

	@commands.command(aliases=['simp'])
	@utils.is_allowed([owner_role_id, admin_role_id, mod_role_id], throw_exc=True)
	async def follow(self, ctx, user: discord.Member) -> None:
		""" Follows a user by moving yourself to the Voice Channel they are in.
		:param member:  The member you intend to follow"""

		author = ctx.author
		user_vc = user.voice
		if not user_vc or not user_vc.channel:
			return await ctx.send(f"**{user} is not in a VC, {author.mention}!**")

		author_vc = author.voice
		if not author_vc or not author_vc.channel:
			return await ctx.send(f"**You're not in a VC, I cannot move you to there, {author.mention}!**")

		try:
			await author.move_to(user_vc.channel)
		except:
			await ctx.send(f"**For some reason I couldn't move you to there, {author.mention}!**")
		else:
			embed = discord.Embed(description=f' :knife: **You followed <@{user.id}> to the <#{author_vc.channel.id}> voice channel**')
			await ctx.send(embed=embed)

	@user_command(name="Pull", guild_ids=guild_ids)
	@utils.is_allowed([owner_role_id, admin_role_id, mod_role_id], throw_exc=True)
	async def _pull(self, ctx, user: discord.Member) -> None:
		""" Pulls a user by moving them to the Voice Channel you are in. """

		author = ctx.author
		user_vc = user.voice
		if not user_vc or not user_vc.channel:
			return await ctx.respond(f"**{user} is not in a VC, {author.mention}!**")

		author_vc = author.voice
		if not author_vc or not author_vc.channel:
			return await ctx.respond(f"**You're not in a VC, I cannot bring them here, {author.mention}!**")

		try:
			await user.move_to(author_vc.channel)
		except:
			await ctx.respond(f"**For some reason I couldn't bring them here, {author.mention}!**")
		else:
			await ctx.respond(f"**They were brought to {user_vc.channel.mention}!**")

	@commands.command()
	@utils.is_allowed([senior_mod_role_id], throw_exc=True)
	async def stealth(self, ctx) -> None:
		""" Makes you stealth, so when you join a VC you don't get the 'in a VC' role. """

		member = ctx.author
		stealth_status = await self.get_stealth_status(member.id)
		
		on = True if stealth_status and stealth_status[1] else False

		confirm = await Confirm(f"**Your Stealth mode is `{'online' if on else 'offline'}` wanna turn it `{'off' if on else 'on'}`?**").prompt(ctx)
		if not confirm:
			return await ctx.send(f"**Not doing it, then, {member.mention}!**")

		try:
			if stealth_status:
				await self.update_stealth_status(member.id, 0 if on else 1)
			else:
				await self.insert_stealth_status(member.id, 1)
		except Exception as e:
			print('stealth error: ', e)
			await ctx.send(f"**Something went wrong, try again or talk with DNK!**")
		else:
			await ctx.send(f"**Your stealth mode has been turned `{'off' if on else 'on'}`, {member.mention}!**")

	@slash_command(name="join", guild_ids=guild_ids)
	@utils.is_allowed(allowed_roles, throw_exc=True)
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def _join_slash(self, ctx,
		channel: Option(discord.VoiceChannel, description="The language voice channel you want to join", required=True)) -> None:
		""" (Patreon) Joins a language channel"""

		await ctx.defer()

		allowed_channels = [popular_lang_cat_id, more_popular_lang_cat_id, dynamic_channels_cat_id, smart_room_cat_id]
		if channel.category.id not in allowed_channels:
			return await ctx.respond("**You are not allowed to join this channel**")

		author_vc = ctx.author.voice
		if not author_vc or not author_vc.channel:
			return await ctx.respond(f"**You're not in a VC, I cannot move you to there, {ctx.author.mention}!**")

		try:
			await ctx.author.move_to(channel)
		except:
			await ctx.respond(f"**For some reason I couldn't move you to there, {ctx.author.mention}!**")
		else:
			await ctx.respond(f"**You got moved to {channel.mention}!**")


	@commands.command()
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def join(self, ctx, channel: Optional[discord.VoiceChannel]) -> None:
		""" (Patreon) Joins a language channel
		:param voice_channel: ID of the language voice channel
		"""

		if not channel:
			return await ctx.send(f"**Inform the channel you want to join, {ctx.author.mention}**")

		# Checks if the channel is not a smartroom
		allowed_channels = [popular_lang_cat_id, more_popular_lang_cat_id, dynamic_channels_cat_id, smart_room_cat_id]
		if channel.category.id not in allowed_channels:
			return await ctx.send("**You do not have permission to access this channel**", delete_after=3)

		author_vc = ctx.author.voice
		if not author_vc or not author_vc.channel:
			return await ctx.respond(f"**You're not in a VC, I cannot move you to there, {ctx.author.mention}!**")

		try:
			await ctx.author.move_to(channel)
		except:
			await ctx.respond(f"**For some reason I couldn't move you to there, {ctx.author.mention}!**")
		else:
			await ctx.respond(f"**You got moved to {channel.mention}!**")

	@commands.command()
	@utils.is_allowed([senior_mod_role_id, admin_role_id, owner_role_id], throw_exc=True)
	async def surf(self, ctx, member: Optional[discord.Member] = None) -> None:
		""" Makes a member surf in the empty Dynamic Rooms, to delete them.
		:param member: The member who's gonna surf. [Optional][Default = You] """

		author: discord.Member = ctx.author

		if not member:
			member = ctx.author

		dynamic_channels: List[discord.TextChannel] = [
			dynamic_vc for dynamic_vc in ctx.guild.voice_channels
			if dynamic_vc.category and dynamic_vc.category.id == dynamic_channels_cat_id
			and dynamic_vc.id != dynamic_vc_id and len(dynamic_vc.members) == 0
		]

		if not len(dynamic_channels):
			return await ctx.send(f"**It seems like there are no VCs to surf on today, {author.mention}!**")

		original_vc: discord.VoiceChannel

		if not member.voice or not (original_vc := member.voice.channel):
			if member.id == author.id:
				return await ctx.send(f"**You are not in a VC, you cannot surf, {member.mention}!**")
			else:
				return await ctx.send(f"**{member.mention} is not in a VC, they cannot surf, {author.mention}!**")

		# Resets the Dynamic Rooms' states.
		await self.client.get_cog('CreateDynamicRoom').setup_dynamic_rooms_callback()

		await ctx.send(f"**{member.mention} is gonna surf on `{len(dynamic_channels)}` VCs!**")

		# Moves the user to all of the channels
		for dynamic_vc in dynamic_channels:
			try: 
				await member.move_to(dynamic_vc)
			except:
				pass
			else:
				await asyncio.sleep(1.5)
		
		# Moves the user back to the channel they were in before
		try:  
			await member.move_to(original_vc)
		except: 
			pass
		else:
			await ctx.send(f"**{member.mention}, is back home, after a long day of surfing,!**")

def setup(client):
	client.add_cog(Tools(client))
