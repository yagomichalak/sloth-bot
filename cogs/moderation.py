from logging import exception
import discord
from discord import user
from discord.ext import commands, tasks, menus
from discord.app.commands import user_command
import asyncio
from mysqldb import *
from datetime import datetime
from typing import List, Union, Optional, Dict, Tuple
import os

from extra.useful_variables import banned_links
from extra.prompt.menu import Confirm
from extra.view import ReportSupportView
from extra import utils
from extra.menu import MemberSnipeLooping, SnipeLooping

from extra.moderation.firewall import ModerationFirewallTable, BypassFirewallTable
from extra.moderation.mutedmember import ModerationMutedMemberTable
from extra.moderation.userinfractions import ModerationUserInfractionsTable
from extra.moderation.watchlist import ModerationWatchlistTable
from extra.moderation.fakeaccounts import ModerationFakeAccountsTable
from extra.moderation.moderatednicknames import ModeratedNicknamesTable
from extra.moderation.user_muted_galaxies import UserMutedGalaxiesTable

# IDs
mod_log_id = int(os.getenv('MOD_LOG_CHANNEL_ID', 123))
welcome_channel_id = int(os.getenv('WELCOME_CHANNEL_ID', 123))
suspect_channel_id = int(os.getenv('SUSPECT_CHANNEL_ID', 123))

last_deleted_message = []

mod_role_id = int(os.getenv('MOD_ROLE_ID', 123))
muted_role_id = int(os.getenv('MUTED_ROLE_ID', 123))
preference_role_id = int(os.getenv('PREFERENCE_ROLE_ID', 123))
senior_mod_role_id: int = int(os.getenv('SENIOR_MOD_ROLE_ID', 123))
allowed_roles = [int(os.getenv('OWNER_ROLE_ID', 123)), int(os.getenv('ADMIN_ROLE_ID', 123)), senior_mod_role_id, mod_role_id]

server_id = int(os.getenv('SERVER_ID', 123))
guild_ids: List[int] = [server_id]

moderation_cogs: List[commands.Cog] = [
	ModerationFirewallTable, BypassFirewallTable, ModerationMutedMemberTable, 
	ModerationUserInfractionsTable, ModerationWatchlistTable, ModerationFakeAccountsTable,
	ModeratedNicknamesTable, UserMutedGalaxiesTable
]

class Moderation(*moderation_cogs):
	""" Moderation related commands. """

	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_ready(self):
		self.look_for_expired_tempmutes.start()
		self.guild = self.client.get_guild(server_id)
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

		current_ts = await utils.get_timestamp()
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
							current_time = await utils.get_time_now()

							# Moderation log embed
							moderation_log = discord.utils.get(guild.channels, id=mod_log_id)
							embed = discord.Embed(title='__**Unmute**__', colour=discord.Colour.light_grey(), timestamp=current_time)
							embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
							inline=False)
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

		if inv_code in ['TE6hPrn65a']:
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
				if not await self.get_bypass_firewall_user(member.id):
					return await member.kick(reason="Possible fake account")
				else:
					await self.delete_bypass_firewall_user(member.id)

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

		if len(last_deleted_message) >= 1000:
			last_deleted_message[1:]
		last_deleted_message.append({message.author.id : {"content" : message.content, "time" : (message.created_at).timestamp(), 'channel' : message.channel }})

	async def search_user_deleted_messages(self, member) -> List[Dict]:
		deleteds_messages = []
		for message in last_deleted_message:
			member_id = next(iter(message))
			if member_id == member.id:
				message = message[member_id]
				deleteds_messages.append({"content" : message["content"], "time" : message["time"], "channel" : message["channel"]})

		deleteds_messages = (sorted(deleteds_messages, key = lambda d: d['time']))
		return deleteds_messages


	@commands.command()
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def snipe(self, ctx, *, message : str = None):
		"""(MOD) Snipes deleted messages.
		:param member: The @ or the ID of one or more users to snipe. (Optional) or
		:param quantity: The quantity of messages to snipe (Optional) """

		member, message_qtd = await utils.greedy_member_reason(ctx, message)

		if not last_deleted_message:
			await ctx.message.delete()
			return await ctx.send("**I couldn't snipe any message**")

		if not member:
			if not message_qtd:
				# Gets the last deleted message
				messages: List[Dict] = [last_deleted_message[-1]]

			else:
				# Gets the requested amount of deleted messages
				if int(message_qtd) <= 0:
					return await ctx.send("**I couldn't snipe any message**")

				if int(message_qtd) > len(last_deleted_message):
					message_qtd: int = len(last_deleted_message)

				messages: List[Dict] = sorted(last_deleted_message, key = lambda d:  d[next(iter(d))]['time'])
				messages: List[Dict] = messages[- int(message_qtd): ]
			menu = menus.MenuPages(SnipeLooping(messages))
			await ctx.message.delete()
			await menu.start(ctx)

		else:
			# Gets all deleted messsages from the user
			messages: List[Dict] = await self.search_user_deleted_messages(member[0])

			if not messages:
				return await ctx.send("**I couldn't snipe any messages from this member**")

			menu = menus.MenuPages(MemberSnipeLooping(messages, member[0]))
			await ctx.message.delete()
			await menu.start(ctx)


	# Purge command
	@commands.command()
	@commands.has_permissions(manage_messages=True)
	async def purge(self, ctx, *, message : str = None):
		""" (MOD) Purges messages.
		:param member: The member from whom to purge the messages. (Optional)
		:param amount: The amount of messages to purge. """

		await ctx.message.delete()

		members, amount = await utils.greedy_member_reason(ctx, message)

		if not members and len(ctx.message.content.split()) > 2:
			return await ctx.send(f"**Use z!purge Member[Optional] amount**", delete_after=5)

		if not amount or not amount.isdigit() or int(amount) < 1:
			return await ctx.send("**Please, insert a valid amount of messages to delete**", delete_after=5)

		perms = ctx.channel.permissions_for(ctx.author)
		if not perms.administrator and not ctx.author.get_role(senior_mod_role_id):
			if int(amount) > 30:
				return await ctx.send(f"**You cannot delete more than `30` messages at a time, {ctx.author.mention}!**")

		# global deleted
		deleted = 0
		if members:
			members_id = [member.id for member in members]
			channel = ctx.channel
			msgs = list(filter(
				lambda m: m.author.id in members_id,
				await channel.history(limit=200).flatten()
			))
			for _ in range(int(amount)):
				await msgs.pop(0).delete()
				deleted += 1

			await ctx.send(f"**`{deleted}` messages deleted from `{' and '.join(member.name for member in members)}`**",
				delete_after=5)

		else:
			await ctx.channel.purge(limit=int(amount))

	@commands.command()
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def clear(self, ctx):
		""" (MOD) Clears the whole channel. """

		special_channels = {
		  int(os.getenv('MUTED_CHANNEL_ID', 123)): 'https://cdn.discordapp.com/attachments/746478846466981938/748605295122448534/Muted.png',
		  int(os.getenv('QUESTION_CHANNEL_ID', 123)): '''**Would you like to ask us a question about the server? Ask them there!**
	`Questions will be answered and deleted immediately.`''',
		  int(os.getenv('SUGGESTION_CHANNEL_ID', 123)): '''**Would you like to suggest a feature for the server? Please follow this template to submit your feature request**

	**Suggestion:**
	`A short idea name/description`

	**Explanation:**
	`Explain the feature in detail and including reasons why you would like this feature to be implemented.`'''
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
	@commands.command(aliases=['warnado'])
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def warn(self, ctx, *, message : str = None) -> None:
		"""(MOD) Warns one or more members.
		:param member: The @ or the ID of one or more users to warn.
		:param reason: The reason for warning one or all users. (Optional)"""

		await ctx.message.delete()

		members, reason = await utils.greedy_member_reason(ctx, message)

		if not members:
			await ctx.send("**Please, inform a member!**", delete_after=3)
		else:
			if len(reason) > 960:
				return await ctx.send(f"**Please, inform a reason that is lower than or equal to 960 characters, {ctx.author.mention}!**", delete_after=3)

			for member in members:
				if ctx.guild.get_member(member.id):
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
						await self._mute_callback(ctx, member=member, reason=reason)
				else:
					await ctx.send(f"**The user `{member}` is not on the server**", delete_after = 5)

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

	@commands.command(aliases=['show_muted_roles', 'check_muted', 'muted_roles', 'removed_roles', 'srr', 'see_removed_roles'])
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def show_removed_roles(self, ctx, member: Union[discord.Member, discord.User] = None) -> None:
		""" Shows the roles that were remove from the user when they got muted.
		:param member: The member to check it. """

		author = ctx.author
		if not member:
			return await ctx.send(f"**Please, inform the member to check the roles, {author.mention}!**")

		if not member.get_role(muted_role_id):
			return await ctx.send(f"**The given user is not even muted, {author.mention}!**")

		roles = await self.get_muted_roles(member.id)
		if not roles:
			return await ctx.send(f"**User had no roles, {author.mention}!**")

		roles = ', '.join([f"<@&{rid[1]}>" for rid in roles if rid[1] != preference_role_id])

		embed: discord.Embed = discord.Embed(
			title="__Removed Roles__",
			description=f"{member.mention} got the following roles removed after being muted:\n\n{roles}",
			color=member.color,
			timestamp=ctx.message.created_at
		)

		await ctx.send(embed=embed)

	async def add_galaxy_room_perms(self, member: discord.Member, muted_galaxies: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
		""" Removes teh user's permissions in all Galaxy Rooms.
		:param member: The member from whom to remove the permissions. """

		# Gets all Galaxy rooms that are created
		SmartRoom = self.client.get_cog('CreateSmartRoom')
		all_galaxies = await SmartRoom.get_galaxy_rooms()
		
		# Gets all Galaxy categories to give perms back
		galaxy_categories: Dict[discord.CategoryChannel, List[int]] = {
			gcat: galaxy for galaxy in all_galaxies
			for mgalaxy in muted_galaxies
			if galaxy[1] == mgalaxy[1]
			and (gcat := discord.utils.get(member.guild.categories, id=galaxy[1]))
		}
		# Gives perms to all Galaxy categories
		for gcat, ginfo in galaxy_categories.items():
			await SmartRoom.handle_permissions([member], ginfo, member.guild, allow=True)

	async def remove_galaxy_room_perms(self, member: discord.Member) -> List[Tuple[int, int]]:
		""" Removes teh user's permissions in all Galaxy Rooms.
		:param member: The member from whom to remove the permissions. """

		removed_grooms = []
		# Gets all Galaxy rooms that are created
		SmartRoom = self.client.get_cog('CreateSmartRoom')
		all_galaxies = await SmartRoom.get_galaxy_rooms()

		# Gets all selected Galaxy categories to remove perms
		galaxy_categories: Dict[discord.CategoryChannel, List[int]] = {
			gcat: galaxy for galaxy in all_galaxies
			if (gcat := discord.utils.get(member.guild.categories, id=galaxy[1]))
		}

		# Removes perms from the selected Galaxy categories
		for gcat, ginfo in galaxy_categories.items():
			overwrites = gcat.overwrites
			if not overwrites.get(member):
				continue

			await SmartRoom.handle_permissions([member], ginfo, member.guild, allow=False)
			removed_grooms.append((member.id, gcat.id))

		return removed_grooms

	@commands.command(name="mute", aliases=["shutup", "shut_up", "stfu", "zitto", "zitta", "shh", "tg", "ta_gueule", "tagueule", "mutado", "xiu", "calaboca"])
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def _mute_command(self, ctx, *, message : str = None) -> None:
		"""(MOD) Mutes one or more members.
		:param member: The @ or the ID of one or more users to mute.
		:param reason: The reason for muting one or all users. (Optional)"""

		members, reason = await utils.greedy_member_reason(ctx, message)

		await ctx.message.delete()

		if not members:
			return await ctx.send("**Please, inform a member!**", delete_after=3)

		for member in members:
			if ctx.guild.get_member(member.id):
				await self._mute_callback(ctx, member, reason)
			else:
				await ctx.send(f"** The user `{member}` is not on the server**")

	@user_command(name="Mute", guild_ids=guild_ids)
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def _mute_slash(self, ctx, user: discord.Member) -> None:
		""" (MOD) Mutes a member.
		:param member: The @ or the ID of the user to mute.
		:param reason: The reason for the mute. """

		await self._mute_callback(ctx, user)

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
			await member.move_to(None)
			keep_roles, remove_roles = await self.get_remove_roles(member, keep_roles=allowed_roles)

			current_ts = await utils.get_timestamp()
			keep_roles.append(role)

			await member.edit(roles=keep_roles)
			user_role_ids = [(member.id, rr.id, current_ts, None) for rr in remove_roles]
			await self.insert_in_muted(user_role_ids)

			removed_grooms = await self.remove_galaxy_room_perms(member)
			await self.insert_user_muted_galaxies(removed_grooms)

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

			# Sends the muted channel rules to the user
			rules_embed = discord.Embed(color=discord.Color.dark_grey(), timestamp=current_time,
				description=
				"""**You have been muted. You can see the reason of your mute above.**
				You can get unmuted only by talking to the Staff member that muted you.

				Behaviours in the <#656730447857975296> that might result in a ban:
				**1**. Trolling
				**2**. Insulting Staff Members
				**3**. Pinging Admins/Moderators

				**P.S.** Being muted does not mean you are banned or being punished. It means that a Staff member wants to talk to you to solve an ongoing case, colaborate with them to be unmuted asap.
			""")
			try:
				await member.send(embed=rules_embed)
			except:
				pass

		else:
			await answer(f'**{member} is already muted!**')

	# Unmutes a member
	@commands.command(name="unmute")
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def _unmute_command(self, ctx, *, message : str = None) -> None:
		"""(MOD) Unmutes one or more members instantly or after a determined amount of time.
		:param member: The @ or the ID of one or more users to unmute.
		:param time: The time before unmuting one or all users. (Optional)"""

		await ctx.message.delete()
		members, time = await utils.greedy_member_reason(ctx, message)

		if not members:
			return await ctx.send("**Please, inform a member!**", delete_after=3)

		if time == None:
			for member in members:
				if ctx.guild.get_member(member.id):
					await self._unmute_callback(ctx, member)
				else:
					await ctx.send(f"** The user `{member}` is not on the server**")
		else:
			role = discord.utils.get(ctx.guild.roles, id=muted_role_id)
			for member in members:
				if ctx.guild.get_member(member.id):
					if role in member.roles:
						current_ts = await utils.get_timestamp()
						time_dict, seconds = await utils.get_time_from_text(ctx, time)

						general_embed = discord.Embed(description=f"**In:** `{time_dict['days']}d`, `{time_dict['hours']}h`, `{time_dict['minutes']}m`\n", colour=discord.Colour.dark_grey(), timestamp=ctx.message.created_at)
						general_embed.set_author(name=f"{member} will be unmuted", icon_url=member.display_avatar)
						await ctx.send(embed=general_embed)

						moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
						embed = discord.Embed(
							description=F"**Unmuting** {member.mention}\n **In:** `{time_dict['days']}d`, `{time_dict['hours']}h`, `{time_dict['minutes']}m`\n**Location:** {ctx.channel.mention}",
							color=discord.Color.lighter_grey(),
							timestamp=ctx.message.created_at)
						embed.set_author(name=f"{ctx.author} (ID {ctx.author.id})", icon_url=ctx.author.display_avatar)
						embed.set_thumbnail(url=member.display_avatar)
						await moderation_log.send(embed=embed)

						# Updating the member muted database
						await ModerationMutedMemberTable.update_mute_time(ctx, member.id, current_ts, seconds)
					else:
						await ctx.send(f"User {member} is not muted")
				else:
					await ctx.send(f"** The user `{member}` is not on the server**")


	@user_command(name="Unmute", guild_ids=guild_ids)
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def _unmute_slash(self, ctx, user: discord.Member) -> None:
		""" (MOD) Mutes a member.
		:param member: The @ or the ID of the user to mute.
		:param reason: The reason for the mute. """

		await self._unmute_callback(ctx, user)

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
			return await answer("**Please, specify a member!**")

		if not member.get_role(role.id):
			return await answer(f'**{member} is not even muted!**')

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

		if muted_galaxies := await self.get_user_muted_galaxies(member.id):
			await self.add_galaxy_room_perms(member, muted_galaxies)
			await self.delete_user_muted_galaxies(member.id)

		try:
			await member.remove_roles(role)
		except:
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
			
	# Mutes a member temporarily
	@commands.command()
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def tempmute(self, ctx, member: discord.Member = None, reason: str = None, *, time: str = None):
		""" Mutes a member for a determined amount of time.
		:param member: The @ or the ID of the user to tempmute.
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

		time_dict, seconds = await utils.get_time_from_text(ctx, time=time)
		if not seconds:
			return

		current_ts = await utils.get_timestamp()

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


	@commands.command(aliases=['kickado'])
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def kick(self, ctx, *, message : str = None):
		""" (MOD) Kicks one or more members from the server.
		:param member: The @ or the ID of one or more users to kick.
		:param reason: The reason for kicking one or all users. (Optional) """

		await ctx.message.delete()

		members, reason = await utils.greedy_member_reason(ctx, message)

		if not members:
			return await ctx.send('**Please, inform a member!**', delete_after=3)

		for member in members:
			if ctx.guild.get_member(member.id):
				if not await utils.is_allowed(allowed_roles).predicate(channel=ctx.channel, member=member):
					confirm = await Confirm(f"**Are you sure you want to kick {member.mention} from the server, {ctx.author.mention}?**").prompt(ctx)
					if not confirm:
						continue

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
				else:
					await ctx.send(f"**You cannot kick a staff member, {ctx.author.mention}!**")
			else:
				await ctx.send(f"** The user `{member}` is not on the server**")

	# Bans a member
	@commands.command(aliases=['banido'])
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def ban(self, ctx, member: Optional[discord.Member] = None, *, reason: Optional[str] = None):
		""" (ModTeam/ADM) Bans a member from the server.
		:param member: The @ or ID of the user to ban.
		:param reason: The reason for banning the user. (Optional)
		
		PS: Needs 4 mods to ban, in a ModTeam ban. """

		await ctx.message.delete()

		channel = ctx.channel
		author = ctx.author

		if not member:
			return await ctx.send('**Member not found!**', delete_after=3)

		if await utils.is_allowed(allowed_roles).predicate(channel=ctx.channel, member=member):
			return await ctx.send(f"**You cannot ban a staff member, {author.mention}!**")
			
		perpetrators = []
		confirmations = {}

		perms = channel.permissions_for(author)

		if not perms.administrator:
			confirmations[author.id] = author.name
			mod_ban_embed = discord.Embed(
				title=f"Ban Request ({len(confirmations)}/4) → (5mins)",
				description=f'''
				{author.mention} wants to ban {member.mention}, it requires 3 more moderator ✅ reactions for it!
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
					mod_ban_embed.title = f"Ban Request ({len(confirmations)}/4) → (5mins)"
					await msg.edit(embed=mod_ban_embed)
					if channel.permissions_for(u).administrator:
						break
					elif len(confirmations) < 4:
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
	async def fban(self, ctx, *, message : str = None):
		""" (ADM) Bansn't a member from the server.
		:param member: The @ or ID of the user to ban.
		:param reason: The reason for banning the user. (Optional) """

		await ctx.message.delete()

		members, reason = await utils.greedy_member_reason(ctx, message)

		if not members:
			await ctx.send('**Member not found!**', delete_after=3)
		else:
			for member in members:
				# General embed
				general_embed = discord.Embed(description=f'**Reason:** {reason}', colour=discord.Colour.dark_red())
				general_embed.set_author(name=f'{member} has been banned', icon_url=member.display_avatar)
				await ctx.send(embed=general_embed)

	# Unbans a member
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def unban(self, ctx, *, member=None):
		""" (ADM) Unbans a member from the server.
		:param member: The full nickname and # of the user to unban. """

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
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def softban(self, ctx, member: Optional[discord.Member] = None, *, reason: Optional[str] = None):
		""" (ModTeam/ADM) Softbans a member from the server.
		:param member: The @ or ID of the user to ban.
		:param reason: The reason for banning the user. (Optional) """
	
		await ctx.message.delete()

		channel = ctx.channel
		author = ctx.author

		if not member:
			return await ctx.send(f"**Member not found, {author.mention}!**", delete_after=3)

		if not await utils.is_allowed(allowed_roles).predicate(channel=ctx.channel, member=member):
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
				await member.ban(delete_message_days=1, reason=reason)
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
					user_id=member.id, infr_type="softban", reason=reason,
					timestamp=current_ts, perpetrator=ctx.author.id)
		else:
				await ctx.send(f"**You cannot softban a staff member, {author.mention}!**")

	@commands.command(aliases=['nitrokick', 'nitro'])
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def nitro_kick(self, ctx, member: Optional[discord.Member] = None) -> None:
		""" (ModTeam/ADM) Mutes & Softbans a member from the server who's posting Nitro scam links.
		:param member: The @ or ID of the user to nitrokick. """
	
		await ctx.message.delete()

		channel = ctx.channel
		author = ctx.author

		current_ts: int = await utils.get_timestamp()

		reason = 'Nitro Scam'

		if not member:
			return await ctx.send(f"**Member not found, {author.mention}!**", delete_after=3)

		if not await utils.is_allowed(allowed_roles).predicate(channel=ctx.channel, member=member):
			perpetrators = []
			confirmations = {}

			if not await utils.is_allowed([senior_mod_role_id]).predicate(channel=ctx.channel, member=author):
				confirmations[author.id] = author.name
				mod_softban_embed = discord.Embed(
					title=f"NitroKick Request ({len(confirmations)}/3) → (5mins)",
					description=f'''
					{author.mention} wants to nitrokick {member.mention}, it requires 2 more moderator ✅ reactions for it!
					```Reason: {reason}```''',
					colour=discord.Colour.nitro_pink(), timestamp=ctx.message.created_at)
				mod_softban_embed.set_author(name=f'{member} is being NitroKicked!', icon_url=member.display_avatar)
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
						mod_softban_embed.description = f'Timeout, {member} is not getting nitrobanned!'
						await msg.remove_reaction('✅', self.client.user)
						return await msg.edit(embed=mod_softban_embed)
					else:
						mod_softban_embed.title = f"NitroKick Request ({len(confirmations)}/3) → (5mins)"
						await msg.edit(embed=mod_softban_embed)
						if await utils.is_allowed([senior_mod_role_id]).predicate(channel=ctx.channel, member=u):
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
			general_embed = discord.Embed(description=f'**Reason:** {reason}', color=discord.Color.nitro_pink())
			general_embed.set_author(name=f'{member} has been nitrokicked', icon_url=member.display_avatar)
			await ctx.send(embed=general_embed)
			try:
				await member.send(content="Your account has been compromised and is now sending nitro scam links, please change your password and enable 2 Factor Authentication in order to regain access to our server\n\nhttps://discord.gg/languages", embed=general_embed)
			except Exception as e:
				pass
			try:

				keep_roles, remove_roles = await self.get_remove_roles(member, keep_roles=allowed_roles)

				await member.edit(roles=keep_roles)
				user_role_ids = [(member.id, rr.id, current_ts, None) for rr in remove_roles]
				await self.insert_in_muted(user_role_ids)
				await member.ban(delete_message_days=1, reason=reason)
				await member.unban(reason=reason)
			except Exception:
				await ctx.send('**You cannot do that!**', delete_after=3)
			else:
				# Moderation log embed
				moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
				embed = discord.Embed(title='__**NitroKick**__', color=discord.Color.nitro_pink(),
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
					user_id=member.id, infr_type="mute", reason=reason,
					timestamp=current_ts, perpetrator=ctx.author.id)
				await self.insert_user_infraction(
					user_id=member.id, infr_type="softban", reason=reason,
					timestamp=current_ts, perpetrator=ctx.author.id)
		else:
				await ctx.send(f"**You cannot nitrokick a staff member, {author.mention}!**")


	# @utils.is_allowed([senior_mod_role_id], throw_exc=True)
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def hackban(self, ctx, user_id: int = None, *, reason: Optional[str] = None):
		""" (ADM) Bans a user that is currently not in the server.
		Only accepts user IDs.
		:param user_id: Member ID
		:param reason: The reason for hackbanning the user. (Optional) """

		await ctx.message.delete()
		if not user_id:
			return await ctx.send("**Inform the user id!**", delete_after=3)

		member = discord.Object(id=user_id)
		if not member:
			return await ctx.send("**Invalid user id!**", delete_after=3)

		guild_member = discord.utils.get(ctx.guild.members, id=member.id)
		if guild_member:
			if await utils.is_allowed(allowed_roles).predicate(channel=ctx.channel, member=guild_member):
				return await ctx.send(f"**You cannot hackban a staff member, {ctx.author}!**", delete_after=3)
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
	@utils.is_allowed([senior_mod_role_id], throw_exc=True)
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

	@commands.command(aliases=['bfw', 'bypassfirewall', 'bypass_fire', 'bypassfire'])
	@utils.is_allowed([senior_mod_role_id, mod_role_id], throw_exc=True)
	async def bypass_firewall(self, ctx, user: discord.User = None) -> None:
		""" Makes a user able to bypass the Firewall.
		:param user: The user to make able to do so. """

		member: discord.Member = ctx.author

		if not user:
			return await ctx.send(f"**Please, inform a user, {member.mention}!**")

		if ctx.guild.get_member(user.id):
			return await ctx.send(f"**This user is already in the server, {member.mention}!**")

		if await self.get_bypass_firewall_user(user.id):
			return await ctx.send(f"**This user can already bypass the Firewall, {member.mention}!**")

		await self.insert_bypass_firewall_user(user.id)
		await ctx.send(f"**The `{user}` user can now bypass the Firewall, {member.mention}!**")

	@commands.command(aliases=['ubfw', 'unbypassfirewall', 'unbypass_fire', 'unbypassfire'])
	@utils.is_allowed([senior_mod_role_id], throw_exc=True)
	async def unbypass_firewall(self, ctx, user: discord.User = None) -> None:
		""" Makes a user not able to bypass the Firewall anymore.
		:param user: The user to make able to do so. """

		member: discord.Member = ctx.author

		if not user:
			return await ctx.send(f"**Please, inform a user, {member.mention}!**")

		if not await self.get_bypass_firewall_user(user.id):
			return await ctx.send(f"**This user wasn't able to bypass the Firewall, {member.mention}!**")

		await self.delete_bypass_firewall_user(user.id)
		await ctx.send(f"**The `{user}` user can no longer bypass the Firewall now, {member.mention}!**")

	@commands.command(aliases=['sbfw', 'showbypassfirewall', 'show_bypass_fire', 'showbypassfire'])
	@utils.is_allowed([senior_mod_role_id], throw_exc=True)
	async def show_bypass_firewall(self, ctx) -> None:
		""" Checks the users who are able to bypass the Firewall. """

		member: discord.Member = ctx.author

		bf_users = await self.get_bypass_firewall_users()
		if not bf_users:
			return await ctx.send(f"**No users can bypass the Firewall, {member.mention}!**")
		
		formatted_bf_users: str = '\n'.join([f"**{await self.client.fetch_user(bf_user[0])}** (`{bf_user[0]}`)" for bf_user in bf_users])

		embed: discord.Embed = discord.Embed(
			title="__Bypass Firewall Users__",
			description=formatted_bf_users,
			color=member.color,
			timestamp=ctx.message.created_at
		)
		embed.set_thumbnail(url=ctx.guild.icon)
		embed.set_footer(text=f"Requested by {member}", icon_url=member.display_avatar)
		await ctx.send(embed=embed)



	# Infraction methods
	@commands.command(aliases=['infr', 'show_warnings', 'sw', 'show_bans', 'sb', 'show_muted', 'sm'])
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def infractions(self, ctx, *, message : str = None) -> None:
		""" Shows all infractions of a specific user.
		:param member: The member to show the infractions from. [Optional] [Default = You] """

		try:
			await ctx.message.delete()
		except:
			pass

		members, _ = await utils.greedy_member_reason(ctx, message)

		if not members:
			members = [ctx.author]

		for member in members:
			# Try to get user infractions
			if user_infractions := await self.get_user_infractions(member.id):
				warns = len([w for w in user_infractions if w[1] == 'warn'])
				mutes = len([m for m in user_infractions if m[1] == 'mute'])
				kicks = len([k for k in user_infractions if k[1] == 'kick'])
				bans = len([b for b in user_infractions if b[1] == 'ban'])
				softbans = len([sb for sb in user_infractions if sb[1] == 'softban'])
				hackbans = len([hb for hb in user_infractions if hb[1] == 'hackban'])
			else:
				await ctx.send(f"**<@{member.id}> doesn't have any existent infractions!**")
				continue

			# Alerts if the user already was unmuted with temporizer
			unmute_alert = ''
			if await self.get_muted_roles(member.id):
				times = await self.get_mute_time(member.id)
				if times[1] != None:
					unmute_alert = f"\u200b\n**	♦️ This user will be unmuted <t:{times[0] + times[1]}:R>**\n\n"

			# Makes the initial embed with their amount of infractions
			embed = discord.Embed(
				title=f"Infractions for {member}",
				description=f"{unmute_alert}```ini\n[Warns]: {warns} | [Mutes]: {mutes} | [Kicks]: {kicks}\n[Bans]: {bans} | [Softbans]: {softbans} | [Hackbans]: {hackbans}```",
				color=member.color,
				timestamp=ctx.message.created_at)
			embed.set_thumbnail(url=member.display_avatar)
			embed.set_author(name=member.id)
			embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.display_avatar)

			# Loops through each infraction and adds a field to the embedded message
			# 0-user_id, 1-infraction_type, 2-infraction_reason, 3-infraction_ts, 4-infraction_id, 5-perpetrator
			for infr in user_infractions:
				if (infr_type := infr[1]) in ['mute', 'warn', 'ban', 'hackban']:
					infr_date = datetime.fromtimestamp(infr[3]).strftime('%Y/%m/%d at %H:%M:%S')
					perpetrator = discord.utils.get(ctx.guild.members, id=infr[5])
					embed.add_field(
						name=f"{infr_type} ID: {infr[4]}",
						value=f"```apache\nGiven on {infr_date}\nBy {perpetrator}\nReason: {infr[2]}```",
						inline=True)

			# Shows the infractions
			await ctx.send(embed=embed)

	@commands.command(aliases=['ri', 'remove_warn', 'remove_warning'])
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def remove_infraction(self, ctx, infrs_id : commands.Greedy[int] = None):
		""" (MOD) Removes one or more infractions by their IDs.
		:param infr_id: The infraction(s) IDs. """

		await ctx.message.delete()

		if not infrs_id:
			return await ctx.send("**Please, inform an infraction ID!**", delete_after = 3)

		for infr_id in infrs_id:
			if user_infractions := await self.get_user_infraction_by_infraction_id(infr_id):
				await self.remove_user_infraction(int(infr_id))
				member = discord.utils.get(ctx.guild.members, id=user_infractions[0][0])
				await ctx.send(f"**Removed infraction with ID `{infr_id}` for {member}**")
			else:
				await ctx.send(f"**Infraction with ID `{infr_id}` was not found!**")


	@commands.command(aliases=['ris', 'remove_warns', 'remove_warnings'])
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def remove_infractions(self, ctx, *, message):
		""" (MOD) Removes all infractions for one or more users.
		:param member: The member(s) to get the infractions from. """

		await ctx.message.delete()

		members, _ = await utils.greedy_member_reason(ctx, message)

		if not members:
			return await ctx.send('**Please, inform a member!**', delete_after=3)

		for member in members:
			if await self.get_user_infractions(member.id):
				await self.remove_user_infractions(member.id)
				await ctx.send(f"**Removed all infractions for {member.mention}!**")
			else:
				await ctx.send(f"**{member.mention} doesn't have any existent infractions!**")		


	@commands.command(aliases=['ei'])
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def edit_infraction(self, ctx, infractions_ids : commands.Greedy[int] = None, *, reason: Optional[str] = ' ') -> None:
		"""(MOD) Edits one or more infractions by their IDs.
		:param infr_id: The infraction(s) ID(s).
		:param reason: The updated reason of the infraction(s)."""
		
		# Remove numbers with less than 5 digits
		string_ids = [str(int_id) for int_id in infractions_ids]
		for i, infr in enumerate(string_ids):
			if len(infr) < 5:
				reason = ' '.join(string_ids[i:]) + ' ' + reason
				del infractions_ids[i:]
				break

		await ctx.message.delete()
		if not infractions_ids:
			return await ctx.send("**Please, inform an infraction id!**", delete_after=3)

		for infr_id in infractions_ids:
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

				embed = discord.Embed(title=f'__**{user_infraction[0][1].lower()} Edited**__', colour=discord.Colour.lighter_grey(),
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

				await self.edit_user_infractions(infr_id, reason)

			else:
				await ctx.send(f"**Infraction `{infr_id}` not found**")


	@commands.command(aliases=['apps'])
	@commands.has_permissions(administrator=True)
	async def applications(self, ctx, message_id: int = None, *, title: str = None) -> None:
		""" Opens/closes the applications for a title in the server.
		:param message_id: The ID of the Report-Support message to edit.
		:param title: The title that appliacations are opening/closing for. Ex: teacher/moderator. """

		member = ctx.author

		mod_app = ['moderator', 'mod', 'staff', 'm', 'moderation']

		teacher_app = ['teacher', 't', 'tchr', 'teaching']

		event_host_app = ['eventhost', 'event host', 'em', 'evnt mng']

		if not message_id:
			return await ctx.send(f"**Please, inform a message ID, {member.mention}!**")

		if not title:
			return await ctx.send(f"**Please, inform a `title`, {member.mention}!**")

		if title.lower() not in mod_app + teacher_app + event_host_app:
			return await ctx.send(f"**Invalid title, {member.mention}!**")

		channel = discord.utils.get(ctx.guild.text_channels, id=int(os.getenv('REPORT_CHANNEL_ID', 123)))
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
		
		elif title.lower() in event_host_app:
			buttons[2].disabled = False if buttons[2].disabled else True

			await ctx.send(f"**Event Manager applications are now {'closed' if buttons[2].disabled else 'open'}, {member.mention}!**")


		confirm = await Confirm(f"**Do you wanna confirm the changes? Otherwise you can disregard the message above, {member.mention}.**").prompt(ctx)
		if confirm:
			await message.edit(view=view)
			await ctx.send(f"**Done!**")
		else:
			await ctx.send("**Not changing it, then...**")


	@commands.command()
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def cases(self, ctx, *, message: str = None) -> None:
		""" Shows people that you muted that don't have an unmute time set,
		in other words, people that you still have to deal with their case.
		:param member: The member to show the cases from. [Optional][Default=You] """
		
		await ctx.message.delete()

		perms = ctx.channel.permissions_for(ctx.author)

		senior_mod_role = discord.utils.get(ctx.guild.roles, id=senior_mod_role_id)

		members, _ = await utils.greedy_member_reason(ctx, message)

		if perms.administrator or senior_mod_role in ctx.author.roles:
			members = members if members else [ctx.message.author]
		else:
			if members:
				if members[0] != ctx.message.author:
					return await ctx.send("**You can't do that!**", delete_after=3)

			members = [ctx.message.author]

		for member in members:
			if await utils.is_allowed(allowed_roles).predicate(channel=ctx.channel, member=member):
				# Gets muted members
				muted_members = await self.get_not_unmuted_members()
				cases = []

				for user_id, mute_ts in muted_members:
					if ctx.guild.get_member(user_id):

						# Gets user infractions
						user_infractions = await self.get_user_infractions(user_id)
						
						for _, infraction_type, _, infraction_ts, infraction_id, perpetrator in user_infractions:
							# If the infraction has the same time as the mute timestamp and the perpetrator is the member add to the cases
							if infraction_type == 'mute' and infraction_ts == mute_ts and perpetrator == member.id:
								cases.append([user_id, mute_ts])
								break
						
				if cases:
					# General embed
					embed = discord.Embed(
						title = f"Open cases for: {member}",
						description = '\u200b\n' + ' '.join([f"<@{user_id}> **muted on <t:{mute_ts}:d> at <t:{mute_ts}:t>**\n\n" for user_id, mute_ts in cases]),
						timestamp=ctx.message.created_at
					)
					embed.set_thumbnail(url=member.display_avatar)
					embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar)
					await ctx.send(embeds=[embed])

				else:
					if member == ctx.author:
						await ctx.send(f"**You don't have any open cases**", delete_after=3)
					else:
						await ctx.send(f"**{member} does not have any open cases**", delete_after=3)
			else:

				await ctx.send(f"**The user {member} is not a staff member**", delete_after=3)

	@commands.command(aliases=["mn", "md_nickname", "mnick", "m_nick"])
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def moderate_nickname(self, ctx, member: discord.Member = None) -> None:
		""" Moderates someone's nickname.
		:param member: The member for whom to moderate the nickname. """

		await ctx.message.delete()
		author: discord.Member = ctx.author

		if not member:
			return await ctx.send(f"**Please, inform a member, {author.mention}!**")

		if await self.get_moderated_nickname(member.id):
			return await ctx.send(f"**This user's nickname has already been moderated, {author.mention}!**")

		name = member.name
		nick = member.display_name
		reason: str = f"Improper Nickname: {nick}"

		try:
			await self.insert_moderated_nickname(member.id, nick)
			await member.edit(nick="Moderated Nickname")
		except Exception as e:
			print('Error at Moderate Nickname: ', e)
			return await ctx.send(f"**For some reason I couldn't moderate this user's nickname, {author.mention}!**")

		# General embed
		general_embed = discord.Embed(description=f'**Reason:** {reason}', color=discord.Color.blue())
		general_embed.set_author(name=f'{member} got their nickname moderated.', icon_url=member.display_avatar)
		await ctx.send(embed=general_embed)
		# Moderation log embed
		moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
		embed = discord.Embed(title='__**Moderated Nickname:**__', color=discord.Color.blue(), timestamp=ctx.message.created_at)
		embed.add_field(name='User info:', value=f'```Name: {name}\nId: {member.id}```', inline=False)
		embed.add_field(name='Reason:', value=f'```{reason}```')
		embed.set_author(name=name)
		embed.set_thumbnail(url=member.display_avatar)
		embed.set_footer(text=f"Nickname-moderated by {author}", icon_url=author.display_avatar)
		await moderation_log.send(embed=embed)
		try:
			await member.send(embed=general_embed)
		except:
			pass

	@commands.command(aliases=["umn", "umd_nickname", "umnick", "um_nick"])
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def unmoderate_nickname(self, ctx, member: discord.Member = None) -> None:
		""" Unmoderates someone's nickname.
		:param member: The member for whom to unmoderate the nickname. """

		author: discord.Member = ctx.author

		if not member:
			return await ctx.send(f"**Please, inform a member, {author.mention}!**")

		if not await self.get_moderated_nickname(member.id):
			return await ctx.send(f"**This user's nickname hasn't been moderated yet, {author.mention}!**")

		try:
			await self.delete_moderated_nickname(member.id)
			await member.edit(nick=None)
		except Exception as e:
			print("Error at Unmoderate Nickname: ", e)
			return await ctx.send(f"**For some reason I couldn't unmoderate this user's nickname, {author.mention}!**")
		
		# General embed
		general_embed = discord.Embed(color=discord.Color.dark_blue())
		general_embed.set_author(name=f'{member} got their nickname unmoderated.', icon_url=member.display_avatar)
		await ctx.send(embed=general_embed)
		# Moderation log embed
		moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
		embed = discord.Embed(title='__**Unmoderated Nickname:**__', color=discord.Color.dark_blue(), timestamp=ctx.message.created_at)
		embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```', inline=False)
		embed.set_author(name=member.display_name)
		embed.set_thumbnail(url=member.display_avatar)
		embed.set_footer(text=f"Nickname-moderated by {author}", icon_url=author.display_avatar)
		await moderation_log.send(embed=embed)
		try:
			await member.send(embed=general_embed)
		except:
			pass

	@commands.command(aliases=["smn", "smnick", "show_mn", "showmn"])
	@utils.is_allowed(allowed_roles, throw_exc=True)
	async def show_moderated_nickname(self, ctx, member: discord.Member = None) -> None:
		""" Shows the user's previous nickname that got moderated.
		:param member: The member to show. """

		author: discord.Member = ctx.author
		if not member:
			return await ctx.send(f"**Please, inform a member to show, {author.mention}!**")

		if not (mn_user := await self.get_moderated_nickname(member.id)):
			return await ctx.send(f"**This user's nickname hasn't even been moderated, {author.mention}!**")

		embed: discord.Embed = discord.Embed(
			title="__Showing Moderated Nickname__",
			description=f"**User:** {member.mention} ({member.id})\n**Moderated Nickname:** {mn_user[1]}",
			color=member.color,
			timestamp=ctx.message.created_at
		)
		embed.set_thumbnail(url=member.display_avatar)
		embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)

		await ctx.send(embed=embed)
	
	@commands.command(aliases=['minfr', 'muted_infr'])
	@utils.is_allowed([senior_mod_role_id], throw_exc=True)
	async def muted_infractions(self, ctx) -> None:
		"""Shows the infractions for all muted members"""

		muted_role = discord.utils.get(ctx.guild.roles, id=muted_role_id)

		muted_members = []

		# Gets all muted members
		for member in ctx.guild.members:
			if muted_role in member.roles:
				muted_members.append(str(member.id))

		if not muted_members:
			return await ctx.send("**There is no muted members**")

		await self.infractions(context=ctx, message=' '.join(muted_members))


def setup(client):
	client.add_cog(Moderation(client))