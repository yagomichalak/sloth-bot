from logging import exception
import discord
from discord import user
from discord.ext import commands, tasks
import asyncio
from mysqldb import *
from datetime import datetime
from typing import List, Union, Dict, Optional
import os

from extra.useful_variables import banned_links
from extra.prompt.menu import Confirm
from extra.view import ReportSupportView
from extra import utils

from extra.moderation.firewall import ModerationFirewallTable
from extra.moderation.mutedmember import ModerationMutedMemberTable
from extra.moderation.userinfractions import ModerationUserInfractionsTable
from extra.moderation.watchlist import ModerationWatchlistTable
from extra.moderation.fakeaccounts import ModerationFakeAccountsTable

# IDs
mod_log_id = int(os.getenv('MOD_LOG_CHANNEL_ID'))
muted_role_id = int(os.getenv('MUTED_ROLE_ID'))
welcome_channel_id = int(os.getenv('WELCOME_CHANNEL_ID'))
last_deleted_message = []
suspect_channel_id = int(os.getenv('SUSPECT_CHANNEL_ID'))

mod_role_id = int(os.getenv('MOD_ROLE_ID'))

allowed_roles = [int(os.getenv('OWNER_ROLE_ID')), int(os.getenv('ADMIN_ROLE_ID')), int(os.getenv('SENIOR_MOD_ROLE_ID')), mod_role_id]
server_id = int(os.getenv('SERVER_ID'))

moderation_cogs: List[commands.Cog] = [
	ModerationFirewallTable, ModerationMutedMemberTable, ModerationUserInfractionsTable,
	ModerationWatchlistTable, ModerationFakeAccountsTable
]

class Moderation(*moderation_cogs):
	""" Moderation related commands. """

	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		self.look_for_expired_tempmutes.start()
		print('Moderation cog is ready!')

	@commands.Cog.listener()
	async def on_message(self, message):
		if not message.guild:
			return

		if message.author.bot:
			return

		# Banned links
		await self.check_banned_links(message)

		# Invite tracker
		msg = str(message.content)
		if 'discord.gg/' in msg.lower() or 'discord.com/invite/' in msg.lower():
			invite_root = 'discord.gg/' if 'discord.gg/' in msg.lower() else 'discord.com/invite/'
			ctx = await self.client.get_context(message)
			if not await utils.is_allowed(allowed_roles).predicate(ctx):
				is_from_guild = await self.check_invite_guild(msg, message.guild, invite_root)

				if not is_from_guild:
					return await self._mute_callback(ctx, member=message.author, reason="Invite Advertisement.")

	async def check_banned_links(self, message: discord.Message) -> None:
		""" Checks if the message sent was or contains a banned link. """

		videos = [v for v in message.attachments if v.content_type in ['video/mp4', 'video/webm']]

		# Checks it in the message attachments
		for video in videos:
			if str(video) in banned_links:
				ctx = await self.client.get_context(message)
				if not await utils.is_allowed(allowed_roles).predicate(ctx):
					return await self._mute_callback(ctx, member=message.author, reason="Banned Link")

		# Checks it in the message content
		for word in message.content.split():
			if word in banned_links:
				ctx = await self.client.get_context(message)
				if not await utils.is_allowed(allowed_roles).predicate(ctx):
					return await self._mute_callback(ctx, member=message.author, reason="Banned Link")

	@tasks.loop(minutes=1)
	async def look_for_expired_tempmutes(self) -> None:
		""" Looks for expired tempmutes and unmutes the users. """

		epoch = datetime.utcfromtimestamp(0)
		current_ts = (datetime.utcnow() - epoch).total_seconds()
		tempmutes = await self.get_expired_tempmutes(current_ts)
		guild = self.client.get_guild(server_id)

		for tm in tempmutes:
			member = discord.utils.get(guild.members, id=tm)
			if not member:
				continue

			try:
				role = discord.utils.get(guild.roles, id=muted_role_id)
				if role:
					if user_roles := await self.get_muted_roles(member.id):

						bot = discord.utils.get(guild.members, id=self.client.user.id)

						member_roles = list([
							a_role for the_role in user_roles if (a_role := discord.utils.get(guild.roles, id=the_role[1]))
							and a_role < bot.top_role
						])
						member_roles.extend(member.roles)

						member_roles = list(set(member_roles))
						if role in member_roles:
							member_roles.remove(role)

						await member.edit(roles=member_roles)
						try:
							await self.remove_all_roles_from_system(member.id)
						except Exception as e:
							print(e)
							pass
						else:
							# Moderation log embed
							moderation_log = discord.utils.get(guild.channels, id=mod_log_id)
							embed = discord.Embed(
								description=F"**Unmuted** {member.mention}\n**Reason:** Tempmute is over",
								color=discord.Color.light_gray())
							embed.set_author(name=f"{self.client.user} (ID {self.client.user.id})", icon_url=self.client.user.display_avatar)
							embed.set_thumbnail(url=member.display_avatar)
							await moderation_log.send(embed=embed)
							try:
								await member.send(embed=embed)
							except:
								pass

			except Exception as e:
				print(e)
				continue


	async def check_invite_guild(self, msg, guild, invite_root: str):
		""" Checks whether it's a guild invite or not. """

		start_index = msg.index(invite_root)
		end_index = start_index + len(invite_root)
		invite_hash = ''
		for c in msg[end_index:]:
			if c == ' ':
				break

			invite_hash += c

		for char in ['!', '@', '.', '(', ')', '[', ']', '#', '?', ':', ';', '`', '"', "'", ',', '{', '}']:
			invite_hash = invite_hash.replace(char, '')
		invite = invite_root + invite_hash
		inv_code = discord.utils.resolve_invite(invite)
		if inv_code == 'languages':
			return True
			
		guild_inv = discord.utils.get(await guild.invites(), code=inv_code)
		if guild_inv:
			return True
		else:
			return False

	@commands.Cog.listener()
	async def on_member_join(self, member):
		
		if member.bot:
			return

		# User timestamp
		the_time = member.created_at
		timestamp = datetime.timestamp(the_time)
		# Actual timestamp
		time_now = await utils.get_timestamp()
		account_age = round((time_now - timestamp)/86400)

		if account_age <= 4:
			if await self.get_firewall_state():
				return await member.kick(reason="Possible fake account")

		if account_age <= 2:
			suspect_channel = discord.utils.get(member.guild.channels, id=suspect_channel_id)
			await suspect_channel.send(f"🔴 Alert! Possible fake account: {member.mention} joined the server. Account was just created.\nAccount age: {account_age} day(s)!")

		if await self.get_muted_roles(member.id):
			muted_role = discord.utils.get(member.guild.roles, id=muted_role_id)
			await member.add_roles(muted_role)
			welcome_channel = discord.utils.get(member.guild.channels, id=welcome_channel_id)
			await welcome_channel.send(f"**Stop right there, {member.mention}! ✋ You were muted, left and rejoined the server, but that won't work!**")

	@commands.Cog.listener()
	async def on_message_delete(self, message):
		if message.author.bot:
			return
		last_deleted_message.clear()
		last_deleted_message.append(message)

	@commands.command()
	@utils.is_allowed(allowed_roles)
	async def snipe(self, ctx):
		'''
		(MOD) Snipes the last deleted message.
		'''
		message = last_deleted_message
		if message:
			message = message[0]
			embed = discord.Embed(title="Sniped", description=f"**>>** {message.content}", color=message.author.color, timestamp=message.created_at)
			embed.set_author(name=message.author, url=message.author.display_avatar, icon_url=message.author.display_avatar)
			await ctx.send(embed=embed)
		else:
			await ctx.send("**I couldn't snipe any messages!**")

	# Purge command
	@commands.command()
	@commands.has_permissions(manage_messages=True)
	async def purge(self, ctx, amount=0, member: discord.Member = None):
		'''
		(MOD) Purges messages.
		:param amount: The amount of messages to purge.
		:param member: The member from whom to purge the messages. (Optional)
		'''

		perms = ctx.channel.permissions_for(ctx.author)
		if not perms.administrator:
			if amount >= 30:
				return await ctx.send(f"**You cannot delete more than `30` messages at a time, {ctx.author.mention}!**")

		await ctx.message.delete()
		# global deleted
		deleted = 0
		if member:
			channel = ctx.channel
			msgs = list(filter(
				lambda m: m.author.id == member.id,
				await channel.history(limit=200).flatten()
			))
			for _ in range(amount):
				await msgs.pop(0).delete()
				deleted += 1

			await ctx.send(f"**`{deleted}` messages deleted for `{member}`**",
				delete_after=5)

		else:
			await ctx.channel.purge(limit=amount)

	@commands.command()
	@utils.is_allowed(allowed_roles)
	async def clear(self, ctx):
		'''
		(MOD) Clears the whole channel.
		'''

		special_channels = {
		  int(os.getenv('MUTED_CHANNEL_ID')): 'https://cdn.discordapp.com/attachments/746478846466981938/748605295122448534/Muted.png',
		  int(os.getenv('QUESTION_CHANNEL_ID')): '''**Would you like to ask us a question about the server? Ask them there!**
	`Questions will be answered and deleted immediately.`''',
		  int(os.getenv('SUGGESTION_CHANNEL_ID')): '''**Would you like to suggest a feature for the server? Please follow this template to submit your feature request**

	**Suggestion:**
	`A short idea name/description`

	**Explanation:**
	`Explain the feature in detail and including reasons why you would like this feature to be implemented.`''',
		}

		if ctx.channel.id not in special_channels.keys():
			return await ctx.send("**You cannot do that here!**")

		embed = discord.Embed(
		  title="Confirmation",
		  description="Clear the whole channel, **are you sure?**",
		  color=discord.Color.green(),
		  timestamp=ctx.message.created_at)
		msg = await ctx.send(embed=embed)

		await msg.add_reaction('✅')
		await msg.add_reaction('❌')

		def check(r, u):
			return r.message.id == msg.id and u.id == ctx.author.id and str(r.emoji) in ['✅', '❌']

		try:
			r, _ = await self.client.wait_for('reaction_add', timeout=60, check=check)
			r = str(r.emoji)
		except asyncio.TimeoutError:
			embed.description = '**Timeout!**'
			return await msg.edit(embed=embed)

		else:
			if r == '❌':
				embed.description = "Good, not doing it then! ❌"
				return await msg.edit(embed=embed)
			else:
				embed.description = "Clearing whole channel..."
				await msg.edit(embed=embed)
				await asyncio.sleep(1)

		while True:
			msgs = await ctx.channel.history().flatten()
			if (lenmsg := len(msgs)) > 0:
				await ctx.channel.purge(limit=lenmsg)
			else:
				break

		if smessage := special_channels.get(ctx.channel.id):
			await ctx.send(smessage)

	# Warns a member
	@commands.command()
	@utils.is_allowed(allowed_roles)
	async def warn(self, ctx, member: discord.Member = None, *, reason: Optional[str] = None):
		'''
		(MOD) Warns a member.
		:param member: The @ or ID of the user to warn.
		:param reason: The reason for warning the user. (Optional)
		'''
		await ctx.message.delete()
		if not member:
			await ctx.send("Please, specify a member!", delete_after=3)
		else:
			# General embed
			general_embed = discord.Embed(description=f'**Reason:** {reason}', colour=discord.Colour.dark_gold())
			general_embed.set_author(name=f'{member} has been warned', icon_url=member.display_avatar)
			await ctx.send(embed=general_embed)
			# Moderation log embed
			moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
			embed = discord.Embed(title='__**Warning**__', colour=discord.Colour.dark_gold(),
								  timestamp=ctx.message.created_at)
			embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
							inline=False)
			embed.add_field(name='Reason:', value=f'```{reason}```')
			embed.set_author(name=member)
			embed.set_thumbnail(url=member.display_avatar)
			embed.set_footer(text=f"Warned by {ctx.author}", icon_url=ctx.author.display_avatar)
			await moderation_log.send(embed=embed)
			# Inserts a infraction into the database
			epoch = datetime.utcfromtimestamp(0)
			current_ts = (datetime.utcnow() - epoch).total_seconds()
			await self.insert_user_infraction(
				user_id=member.id, infr_type="warn", reason=reason,
				timestamp=current_ts, perpetrator=ctx.author.id)
			try:
				await member.send(embed=general_embed)
			except:
				pass

			user_infractions = await self.get_user_infractions(member.id)
			user_warns = [w for w in user_infractions if w[1] == 'warn']
			if len(user_warns) >= 3:
				ctx.author = self.client.user
				await self._mute_callback(ctx, member=member, reason=reason)

	async def get_mute_time(self, ctx: commands.Context, time: List[str]) -> Dict[str, int]:
		""" Gets the mute time in seconds.
		:param ctx: The context.
		:param time: The given time. """


		keys = ['d', 'h', 'm', 's']
		for k in keys:
			if k in time:
				break
		else:
			await ctx.send(f"**Inform a valid time, {ctx.author.mention}**", delete_after=3)
			return False

		the_time_dict = {
			'days': 0,
			'hours': 0,
			'minutes': 0,
			'seconds': 0,
		}

		seconds = 0

		for t in time.split():

			if (just_time := t[:-1]).isdigit():
				just_time = int(t[:-1])

			if 'd' in t and not the_time_dict.get('days'):

				seconds += just_time * 86400
				the_time_dict['days'] = just_time
				continue
			elif 'h' in t and not the_time_dict.get('hours'):
				seconds += just_time * 3600
				the_time_dict['hours'] = just_time
				continue
			elif 'm' in t and not the_time_dict.get('minutes'):
				seconds += just_time * 60
				the_time_dict['minutes'] = just_time
				continue
			elif 's' in t and not the_time_dict.get('seconds'):
				seconds += just_time
				the_time_dict['seconds'] = just_time
				continue

		if seconds <= 0:
			await ctx.send(f"**Something is wrong with it, {ctx.author.mention}!**", delete_after=3)
			return False, False
		else:
			return the_time_dict, seconds

	async def get_remove_roles(self, member: discord.Member, keep_roles: Optional[List[Union[int, discord.Role]]] = []
	) -> List[List[discord.Role]]:
		""" Gets a list of roles the user will have after removing their roles
		and a list that will be removed from them.
		:param keep_roles: The list of roles to keep. [Optional] """


		bot = discord.utils.get(member.guild.members, id=self.client.user.id)

		keep_roles: List[int] = [
			keep_role if isinstance(keep_role, discord.Role) else 
			discord.utils.get(member.guild.roles, id=keep_role)
			for keep_role in keep_roles
		]

		keep_list = []
		remove_list = []

		for i, member_role in enumerate(member.roles):
			if i == 0:
				continue
				
			for role in keep_roles:
				if member_role.id == role.id:
					keep_list.append(role)
					continue

			if member_role < bot.top_role:
				if not member_role.is_premium_subscriber():
					remove_list.append(member_role)

			if member_role.is_premium_subscriber():
				keep_list.append(member_role)

			if member_role >= bot.top_role:
				keep_list.append(member_role)

		return list(set(keep_list)), list(set(remove_list))

	@commands.command()
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def rar(self, ctx: commands.Context, member: discord.Member = None) -> None:
		""" Removes all roles from a user.
		:param member: The member to rar from. """

		author = ctx.author

		if not member:
			return await ctx.send(f"**Please, inform a member to rar, {author.mention}!**")

		keep_roles, _ = await self.get_remove_roles(member, keep_roles=allowed_roles)

		confirm = await Confirm(f"**Are you sure you wanna rar {member.mention}, {author.mention}?**").prompt(ctx)
		if not confirm:
			return await ctx.send(f"**Not doing it, then, {author.mention}!**")

		try:
			await member.edit(roles=keep_roles)
		except:
			await ctx.send(f"**For some reason I couldn't do it, {author.mention}!**")
		else:
			await ctx.send(f"**Successfully rar'd `{member}`, {author.mention}!**")

	@commands.command(name="mute")
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def _mute_command(self, ctx: commands.Context, member: discord.Member = None, *, reason: Optional[str] = None):
		""" (MOD) Mutes a member.
		:param member: The @ or the ID of the user to mute.
		:param reason: The reason for the mute. """

		await self._mute_callback(ctx, member, reason)

	async def _mute_callback(self, ctx: commands.Context, member: discord.Member = None, reason: Optional[str] = None):
		""" (MOD) Mutes a member.
		:param member: The @ or the ID of the user to mute.
		:param reason: The reason for the mute. """

		answer: discord.PartialMessageable = None
		if isinstance(ctx, commands.Context):
			answer = ctx.send
			try:
				await ctx.message.delete()
			except:
				pass
		else:
			answer = ctx.respond

		role = discord.utils.get(ctx.guild.roles, id=muted_role_id)
		if not member:
			return await ctx.send("**Please, specify a member!**")
		if role not in member.roles:
			# await member.add_roles(role)
			await member.move_to(None)
			keep_roles, remove_roles = await self.get_remove_roles(member, keep_roles=allowed_roles)

			current_ts = await utils.get_timestamp()
			keep_roles.append(role)

			await member.edit(roles=keep_roles)
			user_role_ids = [(member.id, rr.id, current_ts, None) for rr in remove_roles]
			await self.insert_in_muted(user_role_ids)
			# General embed
			current_time = await utils.get_time_now()
			general_embed = discord.Embed(description=f'**Reason:** {reason}', colour=discord.Colour.dark_grey(), timestamp=current_time)
			general_embed.set_author(name=f'{member} has been muted', icon_url=member.display_avatar)
			await answer(embed=general_embed)

			# Moderation log embed
			moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
			embed = discord.Embed(title='__**Mute**__', color=discord.Color.dark_grey(),
								  timestamp=current_time)
			embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
							inline=False)
			embed.add_field(name='Reason:', value=f'```{reason}```')

			embed.set_author(name=member)
			embed.set_thumbnail(url=member.display_avatar)
			embed.set_footer(text=f"Muted by {ctx.author}", icon_url=ctx.author.display_avatar)
			await moderation_log.send(embed=embed)
			# Inserts a infraction into the database
			await self.insert_user_infraction(
				user_id=member.id, infr_type="mute", reason=reason,
				timestamp=current_ts, perpetrator=ctx.author.id)
			try:
				await member.send(embed=general_embed)
			except:
				pass

		else:
			await answer(f'**{member} is already muted!**')

	# Unmutes a member
	@commands.command(name="unmute")
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def _unmute_command(self, ctx, member: discord.Member = None) -> None:
		""" (MOD) Unmutes a member.
		:param member: The @ or the ID of the user to unmute. """

		await self._unmute_callback(ctx, member)

	async def _unmute_callback(self, ctx, member: discord.Member = None) -> None:
		""" (MOD) Unmutes a member.
		:param member: The @ or the ID of the user to unmute. """

		answer: discord.PartialMessageable = None
		if isinstance(ctx, commands.Context):
			answer = ctx.send
			try:
				await ctx.message.delete()
			except:
				pass
		else:
			answer = ctx.respond

		role = discord.utils.get(ctx.guild.roles, id=muted_role_id)
		if not member:
			return await answer("**Please, specify a member!**", delete_after=3)
		if role in member.roles:
			if user_roles := await self.get_muted_roles(member.id):

				bot = discord.utils.get(ctx.guild.members, id=self.client.user.id)

				member_roles = list([
					a_role for the_role in user_roles if (a_role := discord.utils.get(member.guild.roles, id=the_role[1]))
					and a_role < bot.top_role
				])
				member_roles.extend(member.roles)

				member_roles = list(set(member_roles))
				if role in member_roles:
					member_roles.remove(role)

				await member.edit(roles=member_roles)

				try:
					await self.remove_all_roles_from_system(member.id)
				except Exception as e:
					print(e)
					pass

			current_time = await utils.get_time_now()
			general_embed = discord.Embed(colour=discord.Colour.light_grey(),
										  timestamp=current_time)
			general_embed.set_author(name=f'{member} has been unmuted', icon_url=member.display_avatar)
			await answer(embed=general_embed)
			# Moderation log embed
			moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
			embed = discord.Embed(title='__**Unmute**__', colour=discord.Colour.light_grey(),
								  timestamp=current_time)
			embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
							inline=False)
			embed.set_author(name=member)
			embed.set_thumbnail(url=member.display_avatar)
			embed.set_footer(text=f"Unmuted by {ctx.author}", icon_url=ctx.author.display_avatar)
			await moderation_log.send(embed=embed)
			try:
				await member.send(embed=general_embed)
			except:
				pass

		else:
			await answer(f'**{member} is not even muted!**', delete_after=5)

	# Mutes a member temporarily
	@commands.command()
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def tempmute(self, ctx, member: discord.Member = None, reason: str = None, *, time: str = None):
		""" Mutes a member for a determined amount of time.
		:param member: The @ or the ID of the user to tempmute.
		:param minutes: The amount of minutes that the user will be muted.
		:param reason: The reason for the tempmute.
		:param time: The time for the mute. """
		await ctx.message.delete()

		role = discord.utils.get(ctx.guild.roles, id=muted_role_id)

		if not member:
			return await ctx.send("**Please, specify a member!**", delete_after=3)

		if not reason:
			return await ctx.send(f"**Specify a reason!**", delete_after=3)

		if not time:
			return await ctx.send('**Inform a time!**', delete_after=3)

		time_dict, seconds = await self.get_mute_time(ctx, time=time)
		if not seconds:
			return

		# print('ah')
		current_ts = await utils.get_timestamp()

		# print(current_ts, seconds)

		if role not in member.roles:
			await member.move_to(None)
			keep_roles, remove_roles = await self.get_remove_roles(member, keep_roles=allowed_roles)
			keep_roles.append(role)

			await member.edit(roles=keep_roles)
			user_role_ids = [(member.id, rr.id, current_ts, seconds) for rr in remove_roles]
			await self.insert_in_muted(user_role_ids)

			# General embed
			general_embed = discord.Embed(description=f"**For:** `{time_dict['days']}d`, `{time_dict['hours']}h`, `{time_dict['minutes']}m` and `{time_dict['seconds']}s`\n**Reason:** {reason}", colour=discord.Colour.dark_grey(), timestamp=ctx.message.created_at)
			general_embed.set_author(name=f"{member} has been tempmuted", icon_url=member.display_avatar)
			await ctx.send(embed=general_embed)
			# Moderation log embed
			moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
			embed = discord.Embed(
				description=F"**Tempmuted** {member.mention} for `{time_dict['days']}d`, `{time_dict['hours']}h`, `{time_dict['minutes']}m` and `{time_dict['seconds']}s`\n**Reason:** {reason}\n**Location:** {ctx.channel.mention}",
				color=discord.Color.lighter_grey(),
				timestamp=ctx.message.created_at)
			embed.set_author(name=f"{ctx.author} (ID {ctx.author.id})", icon_url=ctx.author.display_avatar)
			embed.set_thumbnail(url=member.display_avatar)
			await moderation_log.send(embed=embed)
			# # Inserts a infraction into the database
			await self.insert_user_infraction(
				user_id=member.id, infr_type="mute", reason=reason,
				timestamp=current_ts, perpetrator=ctx.author.id)
			try:
				await member.send(embed=general_embed)
			except:
				pass
		else:
			await ctx.send(f'**{member} is already muted!**', delete_after=5)

	@commands.command(aliases=['kick_muted_members', 'kickmuted'])
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def kick_muted(self, ctx, *, reason: Optional[str] = None) -> None:
		""" Kicks all muted members from at least 2 days ago.
		:param reason: The reason for kicking the muted members. [Optional] """

		await ctx.message.delete()
		perpetrator = ctx.author

		muted_role = discord.utils.get(ctx.guild.roles, id=muted_role_id)
		current_ts = await utils.get_timestamp()
		muted_members = [
			muted_member for m in await self.get_muted_members(current_ts, 2) 
			if (muted_member := discord.utils.get(ctx.guild.members, id=m)) and muted_role in muted_member.roles
		]

		if len(muted_members) == 0:
			return await ctx.send(f"**There are no muted members, {perpetrator.mention}!**")

		confirm = await Confirm(
			f"**Are you sure you want to kick {len(muted_members)} muted members from at least 2 days ago, {perpetrator.mention}?**"
			).prompt(ctx)

		if confirm:
			kicked_members = []

			current_ts = await utils.get_timestamp()

			for muted_member in muted_members:
				try:
					# Kicks the muted member
					await muted_member.kick(reason=reason)
					# Inserts a infraction into the database
					await self.insert_user_infraction(
						user_id=muted_member.id, infr_type="kick", reason=reason,
						timestamp=current_ts, perpetrator=ctx.author.id)
				except Exception:
					await ctx.send('**You cannot do that!**', delete_after=3)
				else:
					kicked_members.append(f"Name: {muted_member.display_name} ({muted_member.id})")

			if len(kicked_members) >= 1:
				# General embed
				general_embed = discord.Embed(description=f'**Reason:** {reason}', colour=discord.Color.teal())
				general_embed.set_author(name=f'{len(muted_members)} muted members have been kicked')
				await ctx.send(embed=general_embed)

				# Moderation log embed
				moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
				embed = discord.Embed(title='__**Kick**__', color=discord.Color.teal(),
									  timestamp=ctx.message.created_at)
				muted_text = '\n'.join(kicked_members)
				embed.add_field(
					name='User info:', 
					value=f'```apache\n{muted_text}```', 
				inline=False)
				embed.add_field(name='Reason:', value=f'```{reason}```')
				embed.set_footer(text=f"Kicked by {perpetrator}", icon_url=perpetrator.display_avatar)
				await moderation_log.send(embed=embed)
				
			else:
				await ctx.send(f"**For some reason I couldn't kick any of the {len(muted_members)} muted members, {perpetrator.mention}!**")
  
		else:
			await ctx.send(f"**Not kicking them, then, {perpetrator.mention}!**")


	@commands.command()
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def kick(self, ctx, member: discord.Member = None, *, reason: Optional[str] = None):
		""" (MOD) Kicks a member from the server.
		:param member: The @ or ID of the user to kick.
		:param reason: The reason for kicking the user. (Optional) """

		await ctx.message.delete()
		if not member:
			return await ctx.send('**Please, specify a member!**', delete_after=3)

		confirm = await Confirm(f"**Are you sure you want to kick {member.mention} from the server, {ctx.author.mention}?**").prompt(ctx)
		if not confirm:
			return

		# General embed
		general_embed = discord.Embed(description=f'**Reason:** {reason}', colour=discord.Colour.magenta())
		general_embed.set_author(name=f'{member} has been kicked', icon_url=member.display_avatar)
		await ctx.send(embed=general_embed)
		try:
			await member.send(embed=general_embed)
		except:
			pass

		try:
			await member.kick(reason=reason)
		except Exception:
			await ctx.send('**You cannot do that!**', delete_after=3)
		else:
			# Moderation log embed
			moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
			embed = discord.Embed(title='__**Kick**__', colour=discord.Colour.magenta(),
									timestamp=ctx.message.created_at)
			embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
							inline=False)
			embed.add_field(name='Reason:', value=f'```{reason}```')
			embed.set_author(name=member)
			embed.set_thumbnail(url=member.display_avatar)
			embed.set_footer(text=f"Kicked by {ctx.author}", icon_url=ctx.author.display_avatar)
			await moderation_log.send(embed=embed)
			# Inserts a infraction into the database
			current_ts = await utils.get_timestamp()
			await self.insert_user_infraction(
				user_id=member.id, infr_type="kick", reason=reason,
				timestamp=current_ts, perpetrator=ctx.author.id)

	# Bans a member
	@commands.command()
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def ban(self, ctx, member: discord.Member = None, *, reason: Optional[str] = None) -> None:
		""" (ModTeam/ADM) Bans a member from the server.
		:param member: The @ or ID of the user to ban.
		:param reason: The reason for banning the user. (Optional) """

		await ctx.message.delete()
		if not member:
			return await ctx.send('**Please, specify a member!**', delete_after=3)

		channel = ctx.channel
		author = ctx.author

		perpetrators = []
		confirmations = {}

		perms = channel.permissions_for(author)

		if not perms.administrator:
			confirmations[author.id] = author.name
			mod_ban_embed = discord.Embed(
				title=f"Ban Request ({len(confirmations)}/5) → (5mins)",
				description=f'''
				{author.mention} wants to ban {member.mention}, it requires 4 more moderator ✅ reactions for it!
				```Reason: {reason}```''',
				colour=discord.Colour.dark_red(), timestamp=ctx.message.created_at)
			mod_ban_embed.set_author(name=f'{member} is going to Brazil...', icon_url=member.display_avatar)
			msg = await ctx.send(embed=mod_ban_embed)
			await msg.add_reaction('✅')

			# Prompts for 3 moderator reactions
			def check_mod(r, u):
				if u.bot:
					return False
				if r.message.id != msg.id:
					return

				if str(r.emoji) == '✅':
					perms = channel.permissions_for(u)
					if mod_role_id in [r.id for r in u.roles] or perms.administrator:
						confirmations[u.id] = u.name
						return True
					else:
						self.client.loop.create_task(
							msg.remove_reaction('✅', u)
							)
						return False

				else:
					self.client.loop.create_task(
						msg.remove_reaction(r.emoji, u)
						)
					return False

			while True:
				try:
					r, u = await self.client.wait_for('reaction_add', timeout=300, check=check_mod)
				except asyncio.TimeoutError:
					mod_ban_embed.description = f'Timeout, {member} is not getting banned!'
					await msg.remove_reaction('✅', self.client.user)
					return await msg.edit(embed=mod_ban_embed)
				else:
					mod_ban_embed.title = f"Ban Request ({len(confirmations)}/5) → (5mins)"
					await msg.edit(embed=mod_ban_embed)
					if channel.permissions_for(u).administrator:
						break
					elif len(confirmations) < 5:
						continue
					else:
						break

		# Checks if it was a moderator ban request or just a normal ban
		if len(confirmations) == 0:
			perpetrators = ctx.author
			icon = ctx.author.display_avatar
		else:
			perpetrators = ', '.join(confirmations.values())
			icon = ctx.guild.icon.url

		# Bans and logs
		# General embed
		general_embed = discord.Embed(description=f'**Reason:** {reason}', colour=discord.Colour.dark_red())
		general_embed.set_author(name=f'{member} has been banned', icon_url=member.display_avatar)
		await ctx.send(embed=general_embed)
		try:
			await member.send(content="If you think you should be unbanned, you can make a ban appeal here: https://discord.gg/f9B7FzYv8D", embed=general_embed)
		except Exception as e:
			pass
		try:
			await member.ban(delete_message_days=7, reason=reason)
		except Exception:
			await ctx.send('**You cannot do that!**', delete_after=3)
		else:
			# Moderation log embed
			moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
			embed = discord.Embed(title='__**Banishment**__', colour=discord.Colour.dark_red(),
								  timestamp=ctx.message.created_at)
			embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
							inline=False)
			embed.add_field(name='Reason:', value=f'```{reason}```')
			embed.set_author(name=member)
			embed.set_thumbnail(url=member.display_avatar)
			embed.set_footer(text=f"Banned by {perpetrators}", icon_url=icon)
			await moderation_log.send(embed=embed)
			# Inserts a infraction into the database
			current_ts = await utils.get_timestamp()
			await self.insert_user_infraction(
				user_id=member.id, infr_type="ban", reason=reason,
				timestamp=current_ts, perpetrator=ctx.author.id)

			

	# Bans a member
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def fban(self, ctx, member: discord.Member = None, *, reason: Optional[str] = None):
		'''
		(ADM) Bansn't a member from the server.
		:param member: The @ or ID of the user to ban.
		:param reason: The reason for banning the user. (Optional)
		'''
		await ctx.message.delete()
		if not member:
			await ctx.send('**Please, specify a member!**', delete_after=3)
		else:
			# General embed
			general_embed = discord.Embed(description=f'**Reason:** {reason}', colour=discord.Colour.dark_red())
			general_embed.set_author(name=f'{member} has been banned', icon_url=member.display_avatar)
			await ctx.send(embed=general_embed)

	# Unbans a member
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def unban(self, ctx, *, member=None):
		'''
		(ADM) Unbans a member from the server.
		:param member: The full nickname and # of the user to unban.
		'''
		await ctx.message.delete()
		if not member:
			return await ctx.send('**Please, inform a member!**', delete_after=3)

		banned_users = await ctx.guild.bans()
		try:
			member_name, member_discriminator = str(member).split('#')
		except ValueError:
			return await ctx.send('**Wrong parameter!**', delete_after=3)

		for ban_entry in banned_users:
			user = ban_entry.user

			if (user.name, user.discriminator) == (member_name, member_discriminator):
				await ctx.guild.unban(user)
				# General embed
				general_embed = discord.Embed(colour=discord.Colour.red())
				general_embed.set_author(name=f'{user} has been unbanned', icon_url=user.display_avatar)
				await ctx.send(embed=general_embed)
				# Moderation log embed
				moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
				embed = discord.Embed(title='__**Unbanishment**__', colour=discord.Colour.red(),
									  timestamp=ctx.message.created_at)
				embed.add_field(name='User info:', value=f'```Name: {user.display_name}\nId: {user.id}```',
								inline=False)
				embed.set_author(name=user)
				embed.set_thumbnail(url=user.display_avatar)
				embed.set_footer(text=f"Unbanned by {ctx.author}", icon_url=ctx.author.display_avatar)
				await moderation_log.send(embed=embed)
				try:
					await user.send(embed=general_embed)
				except:
					pass
				return
		else:
			await ctx.send('**Member not found!**', delete_after=3)

	# Bans a member
	@commands.command()
	@utils.is_allowed(allowed_roles)
	async def softban(self, ctx, member: discord.Member = None, *, reason: Optional[str] = None):
		""" (ModTeam/ADM) Softbans a member from the server.
		:param member: The @ or ID of the user to ban.
		:param reason: The reason for banning the user. (Optional) """

		await ctx.message.delete()
		if not member:
			return await ctx.send('**Please, specify a member!**', delete_after=3)

		channel = ctx.channel
		author = ctx.author

		perpetrators = []
		confirmations = {}

		perms = channel.permissions_for(author)

		if not perms.administrator:
			confirmations[author.id] = author.name
			mod_softban_embed = discord.Embed(
				title=f"Softban Request ({len(confirmations)}/3) → (5mins)",
				description=f'''
				{author.mention} wants to softban {member.mention}, it requires 2 more moderator ✅ reactions for it!
				```Reason: {reason}```''',
				colour=discord.Colour.dark_purple(), timestamp=ctx.message.created_at)
			mod_softban_embed.set_author(name=f'{member} is going to Brazil, but will come back!', icon_url=member.display_avatar)
			msg = await ctx.send(embed=mod_softban_embed)
			await msg.add_reaction('✅')

			# Prompts for 3 moderator reactions
			def check_mod(r, u):
				if u.bot:
					return False
				if r.message.id != msg.id:
					return

				if str(r.emoji) == '✅':
					perms = channel.permissions_for(u)
					if mod_role_id in [r.id for r in u.roles] or perms.administrator:
						confirmations[u.id] = u.name
						return True
					else:
						self.client.loop.create_task(
							msg.remove_reaction('✅', u)
							)
						return False

				else:
					self.client.loop.create_task(
						msg.remove_reaction(r.emoji, u)
						)
					return False

			while True:
				try:
					r, u = await self.client.wait_for('reaction_add', timeout=300, check=check_mod)
				except asyncio.TimeoutError:
					mod_softban_embed.description = f'Timeout, {member} is not getting softbanned!'
					await msg.remove_reaction('✅', self.client.user)
					return await msg.edit(embed=mod_softban_embed)
				else:
					mod_softban_embed.title = f"Softban Request ({len(confirmations)}/3) → (5mins)"
					await msg.edit(embed=mod_softban_embed)
					if channel.permissions_for(u).administrator:
						break
					elif len(confirmations) < 3:
						continue
					else:
						break

		# Checks if it was a moderator ban request or just a normal ban
		if len(confirmations) == 0:
			perpetrators = ctx.author
			icon = ctx.author.display_avatar
		else:
			perpetrators = ', '.join(confirmations.values())
			icon = ctx.guild.icon.url

		# Bans and logs
		# General embed
		general_embed = discord.Embed(description=f'**Reason:** {reason}', colour=discord.Colour.dark_purple())
		general_embed.set_author(name=f'{member} has been softbanned', icon_url=member.display_avatar)
		await ctx.send(embed=general_embed)
		try:
			await member.send(content="https://discord.gg/languages", embed=general_embed)
		except Exception as e:
			pass
		try:
			await member.ban(delete_message_days=7, reason=reason)
			await member.unban(reason=reason)
		except Exception:
			await ctx.send('**You cannot do that!**', delete_after=3)
		else:
			# Moderation log embed
			moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
			embed = discord.Embed(title='__**SoftBanishment**__', colour=discord.Colour.dark_purple(),
								  timestamp=ctx.message.created_at)
			embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
							inline=False)
			embed.add_field(name='Reason:', value=f'```{reason}```')
			embed.set_author(name=member)
			embed.set_thumbnail(url=member.display_avatar)
			embed.set_footer(text=f"Banned by {perpetrators}", icon_url=icon)
			await moderation_log.send(embed=embed)
			# Inserts a infraction into the database
			current_ts = await utils.get_timestamp()
			await self.insert_user_infraction(
				user_id=member.id, infr_type="kick", reason=reason,
				timestamp=current_ts, perpetrator=ctx.author.id)

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def hackban(self, ctx, user_id: int = None, *, reason: Optional[str] = None):
		"""
		(ADM) Bans a user that is currently not in the server.
		Only accepts user IDs.
		:param user_id: Member ID
		:param reason: The reason for hackbanning the user. (Optional)
		"""

		await ctx.message.delete()
		if not user_id:
			return await ctx.send("**Inform the user id!**", delete_after=3)
		member = discord.Object(id=user_id)
		if not member:
			return await ctx.send("**Invalid user id!**", delete_after=3)
		try:
			await ctx.guild.ban(member, reason=reason)
			# General embed
			general_embed = discord.Embed(description=f'**Reason:** {reason}', colour=discord.Colour.dark_teal(),
										  timestamp=ctx.message.created_at)
			general_embed.set_author(name=f'{self.client.get_user(user_id)} has been hackbanned')
			await ctx.send(embed=general_embed)
			try:
				await member.send(embed=general_embed)
			except Exception as e:
				pass

			# Moderation log embed
			moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
			embed = discord.Embed(title='__**HackBanishment**__', colour=discord.Colour.dark_teal(),
								  timestamp=ctx.message.created_at)
			embed.add_field(name='User info:', value=f'```Name: {self.client.get_user(user_id)}\nId: {member.id}```',
							inline=False)
			embed.add_field(name='Reason:', value=f'```{reason}```')

			embed.set_author(name=self.client.get_user(user_id))
			embed.set_footer(text=f"HackBanned by {ctx.author}", icon_url=ctx.author.display_avatar)
			await moderation_log.send(embed=embed)

			# Inserts a infraction into the database
			current_ts = await utils.get_timestamp()
			await self.insert_user_infraction(
				user_id=member.id, infr_type="hackban", reason=reason,
				timestamp=current_ts, perpetrator=ctx.author.id)

		except discord.errors.NotFound:
			return await ctx.send("**Invalid user id!**", delete_after=3)

	@commands.command(aliases=['fire', 'wall', 'fire_wall'])
	@commands.has_permissions(administrator=True)
	async def firewall(self, ctx) -> None:
		""" Turns on and off the firewall.
		When turned on, it'll kick new members having accounts created in less than 4 days. """

		member = ctx.author

		if not await self.check_table_firewall_exists():
			return await ctx.send(f"**It looks like the firewall is on maintenance, {member.mention}!**")

		if await self.get_firewall_state():
			confirm = await Confirm(f"The Firewall is activated, do you want to turn it off, {member.mention}?").prompt(ctx)
			if confirm:
				await self.set_firewall_state(0)
				await ctx.send(f"**Firewall deactivated, {member.mention}!**")
				await self.client.get_cog('ReportSupport').audio(member, 'troll_firewall_off')
		else:
			confirm = await Confirm(f"The Firewall is deactivated, do you want to turn it on, {member.mention}?").prompt(ctx)
			if confirm:
				await self.set_firewall_state(1)
				await ctx.send(f"**Firewall activated, {member.mention}!**")
				await self.client.get_cog('ReportSupport').audio(member, 'troll_firewall_on')


	# Infraction methods
	@commands.command(aliases=['infr', 'show_warnings', 'sw', 'show_bans', 'sb', 'show_muted', 'sm'])
	@utils.is_allowed(allowed_roles)
	async def infractions(self, ctx, member: Optional[Union[discord.User, discord.Member]] = None) -> None:
		""" Shows all infractions of a specific user.
		:param member: The member to show the infractions from. [Optional] [Default = You] """

		if not member:
			return await ctx.send("**Inform a member!**")

		# Try to get user infractions
		if user_infractions := await self.get_user_infractions(member.id):
			warns = len([w for w in user_infractions if w[1] == 'warn'])
			mutes = len([m for m in user_infractions if m[1] == 'mute'])
			kicks = len([k for k in user_infractions if k[1] == 'kick'])
			bans = len([b for b in user_infractions if b[1] == 'ban'])
			softbans = len([sb for sb in user_infractions if sb[1] == 'softban'])
			hackbans = len([hb for hb in user_infractions if hb[1] == 'hackban'])
		else:
			return await ctx.send(f"**<@{member.id}> doesn't have any existent infractions!**")

		# Makes the initial embed with their amount of infractions
		embed = discord.Embed(
			title=f"Infractions for {member}",
			description=f"```ini\n[Warns]: {warns} | [Mutes]: {mutes} | [Kicks]: {kicks}\n[Bans]: {bans} | [Softbans]: {softbans} | [Hackbans]: {hackbans}```",
			color=member.color,
			timestamp=ctx.message.created_at)
		embed.set_thumbnail(url=member.display_avatar)
		embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.display_avatar)

		# Loops through each infraction and adds a field to the embedded message
		# 0-user_id, 1-infraction_type, 2-infraction_reason, 3-infraction_ts, 4-infraction_id, 5-perpetrator
		for infr in user_infractions:
			if (infr_type := infr[1]) in ['mute', 'warn']:
				infr_date = datetime.fromtimestamp(infr[3]).strftime('%Y/%m/%d at %H:%M:%S')
				perpetrator = discord.utils.get(ctx.guild.members, id=infr[5])
				embed.add_field(
					name=f"{infr_type} ID: {infr[4]}",
					value=f"```apache\nGiven on {infr_date}\nBy {perpetrator}\nReason: {infr[2]}```",
					inline=True)

		# Shows the infractions
		await ctx.send(embed=embed)

	@commands.command(aliases=['ri', 'remove_warn', 'remove_warning'])
	@utils.is_allowed(allowed_roles)
	async def remove_infraction(self, ctx, infr_id: int = None):
		"""
		(MOD) Removes a specific infraction by ID.
		:param infr_id: The infraction ID.
		"""

		if not infr_id:
			return await ctx.send("**Inform the infraction ID!**")

		if user_infractions := await self.get_user_infraction_by_infraction_id(infr_id):
			await self.remove_user_infraction(infr_id)
			member = discord.utils.get(ctx.guild.members, id=user_infractions[0][0])
			await ctx.send(f"**Removed infraction with ID `{infr_id}` for {member}**")
		else:
			await ctx.send(f"**Infraction with ID `{infr_id}` was not found!**")

	@commands.command(aliases=['ris', 'remove_warns', 'remove_warnings'])
	@utils.is_allowed(allowed_roles)
	async def remove_infractions(self, ctx, member: discord.Member = None):
		"""
		(MOD) Removes all infractions for a specific user.
		:param member: The member to get the warns from.
		"""

		if not member:
			return await ctx.send("**Inform a member!**")

		if await self.get_user_infractions(member.id):
			await self.remove_user_infractions(member.id)
			await ctx.send(f"**Removed all infractions for {member.mention}!**")
		else:
			await ctx.send(f"**{member.mention} doesn't have any existent infractions!**")
	

	@commands.command(aliases=['ei'])
	@utils.is_allowed(allowed_roles)
	async def edit_infraction(self, ctx, infr_id: int = None, *, reason: str) -> None:
		"""(MOD) Edits a specific infraction by ID.
		:param infr_id: The infraction ID.
		:param reason: New reason for the infraction."""

		if not infr_id:
			return await ctx.send("**Inform an infraction id!**")

		if user_infraction := await self.get_user_infraction_by_infraction_id(infr_id):
			
			# Get user by id
			member = self.client.get_user(user_infraction[0][0])

			# General embed
			general_embed = discord.Embed(description=f'**New Reason:** {reason}', colour=discord.Colour.lighter_grey())
			general_embed.set_author(name=f"{member}'s {user_infraction[0][1].capitalize()} reason has been edited", icon_url=member.display_avatar)
			general_embed.set_footer(text=f"Edited by {ctx.author}", icon_url=ctx.author.display_avatar)
			
			await ctx.send(embed=general_embed)
			
			# Moderation log embed
			moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)

			embed = discord.Embed(title=f'__**{user_infraction[0][1].capitalize()} Edited**__', colour=discord.Colour.lighter_grey(),
								  timestamp=ctx.message.created_at)

			embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
							inline=False)
			embed.add_field(name='New reason:', value=f'```{reason}```')
			embed.set_author(name=member)
			embed.set_thumbnail(url=member.display_avatar)
			embed.set_footer(text=f"Edited by {ctx.author}", icon_url=ctx.author.display_avatar)
			await moderation_log.send(embed=embed)

			try:
				await member.send(embed=general_embed)
			except Exception:
				pass

			return await self.edit_user_infractions(infr_id, reason)

		else:
			return await ctx.send(f"Infraction **{infr_id}** not found**")


	@commands.command(aliases=['apps'])
	@commands.has_permissions(administrator=True)
	async def applications(self, ctx, message_id: int = None, *, title: str = None) -> None:
		""" Opens/closes the applications for a title in the server.
		:param message_id: The ID of the Report-Support message to edit.
		:param title: The title that appliacations are opening/closing for. Ex: teacher/moderator. """

		member = ctx.author

		mod_app = ['moderator', 'mod', 'staff', 'm', 'moderation']

		teacher_app = ['teacher', 't', 'tchr', 'teaching']

		event_manager_app = ['eventmanager', 'event manager', 'em', 'evnt mng']

		if not message_id:
			return await ctx.send(f"**Please, inform a message ID, {member.mention}!**")

		if not title:
			return await ctx.send(f"**Please, inform a `title`, {member.mention}!**")

		if title.lower() not in mod_app + teacher_app + event_manager_app:
			return await ctx.send(f"**Invalid title, {member.mention}!**")

		channel = discord.utils.get(ctx.guild.text_channels, id=int(os.getenv('REPORT_CHANNEL_ID')))
		message = await channel.fetch_message(message_id) # Message containing the application buttons
		if not message:
			return await ctx.send(f"**Message not found, {member.mentio}!**")
		view = ReportSupportView.from_message(message)

		buttons = view.children

		if title.lower() in mod_app:
			buttons[1].disabled = False if buttons[1].disabled else True

			await ctx.send(f"**Moderator applications are now {'closed' if buttons[1].disabled else 'open'}, {member.mention}!**")

		elif title.lower() in teacher_app:
			buttons[0].disabled = False if buttons[0].disabled else True

			await ctx.send(f"**Teacher applications are now {'closed' if buttons[0].disabled else 'open'}, {member.mention}!**")
		
		elif title.lower() in event_manager_app:
			buttons[2].disabled = False if buttons[2].disabled else True

			await ctx.send(f"**Event Manager applications are now {'closed' if buttons[2].disabled else 'open'}, {member.mention}!**")


		confirm = await Confirm(f"**Do you wanna confirm the changes? Otherwise you can disregard the message above, {member.mention}.**").prompt(ctx)
		if confirm:
			await message.edit(view=view)
			await ctx.send(f"**Done!**")
		else:
			await ctx.send("**Not changing it, then...**")



def setup(client):
	client.add_cog(Moderation(client))
