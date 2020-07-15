import discord
from discord.ext import commands
from mysqldb2 import the_data_base3
import asyncio
from extra.useful_variables import list_of_commands

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

	@commands.Cog.listener()
	async def on_ready(self):
		print('ReportSupport cog is online!')


	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		# Checks if it wasn't a bot's reaction
		if not payload.member or payload.member.bot:
			return

		# Checks if the reaction was in the RepportSupport channel
		channel = self.client.get_channel(payload.channel_id)
		#print(channel)
		if not channel or str(channel).startswith('Direct Message with')  or channel.id != reportsupport_channel_id:
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
			link = "https://docs.google.com/forms/d/1H-rzl9AKgfH1WuKN7nYAW-xJx411Q4-HxfPXuPUFQXs/viewform?edit_requested=true"
			await member.send(f"**You can apply for being a teacher by filling out this form:**\n{link}")
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
			if await self.member_has_open_channel(member.id):
				embed = discord.Embed(title="Error!", description="**You already has an open channel!**", color=discord.Color.red())
				return await member.send(embed=embed)

			# Report someone
			case_cat = discord.utils.get(guild.categories, id=case_cat_id)
			counter = await self.get_case_number()
			moderator = discord.utils.get(guild.roles, id=moderator_role_id)
			overwrites = {guild.default_role: discord.PermissionOverwrite(
				read_messages=False, send_messages=False, connect=False, view_channel=False), 
			member: discord.PermissionOverwrite(
				read_messages=True, send_messages=True, connect=False, view_channel=True), 
			moderator: discord.PermissionOverwrite(
				read_messages=True, send_messages=True, connect=False, view_channel=True, manage_messages=True)}
			the_channel = await guild.create_text_channel(name=f"case-{counter[0][0]}", category=case_cat, overwrites=overwrites)
			print('created!')
			await self.insert_user_open_channel(member.id, the_channel.id)
			await self.increase_case_number()
			embed = discord.Embed(title="Report Support!", description=f"Please, {member.mention}, try to explain what happened and who you wanna report.",
				color=discord.Color.red())
			await the_channel.send(content=f"{member.mention}, {moderator.mention}", embed=embed)
			# try:
			# 	await the_channel.edit(overwrites=overwrites)
			# except Exception:
			# 	pass

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
					await self.remove_user_open_channel(member.id)
				else:
					embed.description = "Not deleting it!"
					await confirmation.edit(content='', embed=embed)
		else:
			await ctx.send(f"**What do you think that you are doing? You cannot delete this channel, {ctx.author.mention}!**")


	async def dnk_embed(self, member):
		def check(r, u):
			return u == member and str(r.message.channel) == str(the_msg.channel) and str(r.emoji) in ['⬅️', '➡️']

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
				pending_tasks = [self.client.wait_for('reaction_add', timeout=60, check=check),
				self.client.wait_for('reaction_remove', timeout=60, check=check)]
				done_tasks, pending_tasks = await asyncio.wait(pending_tasks, return_when=asyncio.FIRST_COMPLETED)
				for task in pending_tasks:
					task.cancel()
				for task in done_tasks: 
					reaction, user = await task
					
			except asyncio.TimeoutError:
				for task in pending_tasks:
					task.cancel()
				await the_msg.remove_reaction('⬅️', self.client.user)
				await the_msg.remove_reaction('➡️', self.client.user)

			else:
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