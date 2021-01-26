import discord
from discord.ext import commands, tasks, menus
from mysqldb import the_database
from typing import Union, List, Any
from extra.customerrors import MissingRequiredSlothClass, ActionSkillOnCooldown
from extra.menu import ConfirmSkill, prompt_message, prompt_number, OpenShopLoop
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
		self.safe_categories = [
			int(os.getenv('LESSON_CAT_ID')),
			int(os.getenv('CASE_CAT_ID')),
			int(os.getenv('EVENTS_CAT_ID')),
			int(os.getenv('DEBATE_CAT_ID')),
			int(os.getenv('CULTURE_CAT_ID')),
			int(os.getenv('APPLICATION_CAT_ID'))
		]

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
		await self.try_to_run(self.check_transmutations)
		await self.try_to_run(self.check_open_shop_items)
		await self.try_to_run(self.check_hacks)
		await self.try_to_run(self.check_knock_outs)

	async def try_to_run(self, func):
		""" Tries to run a function/method and ignore failures. """

		try:
			await func()
		except:
			pass

	async def check_steals(self) -> None:
		""" Check on-going steals and their expiration time. """
		
		steals = await self.get_expired_steals()
		for steal in steals:
			try:
				channel = self.bots_txt
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
			await self.delete_skill_action_by_target_id_and_skill_type(dp[3], 'divine_protection')

			channel = self.bots_txt
			

			await channel.send(
				content=f"<@{dp[0]}>, <@{dp[3]}>", 
				embed=discord.Embed(
					description=f"**<@{dp[3]}>'s `Divine Protection` from <@{dp[0]}> just expired!**",
					color=discord.Color.red()))

	async def check_transmutations(self) -> None:

		""" Check on-going transmutations and their expiration time. """

		transmutations = await self.get_expired_transmutations()
		for tm in transmutations:
			print(tm)
			await self.delete_skill_action_by_target_id_and_skill_type(tm[3], 'transmutation')

			channel = self.bots_txt
			

			await channel.send(
				content=f"<@{tm[0]}>", 
				embed=discord.Embed(
					description=f"**<@{tm[3]}>'s `Transmutation` has just expired! 🐩→💥→🦥**",
					color=discord.Color.red()))

	async def check_open_shop_items(self) -> None:

		""" Check on-going open-shop items and their expiration time. """

		transmutations = await self.get_expired_open_shop_items()
		for tm in transmutations:
			print(tm)
			await self.delete_skill_action_by_target_id_and_skill_type(tm[3], 'potion')

			channel = self.bots_txt
		
			await channel.send(
				content=f"<@{tm[0]}>",
				embed=discord.Embed(
					description=f"**<@{tm[3]}>'s `changing-Sloth-class potion` has just expired! Then it's been removed from the `Sloth class shop`! 🍯**",
					color=discord.Color.red()))

	async def check_hacks(self) -> None:

		""" Check on-going hacks and their expiration time. """

		hacks = await self.get_expired_hacks()
		for h in hacks:
			await self.delete_skill_action_by_target_id_and_skill_type(h[3], 'hack')
			await self.update_user_is_hacked(h[3], 0)

			channel = self.bots_txt
		
			await channel.send(
				content=f"<@{h[0]}>",
				embed=discord.Embed(
					description=f"**<@{h[3]}> updated his firewall so <@{h[0]}>'s hacking has no effect anymore! 💻**",
					color=discord.Color.red()))


	async def check_knock_outs(self) -> None:

		""" Check on-going knock-outs and their expiration time. """

		knock_outs = await self.get_expired_knock_outs()
		for ko in knock_outs:
			await self.delete_skill_action_by_target_id_and_skill_type(ko[3], 'hit')
			await self.update_user_is_knocked_out(ko[3], 0)

			channel = self.bots_txt
		
			await channel.send(
				content=f"<@{ko[0]}>",
				embed=discord.Embed(
					description=f"**<@{ko[3]}> got better from <@{ko[0]}>'s knock-out! 🤕**",
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
			if skill_action[6] == '🛡️' and emoji == '🛡️':

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

	@commands.command(aliases=['sloth_class', 'slothclasses'])
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
			raise MissingRequiredSlothClass(
				required_class=command_class, error_message="You don't have the required Sloth Class to run this command!")
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

	@commands.command(aliases=['ko', 'knock-out', 'knock_out', 'knock'])
	@skill_on_cooldown()
	@user_is_class('warrior')
	async def hit(self, ctx, target: discord.Member = None) -> None:
		""" A command for Warriors. """

		attacker = ctx.author

		if ctx.channel.id != bots_and_commands_channel_id:
			return await ctx.send(f"**{attacker.mention}, you can only use this command in {self.bots_txt.mention}!**")

		if await self.is_user_knocked_out(attacker.id):
			return await ctx.send(f"**{attacker.mention}, you can't use your skill, because you are knocked-out!**")

		if not target:
			return await ctx.send(f"**Please, inform a target member, {attacker.mention}!**")

		# if attacker.id == target.id:
		# 	return await ctx.send(f"**{attacker.mention}, you cannot knock yourself out!**")

		if target.bot:
			return await ctx.send(f"**{attacker.mention}, you cannot knock out a bot!**")

		if await self.is_user_protected(target.id):
			return await ctx.send(f"**{attacker.mention}, {target.mention} is protected, you can't knock them out!**")

		if await self.is_user_knocked_out(target.id):
			return await ctx.send(f"**{attacker.mention}, {target.mention} is already knocked out!**")


		confirmed = await ConfirmSkill(f"**{attacker.mention}, are you sure you want to knock {target.mention} out?**").prompt(ctx)
		if not confirmed:
			return await ctx.send("**Not knocking them out, then!**")

		try:
			current_timestamp = await self.get_timestamp()
			# Don't need to store it, since it is forever
			await self.update_user_is_knocked_out(target.id, 1)
			await self.insert_skill_action(
				user_id=attacker.id, skill_type="hit", skill_timestamp=current_timestamp,
				target_id=target.id, channel_id=ctx.channel.id
			)
			await self.update_user_action_skill_ts(attacker.id, current_timestamp)
			hit_embed = await self.get_hit_embed(
				channel=ctx.channel, perpetrator_id=attacker.id, target_id=target.id)
			msg = await ctx.send(embed=hit_embed)
		except Exception as e:
			print(e)
			return await ctx.send(f"**Something went wrong and your `Hit` skill failed, {attacker.mention}!**")

	@commands.command(aliases=['transmutate', 'trans'])
	@skill_on_cooldown()
	@user_is_class('metamorph')
	async def transmutation(self, ctx) -> None:
		""" A command for Metamorphs. """

		if ctx.channel.id != bots_and_commands_channel_id:
			return await ctx.send(f"**{ctx.author.mention}, you can only use this command in {self.bots_txt.mention}!**")

		member = ctx.author

		if await self.is_user_knocked_out(member.id):
			return await ctx.send(f"**{member.mention}, you can't use your skill, because you are knocked-out!**")

		if await self.is_transmutated(member.id):
			return await ctx.send(f"**You are already transmutated, {member.mention}!**")

		confirmed = await ConfirmSkill(f"**{member.mention}, are you sure you want to transmutate yourself into a diffrent form for 1 hour?**").prompt(ctx)
		if not confirmed:
			return await ctx.send(f"**{member.mention}, not transmutating, then!**")

		timestamp = await self.get_timestamp()
		await self.insert_skill_action(
			user_id=member.id, skill_type="transmutation",
			skill_timestamp=timestamp, target_id=member.id,
			channel_id=ctx.channel.id
		)
		await self.update_user_action_skill_ts(member.id, timestamp)

		transmutation_embed = await self.get_transmutation_embed(channel=ctx.channel, perpetrator_id=ctx.author.id)
		await ctx.send(embed=transmutation_embed)

	@commands.command(aliases=['ma'])
	@skill_on_cooldown()
	@user_is_class('agares')
	async def magic_pull(self, ctx, target: discord.Member = None) -> None:
		""" A command for Agares. """

		attacker = ctx.author

		if ctx.channel.id != bots_and_commands_channel_id:
			return await ctx.send(f"**{attacker.mention}, you can only use this command in {self.bots_txt.mention}!**")

		if await self.is_user_knocked_out(attacker.id):
			return await ctx.send(f"**{attacker.mention}, you can't use your skill, because you are knocked-out!**")

		attacker_state = attacker.voice
		if not attacker_state or not (attacker_vc := attacker_state.channel):
			return await ctx.send(f"**{attacker.mention}, you first need to be in a voice channel to magic pull someone!**")

		if not target:
			return await ctx.send(f"**Please, inform a target member, {attacker.mention}!**")

		if attacker.id == target.id:
			return await ctx.send(f"**{attacker.mention}, you cannot magic pull yourself!**")

		if target.bot:
			return await ctx.send(f"**{attacker.mention}, you cannot magic pull a bot!**")

		target_state = target.voice

		if not target_state or not (target_vc := target_state.channel):
			return await ctx.send(f"**{attacker.mention}, you cannot magic pull {target.mention}, because they are not in a voice channel!!**")

		if target_vc.category and target_vc.category.id in self.safe_categories:
			return await ctx.send(
				f"**{attacker.mention}, you can't magic pull {target.mention} from `{target_vc}`, because it's a safe channel.**")

		if await self.is_user_protected(target.id):
			return await ctx.send(f"**{attacker.mention}, {target.mention} is protected, you can't magic pull them!**")

		try:
			await target.move_to(attacker_vc)
		except Exception as e:
			print(e)
			await ctx.send(
				f"**{attacker.mention}, for some reason I couldn't magic pull {target.mention} from `{target_vc}` to `{attacker_vc}`**")
		else:
			# Puts the attacker's skill on cooldown
			current_ts = await self.get_timestamp()
			await self.update_user_action_skill_ts(attacker.id, current_ts)
			# Sends embedded message into the channel
			magic_pull_embed = await self.get_magic_pull_embed(
				channel=ctx.channel, perpetrator_id=attacker.id, target_id=target.id,
				t_before_vc=target_vc, t_after_vc=attacker_vc)
			await ctx.send(content=target.mention, embed=magic_pull_embed)

	@commands.command(aliases=['eb', 'energy', 'boost'])
	@skill_on_cooldown()
	@user_is_class('cybersloth')
	async def hack(self, ctx, target: discord.Member = None) -> None:
		""" A command for Cybersloths. """

		# return await ctx.send("**Command not ready yet!**")

		attacker = ctx.author

		if ctx.channel.id != bots_and_commands_channel_id:
			return await ctx.send(f"**{attacker.mention}, you can only use this command in {self.bots_txt.mention}!**")

		if await self.is_user_knocked_out(attacker.id):
			return await ctx.send(f"**{attacker.mention}, you can't use your skill, because you are knocked-out!**")

		if not target:
			return await ctx.send(f"**Please, inform a target member, {attacker.mention}!**")

		if attacker.id == target.id:
			return await ctx.send(f"**{attacker.mention}, you cannot hack yourself!**")

		if target.bot:
			return await ctx.send(f"**{attacker.mention}, you cannot hack a bot!**")

		if not await self.get_user_currency(target.id):
			return await ctx.send(f"**You cannot hack someone who doesn't have an account, {attacker.mention}!**")

		if await self.is_user_protected(target.id):
			return await ctx.send(f"**{attacker.mention}, {target.mention} is protected, you can't hack them!**")

		if await self.is_user_hacked(target.id):
			return await ctx.send(f"**{attacker.mention}, {target.mention} is already hacked!**")


		confirmed = await ConfirmSkill(f"**{attacker.mention}, are you sure you want to hack {target.mention}?**").prompt(ctx)
		if not confirmed:
			return await ctx.send("**Not hacking them, then!**")

		try:
			current_timestamp = await self.get_timestamp()
			# Don't need to store it, since it is forever
			await self.update_user_is_hacked(target.id, 1)
			await self.insert_skill_action(
				user_id=attacker.id, skill_type="hack", skill_timestamp=current_timestamp,
				target_id=target.id, channel_id=ctx.channel.id
			)
			await self.update_user_action_skill_ts(attacker.id, current_timestamp)
			hack_embed = await self.get_hack_embed(
				channel=ctx.channel, perpetrator_id=attacker.id, target_id=target.id)
			msg = await ctx.send(embed=hack_embed)
		except Exception as e:
			print(e)
			return await ctx.send(f"**Something went wrong and your `Hack` skill failed, {attacker.mention}!**")

	@commands.command(aliases=['os', 'open', 'shop'])
	@skill_on_cooldown()
	@user_is_class('merchant')
	async def open_shop(self, ctx) -> None:
		""" A command for Merchants. """

		if ctx.channel.id != bots_and_commands_channel_id:
			return await ctx.send(f"**{ctx.author.mention}, you can only use this command in {self.bots_txt.mention}!**")

		member = ctx.author

		if await self.is_user_knocked_out(member.id):
			return await ctx.send(f"**{member.mention}, you can't use your skill, because you are knocked-out!**")

		if (shopitem := await self.get_skill_action_by_user_id(member.id)):
			return await ctx.send(f"**{member.mention}, you already have an item in your shop!**")


		item_price = await prompt_number(self.client, ctx, f"**{member.mention}, for how much do you want to sell your changing-Sloth-class potion?**", member)
		if item_price is None:
			return

		confirm = await ConfirmSkill(f"**{member.mention}, are you sure you want to spend 50łł to put an item in your shop with the price of `{item_price}`łł ?**").prompt(ctx)
		if confirm:
			user_currency = await self.get_user_currency(member.id)
			if user_currency[1] >= 50:
				await self.update_user_money(member.id, -50)
			else:
				return await ctx.send(f"**{member.mention}, you don't have `50łł`!**")

			try:
				current_timestamp = await self.get_timestamp()
				await self.insert_skill_action(
					user_id=member.id, skill_type="potion", skill_timestamp=current_timestamp, 
					target_id=member.id, channel_id=ctx.channel.id, price=item_price
				)
				await self.update_user_action_skill_ts(member.id, current_timestamp)
				open_shop_embed = await self.get_open_shop_embed(
					channel=ctx.channel, perpetrator_id=member.id, price=item_price)
				await ctx.send(embed=open_shop_embed)
			except Exception as e:
				print(e)
				return await ctx.send(f"**{member.mention}, something went wrong with it, try again later!**")
			else:
				await ctx.send(f"**{member}, your item is now in the shop, check `z!sloth_shop` to see it there!**")
		else:
			return await ctx.send(f"**Not doing it, then, {member.mention}!**")

	@commands.command(aliases=['dp', 'divine', 'protection'])
	@skill_on_cooldown()
	@user_is_class('seraph')
	async def divine_protection(self, ctx, target: discord.Member = None) -> None:
		""" A command for Seraphs. """

		if ctx.channel.id != bots_and_commands_channel_id:
			return await ctx.send(f"**{ctx.author.mention}, you can only use this command in {self.bots_txt.mention}!**")

		if await self.is_user_knocked_out(ctx.author.id):
			return await ctx.send(f"**{ctx.author.mention}, you can't use your skill, because you are knocked-out!**")

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

	@commands.command(aliases=['stl', 'rob'])
	@skill_on_cooldown()
	@user_is_class('prawler')
	async def steal(self, ctx, target: discord.Member = None) -> None:
		""" A command for Prawlers. 
		:param target: The member from whom you want to steal. """

		if ctx.channel.id != bots_and_commands_channel_id:
			return await ctx.send(f"**{ctx.author.mention}, you can only use this command in {self.bots_txt.mention}!**")

		attacker = ctx.author

		if await self.is_user_knocked_out(attacker.id):
			return await ctx.send(f"**{attacker.mention}, you can't use your skill, because you are knocked-out!**")

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

		if ctx.channel.id != bots_and_commands_channel_id:
			return await ctx.send(f"**{ctx.author.mention}, you can only use this command in {self.bots_txt.mention}!**")

		attacker = ctx.author

		if await self.is_user_knocked_out(attacker.id):
			return await ctx.send(f"**{attacker.mention}, you can't use your skill, because you are knocked-out!**")

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
			munk_embed = await self.get_munk_embed(
				channel=ctx.channel, perpetrator_id=ctx.author.id, target_id=target.id)
			msg = await ctx.send(embed=munk_embed)
		except Exception as e:
			print(e)
			return await ctx.send(f"**Something went wrong and your `Munk` skill failed, {attacker.mention}!**")

		else:
			await msg.edit(content=f"<@{target.id}>")

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
				emoji VARCHAR(50) DEFAULT NULL, PRICE INT DEFAULT 0
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

	async def insert_skill_action(self, user_id: int, skill_type: str, skill_timestamp: int, target_id: int = None, message_id: int = None, channel_id: int = None, emoji: str = None, price: int = 0) -> None:
		""" Inserts a skill action into the database, if needed.
		:param user_id: The ID of the perpetrator of the skill action.
		:param skill_type: The type of the skill action.
		:param skill_timestamp: The timestamp of the skill action.
		:param target_id: The ID of the target member of the skill action. 
		:param message_id: The ID of the message related to the action, if there's any. 
		:param price: The price of the item or something, if it is for sale. """

		mycursor, db = await the_database()
		await mycursor.execute("""
			INSERT INTO SlothSkills (user_id, skill_type, skill_timestamp, target_id, message_id, channel_id, emoji, price) 
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", (user_id, skill_type, skill_timestamp, target_id, message_id, channel_id, emoji, price))
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

	async def get_skill_action_by_target_id_and_skill_type(self, target_id: int, skill_type: str) -> Union[List[Union[int, str]], bool]:
		""" Gets a skill action by target ID and skill type.
		:param target_id: The target ID with which to get the skill action. 
		:param skill_type: The skill type of the skill action. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM SlothSkills WHERE target_id = %s and skill_type = %s", (target_id, skill_type))
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

	async def get_skill_action_by_user_id(self, user_id: int) -> Union[List[Union[int, str]], bool]:
		""" Gets a skill action by reaction context.
		:param user_id: The ID of the user of the skill action. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM SlothSkills WHERE user_id = %s AND skill_type = 'potion'", (user_id,))
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

	async def get_expired_transmutations(self) -> None:
		""" Gets expired transmutation skill actions. """

		the_time = await self.get_timestamp()
		mycursor, db = await the_database()
		await mycursor.execute("""
			SELECT * FROM SlothSkills 
			WHERE skill_type = 'transmutation' AND (%s - skill_timestamp) >= 3600
			""", (the_time,))
		transmutations = await mycursor.fetchall()
		await mycursor.close()
		return transmutations

	async def get_expired_open_shop_items(self) -> None:
		""" Gets expired transmutation skill actions. """

		the_time = await self.get_timestamp()
		mycursor, db = await the_database()
		await mycursor.execute("""
			SELECT * FROM SlothSkills 
			WHERE skill_type = 'potion' AND (%s - skill_timestamp) >= 86400
			""", (the_time,))
		transmutations = await mycursor.fetchall()
		await mycursor.close()
		return transmutations

	async def get_expired_hacks(self) -> None:
		""" Gets expired hack skill actions. """

		the_time = await self.get_timestamp()
		mycursor, db = await the_database()
		await mycursor.execute("""
			SELECT * FROM SlothSkills 
			WHERE skill_type = 'hack' AND (%s - skill_timestamp) >= 86400
			""", (the_time,))
		hacks = await mycursor.fetchall()
		await mycursor.close()
		return hacks

	async def get_expired_knock_outs(self) -> None:
		""" Gets expired knock-out skill actions. """

		the_time = await self.get_timestamp()
		mycursor, db = await the_database()
		await mycursor.execute("""
			SELECT * FROM SlothSkills 
			WHERE skill_type = 'hit' AND (%s - skill_timestamp) >= 86400
			""", (the_time,))
		knock_outs = await mycursor.fetchall()
		await mycursor.close()
		return knock_outs

	async def get_user_currency(self, user_id: int) -> Union[List[Union[str, int]], bool]:
		""" Gets the user currency. 
		:param user_id: The ID of the user to get. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM UserCurrency WHERE user_id = %s", (user_id,))
		user = await mycursor.fetchone()
		await mycursor.close()
		return user

	@commands.command()
	@commands.has_permissions()
	async def get_ts(self, ctx) -> None:
		""" Gets the current timestamp"""

		timestamp = await self.get_timestamp()
		await ctx.send(f"**{timestamp}**")

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

	async def delete_skill_action_by_target_id_and_skill_type(self, target_id: int, skill_type: str) -> None:
		""" Deletes a skill action by target ID.
		:param target_id: The ID of the target member. 
		:param skill_type: The type of the action skill. """

		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM SlothSkills WHERE target_id = %s AND skill_type = %s", (target_id, skill_type))
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

	async def update_user_has_potion(self, user_id: int, has_it: int) -> None:
		""" Updates the user's protected state.
		:param user_id: The ID of the member to update. 
		:param has_it: Whether it's gonna be set to true or false. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE UserCurrency SET has_potion = %s WHERE user_id = %s", (has_it, user_id))
		await db.commit()
		await mycursor.close()

	async def update_user_is_hacked(self, user_id: int, hacked: int) -> None:
		""" Updates the user's protected state.
		:param user_id: The ID of the member to update. 
		:param hacked: Whether it's gonna be set to true or false. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE UserCurrency SET hacked = %s WHERE user_id = %s", (hacked, user_id))
		await db.commit()
		await mycursor.close()

	async def update_user_is_knocked_out(self, user_id: int, is_it: int) -> None:
		""" Updates the user's protected state.
		:param user_id: The ID of the member to update. 
		:param is_it: Whether it's gonna be set to true or false. """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE UserCurrency SET knocked_out = %s WHERE user_id = %s", (is_it, user_id))
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
		""" (ADMIN) Resets the action skill cooldown of the given member. 
		:param member: The member to reset the cooldown (default = author). """

		if not member:
			member = ctx.author

		await self.reset_user_action_skill_cooldown(member.id)
		return await ctx.send(f"**Action skill cooldown reset for {member.mention}!**")

	async def get_steal_embed(self, channel, attacker_id: int, target_id: int, attack_succeeded: bool = False) -> discord.Embed:
		""" Makes an embedded message for a steal action.
		:param channel: The context channel.
		:param perpetrator_id: The ID of the perpetrator of the stealing.
		:param target_id: The ID of the target member who is beeing stolen from. 
		:param attack_succeed: Whether the attack succeeded or not. """

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

		divine_embed = discord.Embed(
			title="A Divine Protection has been executed!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)
		divine_embed.description=f"🛡️ <@{perpetrator_id}> protected <@{target_id}> from attacks for 24 hours! 🛡️"
		divine_embed.color=discord.Color.green()

		divine_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Seraph.png")
		divine_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return divine_embed

	async def get_munk_embed(self, channel, perpetrator_id: int, target_id: int) -> discord.Embed:
		""" Makes an embedded message for a munk action. 
		:param channel: The context channel.
		:param perpetrator_id: The ID of the perpetrator of the munk skill.
		:param target_id: The ID of the target member that is gonna be protected. """

		timestamp = await self.get_timestamp()

		munk_embed = discord.Embed(
			title="A Munk Convertion has been delightfully performed!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)
		munk_embed.description=f"🐿️ <@{perpetrator_id}> converted <@{target_id}> into a `Munk`! 🐿️"
		munk_embed.color=discord.Color.green()

		munk_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Munk.png")
		munk_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return munk_embed

	async def get_transmutation_embed(self, channel, perpetrator_id: int) -> discord.Embed:
		""" Makes an embedded message for a transmutation action. 
		:param channel: The context channel.
		:param perpetrator_id: The ID of the perpetrator of the transmutation. """

		timestamp = await self.get_timestamp()

		transmutation_embed = discord.Embed(
			title="A Transmutation just happened in front of everyone's eyes!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)
		transmutation_embed.description=f"**<@{perpetrator_id}> transmutated themselves into something else! 🦥→💥→🐩**"
		transmutation_embed.color=discord.Color.green()

		transmutation_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Metamorph.png")
		transmutation_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return transmutation_embed

	async def get_magic_pull_embed(self, channel, perpetrator_id: int, target_id: int, t_before_vc: discord.VoiceChannel, t_after_vc: discord.VoiceChannel) -> discord.Embed:
		""" Makes an embedded message for a magic pull action. 
		:param channel: The context channel.
		:param perpetrator_id: The ID of the perpetrator of the magic pulling. 
		:param target_id: The ID of the target of the magic pulling. """

		timestamp = await self.get_timestamp()

		magic_pull_embed = discord.Embed(
			title="A Magic Pull has been Successfully Pulled Off!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)
		magic_pull_embed.description=f"**<@{perpetrator_id}> magic pulled <@{target_id}> from `{t_before_vc}` to `{t_after_vc}`!** 🧲"
		magic_pull_embed.color=discord.Color.green()

		magic_pull_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Agares.png")
		magic_pull_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return magic_pull_embed

	async def get_open_shop_embed(self, channel, perpetrator_id: int, price: int) -> discord.Embed:
		""" Makes an embedded message for a magic pull action. 
		:param channel: The context channel.
		:param perpetrator_id: The ID of the perpetrator of the magic pulling. 
		:param price: The price of the item that Merchant put into the shop. """

		timestamp = await self.get_timestamp()

		open_shop_embed = discord.Embed(
			title="A Merchant item has been put into the `Sloth Class Shop`!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)
		open_shop_embed.description=f"**<@{perpetrator_id}> put a `changing-Sloth-class potion` into the Sloth class shop, for the price of `{price}łł`!** 🍯"
		open_shop_embed.color=discord.Color.green()

		open_shop_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Merchant.png")
		open_shop_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return open_shop_embed

	async def get_hit_embed(self, channel, perpetrator_id: int, target_id: int) -> discord.Embed:
		""" Makes an embedded message for a knock-out action.
		:param channel: The context channel.
		:param perpetrator_id: The ID of the perpetrator of the knock-out.
		:param target_id: The ID of the target of the knock-out. """

		timestamp = await self.get_timestamp()

		hit_embed = discord.Embed(
			title="Someone was Knocked Out!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)
		hit_embed.description=f"**<@{perpetrator_id}> knocked <@{target_id}> out!** 😵"
		hit_embed.color=discord.Color.green()

		hit_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Warrior.png")
		hit_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return hit_embed

	async def get_hack_embed(self, channel: discord.TextChannel, perpetrator_id: int, target_id: int,) -> discord.Embed:
		""" Makes an embedded message for a hacking skill action.
		:param channel: The context channel.
		:param perpetrator_id: The ID of the perpetrator of the hacking.
		:param target_id: The ID of the target of the hacking. """

		timestamp = await self.get_timestamp()

		hack_embed = discord.Embed(
			title="Someone just got Hacked and lost Control of Everything!",
			timestamp=datetime.utcfromtimestamp(timestamp)
		)
		hack_embed.description=f"**<@{perpetrator_id}> hacked <@{target_id}>!** <a:hackerman:652303204809179161>"
		# hack_embed.description=f"**<@{perpetrator_id}> hacked <@{attacker_id}>!** <a:hackerman:802354539184259082>"
		hack_embed.color=discord.Color.green()

		hack_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Cybersloth.png")
		hack_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return hack_embed

	async def is_user_protected(self, user_id: int) -> bool:
		""" Checks whether user is protected.
		:param user_id: The ID of the user to check it. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT protected FROM UserCurrency WHERE user_id = %s", (user_id,))
		user_protected = await mycursor.fetchone()
		await mycursor.close()
		return user_protected is not None and user_protected[0]

	async def is_transmutated(self, user_id: int) -> bool:
		""" Checks whether user is transmutated.
		:param user_id: The ID of the user to check it. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT COUNT(*) FROM SlothSkills WHERE user_id = %s AND skill_type = 'transmutation'", (user_id,))
		user_transmutated = await mycursor.fetchone()
		await mycursor.close()
		return user_transmutated[0]

	async def is_user_hacked(self, user_id: int) -> bool:
		""" Checks whether user is hacked.
		:param user_id: The ID of the user to check it. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT hacked FROM UserCurrency WHERE user_id = %s", (user_id,))
		user_hacked = await mycursor.fetchone()
		await mycursor.close()
		return user_hacked is not None and user_hacked[0]

	async def is_user_knocked_out(self, user_id: int) -> bool:
		""" Checks whether user is knocked out.
		:param user_id: The ID of the user to check it. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT knocked_out FROM UserCurrency WHERE user_id = %s", (user_id,))
		user_knocked_out = await mycursor.fetchone()
		await mycursor.close()
		return user_knocked_out is not None and user_knocked_out[0]

	async def get_open_shop_items(self) -> List[List[Union[str, int]]]:
		""" Gets all open shop items. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM SlothSkills WHERE skill_type = 'potion'")
		potions = await mycursor.fetchall()
		await mycursor.close()
		return potions

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

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def sloth_shop(self, ctx) -> None:
		""" Shows all class related items in the Sloth shop. """

		embed = discord.Embed(
			title="__Sloth Class Shop__",
			description="All available items related to Sloth classes.",
			color=ctx.author.color,
			timestamp=ctx.message.created_at
			)

		potions = await self.get_open_shop_items()
		if potions:
			the_menu = menus.MenuPages(source=OpenShopLoop(potions), clear_reactions_after=True)
			await the_menu.start(ctx)
		else:
			return await ctx.send(f"**There are no items in the `Sloth class shop` yet, {ctx.author.mention}!**")

	@commands.command(aliases=['bp', 'buy'])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def buy_potion(self, ctx, member: discord.Member = None) -> None:
		""" Buys a changing-Sloth-class potion from a Merchant. """

		buyer = ctx.author
		if not member:
			return await ctx.send(f"**Please, inform a `Merchant`, {buyer.mention}!**")


		if not (merchant_item := await self.get_skill_action_by_user_id(member.id)):
			return await ctx.send(
				f"**{member} is either not a `Merchant` or they don't have a potion available for purchase, {buyer.mention}!**")


		user_info = await self.get_user_currency(buyer.id)
		if not user_info:
			await ctx.send(embed=discord.Embed(description=f"**{buyer.mention}, you don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one!**"))

		elif user_info[7].lower() == 'default':
			await ctx.send(embed=discord.Embed(description=f"**{buyer.mention}, you don't have a Sloth class yet. Click [here](https://thelanguagesloth.com/profile/slothclass) to choose one!**"))

		elif user_info[11]:
			await ctx.send(embed=discord.Embed(description=f"**{buyer.mention}, you already have a potion, you can't buy another one!**"))

		elif user_info[1] < merchant_item[7]:
			await ctx.send(embed=discord.Embed(description=f"**{buyer.mention}, the potion costs {merchant_item[7]}, but you only have {user_info[1]}łł!**"))

		else:
			confirm = await ConfirmSkill(f"**{buyer.mention}, are you sure you want to buy a `changing-Sloth-class potion` for `{merchant_item[7]}łł`?**").prompt(ctx)
			if not confirm:
				return await ctx.send(f"**Not buying it, then, {buyer.mention}!**")

			try:
				# Updates both buyer and seller's money
				await self.update_user_money(buyer.id, - merchant_item[7])
				await self.update_user_money(member.id, merchant_item[7])
				# Gives the buyer their potion and removes the potion from the store
				await self.update_user_has_potion(buyer.id, 1)
				await self.delete_skill_action_by_target_id_and_skill_type(member.id, 'potion')
			except Exception as e:
				print(e)
				await ctx.send(embed=discord.Embed(
					title="Error!",
					description=f"**Something went wrong with that purchase, {buyer.mention}!**",
					color=discord.Color.red(),
					timestamp=ctx.message.created_at
					))

			else:
				await ctx.send(embed=discord.Embed(
					title="__Successful Acquisition__",
					description=f"{buyer.mention} bought a `changing-Sloth-class potion` from {member.mention}!",
					color=discord.Color.green(),
					timestamp=ctx.message.created_at
					))

def setup(client) -> None:
	""" Cog's setup function. """

	client.add_cog(SlothClass(client))