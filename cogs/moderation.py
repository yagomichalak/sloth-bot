import discord
from discord.ext import commands, tasks
import asyncio
from mysqldb import *
from datetime import datetime
import time
from typing import List, Union, Dict, Tuple
import os

mod_log_id = int(os.getenv('MOD_LOG_CHANNEL_ID'))
muted_role_id = int(os.getenv('MUTED_ROLE_ID'))
general_channel = int(os.getenv('GENERAL_CHANNEL_ID'))
last_deleted_message = []
suspect_channel_id = int(os.getenv('SUSPECT_CHANNEL_ID'))
mod_role_id = int(os.getenv('MOD_ROLE_ID'))
allowed_roles = [int(os.getenv('OWNER_ROLE_ID')), int(os.getenv('ADMIN_ROLE_ID')), mod_role_id]
server_id = int(os.getenv('SERVER_ID'))

class Moderation(commands.Cog):
	'''
	Moderation related commands.
	'''

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

		# Invite tracker
		msg = str(message.content)
		if 'discord.gg/' in msg.lower():
			ctx = await self.client.get_context(message)
			perms = ctx.channel.permissions_for(ctx.author)
			if not perms.administrator and mod_role_id not in [r.id for r in ctx.author.roles]:
				is_from_guild = await self.check_invite_guild(msg, message.guild)
				if not is_from_guild:
					return await self.mute(ctx=ctx, member=message.author, reason="Invite Advertisement.")


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
						user_role_ids = [(member.id, mrole[1]) for mrole in user_roles]
						try:
							await self.remove_role_from_system(user_role_ids)
						except Exception as e:
							print(e)
							pass



					# Moderation log embed
					moderation_log = discord.utils.get(guild.channels, id=mod_log_id)
					embed = discord.Embed(
						description=F"**Unmuted** {member.mention}\n**Reason:** Tempmute is over",
						color=discord.Color.light_gray())
					embed.set_author(name=f"{self.client.user} (ID {self.client.user.id})", icon_url=self.client.user.avatar_url)
					embed.set_thumbnail(url=member.avatar_url)
					await moderation_log.send(embed=embed)
					try:
						await member.send(embed=embed)
					except:
						pass

			except Exception as e:
				print(e)
				continue

	async def get_expired_tempmutes(self, current_ts: int) -> List[int]:
		""" Gets expired tempmutes.
		:param current_ts: The current timestamp. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT DISTINCT(user_id) FROM mutedmember WHERE (%s -  mute_ts) >= muted_for_seconds", (current_ts,))
		tempmutes = list(map(lambda m: m[0], await mycursor.fetchall()))
		await mycursor.close()
		return tempmutes

				
	async def check_invite_guild(self, msg, guild):
		'''
		Checks whether it's a guild invite or not
		'''

		invite = 'discord.gg/'
		start_index = msg.index(invite)
		end_index = start_index + 11
		for c in msg[end_index:]:
			if c == ' ':
				break

			invite += c

		inv_code = discord.utils.resolve_invite(invite)
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
		time_now = datetime.timestamp(datetime.utcnow())
		account_age = round((time_now - timestamp)/86400)
		if account_age <= 2:
			suspect_channel = discord.utils.get(member.guild.channels, id=suspect_channel_id)
			await suspect_channel.send(f"🔴 Alert! Possible fake account: {member.mention} joined the server. Account was just created.\nAccount age: {account_age} day(s)!")


		if await self.get_muted_roles(member.id):
			muted_role = discord.utils.get(member.guild.roles, id=muted_role_id)
			await member.add_roles(muted_role)
			general = discord.utils.get(member.guild.channels, id=general_channel)
			await general.send(f"**Stop right there, {member.mention}! ✋ You were muted, left and rejoined the server, but that won't work!**")
	
	@commands.Cog.listener()
	async def on_message_delete(self, message):
		if message.author.bot:
			return
		last_deleted_message.clear()
		last_deleted_message.append(message)

	@commands.command()
	@commands.has_any_role(*allowed_roles)
	async def snipe(self, ctx):
		'''
		(MOD) Snipes the last deleted message.
		'''
		message = last_deleted_message
		if message:
			message = message[0]
			embed = discord.Embed(title="Sniped", description=f"**>>** {message.content}", color=message.author.color, timestamp=message.created_at)
			embed.set_author(name=message.author,url=message.author.avatar_url, icon_url=message.author.avatar_url)
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
	@commands.has_any_role(*allowed_roles)
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
	@commands.has_any_role(*allowed_roles)
	async def warn(self, ctx, member: discord.Member = None, *, reason=None):
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
			general_embed.set_author(name=f'{member} has been warned', icon_url=member.avatar_url)
			await ctx.send(embed=general_embed)
			# Moderation log embed
			moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
			embed = discord.Embed(title='__**Warning**__', colour=discord.Colour.dark_gold(),
								  timestamp=ctx.message.created_at)
			embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
							inline=False)
			embed.add_field(name='Reason:', value=f'```{reason}```')
			embed.set_author(name=member)
			embed.set_thumbnail(url=member.avatar_url)
			embed.set_footer(text=f"Warned by {ctx.author}", icon_url=ctx.author.avatar_url)
			await moderation_log.send(embed=embed)
			# Inserts a infraction into the database
			epoch = datetime.utcfromtimestamp(0)
			current_ts = (datetime.utcnow() - epoch).total_seconds()
			await self.insert_user_infraction(
				user_id=member.id, infr_type="warn", reason=reason,
				timestamp=current_ts , perpetrator=ctx.author.id)
			try:
				await member.send(embed=general_embed)
			except:
				pass

			user_infractions = await self.get_user_infractions(member.id)
			user_warns = [w for w in user_infractions if w[1] == 'warn']
			if len(user_warns) >= 3:
				ctx.author = self.client.user
				await self.mute(ctx=ctx, member=member, reason=reason)

	async def get_mute_time(self, ctx: commands.Context, time: List[str]) -> Dict[str, int]:
		""" Gets the mute time in seconds.
		:param ctx: The context.
		:param time: The given time. """

		print('here?')
		
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


	@commands.command()
	@commands.has_any_role(*allowed_roles)
	async def mute(self, ctx, member: discord.Member = None, *, reason = None):
		'''
		(MOD) Mutes a member.
		:param member: The @ or the ID of the user to mute.
		:param reason: The reason for the mute.
		'''
		try:
			await ctx.message.delete()
		except:
			pass

		role = discord.utils.get(ctx.guild.roles, id=muted_role_id)
		if not member:
			return await ctx.send("**Please, specify a member!**")
		if role not in member.roles:
			# await member.add_roles(role)
			await member.move_to(None)
			remove_roles = []
			keep_roles = [role]

			bot = discord.utils.get(ctx.guild.members, id=self.client.user.id)

			for i, member_role in enumerate(member.roles):
				if i == 0:
					continue

				if member_role.id == role.id:
					continue

				if member_role < bot.top_role:
					remove_roles.append(member_role)

				if member_role >= bot.top_role:
					keep_roles.append(member_role)

			await member.edit(roles=keep_roles)
			user_role_ids = [(member.id, rr.id, None, None) for rr in remove_roles]
			await self.insert_in_muted(user_role_ids)

			# General embed
			general_embed = discord.Embed(description=f'**Reason:** {reason}', colour=discord.Colour.dark_grey(), timestamp=ctx.message.created_at)
			general_embed.set_author(name=f'{member} has been muted', icon_url=member.avatar_url)
			await ctx.send(embed=general_embed)
			# Moderation log embed
			moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
			embed = discord.Embed(title='__**Mute**__', colour=discord.Colour.dark_grey(),
								  timestamp=ctx.message.created_at)
			embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
							inline=False)
			embed.add_field(name='Reason:', value=f'```{reason}```')

			embed.set_author(name=member)
			embed.set_thumbnail(url=member.avatar_url)
			embed.set_footer(text=f"Muted by {ctx.author}", icon_url=ctx.author.avatar_url)
			await moderation_log.send(embed=embed)
			# Inserts a infraction into the database
			epoch = datetime.utcfromtimestamp(0)
			current_ts = (datetime.utcnow() - epoch).total_seconds()
			await self.insert_user_infraction(
				user_id=member.id, infr_type="mute", reason=reason,
				timestamp=current_ts , perpetrator=ctx.author.id)
			try:
				await member.send(embed=general_embed)
			except:
				pass
		
		else:
			await ctx.send(f'**{member} is already muted!**')

	# Unmutes a member
	@commands.command()
	@commands.has_any_role(*allowed_roles)
	async def unmute(self, ctx, member: discord.Member = None):
		'''
		(MOD) Unmutes a member.
		:param member: The @ or the ID of the user to unmute.
		'''
		await ctx.message.delete()
		role = discord.utils.get(ctx.guild.roles, id=muted_role_id)
		if not member:
			return await ctx.send("**Please, specify a member!**", delete_after=3)
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
				user_role_ids = [(member.id, mrole[1]) for mrole in user_roles]
				try:
					await self.remove_role_from_system(user_role_ids)
				except Exception as e:
					print(e)
					pass

			general_embed = discord.Embed(colour=discord.Colour.light_grey(),
										  timestamp=ctx.message.created_at)
			general_embed.set_author(name=f'{member} has been unmuted', icon_url=member.avatar_url)
			await ctx.send(embed=general_embed)
			# Moderation log embed
			moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
			embed = discord.Embed(title='__**Unmute**__', colour=discord.Colour.light_grey(),
								  timestamp=ctx.message.created_at)
			embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
							inline=False)
			embed.set_author(name=member)
			embed.set_thumbnail(url=member.avatar_url)
			embed.set_footer(text=f"Unmuted by {ctx.author}", icon_url=ctx.author.avatar_url)
			await moderation_log.send(embed=embed)
			try:
				await member.send(embed=general_embed)
			except:
				pass

		else:
			await ctx.send(f'**{member} is not even muted!**', delete_after=5)

	# Mutes a member temporarily
	@commands.command()
	@commands.has_any_role(*allowed_roles)
	async def tempmute(self, ctx, member: discord.Member = None, reason: str =  None, *, time: str = None):
		"""
		Mutes a member for a determined amount of time.
		:param member: The @ or the ID of the user to tempmute.
		:param minutes: The amount of minutes that the user will be muted.
		:param reason: The reason for the tempmute.
		:param time: The time for the mute.
		"""
		await ctx.message.delete()

		role = discord.utils.get(ctx.guild.roles, id=muted_role_id)

		if not member:
			return await ctx.send("**Please, specify a member!**", delete_after=3)

		if not reason:
			return await ctx.send(f"**Specify a reason!**", delete_after=3)

		if not time:
			return await ctx.send('**Inform a time!**', delete_after=3)


		time_dict, seconds = await self.get_mute_time(ctx=ctx, time=time)
		if not seconds:
			return


		# print('ah')
		epoch = datetime.utcfromtimestamp(0)
		current_ts = int((datetime.utcnow() - epoch).total_seconds())

		# print(current_ts, seconds)

		if role not in member.roles:
			# await member.add_roles(role)
			await member.move_to(None)
			remove_roles = []
			keep_roles = [role]

			bot = discord.utils.get(ctx.guild.members, id=self.client.user.id)

			for i, member_role in enumerate(member.roles):
				if i == 0:
					continue

				if member_role.id == role.id:
					continue

				if member_role < bot.top_role:
					remove_roles.append(member_role)

				if member_role >= bot.top_role:
					keep_roles.append(member_role)

			await member.edit(roles=keep_roles)
			user_role_ids = [(member.id, rr.id, current_ts, seconds) for rr in remove_roles]
			await self.insert_in_muted(user_role_ids)

			# General embed
			general_embed = discord.Embed(description=f"**For:** `{time_dict['days']}d`, `{time_dict['hours']}h`, `{time_dict['minutes']}m` and `{time_dict['seconds']}s`\n**Reason:** {reason}", colour=discord.Colour.dark_grey(), timestamp=ctx.message.created_at)
			general_embed.set_author(name=f"{member} has been tempmuted", icon_url=member.avatar_url)
			await ctx.send(embed=general_embed)
			# Moderation log embed
			moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
			embed = discord.Embed(
				description=F"**Tempmuted** {member.mention} for `{time_dict['days']}d`, `{time_dict['hours']}h`, `{time_dict['minutes']}m` and `{time_dict['seconds']}s`\n**Reason:** {reason}\n**Location:** {ctx.channel.mention}",
				color=discord.Color.lighter_grey(),
				timestamp=ctx.message.created_at)
			embed.set_author(name=f"{ctx.author} (ID {ctx.author.id})", icon_url=ctx.author.avatar_url)
			embed.set_thumbnail(url=member.avatar_url)
			await moderation_log.send(embed=embed)
			# # Inserts a infraction into the database
			await self.insert_user_infraction(
				user_id=member.id, infr_type="mute", reason=reason,
				timestamp=current_ts , perpetrator=ctx.author.id)
			try:
				await member.send(embed=general_embed)
			except:
				pass
		else:
			await ctx.send(f'**{member} is already muted!**', delete_after=5)


	@commands.command()
	@commands.has_any_role(*allowed_roles)
	async def kick(self, ctx, member: discord.Member = None, *, reason=None):
		'''
		(MOD) Kicks a member from the server.
		:param member: The @ or ID of the user to kick.
		:param reason: The reason for kicking the user. (Optional)
		'''
		await ctx.message.delete()
		if not member:
			await ctx.send('**Please, specify a member!**', delete_after=3)
		else:
			try:
				await member.kick(reason=reason)
			except Exception:
				await ctx.send('**You cannot do that!**', delete_after=3)
			else:
				# General embed
				general_embed = discord.Embed(description=f'**Reason:** {reason}', colour=discord.Colour.magenta())
				general_embed.set_author(name=f'{member} has been kicked', icon_url=member.avatar_url)
				await ctx.send(embed=general_embed)
				# Moderation log embed
				moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
				embed = discord.Embed(title='__**Kick**__', colour=discord.Colour.magenta(),
									  timestamp=ctx.message.created_at)
				embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
								inline=False)
				embed.add_field(name='Reason:', value=f'```{reason}```')
				embed.set_author(name=member)
				embed.set_thumbnail(url=member.avatar_url)
				embed.set_footer(text=f"Kicked by {ctx.author}", icon_url=ctx.author.avatar_url)
				await moderation_log.send(embed=embed)
				# Inserts a infraction into the database
				epoch = datetime.utcfromtimestamp(0)
				current_ts = (datetime.utcnow() - epoch).total_seconds()
				await self.insert_user_infraction(
					user_id=member.id, infr_type="kick", reason=reason,
					timestamp=current_ts , perpetrator=ctx.author.id)
				try:
					await member.send(embed=general_embed)
				except:
					pass

	# Bans a member
	@commands.command()
	@commands.has_any_role(*allowed_roles)
	async def ban(self, ctx, member: discord.Member = None, *, reason=None) -> None:
		'''
		(ModTeam/ADM) Bans a member from the server.
		:param member: The @ or ID of the user to ban.
		:param reason: The reason for banning the user. (Optional)
		'''
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
				title=f"Ban Request ({len(confirmations)}/5) → (2mins)",
				description=f'''
				{author.mention} wants to ban {member.mention}, it requires 4 more moderator ✅ reactions for it!
				```Reason: {reason}```''',
				colour=discord.Colour.dark_red(), timestamp=ctx.message.created_at)
			mod_ban_embed.set_author(name=f'{member} is going to Brazil...', icon_url=member.avatar_url)
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
					r, _ = await self.client.wait_for('reaction_add', timeout=120, check=check_mod)
				except asyncio.TimeoutError:
					mod_ban_embed.description = f'Timeout, {member} is not getting banned!'
					await msg.remove_reaction('✅', self.client.user)
					return await msg.edit(embed=mod_ban_embed)
				else:
					mod_ban_embed.title = f"Ban Request ({len(confirmations)}/5) → (2mins)"
					await msg.edit(embed=mod_ban_embed)
					if len(confirmations) < 5:
						continue
					else:
						break

		# Checks if it was a moderator ban request or just a normal ban
		if len(confirmations) <= 1:
			perpetrators = ctx.author
			icon = ctx.author.avatar_url
		else:
			perpetrators = ', '.join(confirmations.values())
			icon = ctx.guild.icon_url

		# Bans and logs
		try:
			await member.ban(delete_message_days=7, reason=reason)
		except Exception:
			await ctx.send('**You cannot do that!**', delete_after=3)
		else:
			# General embed
			general_embed = discord.Embed(description=f'**Reason:** {reason}', colour=discord.Colour.dark_red())
			general_embed.set_author(name=f'{member} has been banned', icon_url=member.avatar_url)
			await ctx.send(embed=general_embed)
			# Moderation log embed
			moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
			embed = discord.Embed(title='__**Banishment**__', colour=discord.Colour.dark_red(),
								  timestamp=ctx.message.created_at)
			embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
							inline=False)
			embed.add_field(name='Reason:', value=f'```{reason}```')
			embed.set_author(name=member)
			embed.set_thumbnail(url=member.avatar_url)
			embed.set_footer(text=f"Banned by {perpetrators}", icon_url=icon)
			await moderation_log.send(embed=embed)
			# Inserts a infraction into the database
			epoch = datetime.utcfromtimestamp(0)
			current_ts = (datetime.utcnow() - epoch).total_seconds()
			await self.insert_user_infraction(
				user_id=member.id, infr_type="ban", reason=reason,
				timestamp=current_ts , perpetrator=ctx.author.id)
			try:
				await member.send(embed=general_embed)
			except:
				pass


	# Bans a member
	@commands.command()
	@commands.has_permissions(administrator=True)
	async def fban(self, ctx, member: discord.Member = None, *, reason=None):
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
			general_embed.set_author(name=f'{member} has been banned', icon_url=member.avatar_url)
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
				general_embed.set_author(name=f'{user} has been unbanned', icon_url=user.avatar_url)
				await ctx.send(embed=general_embed)
				# Moderation log embed
				moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
				embed = discord.Embed(title='__**Unbanishment**__', colour=discord.Colour.red(),
									  timestamp=ctx.message.created_at)
				embed.add_field(name='User info:', value=f'```Name: {user.display_name}\nId: {user.id}```',
								inline=False)
				embed.set_author(name=user)
				embed.set_thumbnail(url=user.avatar_url)
				embed.set_footer(text=f"Unbanned by {ctx.author}", icon_url=ctx.author.avatar_url)
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
	@commands.has_permissions(administrator=True)
	async def softban(self, ctx, member: discord.Member = None, *, reason=None):
		'''
		(ADM) Bans and unbans a member from the server; deleting their messages from the last 7 seven days.
		:param member: The @ or ID of the user to softban.
		:param reason: The reason for softbanning the user. (Optional)
		'''
		await ctx.message.delete()
		if not member:
			await ctx.send('**Please, specify a member!**', delete_after=3)
		else:
			try:
				await member.ban(delete_message_days=7, reason=reason)
				await member.unban(reason=reason)
			except Exception:
				await ctx.send('**You cannot do that!**', delete_after=3)
			else:
				# General embed
				general_embed = discord.Embed(description=f'**Reason:** {reason}', colour=discord.Colour.dark_purple())
				general_embed.set_author(name=f'{member} has been softbanned', icon_url=member.avatar_url)
				await ctx.send(embed=general_embed)
				# Moderation log embed
				moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
				embed = discord.Embed(title='__**SoftBanishment**__', colour=discord.Colour.dark_purple(),
									  timestamp=ctx.message.created_at)
				embed.add_field(name='User info:', value=f'```Name: {member.display_name}\nId: {member.id}```',
								inline=False)
				embed.add_field(name='Reason:', value=f'```{reason}```')
				embed.set_author(name=member)
				embed.set_thumbnail(url=member.avatar_url)
				embed.set_footer(text=f"SoftBanned by {ctx.author}", icon_url=ctx.author.avatar_url)
				await moderation_log.send(embed=embed)
				# Inserts a infraction into the database
				epoch = datetime.utcfromtimestamp(0)
				current_ts = (datetime.utcnow() - epoch).total_seconds()
				await self.insert_user_infraction(
					user_id=member.id, infr_type="softban", reason=reason,
					timestamp=current_ts , perpetrator=ctx.author.id)
				try:
					await member.send(embed=general_embed)
				except:
					pass

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def hackban(self, ctx, user_id: int = None, *, reason=None):
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

			# Moderation log embed
			moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
			embed = discord.Embed(title='__**HackBanishment**__', colour=discord.Colour.dark_teal(),
								  timestamp=ctx.message.created_at)
			embed.add_field(name='User info:', value=f'```Name: {self.client.get_user(user_id)}\nId: {member.id}```',
							inline=False)
			embed.add_field(name='Reason:', value=f'```{reason}```')

			embed.set_author(name=self.client.get_user(user_id))
			embed.set_footer(text=f"HackBanned by {ctx.author}", icon_url=ctx.author.avatar_url)
			await moderation_log.send(embed=embed)

			# Inserts a infraction into the database
			epoch = datetime.utcfromtimestamp(0)
			current_ts = (datetime.utcnow() - epoch).total_seconds()
			await self.insert_user_infraction(
				user_id=member.id, infr_type="hackban", reason=reason,
				timestamp=current_ts , perpetrator=ctx.author.id)
			try:
				await member.send(embed=general_embed)
			except:
				pass

		except discord.errors.NotFound:
			return await ctx.send("**Invalid user id!**", delete_after=3)

	async def insert_in_muted(self, user_role_ids: List[Tuple[int]]):
		mycursor, db = await the_database()
		await mycursor.executemany("""
			INSERT INTO mutedmember (
			user_id, role_id, mute_ts, muted_for_seconds) VALUES (%s, %s, %s, %s)""", user_role_ids
		)
		await db.commit()
		await mycursor.close()

	async def get_muted_roles(self, user_id: int):
		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM mutedmember WHERE user_id = %s", (user_id,))
		user_roles = await mycursor.fetchall()
		await mycursor.close()
		return user_roles

	async def remove_role_from_system(self, user_role_ids: int):
		mycursor, db = await the_database()
		await mycursor.executemany("DELETE FROM MutedMember WHERE user_id = %s AND role_id = %s", user_role_ids)
		await db.commit()
		await mycursor.close()


	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def create_table_mutedmember(self, ctx) -> None:
		""" (ADM) Creates the UserInfractions table. """

		if await self.check_table_mutedmember_exists():
			return await ctx.send("**Table __MutedMember__ already exists!**")
		
		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute("""CREATE TABLE mutedmember (
			user_id BIGINT NOT NULL, role_id BIGINT NOT NULL, mute_ts BIGINT DEFAULT NULL, muted_for_seconds BIGINT DEFAULT NULL)""")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table __MutedMember__ created!**", delete_after=3)

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def drop_table_mutedmember(self, ctx) -> None:
		""" (ADM) Creates the UserInfractions table """
		if not await self.check_table_mutedmember_exists():
			return await ctx.send("**Table __MutedMember__ doesn't exist!**")
		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute("DROP TABLE mutedmember")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table __MutedMember__ dropped!**", delete_after=3)

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def reset_table_mutedmember(self, ctx):
		'''
		(ADM) Resets the MutedMember table.
		'''
		if not await self.check_table_mutedmember_exists():
			return await ctx.send("**Table __MutedMember__ doesn't exist yet**")

		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM mutedmember")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table __mutedmember__ reset!**", delete_after=3)

	async def check_table_mutedmember_exists(self) -> bool:
		'''
		Checks if the MutedMember table exists
		'''
		mycursor, db = await the_database()
		await mycursor.execute("SHOW TABLE STATUS LIKE 'mutedmember'")
		table_info = await mycursor.fetchall()
		await mycursor.close()

		if len(table_info) == 0:
			return False

		else:
			return True
		

	# Infraction methods
	@commands.command(aliases=['infr', 'show_warnings', 'sw', 'show_bans', 'sb', 'show_muted', 'sm'])
	@commands.has_any_role(*allowed_roles)
	async def infractions(self, ctx, member: discord.Member = None) -> None:
		'''
		Shows all infractions of a specific user.
		:param member: The member to show the infractions from.
		'''
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
			return await ctx.send(f"**{member.mention} doesn't have any existent infractions!**")

		# Makes the initial embed with their amount of infractions
		embed = discord.Embed(
			title=f"Infractions for {member}",
			description=f"```ini\n[Warns]: {warns} | [Mutes]: {mutes} | [Kicks]: {kicks}\n[Bans]: {bans} | [Softbans]: {softbans} | [Hackbans]: {hackbans}```",
			color=member.color,
			timestamp=ctx.message.created_at)
		embed.set_thumbnail(url=member.avatar_url)
		embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar_url)

		# Loops through each infraction and adds a field to the embedded message
		## 0-user_id, 1-infraction_type, 2-infraction_reason, 3-infraction_ts, 4-infraction_id, 5-perpetrator
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

	# Database methods

	async def insert_user_infraction(self, user_id: int, infr_type: str, reason: str, timestamp: int, perpetrator: int) -> None:
		""" Insert a warning into the system. """

		mycursor, db = await the_database()
		await mycursor.execute("""
			INSERT INTO UserInfractions (
			user_id, infraction_type, infraction_reason,
			infraction_ts, perpetrator)
			VALUES (%s, %s, %s, %s, %s)""",
			(user_id, infr_type, reason, timestamp, perpetrator))
		await db.commit()
		await mycursor.close()


	async def get_user_infractions(self, user_id: int) -> List[List[Union[str, int]]]:
		""" Gets all infractions from a user. """

		mycursor, db = await the_database()
		await mycursor.execute(f"SELECT * FROM UserInfractions WHERE user_id = {user_id}")
		user_infractions = await mycursor.fetchall()
		await mycursor.close()
		return user_infractions


	async def get_user_infraction_by_infraction_id(self, infraction_id: int) -> List[List[Union[str, int]]]:
		""" Gets a specific infraction by ID. """

		mycursor, db = await the_database()
		await mycursor.execute(f"SELECT * FROM UserInfractions WHERE infraction_id = {infraction_id}")
		user_infractions = await mycursor.fetchall()
		await mycursor.close()
		return user_infractions

	async def remove_user_infraction(self, infraction_id: int) -> None:
		""" Removes a specific infraction by ID. """

		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM UserInfractions WHERE infraction_id = %s", (infraction_id,))
		await db.commit()
		await mycursor.close()

	async def remove_user_infractions(self, user_id: int) -> None:
		""" Removes all infractions of a user by ID. """

		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM UserInfractions WHERE user_id = %s", (user_id,))
		await db.commit()
		await mycursor.close()

	@commands.command(aliases=['ri', 'remove_warn', 'remove_warning'])
	@commands.has_any_role(*allowed_roles)
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
	@commands.has_any_role(*allowed_roles)
	async def remove_infractions(self, ctx, member: discord.Member = None):
		"""
		(MOD) Removes all infractions for a specific user.
		:param member: The member to get the warns from.
		"""

		if not member:
			return await ctx.send("**Inform a member!**")
		
		if user_infractions := await self.get_user_infractions(member.id):
			await self.remove_user_infractions(member.id)
			await ctx.send(f"**Removed all infractions for {member.mention}!**")
		else:
			await ctx.send(f"**{member.mention} doesn't have any existent infractions!**")

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def create_table_user_infractions(self, ctx) -> None:
		""" (ADM) Creates the UserInfractions table. """

		if await self.check_table_user_infractions():
			return await ctx.send("**Table __UserInfractions__ already exists!**")
		
		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute("""CREATE TABLE UserInfractions (
			user_id BIGINT NOT NULL,
			infraction_type VARCHAR(7) NOT NULL,
			infraction_reason VARCHAR(100) DEFAULT NULL,
			infraction_ts BIGINT NOT NULL,
			infraction_id BIGINT NOT NULL AUTO_INCREMENT,
			perpetrator BIGINT NOT NULL,
			PRIMARY KEY(infraction_id)
			)""")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table __UserInfractions__ created!**", delete_after=3)

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def drop_table_user_infractions(self, ctx) -> None:
		""" (ADM) Creates the UserInfractions table """
		if not await self.check_table_user_infractions():
			return await ctx.send("**Table __UserInfractions__ doesn't exist!**")
		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute("DROP TABLE UserInfractions")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table __UserInfractions__ dropped!**", delete_after=3)

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def reset_table_user_infractions(self, ctx) -> None:
		""" (ADM) Creates the UserInfractions table """

		if not await self.check_table_user_infractions():
			return await ctx.send("**Table __UserInfractions__ doesn't exist yet!**")

		await ctx.message.delete()
		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM UserInfractions")
		await db.commit()
		await mycursor.close()

		return await ctx.send("**Table __UserInfractions__ reset!**", delete_after=3)

	async def check_table_user_infractions(self) -> bool:
		""" Checks if the UserInfractions table exists """

		mycursor, db = await the_database()
		await mycursor.execute("SHOW TABLE STATUS LIKE 'UserInfractions'")
		table_info = await mycursor.fetchall()
		await mycursor.close()

		if len(table_info) == 0:
			return False

		else:
			return True


def setup(client):
	client.add_cog(Moderation(client))
