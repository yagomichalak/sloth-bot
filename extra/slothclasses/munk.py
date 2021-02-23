import discord
from discord.ext import commands
from .player import Player
from mysqldb import the_database
from extra.menu import ConfirmSkill
import os
from datetime import datetime
from typing import List, Union, Dict, Any
import asyncio

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))

class Munk(Player):

	def __init__(self, client) -> None:
		self.client = client


	@commands.command()
	@Player.skill_on_cooldown()
	@Player.user_is_class('munk')
	@Player.skill_mark()
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

		target_currency = await self.get_user_currency(target.id)
		if not target_currency:
			return await ctx.send(f"**You cannot convert someone who doesn't have an account, {attacker.mention}!**")

		if target_currency[7] == 'default':
			return await ctx.send(f"**You cannot convert someone who has a `default` Sloth class, {attacker.mention}!**")

		if await self.is_user_protected(target.id):
			return await ctx.send(f"**{attacker.mention}, you cannot convert {target.mention} into a `Munk`, because they are protected against attacks!**")

		confirmed = await ConfirmSkill(f"**{attacker.mention}, are you sure you want to convert {target.mention} into a `Munk`?**").prompt(ctx)
		if not confirmed:
			return await ctx.send("**Not converting them, then!**")

		await self.check_cooldown(user_id=attacker.id, skill_number=1)

		try:
			await target.edit(nick=f"{target.display_name} Munk")
			current_timestamp = await self.get_timestamp()
			# Don't need to store it, since it is forever
			# await self.insert_skill_action(
			# 	user_id=attacker.id, skill_type="munk", skill_timestamp=current_timestamp, 
			# 	target_id=target.id, channel_id=ctx.channel.id
			# )
			await self.update_user_action_skill_ts(attacker.id, current_timestamp)
			# Updates user's skills used counter
			await self.update_user_skills_used(user_id=attacker.id)
			munk_embed = await self.get_munk_embed(
				channel=ctx.channel, perpetrator_id=ctx.author.id, target_id=target.id)
			msg = await ctx.send(embed=munk_embed)
		except Exception as e:
			print(e)
			return await ctx.send(f"**Something went wrong and your `Munk` skill failed, {attacker.mention}!**")

		else:
			await msg.edit(content=f"<@{target.id}>")


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

	async def get_join_tribe_embed(self, channel, inviter: discord.Member, target: discord.Member, tribe: Dict[str, Union[int, str]]) -> discord.Embed:
		""" Makes an embedded message for a tribe joining.
		:param channel: The context channel.
		:param inviter: The inviter.
		:param target_id: The target member that is gonna be invited to a tribe. 
		:param tribe: The tribe and its information. """

		timestamp = await self.get_timestamp()

		join_tribe_embed = discord.Embed(
			title="Someone just joined a Tribe!",
			description=f"🏕️ {target.mention} just joined `{tribe['name']}`! 🏕️",
			color=discord.Color.green(),
			timestamp=datetime.utcfromtimestamp(timestamp),
			url=tribe['link']
		)

		join_tribe_embed.set_author(name=inviter, icon_url=inviter.avatar_url)
		if tribe['thumbnail']:
			join_tribe_embed.set_thumbnail(url=tribe['thumbnail'])
		join_tribe_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

		return join_tribe_embed

	async def get_tribe_info_by_name(self, name: str) -> Dict[str, Union[str, int]]:
		""" Gets information about a specific tribe. 
		:param name: The name of the tribe. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM UserTribe WHERE tribe_name = %s", (name,))
		tribe = await mycursor.fetchone()
		await mycursor.close()

		tribe_info = {
			'owner_id': None,
			'name': None,
			'description': None,
			'two_emojis': None,
			'thumbnail': None,
			'form': None,
			'link': None
		}

		if tribe:
			tribe_info = {
				'owner_id': tribe[0] ,
				'name': tribe[1],
				'description': tribe[2],
				'two_emojis': tribe[3],
				'thumbnail': tribe[4],
				'form': tribe[5],
				'link': f"https://thelanguagesloth.com/{tribe[6]}"
			}

		return tribe_info


	async def get_tribe_info_by_user_id(self, user_id: str) -> Dict[str, Union[str, int]]:
		""" Gets information about a specific tribe. 
		:param user_id: The ID of the user owner of the tribe. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM UserTribe WHERE user_id = %s", (user_id,))
		tribe = await mycursor.fetchone()
		await mycursor.close()

		tribe_info = {
			'owner_id': None,
			'name': None,
			'description': None,
			'two_emojis': None,
			'thumbnail': None,
			'form': None,
			'link': None
		}

		if tribe:
			tribe_info = {
				'owner_id': tribe[0] ,
				'name': tribe[1],
				'description': tribe[2],
				'two_emojis': tribe[3],
				'thumbnail': tribe[4],
				'form': tribe[5],
				'link': f"https://thelanguagesloth.com/{tribe[6]}"
			}

		return tribe_info




	@commands.command(aliases=['request_logo', 'ask_thumbnail', 'ask_logo'])
	@commands.cooldown(1, 3600, commands.BucketType.user)
	async def request_thumbnail(self, ctx, image_url: str = None) -> None:
		""" Request a thumbnail for your tribe.
		:param image_url: The URL link of the thumbnail image. """

		requester = ctx.author

		if not image_url:
			return await ctx.send(f"You need to inform an image URL, {requester.mention}!**")

		if not image_url.startswith('https://'):
			return await ctx.send(f"You need to inform an image URL that has HTTPS in it, {requester.mention}!**")

		if len(image_url) > 200:
			return await ctx.send(f"You need to inform an image URL within 200 characters, {requester.mention}!**")

		user_tribe = await self.get_tribe_info_by_user_id(user_id=requester.id)
		if not user_tribe['name']:
			return await ctx.send(f"**You don't even have a tribe, you cannot request it, {request.mention}!**")

		confirm = await ConfirmSkill(content=requester.mention, 
			msg=f"**Are you sure you want to request [this]({image_url}) to be `{user_tribe['name']}`'s thumbnail/logo?**")
		if confirm:
			# Sends message to a moderation-clearance room
			room = None
			request_embed = discord.Embed(
				title="__Thumbnail Request__",
				description=f"{requester.mention} is requesting the image below to be their tribe's (`{user_tribe['name']}`) thumbnail/logo. Use z!approve_thumbnail"
				)
			request_embed.set_image(url=image_url)
			await room.send(embed=request_embed)

		else:
			await ctx.send(f"**Not doing requesting it, then, {requester.mention}!**")



	@commands.command(aliases=['invite'])
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def tribe_invite(self, ctx, member: discord.Member = None) -> None:
		""" Invites a user to your tribe.
		:param member: The member to invite. """

		inviter = ctx.author
		user_tribe = await self.get_tribe_info_by_user_id(user_id=inviter.id)
		if not user_tribe['name']:
			return await ctx.send(f"**You don't have a tribe, {inviter.mention}**!")

		if not member:
			return await ctx.send(f"**Please, inform a member to invite to your tribe, {inviter.mention}!**")

		if inviter.id == member.id:
			return await ctx.send(f"**You cannot invite yourself into your own tribe, {inviter.mention}!**")

		confirm = await ConfirmSkill(f"Are you sure you want to invite, {member.mention} to `{user_tribe['name']}`?").prompt(ctx)
		if not confirm:
			return await ctx.send("**Not inviting them, then!**")


		# Checks whether user is already in a tribe.
		user_currency = await self.get_user_currency(member.id)
		if not user_currency:
			return await ctx.send(f"**You cannot invite someone that doesn't have an account, {inviter.mention}!**")
		if user_currency[7] == 'default':
			return await ctx.send(f"**You cannot invite someone that doesn't have a Sloth Class, {inviter.mention}!**")
		if user_currency[18]:
			return await ctx.send(f"**You cannot invite someone that is already in a tribe, {inviter.mention}!**")


		custom_ctx = ctx
		custom_ctx.author = member
		invite = await ConfirmSkill(content=f"{member.mention}", msg=f"{inviter.mention} invited you to join their tribe called `{user_tribe['name']}`, do you wanna join?").prompt(custom_ctx)
		if invite:
			if not user_currency[18]:
				try:
					await self.update_someones_tribe(user_id=member.id, tribe_name=user_tribe['name'])
				except Exception as e:
					print(e)
					await ctx.send(f"**Something went wrong with it, {member.mention}, {inviter.mention}!**")
				else:
					join_tribe_embed = await self.get_join_tribe_embed(
						channel=ctx.channel, inviter=inviter, target=member, tribe=user_tribe)
					await ctx.send(embed=join_tribe_embed)
			else:
				await ctx.send(f"**You're already in a tribe, {member.mention}!**")
		else:
			await ctx.send(f"**{member.mention} refused your invitation to join `{user_tribe['name']}`, {inviter.mention}!**")

	@commands.command(aliases=['expel', 'kick_out', 'can_i_show_you_the_door?'])
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def kickout(self, ctx, member: discord.Member = None) -> None:
		""" Exepels someone from your tribe.
		:param member: The member to expel. """

		expeller = ctx.author
		user_tribe = await self.get_tribe_info_by_user_id(user_id=expeller.id)
		if not user_tribe['name']:
			return await ctx.send(f"**You don't have a tribe, {expeller.mention}**!")

		if not member:
			return await ctx.send(f"**Please, inform a member to invite to your tribe, {expeller.mention}!**")

		# if expeller.id == member.id:
		# 	return await ctx.send(f"**You cannot kick yourself out of your own tribe, {expeller.mention}!**")

		confirm = await ConfirmSkill(f"Are you sure you want to kick, {member.mention} to `{user_tribe['name']}`?").prompt(ctx)
		if not confirm:
			return await ctx.send("**Not inviting them, then!**")


		# Checks whether user is already in a tribe.
		user_currency = await self.get_user_currency(member.id)
		if not user_currency:
			return await ctx.send(f"**You cannot kick out someone that doesn't even have an account, {expeller.mention}!**")
		if user_currency[18] != user_tribe['name']:
			return await ctx.send(f"**You cannot kick out someone that is not in your tribe, {expeller.mention}!**")

		try:
			await self.update_someones_tribe(user_id=member.id, tribe_name=None)
		except Exception as e:
			print(e)
			await ctx.send(f"**Something went wrong with it, {expeller.mention}!**")
		else:
			await ctx.send(f"**You successfully kicked {member.mention} out of `{user_tribe['name']}`, {expeller.mention}!**")


	async def update_someones_tribe(self, user_id: int, tribe_name: str = None) -> None:
		""" Updates someone's tribe status.
		:param user_id: The ID of the user who's gonna be updated. 
		:param tribe_name: The name of the tribe the user is gonna be set to. (default = None) """

		mycursor, db = await the_database()
		await mycursor.execute("UPDATE UserCurrency SET tribe = %s WHERE user_id = %s", (tribe_name, user_id))
		await db.commit()
		await mycursor.close()


	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def create_table_user_tribe(self, ctx) -> None:
		""" (Owner) Creates the UserTribe table. """

		if await self.table_user_tribe_exists():
			return await ctx.send("**The `UserTribe` table already exists!**")

		mycursor, db = await the_database()
		await mycursor.execute("""
			CREATE TABLE UserTribe (
				user_id BIGINT NOT NULL, tribe_name VARCHAR(50) NOT NULL,
				tribe_description VARCHAR(200) NOT NULL, two_emojis VARCHAR(2) NOT NULL,
				tribe_thumbnail VARCHAR(200) DEFAULT NULL, tribe_form VARCHAR(100) DEFAULT NULL,
				slug VARCHAR(75) NOT NULL
			) DEFAULT CHARSET=utf8mb4""")
		await db.commit()
		await mycursor.close()
		await ctx.send("**Created `UserTribe` table!**")

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def drop_table_user_tribe(self, ctx) -> None:
		""" (Owner) Drops the UserTribe table. """

		if not await self.table_user_tribe_exists():
			return await ctx.send("**The `UserTribe` table doesn't exist!**")

		mycursor, db = await the_database()
		await mycursor.execute("DROP TABLE UserTribe")
		await db.commit()
		await mycursor.close()
		await ctx.send("**Dropped `UserTribe` table!**")

	@commands.command(hidden=True)
	@commands.has_permissions(administrator=True)
	async def reset_table_user_tribe(self, ctx) -> None:
		""" (Owner) Resets the UserTribe table. """

		if not await self.table_user_tribe_exists():
			return await ctx.send("**The `UserTribe` table doesn't exist yet!**")

		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM UserTribe")
		await db.commit()
		await mycursor.close()
		await ctx.send("**Reset `UserTribe` table!**")

	async def table_user_tribe_exists(self) -> bool:
		""" Checks whether the UserTribe table exists. """

		mycursor, db = await the_database()
		await mycursor.execute("SHOW TABLE STATUS LIKE 'UserTribe'")
		table_info = await mycursor.fetchall()
		await mycursor.close()
		if len(table_info) == 0:
			return False
		else:
			return True