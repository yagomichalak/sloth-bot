import discord
from discord.ext import commands, tasks
from mysqldb import the_database
from typing import Union, List, Any
from extra.customerrors import MissingRequiredSlothClass, ActionSkillOnCooldown
from extra.menu import ConfirmSkill
from datetime import datetime
from pytz import timezone
import os

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))
# bots_and_commands_channel_id = 777886760994471986

class SlothClass(commands.Cog):
	""" A category for the Sloth Class system. """

	def __init__(self, client) -> None:
		""" Class initializing method. """

		self.client = client

	@commands.Cog.listener()
	async def on_ready(self) -> None:
		""" Tells when the cog is ready to use. """
		self.bots_txt = await self.client.fetch_channel(bots_and_commands_channel_id)
		self.check_skill_actions.start()
		print("SlothClass cog is online")

	@tasks.loop(minutes=1)
	async def check_skill_actions(self):
		""" Checks all skill actions and events. """

		await self.try_to_run(self.check_steals)
		await self.try_to_run(self.check_protections)


	async def try_to_run(self, func):
		""" Tries to run a function/method and ignore failures. """

		try:
			await func()
		except:
			pass


	# @tasks.loop(minutes=1)
	async def check_steals(self) -> None:
		""" Check on-going steals and their expiration time. """
		
		steals = await self.get_expired_steals()
		for steal in steals:
			try:
				channel = self.client.get_channel(steal[5])
				if not channel:
					channel = self.bots_txt
				else:
					message = await channel.fetch_message(steal[4])
					if message:
						message_embed = message.embeds[0]
						message_embed.color = discord.Color.red()
						message_embed.description=f"**Too late, <@{steal[3]}>! You were robbed by <@{steal[0]}>!**"
						await message.edit(embed=message_embed)
						await message.remove_reaction('🛡️', self.client.user)
				# Removes skill action from the database
				await self.delete_skill_action_by_message_id(steal[4])
				# Gives money to the attacker
				user_currency = await self.get_user_currency(steal[3])
				if user_currency and user_currency[1] >= 5:
					await self.update_user_money(steal[0], 5)
					await self.update_user_money(steal[3], -5)
					steal_embed = await self.get_steal_embed(
						channel=channel, attacker_id=steal[0], target_id=steal[3], attack_succeeded=True)
					await channel.send(content=f"<@{steal[0]}>", embed=steal_embed)
				else:
					steal_embed = await self.get_steal_embed(
						channel=channel, attacker_id=steal[0], target_id=steal[3])
					await channel.send(content=f"<@{steal[0]}>", embed=steal_embed)

			except Exception as e:
				print(e)
				pass


	async def check_protections(self) -> None:
		""" Check on-going protections and their expiration time. """
		
		divine_protections = await self.get_expired_protections()
		for dp in divine_protections:
			print(dp)
			await self.update_user_protected(dp[3], 0)
			await self.delete_skill_action_by_target_id(dp[3])

			channel = self.client.get_channel(dp[5])
			if not channel:
				channel = self.bots_txt
			

			await channel.send(
				content=f"<@{dp[0]}>, <@{dp[3]}>", 
				embed=discord.Embed(
					description=f"**<@{dp[3]}>'s `Divine Protection` from <@{dp[0]}> just expired!**",
					color=discord.Color.red()))

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload) -> None:
		""" Checks reactions related to skill actions. """

		# Checks if it wasn't a bot's reaction
		if not payload.guild_id:
			return

		# Checks whether it's a valid member and not a bot
		if not payload.member or payload.member.bot:
			return

		skill_action = await self.get_skill_action_by_reaction_context(payload.message_id, payload.user_id)
		if skill_action is not None:
			emoji = str(payload.emoji)

			# Checks whether it's a steal
			if skill_action[6] == '🛡️':

				await self.delete_skill_action_by_message_id(payload.message_id)
				channel = self.client.get_channel(skill_action[5])
				if not channel:
					channel = self.bots_txt
				else:
					message = await channel.fetch_message(skill_action[4])
					if message:
						message_embed = message.embeds[0]
						message_embed.color = discord.Color.green()
						message_embed.description=f"**Good job, <@{skill_action[3]}>! You saved yourself against <@{skill_action[0]}>'s stealing!**"
						await message.edit(embed=message_embed)
						await message.remove_reaction('🛡️', self.client.user)
						await message.remove_reaction('🛡️', payload.member)

				return await channel.send(
					embed=discord.Embed(
						description=f"**{payload.member.mention} defended themselves against <@{skill_action[0]}>'s stealing, good luck next time!**",
						color=discord.Color.green()))



	@commands.command(aliases=['sloth_class'])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def sloth_classes(self, ctx) -> None:
		""" Shows how many people are in each Sloth Class team. """

		mycursor, db = await the_database()
		await mycursor.execute("""
			SELECT sloth_class, COUNT(sloth_class) AS sloth_count
			FROM UserCurrency 
			WHERE sloth_class != 'default'
			GROUP BY sloth_class
			ORDER BY sloth_count DESC
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

	def skill_on_cooldown():
		""" Checks whether the user's action skill is on cooldown. """

		async def get_user_action_skill_ts(user_id: int) -> Union[str, bool]:
			""" Gets the user's last action skill timestamp from the database.
			:param user_id: The ID of the user to get the action skill timestamp. """

			mycursor, db = await the_database()
			await mycursor.execute("SELECT last_skill_ts FROM UserCurrency WHERE user_id = %s", (user_id,))
			last_skill_ts = await mycursor.fetchone()
			await mycursor.close()
			if last_skill_ts:
				return last_skill_ts[0]
			else:
				return None

		async def real_check(ctx):
			""" Perfoms the real check. """

			last_skill_ts = await get_user_action_skill_ts(ctx.author.id)
			current_time = ctx.message.created_at
			cooldown_in_seconds = (current_time - datetime.utcfromtimestamp(last_skill_ts)).total_seconds()
			if cooldown_in_seconds >= 86400:
				return True
			raise ActionSkillOnCooldown(try_after=cooldown_in_seconds, error_message="Action skill on cooldown!")

		return commands.check(real_check)




	@commands.command()
	@skill_on_cooldown()
	@user_is_class('warrior')
	async def claw_attack(self, ctx) -> None:
		""" A command for Warriors. """

		return await ctx.send("**Command not ready yet!**")


	@commands.command()
	@skill_on_cooldown()
	@user_is_class('metamorph')
	async def transmutation(self, ctx) -> None:
		""" A command for Metamorphs. """

		return await ctx.send("**Command not ready yet!**")

	@commands.command()
	@skill_on_cooldown()
	@user_is_class('agares')
	async def magical_armor(self, ctx) -> None:
		""" A command for Agares. """

		return await ctx.send("**Command not ready yet!**")

	@commands.command()
	@skill_on_cooldown()
	@user_is_class('cybersloth')
	async def energy_boost(self, ctx) -> None:
		""" A command for Cybersloths. """

		return await ctx.send("**Command not ready yet!**")

	@commands.command()
	@skill_on_cooldown()
	@user_is_class('merchant')
	async def open_shop(self, ctx) -> None:
		""" A command for Merchants. """

		return await ctx.send("**Command not ready yet!**")

	@commands.command(aliases=['dp'])
	@skill_on_cooldown()
	@user_is_class('seraph')
	async def divine_protection(self, ctx, target: discord.Member = None) -> None:
		""" A command for Seraphs. """

		if not target:
			target = ctx.author

		if await self.is_user_protected(target.id):
			return await ctx.send(f"**{target.mention} is already protected, {ctx.author.mention}!**")

		confirmed = await ConfirmSkill(f"**{ctx.author.mention}, are you sure you want to use your skill, to protect {target.mention}?**").prompt(ctx)
		if confirmed:
			current_timestamp = await self.get_timestamp()
			await self.insert_skill_action(
				user_id=ctx.author.id, skill_type="divine_protection", skill_timestamp=current_timestamp, 
				target_id=target.id, channel_id=ctx.channel.id
			)
			await self.update_user_protected(target.id, 1)
			await self.update_user_action_skill_ts(ctx.author.id, current_timestamp)
			divine_protection_embed = await self.get_divine_protection_embed(
				channel=ctx.channel, perpetrator_id=ctx.author.id, target_id=target.id)
			await ctx.send(embed=divine_protection_embed)
		else:
			await ctx.send("**Not protecting anyone, then!**")

	@commands.command()
	@skill_on_cooldown()
	@user_is_class('prawler')
	async def steal(self, ctx, target: discord.Member = None) -> None:
		""" A command for Prawlers. 
		:param target: The member from whom you want to steal. """

		# return await ctx.send("**Command not ready yet!**")

		attacker = ctx.author
		if not target:
			return await ctx.send(f"**Inform a member to steal, {attacker.mention}!**")

		if attacker.id == target.id:
			return await ctx.send("**You cannot steal from yourself!**")

		if not await self.get_user_currency(target.id):
			return await ctx.send(f"**You cannot steal from someone who doesn't have an account, {attacker.mention}!**")

		if await self.is_user_protected(target.id):
			return await ctx.send(f"**{attacker.mention}, you cannot steal from {target.mention}, because they are protected against attacks!**")

		confirmed = await ConfirmSkill(f"**{attacker.mention}, are you sure you want to steal from {target.mention}?**").prompt(ctx)
		if not confirmed:
			return await ctx.send("**Not stealing from anyone, then!**")

		current_timestamp = await self.get_timestamp()

		embed = discord.Embed(
			description=f"**{target.mention}, you are being robbed by {attacker.mention}! Defend yourself by reacting with 🛡️!**",
			color=discord.Color.orange())
		embed.set_footer(text="You have 40 minutes to defend yourself!")

		try:
			steal = await ctx.send(embed=embed)
			await self.insert_skill_action(
				user_id=attacker.id, skill_type="steal", skill_timestamp=current_timestamp, 
				target_id=target.id, message_id=steal.id, channel_id=steal.channel.id, emoji="🛡️"
			)
			await self.update_user_action_skill_ts(attacker.id, current_timestamp)
		except Exception as e:
			print(e)
			await steal.delete()
			return await ctx.send(f"**Your skill failed miserably for some reason, {attacker.mention}!**")

		else:
			await steal.add_reaction('🛡️')
			await steal.edit(content=f"<@{target.id}>")


	@commands.command()
	@skill_on_cooldown()
	@user_is_class('munk')
	async def munk(self, ctx, target: discord.Member = None) -> None:
		""" Converts a user into a real Munk. 
		:param target: The person you want to convert to a Munk. """

		attacker = ctx.author
		if not target:
			return await ctx.send(f"**Please, choose a member to use the `Munk` skill, {attacker.mention}!**")

		if attacker.id == target.id:
			return await ctx.send(f"**You cannot convert yourself, since you are already a `Munk`, {attacker.mention}!**")

		if target.display_name.strip().title().endswith('Munk'):
			return await ctx.send(f"**{target.mention} is already a `Munk`, {attacker.mention}!**")

		if not await self.get_user_currency(target.id):
			return await ctx.send(f"**You cannot convert someone who doesn't have an account, {attacker.mention}!**")

		if await self.is_user_protected(target.id):
			return await ctx.send(f"**{attacker.mention}, you cannot convert {target.mention} into a `Munk`, because they are protected against attacks!**")

		confirmed = await ConfirmSkill(f"**{attacker.mention}, are you sure you want to convert {target.mention} into a `Munk`?**").prompt(ctx)
		if not confirmed:
			return await ctx.send("**Not converting them, then!**")

		try:
			await target.edit(nick=f"{target.display_name} Munk")
			current_timestamp = await self.get_timestamp()
			# Don't need to store it, since it is forever
			# await self.insert_skill_action(
			# 	user_id=attacker.id, skill_type="munk", skill_timestamp=current_timestamp, 
			# 	target_id=target.id, channel_id=ctx.channel.id
			# )
			await self.update_user_action_skill_ts(attacker.id, current_timestamp)
			divine_protection_embed = await self.get_munk_embed(
				channel=ctx.channel, perpetrator_id=ctx.author.id, target_id=target.id)
			await ctx.send(embed=divine_protection_embed)
		except Exception as e:
			pritn(e)
			return await ctx.send(f"**Something went wrong and your `Munk` skill failed, {attacker.mention}!**")

		else:
			return await ctx.send(f"**{target.mention} has been converted into a `Munk`, thanks to {attacker.mention}!**")

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def create_table_sloth_skills(self, ctx) -> None:
		""" (Owner) Creates the SlothSkills table. """

		if await self.table_sloth_skills_exists():
			return await ctx.send("**The `SlothSkills` table already exists!**")

		mycursor, db = await the_database()
		await mycursor.execute("""
			CREATE TABLE SlothSkills (
				user_id BIGINT NOT NULL, skill_type VARCHAR(30) NOT NULL,
				skill_timestamp BIGINT NOT NULL, target_id BIGINT DEFAULT NULL,
				message_id BIGINT DEFAULT NULL, channel_id BIGINT DEFAULT NULL,
				emoji VARCHAR(50) DEFAULT NULL
			) DEFAULT CHARSET=utf8mb4""")
		await db.commit()
		await mycursor.close()
		await ctx.send("**Created `SlothSkills` table!**")

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def drop_table_sloth_skills(self, ctx) -> None:
		""" (Owner) Drops the SlothSkills table. """

		if not await self.table_sloth_skills_exists():
			return await ctx.send("**The `SlothSkills` table doesn't exist!**")

		mycursor, db = await the_database()
		await mycursor.execute("DROP TABLE SlothSkills")
		await db.commit()
		await mycursor.close()
		await ctx.send("**Dropped `SlothSkills` table!**")

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def reset_table_sloth_skills(self, ctx) -> None:
		""" (Owner) Resets the SlothSkills table. """

		if not await self.table_sloth_skills_exists():
			return await ctx.send("**The `SlothSkills` table doesn't exist yet!**")

		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM SlothSkills")
		await db.commit()
		await mycursor.close()
		await ctx.send("**Reset `SlothSkills` table!**")

	async def table_sloth_skills_exists(self) -> bool:
		""" Checks whether the SlothSkills table exists. """

		mycursor, db = await the_database()
		await mycursor.execute("SHOW TABLE STATUS LIKE 'SlothSkills'")
		table_info = await mycursor.fetchall()
		await mycursor.close()
		if len(table_info) == 0:
			return False
		else:
			return True

	async def insert_skill_action(self, user_id: int, skill_type: str, skill_timestamp: int, target_id: int = None, message_id: int = None, channel_id: int = None, emoji: str = None) -> None:
		""" Inserts a skill action into the database, if needed.
		:param user_id: The ID of the perpetrator of the skill action.
		:param skill_type: The type of the skill action.
		:param skill_timestamp: The timestamp of the skill action.
		:param target_id: The ID of the target member of the skill action. 
		:param message_id: The ID of the message related to the action, if there's any. """

		mycursor, db = await the_database()
		await mycursor.execute("""
			INSERT INTO SlothSkills (user_id, skill_type, skill_timestamp, target_id, message_id, channel_id, emoji) 
			VALUES (%s, %s, %s, %s, %s, %s, %s)""", (user_id, skill_type, skill_timestamp, target_id, message_id, channel_id, emoji))
		await db.commit()
		await mycursor.close()

	async def get_skill_action_by_message_id(self, message_id: int) -> Union[List[Union[int, str]], bool]:
		""" Gets a skill action by message ID.
		:param message_id: The ID with which to get the skill action. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM SlothSkills WHERE message_id = %s", (message_id,))
		skill_action = await mycursor.fetchone()
		await mycursor.close()
		return skill_action

	async def get_skill_action_by_reaction_context(self, message_id: int, target_id: int) -> Union[List[Union[int, str]], bool]:
		""" Gets a skill action by reaction context.
		:param message_id: The ID of the message of the skill action.
		:param target_id: The ID of the target member of the skill action. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM SlothSkills WHERE message_id = %s AND target_id = %s", (message_id, target_id))
		skill_action = await mycursor.fetchone()
		await mycursor.close()
		return skill_action

	async def get_timestamp(self) -> int:
		""" Gets the current timestamp. """

		epoch = datetime.utcfromtimestamp(0)
		the_time = (datetime.utcnow() - epoch).total_seconds()
		return the_time

	async def get_expired_steals(self) -> List[List[Union[str, int]]]:
		""" Gets expired steal skill actions. """

		the_time = await self.get_timestamp()
		mycursor, db = await the_database()
		await mycursor.execute("""
			SELECT * FROM SlothSkills 
			WHERE skill_type = 'steal' AND (%s - skill_timestamp) >= 2400
			""", (the_time,))
		steals = await mycursor.fetchall()
		await mycursor.close()
		return steals

	async def get_expired_protections(self) -> None:
		""" Gets expired divine protection skill actions. """

		the_time = await self.get_timestamp()
		mycursor, db = await the_database()
		await mycursor.execute("""
			SELECT * FROM SlothSkills 
			WHERE skill_type = 'divine_protection' AND (%s - skill_timestamp) >= 86400
			""", (the_time,))
		divine_protections = await mycursor.fetchall()
		await mycursor.close()
		return divine_protections

	async def get_user_currency(self, user_id: int) -> Union[List[Union[str, int]], bool]:
		""" Gets the user currency. 
		:param user_id: The ID of the user to get. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM UserCurrency WHERE user_id = %s", (user_id,))
		user = await mycursor.fetchone()
		await mycursor.close()
		return user

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def get_ts(self, ctx) -> None:
		timestamp = await self.get_timestamp()
		await ctx.send(timestamp)

	async def delete_skill_action_by_message_id(self, message_id: int) -> None:
		""" Deletes a skill action by message ID.
		:param message_id: The ID of the skill action. """

		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM SlothSkills WHERE message_id = %s", (message_id,))
		await db.commit()
		await mycursor.close()

	async def delete_skill_action_by_target_id(self, target_id: int) -> None:
		""" Deletes a skill action by target ID.
		:param target_id: The ID of the target member. """

		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM SlothSkills WHERE target_id = %s", (target_id,))
		await db.commit()
		await mycursor.close()

	async def update_user_money(self, user_id: int, money: int):
		""" Updates the user's money.
		:param user_id: The ID of the user to update the money.
		:param money: The money to be incremented (it works with negative numbers). """

		mycursor, db = await the_database()
		await mycursor.execute("""
			UPDATE UserCurrency SET user_money = user_money + %s 
			WHERE user_id = %s""", (money, user_id))
		await db.commit()
		await mycursor.close()

	async def update_user_action_skill_ts(self, user_id: int, current_ts: int) -> None:
		""" Updates the user's last action skill timestamp.
		:param user_id: The ID of the member to update. 
		:param current_ts: The timestamp to update to. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE UserCurrency SET last_skill_ts = %s WHERE user_id = %s", (current_ts, user_id))
		await db.commit()
		await mycursor.close()

	async def update_user_protected(self, user_id: int, protected: int) -> None:
		""" Updates the user's protected state.
		:param user_id: The ID of the member to update. 
		:param protected: Whether it's gonna be set to true or false. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE UserCurrency SET protected = %s WHERE user_id = %s", (protected, user_id))
		await db.commit()
		await mycursor.close()

	async def reset_user_action_skill_cooldown(self, user_id: int) -> None:
		""" Resets the user's action skill cooldown. 
		:param user_id: The ID of the user to reet the cooldown. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE UserCurrency SET last_skill_ts = 0 WHERE user_id = %s", (user_id,))
		await db.commit()
		await mycursor.close()

	@commands.command(aliases=['rsc'])
	@commands.has_permissions(administrator=True)
	async def reset_skill_cooldown(self, ctx, member: discord.Member = None) -> None:
		""" Resets the action skill cooldown of the given member. 
		:param member: The member to reset the cooldown (default = author). """

		if not member:
			member = ctx.author

		await self.reset_user_action_skill_cooldown(member.id)
		return await ctx.send(f"**Action skill cooldown reset for {member.mention}!**")


	async def get_steal_embed(self, channel, attacker_id: int, target_id: int, attack_succeeded: bool = False) -> discord.Embed:
		""" Makes an embedded message for a steal action. """

		timestamp = await self.get_timestamp()

		steal_embed = discord.Embed(
			title="A steal just happend!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)
		if attack_succeeded:
			steal_embed.description=f"🍃 <@{attacker_id}> stole 5łł from <@{target_id}>! 🍃"
			steal_embed.color=discord.Color.red()
		else:
			steal_embed.description=f"🍃 <@{attacker_id}> tried to steal 5łł from <@{target_id}>, but they didn't have it! 🍃"
			steal_embed.color=discord.Color.green()

		steal_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Prawler.png")
		steal_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return steal_embed

	async def get_divine_protection_embed(self, channel, perpetrator_id: int, target_id: int) -> discord.Embed:
		""" Makes an embedded message for a divine protection action.
		:param channel: The context channel.
		:param perpetrator_id: The ID of the perpetrator of the divine protection.
		:param target_id: The ID of the target member that is gonna be protected. """

		timestamp = await self.get_timestamp()

		steal_embed = discord.Embed(
			title="A Divine Protection has been executed!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)
		steal_embed.description=f"🛡️ <@{perpetrator_id}> protected <@{target_id}> from attacks for 24 hours! 🛡️"
		steal_embed.color=discord.Color.green()

		steal_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Seraph.png")
		steal_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return steal_embed

	async def get_munk_embed(self, channel, perpetrator_id: int, target_id: int) -> discord.Embed:
		""" Makes an embedded message for a munk action. 
		:param channel: The context channel.
		:param perpetrator_id: The ID of the perpetrator of the divine protection.
		:param target_id: The ID of the target member that is gonna be protected. """

		timestamp = await self.get_timestamp()

		steal_embed = discord.Embed(
			title="A Munk Convertion has been delightfully performed!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)
		steal_embed.description=f"🐿️ <@{perpetrator_id}> converted <@{target_id}> into a `Munk`! 🐿️"
		steal_embed.color=discord.Color.green()

		steal_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Munk.png")
		steal_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return steal_embed

	async def is_user_protected(self, user_id: int) -> bool:
		""" Checks whether user is protected.
		:param user_id: The ID of the user to check it. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT protected FROM UserCurrency WHERE user_id = %s", (user_id,))
		user_protected = await mycursor.fetchone()
		await mycursor.close()
		return user_protected is not None and user_protected[0]


	@commands.command(aliases=['my_skills'])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def skills(self, ctx):
		""" Shows all skills for the user's Sloth class. """


		user = await self.get_user_currency(ctx.author.id)
		if not user:
			return await ctx.send(embed=discord.Embed(description="**You don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one!**"))
		if user[7] == 'default':
			return await ctx.send(embed=discord.Embed(description="**You don't have a default Sloth class. Click [here](https://thelanguagesloth.com/profile/slothclass) to choose one!**"))

		cmds = []
		for c in ctx.cog.get_commands():
			try:
				if c.hidden:
					continue
				elif c.parent:
					continue
				elif not c.checks:
					continue
				elif not [check for check in c.checks if check.__qualname__ == 'SlothClass.user_is_class.<locals>.real_check']:
					continue

				await c.can_run(ctx)
				cmds.append(c)
			except commands.CommandError:
				continue
			except Exception as e:
				print(e)
				continue

		cmds = list(map(lambda c: c.qualified_name, cmds))
		skills_embed = discord.Embed(
			title=f"__Available Skills for__: `{user[7]}`",
			description=f"```apache\nSkills: {', '.join(cmds)}```",
			color=ctx.author.color,
			timestamp=ctx.message.created_at
		)
		skills_embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
		skills_embed.set_thumbnail(url=f"https://thelanguagesloth.com/media/sloth_classes/{user[7]}.png")
		skills_embed.set_footer(text=ctx.guild, icon_url=ctx.guild.icon_url)
		await ctx.send(embed=skills_embed)

def setup(client) -> None:
	""" Cog's setup function. """

	client.add_cog(SlothClass(client))