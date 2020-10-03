import discord
from discord.ext import commands
from mysqldb2 import the_data_base3
import asyncio
from extra.useful_variables import list_of_commands
import time

reportsupport_channel_id = 729454413290143774
dnk_id = 647452832852869120
case_cat_id = 562939721253126146
moderator_role_id = 497522510212890655

class ReportSupport(commands.Cog):
	'''
	A cog related to the system of reports and some other things.
	'''

	def __init__(self, client):
		self.client = client
		self.app_channel_id = 672827061479538714
		self.cosmos_id = 423829836537135108
		self.cache = {}
		self.report_cache = {}

	@commands.Cog.listener()
	async def on_ready(self):
		print('ReportSupport cog is online!')


	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		# Checks if it wasn't a bot's reaction
		if not payload.guild_id:
			return

		if not payload.member or payload.member.bot:
			return

		# Checks if the reaction was in the RepportSupport channel
		channel = self.client.get_channel(payload.channel_id)
		#print(channel)
		if not channel or str(channel).startswith('Direct Message with') or channel.id != reportsupport_channel_id:
			return

		# Deletes the reaction
		msg = await channel.fetch_message(payload.message_id)
		await msg.remove_reaction(payload.emoji, payload.member)

		# Checks if the member does not have kick_member permissions (not from the staff)
		member = payload.member
		category = channel.category
		perms = category.permissions_for(member)
		# if perms.kick_members:
		# 	return

		# Checks which reaction they reacted and redirects them to the respective option.
		mid = payload.message_id
		emoji = payload.emoji
		guild = self.client.get_guild(payload.guild_id)

		if mid == 729455417742327879 and str(emoji) == '✅':
			# Apply to be a teacher
			#link = "https://docs.google.com/forms/d/1H-rzl9AKgfH1WuKN7nYAW-xJx411Q4-HxfPXuPUFQXs/viewform?edit_requested=true"
			#await member.send(f"**You can apply for being a teacher by filling out this form:**\n{link}")
			member_ts = self.cache.get(member.id)
			time_now = time.time()
			if member_ts:
				sub = time_now - member_ts
				if sub <= 1800:
					return await member.send(
						f"**You are on cooldown to apply, try again in {(1800-sub)/60:.1f} minutes**")
			await self.send_application(member)

		elif mid == 729456191733760030 and str(emoji) == '🤖':
			# Order a bot
			dnk = self.client.get_user(dnk_id)
			embed = discord.Embed(title="New possible order!", 
				description=f"{member.mention} wants to order something from you!", 
				color=member.color)
			embed.set_thumbnail(url=member.avatar_url)
			await dnk.send(embed=embed)
			await member.send("**DNK is going to DM you as soon as possible!**")
			await self.dnk_embed(member)
		elif mid == 729458094194688060 and str(emoji) == '❤️':
			# Support us on Patreon
			await member.send(f"**Support us on Patreon!**\nhttps://www.patreon.com/Languagesloth")

		elif mid == 729458598966460426 and str(emoji) == '<:ban:593407893248802817>' and not perms.kick_members:
			member_ts = self.report_cache.get(member.id)
			time_now = time.time()
			if member_ts:
				sub = time_now - member_ts
				if sub <= 240:
					return await member.send(
						f"**You are on cooldown to report, try again in {round(240-sub)} seconds**")

			self.report_cache[member.id] = time.time()
			await self.select_report(member, guild)

	async def send_application(self, member):

		def msg_check(message):
			if message.author == member and not message.guild:
				if len(message.content) <= 100:
					return True
				else:
					self.client.loop.create_task(member.send("**Your answer must be within 100 characters**"))
			else:
				return False

		embed = discord.Embed(title=f"__Teacher Application__")
		embed.set_footer(text=f"by {member}", icon_url=member.avatar_url)

		embed.description = '''
		- Hello, there you've reacted to apply to become a teacher.
		To apply please answer to these following questions with One message at a time
		Question one:
		What language are you applying to teach?'''
		q1 = await member.send(embed=embed)
		a1 = await self.get_message(member, msg_check)
		if not a1:
			return

		embed.description = '''
		- Why do you want to teach that language on the language sloth? 
		Please answer with one message.'''
		q2 = await member.send(embed=embed)
		a2 = await self.get_message(member, msg_check)
		if not a2:
			return
		
		embed.description = '''
		- On The Language Sloth, our classes happen once a week at the same time weekly. 
		Please let us know when would be the best time for you to teach,
		E.A: Thursdays 3 pm CET, you can specify your timezone.
		Again remember to answer with one message.'''
		q3 = await member.send(embed=embed)
		a3 = await self.get_message(member, msg_check)
		if not a3:
			return

		embed.description = '''
		-Let's talk about your English level, how do you consider your English level? 
		Are you able to teach lessons in English? 
		Please answer using one message only'''
		q4 = await member.send(embed=embed)
		a4 = await self.get_message(member, msg_check)
		if not a4:
			return

		embed.description = '''- Have you ever taught people before?'''
		q5 = await member.send(embed=embed)
		a5 = await self.get_message(member, msg_check)
		if not a5:
			return

		embed.description = '''- Inform a short description for you class.'''
		q6 = await member.send(embed=embed)
		a6 = await self.get_message(member, msg_check)
		if not a6:
			return

		# Get user's native roles
		user_native_roles = []
		for role in member.roles:
			if str(role.name).lower().startswith('native'):
				user_native_roles.append(role.name.title())

		# Application result
		app = f"""```ini\n[Username]: {member} ({member.id})\n[Joined the server]: {member.joined_at.strftime("%a, %d %B %y, %I %M %p UTC")}\n[Applying to teach]: {a1.title()}\n[Native roles]: {', '.join(user_native_roles)}\n[Motivation for teaching]: {a2.capitalize()}\n[Applying to teach on]: {a3.upper()}\n[English level]: {a4.capitalize()}\n[Experience teaching]: {a5.capitalize()}\n[Description]:{a6.capitalize()}```"""
		await member.send(app)
		embed.description = '''
		Are you sure you want to apply this? :white_check_mark: to send and :x: to Cancel
		'''
		app_conf = await member.send(embed=embed)
		await app_conf.add_reaction('✅')
		await app_conf.add_reaction('❌')

		# Waits for reaction confirmation
		def check_reaction(r, u):
			return u.id == member.id and not r.message.guild and str(r.emoji) in ['✅', '❌']


		r = await self.get_reaction(member, check_reaction)
		if r is None:
			return

		if r == '✅':
			embed.description = "**Application successfully made, please be patient now!**"
			await member.send(embed=embed)
			app_channel = await self.client.fetch_channel(self.app_channel_id)
			cosmos = discord.utils.get(app_channel.guild.members, id=self.cosmos_id)
			await app_channel.send(content=f"{cosmos.mention}, {member.mention}\n{app}")
			self.cache[member.id] = time.time()
		else:
			await member.send("**Let's do it again then! If you want to cancel your application, let it timeout!**")
			return await self.send_application(member)


	# Report methods
	async def select_report(self, member, guild):

		# Ask what they want to do [Report someone, general help, missclick]
		react_list = ['1️⃣','2️⃣','3️⃣', '❌']

		report_embed = discord.Embed(
			title="What kind of report would you like to start?")
		report_embed.description = '''
		1️⃣ Report another user for breaking the rules.

		2️⃣ I need help with the server in general.

		3️⃣ I need to change some roles and I can't.

		❌ Cancel, I missclicked.'''
		msg = await member.send(embed=report_embed)

		for react in react_list:
			await msg.add_reaction(react)

		try:
			r, _ = await self.client.wait_for(
				'reaction_add', 
				timeout=240, 
				check=lambda r, u: u.id == member.id and r.emoji in react_list \
					and r.message.id == msg.id
			)
		except asyncio.TimeoutError:
			timeout_embed = discord.Embed(
				title="Timeout", 
				description='**Try again!**',
				color=discord.Color.red())
			await member.send(embed=timeout_embed)
			
		else:
			emoji = str(r.emoji)
			if emoji == '1️⃣':
				# Report another user for breaking the rules
				return await self.report_someone(member, guild)
			elif emoji == '2️⃣':
				# I need help with the server in general
				message = f"Please, {member.mention}, try to explain what kind of help you want related to the server."
				return await self.generic_help(member, guild, 'server help', message)
			elif emoji == '3️⃣':
				# I need to change some roles and I can't
				message = f"Please, {member.mention}, inform us what roles you want, and if you spotted a specific problem with the reaction-role selection."
				return await self.generic_help(member, guild, 'role help', message)
			elif emoji == '❌':
				# Cancel, I misclicked
				return await member.send("**All right, cya!**")



	#- Report someone
	async def report_someone(self, member, guild):
					
		if await self.member_has_open_channel(member.id):
			embed = discord.Embed(title="Error!", description="**You already have an open channel!**", color=discord.Color.red())
			return await member.send(embed=embed)

		# Report someone
		case_cat = discord.utils.get(guild.categories, id=case_cat_id)
		counter = await self.get_case_number()
		moderator = discord.utils.get(guild.roles, id=moderator_role_id)
		cosmos = discord.utils.get(guild.members, id=self.cosmos_id)
		overwrites = {guild.default_role: discord.PermissionOverwrite(
			read_messages=False, send_messages=False, connect=False, view_channel=False), 
		member: discord.PermissionOverwrite(
			read_messages=True, send_messages=True, connect=False, view_channel=True), 
		moderator: discord.PermissionOverwrite(
			read_messages=True, send_messages=True, connect=False, view_channel=True, manage_messages=True)}
		the_channel = await guild.create_text_channel(name=f"case-{counter[0][0]}", category=case_cat, overwrites=overwrites)
		#print('created!')
		created_embed = discord.Embed(
			title="Report room created!", 
			description=f"**Go to {the_channel.mention}!**", 
			color=discord.Color.green())
		await member.send(embed=created_embed)
		await self.insert_user_open_channel(member.id, the_channel.id)
		await self.increase_case_number()
		embed = discord.Embed(title="Report Support!", description=f"Please, {member.mention}, try to explain what happened and who you want to report.",
			color=discord.Color.red())
		await the_channel.send(content=f"{member.mention}, {moderator.mention}, {cosmos.mention}", embed=embed)

	#- Report someone
	async def generic_help(self, member, guild, type_help, message):
					
		if await self.member_has_open_channel(member.id):
			embed = discord.Embed(title="Error!", description="**You already have an open channel!**", color=discord.Color.red())
			return await member.send(embed=embed)

		# General help
		case_cat = discord.utils.get(guild.categories, id=case_cat_id)
		moderator = discord.utils.get(guild.roles, id=moderator_role_id)
		overwrites = {guild.default_role: discord.PermissionOverwrite(
			read_messages=False, send_messages=False, connect=False, view_channel=False), 
		member: discord.PermissionOverwrite(
			read_messages=True, send_messages=True, connect=False, view_channel=True), 
		moderator: discord.PermissionOverwrite(
			read_messages=True, send_messages=True, connect=False, view_channel=True, manage_messages=True)}
		the_channel = await guild.create_text_channel(name=f"{'-'.join(type_help.split())}", category=case_cat, overwrites=overwrites)
		#print('created!')
		created_embed = discord.Embed(
			title=f"Room for `{type_help}` created!", 
			description=f"**Go to {the_channel.mention}!**", 
			color=discord.Color.green())
		await member.send(embed=created_embed)
		await self.insert_user_open_channel(member.id, the_channel.id)
		embed = discord.Embed(title=f"{type_help.title()}!", 
		description=f"{message}",
			color=discord.Color.red())
		await the_channel.send(content=f"{member.mention}, {moderator.mention}", embed=embed)


	async def get_message(self, member, check):
		try:
			message = await self.client.wait_for('message', timeout=240, 
			check=check)
		except asyncio.TimeoutError:
			await member.send("**Timeout! Try again.**")
			return None
		else:
			content = message.content
			return content

	async def get_reaction(self, member, check):
		try:
			reaction, user = await self.client.wait_for('reaction_add', 
			timeout=120, check=check)
		except asyncio.TimeoutError:
			await member.send("**Timeout! Try again.**")
			return None
		else:
			return str(reaction.emoji)

	async def member_has_open_channel(self, member_id: int):
		mycursor, db = await the_data_base3()
		await mycursor.execute(f"SELECT * FROM OpenChannels WHERE user_id = {member_id}")
		user = await mycursor.fetchall()
		await mycursor.close()
		return user

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def create_table_case_counter(self, ctx):
		'''
		(ADM) Creates the CaseCounter table.
		'''
		await ctx.message.delete()
		if await self.table_case_counter_exists():
			return await ctx.send("**Table __CaseCounter__ already exists!**", delete_after=3)

		mycursor, db = await the_data_base3()
		await mycursor.execute("CREATE TABLE CaseCounter (case_number bigint default 0)")
		await mycursor.execute("INSERT INTO CaseCounter (case_number) VALUES (0)")
		await db.commit()
		await mycursor.close()
		await ctx.send("**Table __CaseCounter__ created!**", delete_after=3)

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def drop_table_case_counter(self, ctx):
		'''
		(ADM) Drops the CaseCounter table.
		'''
		await ctx.message.delete()
		if not await self.table_case_counter_exists():
			return await ctx.send("**Table __CaseCounter__ doesn't exist!**", delete_after=3)

		mycursor, db = await the_data_base3()
		await mycursor.execute("DROP TABLE CaseCounter")
		await db.commit()
		await mycursor.close()
		return await ctx.send("**Table __CaseCounter__ dropped!**", delete_after=3)

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def reset_table_case_counter(self, ctx):
		'''
		(ADM) Resets the CaseCounter table.
		'''
		await ctx.message.delete()
		if not await self.table_case_counter_exists():
			return await ctx.send("**Table __CaseCounter__ doesn't exist yet!**", delete_after=3)

		mycursor, db = await the_data_base3()
		await mycursor.execute("DELETE FROM CaseCounter")
		await mycursor.execute("INSERT INTO CaseCounter (case_number) VALUES (0)")
		await db.commit()
		await mycursor.close()
		return await ctx.send("**Table __CaseCounter__ reset!**", delete_after=3)

	async def table_case_counter_exists(self):
		mycursor, db = await the_data_base3()
		await mycursor.execute(f"SHOW TABLE STATUS LIKE 'CaseCounter'")
		table_info = await mycursor.fetchall()
		await mycursor.close()
		if len(table_info) == 0:
			return False
		else:
			return True 


	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def create_table_open_channels(self, ctx):
		'''
		(ADM) Creates the OpenChannels table.
		'''
		await ctx.message.delete()
		if await self.table_open_channels_exists():
			return await ctx.send("**Table __OpenChannels__ already exists!**", delete_after=3)

		mycursor, db = await the_data_base3()
		await mycursor.execute("CREATE TABLE OpenChannels (user_id bigint, channel_id bigint)")
		await db.commit()
		await mycursor.close()
		await ctx.send("**Table __OpenChannels__ created!**", delete_after=3)

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def drop_table_open_channels(self, ctx):
		'''
		(ADM) Drops the OpenChannels table.
		'''
		await ctx.message.delete()
		if not await self.table_open_channels_exists():
			return await ctx.send("**Table __OpenChannels__ doesn't exist!**", delete_after=3)

		mycursor, db = await the_data_base3()
		await mycursor.execute("DROP TABLE OpenChannels")
		await db.commit()
		await mycursor.close()
		return await ctx.send("**Table __OpenChannels__ dropped!**", delete_after=3)

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def reset_table_open_channels(self, ctx):
		'''
		(ADM) Resets the OpenChannels table.
		'''
		await ctx.message.delete()
		if not await self.table_open_channels_exists():
			return await ctx.send("**Table __OpenChannels__ doesn't exist yet!**", delete_after=3)

		mycursor, db = await the_data_base3()
		await mycursor.execute("DELETE FROM OpenChannels")
		await db.commit()
		await mycursor.close()
		return await ctx.send("**Table __OpenChannels__ reset!**", delete_after=3)


	async def table_open_channels_exists(self):
		mycursor, db = await the_data_base3()
		await mycursor.execute(f"SHOW TABLE STATUS LIKE 'OpenChannels'")
		table_info = await mycursor.fetchall()
		await mycursor.close()
		if len(table_info) == 0:
			return False
		else:
			return True 

	async def get_case_number(self):
		mycursor, db = await the_data_base3()
		await mycursor.execute(f"SELECT * FROM CaseCounter")
		counter = await mycursor.fetchall()
		await mycursor.close()
		return counter

	async def increase_case_number(self):
		mycursor, db = await the_data_base3()
		await mycursor.execute(f"UPDATE CaseCounter SET case_number = case_number + 1")
		await db.commit()
		await mycursor.close()

	async def insert_user_open_channel(self, member_id: int, channel_id: int):
		mycursor, db = await the_data_base3()
		await mycursor.execute(f"INSERT INTO OpenChannels (user_id, channel_id) VALUES (%s, %s)", (member_id, channel_id))
		await db.commit()
		await mycursor.close()

	async def remove_user_open_channel(self, member_id: int):
		mycursor, db = await the_data_base3()
		await mycursor.execute(f"DELETE FROM OpenChannels WHERE user_id = {member_id}")
		await db.commit()
		await mycursor.close()

	async def get_case_channel(self, channel_id: int):
		mycursor, db = await the_data_base3()
		await mycursor.execute(f"SELECT * FROM OpenChannels WHERE channel_id = {channel_id}")
		channel = await mycursor.fetchall()
		await mycursor.close()
		return channel

	@commands.command()
	@commands.has_permissions(kick_members=True)
	async def close_channel(self, ctx):
		'''
		(MOD) Closes a Case-Channel.
		'''
		user_channel = await self.get_case_channel(ctx.channel.id)
		if user_channel:
			channel = discord.utils.get(ctx.guild.channels, id=user_channel[0][1])
			embed = discord.Embed(title="Confirmation",
				description="Are you sure that you want to delete this channel?",
				color=ctx.author.color,
				timestamp=ctx.message.created_at)
			confirmation = await ctx.send(content=ctx.author.mention, embed=embed)
			await confirmation.add_reaction('✅')
			await confirmation.add_reaction('❌')
			try:
				reaction, user = await self.client.wait_for('reaction_add', timeout=20, 
					check=lambda r, u: u == ctx.author and r.message.channel == ctx.channel and str(r.emoji) in ['✅', '❌'])
			except asyncio.TimeoutError:
				embed = discord.Embed(title="Confirmation",
				description="You took too long to answer the question; not deleting it!",
				color=discord.Color.red(),
				timestamp=ctx.message.created_at)
				return await confirmation.edit(content=ctx.author.mention, embed=embed)
			else:
				if str(reaction.emoji) == '✅':
					embed.description = f"**Channel {ctx.channel.mention} is being deleted...**"
					await confirmation.edit(content=ctx.author.mention, embed=embed)
					await asyncio.sleep(3)
					await channel.delete()
					await self.remove_user_open_channel(user_channel[0][0])
				else:
					embed.description = "Not deleting it!"
					await confirmation.edit(content='', embed=embed)
		else:
			await ctx.send(f"**What do you think that you are doing? You cannot delete this channel, {ctx.author.mention}!**")


	async def dnk_embed(self, member):
		def check(r, u):
			return u == member and str(r.message.id) == str(the_msg.id) and str(r.emoji) in ['⬅️', '➡️']

		command_index = 0
		initial_embed = discord.Embed(title="__Table of Commands and their Prices__",
				description="These are a few of commands and features that DNK can do.",
				color=discord.Color.blue())
		the_msg = await member.send(embed=initial_embed)
		await the_msg.add_reaction('⬅️')
		await the_msg.add_reaction('➡️')
		while True:
			embed = discord.Embed(title=f"__Table of Commands and their Prices__ ({command_index+1}/{len(list_of_commands)})",
				description="These are a few of commands and features that DNK can do.",
				color=discord.Color.blue())
			embed.add_field(name=list_of_commands[command_index][0],
				value=list_of_commands[command_index][1])
			await the_msg.edit(embed=embed)

			try:
				pending_tasks = [self.client.wait_for('reaction_add', check=check),
				self.client.wait_for('reaction_remove', check=check)]
				done_tasks, pending_tasks = await asyncio.wait(pending_tasks, timeout=60, return_when=asyncio.FIRST_COMPLETED)
				if not done_tasks:
					raise asyncio.TimeoutError

				for task in pending_tasks:
					task.cancel()
				
			except asyncio.TimeoutError:
				await the_msg.remove_reaction('⬅️', self.client.user)
				await the_msg.remove_reaction('➡️', self.client.user)
				break

			else:
				for task in done_tasks: 
					reaction, user = await task
				if str(reaction.emoji) == "➡️":
					#await the_msg.remove_reaction(reaction.emoji, member)
					if command_index < (len(list_of_commands) - 1):
						command_index += 1
					continue
				elif str(reaction.emoji) == "⬅️":
					#await the_msg.remove_reaction(reaction.emoji, member)
					if command_index > 0:
						command_index -= 1
					continue

def setup(client):
	client.add_cog(ReportSupport(client))