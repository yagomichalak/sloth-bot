import discord
from discord.ext import commands
from typing import Any, List, Union, Dict
from mysqldb import the_database
import asyncio
from datetime import datetime
import os

allowed_roles = [int(os.getenv('OWNER_ROLE_ID')), int(os.getenv('ADMIN_ROLE_ID')), int(os.getenv('MOD_ROLE_ID'))]

class EmbedManagement(commands.Cog):
	""" A category for managing embeds; show, create, delete and edit. """

	def __init__(self, client) -> None:
		"""" Class initializing method. """

		self.client = client

	@commands.Cog.listener()
	async def on_ready(self) -> None:
		""" Tells when the cog is ready to use. """
		print("EmbedManagement cog is online!")


	# Database methods
	async def insert_embed(self, embed_name: str) -> None:
		""" Inserts an embed from the DB. 
		:param embed_name: The name of the embed to insert.
		"""

		mycursor, db = await the_database()
		await mycursor.execute("INSERT INTO EmbedNames VALUES (%s)", (embed_name,))
		await db.commit()
		await mycursor.close()

	async def delete_embed(self, embed_name: str) -> None:
		""" Deletes an embed from the DB. 
		:param embed_name: The name of the embed to delete.
		"""

		fields = [
			"EmbedAuthor", "EmbedTitle",
			"EmbedDescription", "EmbedThumbnail",
			"EmbedImage", "EmbedColor",
			"EmbedFooter", "EmbedTimestamp",
			"EmbedFields"
		]

		mycursor, db = await the_database()
		await mycursor.execute("DELETE FROM EmbedNames WHERE embed_name = %s", (embed_name,))
		for field in fields:
			sql = "DELETE FROM " + field + " WHERE embed_name = %s"
			await mycursor.execute(sql, (embed_name,))
		await db.commit()
		await mycursor.close()


	async def delete_text_field(self, embed_name: str, field_index: int) -> bool:
		""" Deletes a text field from the DB.
		:param embed_name: The name of the embed which the field is gonna be deleted
		:param field_index: The index of the text field that is gonna be deleted from the embed. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT * FROM EmbedFields WHERE embed_name = %s", (embed_name,))
		fields = await mycursor.fetchall()
		try:
			the_field = fields[field_index-1]
			sql = "DELETE FROM EmbedFields WHERE embed_name = %s AND field_name = %s AND field_value = %s"
			await mycursor.execute(sql, (embed_name, the_field[1], the_field[2]))
			await db.commit()
		except:
			await mycursor.close()
			return False
		else:
			await mycursor.close()
			return True 

	async def delete_field(self, embed_name: str, field_name: str) -> None:
		""" Deletes a field from the DB.
		:param embed_name: The name of the embed which the field is gonna be deleted
		:param field_name: The field that is gonna be deleted from the embed. """

		mycursor, db = await the_database()
		sql = "DELETE FROM " + field_name + " WHERE embed_name = %s"
		await mycursor.execute(sql, (embed_name,))
		await db.commit()
		await mycursor.close()

	async def get_embed_names(self) -> List[str]:
		""" Gets all embed names from the DB. """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT embed_name FROM EmbedNames")
		embeds_list: List[str] = await mycursor.fetchall()
		await mycursor.close()
		return embeds_list

	async def get_embed_fields(self, embed_name: str) -> Dict[str, Union[None, List[str]]]:
		""" Get all embed fields from the DB if there are any. 
		:param embed_name: The name of the embed from which to get the fields. """

		fields = {
			"EmbedAuthor": None,
			"EmbedTitle": None,
			"EmbedDescription": None,
			"EmbedThumbnail": None,
			"EmbedImage": None,
			"EmbedColor": None,
			"EmbedFooter": None,
			"EmbedTimestamp": None,
			"EmbedFields": None
		}

		mycursor, db = await the_database()
		for field in fields:
			sql = "SELECT * FROM "+ field + " WHERE embed_name = %s"
			await mycursor.execute(sql, (embed_name,))
			field_data: List[str] = await mycursor.fetchall()
			fields[field] = field_data[:]

		await mycursor.close()
		return fields

	async def embed_exists(self, embed_name: str) -> bool:
		""" Checks if embed exists in the DB. 
		:param embed_name: The name of embed which . """

		mycursor, db = await the_database()
		await mycursor.execute("SELECT embed_name FROM EmbedNames WHERE embed_name = %s", (embed_name,))
		exists = await mycursor.fetchone()
		await mycursor.close()
		if exists:
			return True
		else:
			return False

	# In-Discord methods / commands

	@commands.group()
	@commands.has_any_role(*allowed_roles)
	async def embed(self, ctx) -> None:
		""" Embeds a message."""

		if ctx.invoked_subcommand:
			return

		cmd = self.client.get_command('embed')
		prefix = self.client.command_prefix
		subcommands = [f"{prefix}{c.qualified_name}" for c in cmd.commands
			  ]

		subcommands = '\n'.join(subcommands)
		embed = discord.Embed(
		  title="Subcommads",
		  description=f"```apache\n{subcommands}```",
		  color=ctx.author.color,
		  timestamp=ctx.message.created_at
		)
		await ctx.send(embed=embed)

	# Subcommands (Tier 2)

	@embed.group()
	async def show(self, ctx, embed_name: str = None) -> None:
		""" Shows an embed. 
		:param embed_name: The name of the embed that you want to show. """

		if not embed_name:
			embeds_list: List[str] = await self.get_embed_names()

			embed = discord.Embed(
				title="__Available Embeds__",
				color=ctx.author.color,
				timestamp=ctx.message.created_at
			)

			if embeds_list:
				new_list: List[str] = []
				for lst in embeds_list:
					new_list.append(lst[0])
				values = '\n'.join(new_list)
				embed.description=f"```apache\n{values}```**Example usage:** `{self.client.command_prefix}embed show embed_name`"

			else:
				embed.description = "**No embeds were created yet!**"

			return await ctx.send(embed=embed, content=f"**Inform an embed name, {ctx.author.mention}!**")

		#try to get embed_name from db (check if exists)
		#
		if len(embed_name) > 30:
			return await ctx.send(f"**The `embed_name` must be within 1-30 characters, {ctx.author.mention}!**")

		if not await self.embed_exists(embed_name):
			return await ctx.send(f"**Embed `{embed_name}` doesn't exist, {ctx.author.mention}!**")

		unsorted_embed = await self.get_embed_fields(embed_name)
		if unsorted_embed:
			sorted_embed_obj = SortEmbed(unsorted_embed)
			sorted_embed = await sorted_embed_obj.sort_embed_fields()
			await ctx.send(embed=sorted_embed)
		else:
			return await ctx.send(f"**Embed `{embed_name}` doesn't exist, {ctx.author.mention}!**")

	@embed.group()
	@commands.has_permissions(administrator=True)
	async def create(self, ctx, embed_name: str = None) -> None:
		""" Creates an embed in the DB. 
		:param embed_name: The name of the embed. """

		if not embed_name:
			return await ctx.send(f"**Inform an embed name, {ctx.author.mention}!**")

		if len(embed_name) > 30:
			return await ctx.send(f"**The `embed_name` must be within 1-30 characters, {ctx.author.mention}!**")

		if await self.embed_exists(embed_name):
			return await ctx.send(f"**Embed `{embed_name}` already exists, {ctx.author.mention}!**")

		confirmation = await self.reaction_confirmation(ctx=ctx, member=ctx.author, value=embed_name)

		if confirmation:
			# Adds value into DB
			await self.insert_embed(embed_name)
			await ctx.send(f"**`{embed_name}` added into database!**")

	@embed.group()
	@commands.has_permissions(administrator=True)
	async def delete(self, ctx, embed_name: str =  None, field: str = None) -> None:
		""" Deletes a field from the DB.
		:param embed_name: The name of the embed that is gonna be deleted a field or entirely.
		:param field: The name of the field. """

		member = ctx.author

		options = {
			'author': 'EmbedAuthor', 'description': 'EmbedDescription',
			'footer': 'EmbedFooter', 'thumbnail': 'EmbedThumbnail',
			'image': 'EmbedImage', 'timestamp': 'EmbedTimestamp',
			'color': 'EmbedColor', 'title': 'EmbedTitle',
			'field': 'EmbedFields', 'all': 'EmbedNames'
		}

		embed = discord.Embed(
				title="Available options",
				description=f"""```apache\n{', '.join(list(options.keys()))}```""",
				color=member.color,
				timestamp=ctx.message.created_at
			)
		embed.set_footer(text="ALL -> deletes the embed", icon_url=ctx.guild.icon_url)

		if not embed_name:
			return await ctx.send(f"**Please, inform an `embed_name` to remove something from, {member.mention}!**")

		if len(embed_name) > 30:
			return await ctx.send(f"**Please, inform a `embed_name` witihin 1-30 characters, {member.mention}!**")

		if not field:
			return await ctx.send(f"**Inform a field name, {member.mention}!**", embed=embed)

		if field.lower() not in list(options.keys()):
			return await ctx.send(
				f"**Please, write a `field` that is in the available options, {member.mention}!**",
				embed=embed
			)

		if not await self.embed_exists(embed_name):
			return await ctx.send(f"**Embed `{embed_name}` doesn't exist, {member.mention}!**")

		field_index = None
		# prompts user for which field that they want to delete
		if field.lower() == 'field':
			field_index = await self.prompt_index(ctx, member)
			if not field_index: return

		confirmation = await self.reaction_confirmation(ctx=ctx, member=member, value=field)

		if confirmation:
			# Deletes value from DB.
			if field.lower() == 'all':
				await self.delete_embed(embed_name.lower())
			elif field.lower() == 'field':
				deleted = await self.delete_text_field(embed_name, field_index)
				if not deleted: 
					return await ctx.send("**I couldn't delete this index, are you sure it exists?**")
			else:
				await self.delete_field(embed_name, options[field.lower()])

			await ctx.send(f"**`{field}` deleted from database!**")

	@embed.group()
	@commands.has_permissions(administrator=True)
	async def edit(self, ctx) -> None:	
		""" Edits an embed in the DB. """

		if ctx.invoked_subcommand:
			return

		cmd = self.client.get_command('embed edit')
		prefix = self.client.command_prefix
		subcommands = [f"{prefix}{c.qualified_name}" for c in cmd.commands
			  ]

		subcommands = '\n'.join(subcommands)
		embed = discord.Embed(
		  title="Subcommads",
		  description=f"```apache\n{subcommands}```",
		  color=ctx.author.color,
		  timestamp=ctx.message.created_at
		)
		await ctx.send(embed=embed)


	# SubcomMands (Tier 3)
	@edit.command()
	async def author(self, ctx, embed_name: str = None, name: str = None, icon_link: str = None) -> None:
		
		""" Sets the author for the given saved embed. 
		:param embed_name: The name of the embed to insert.
		:param name: The author name.
		:param icon_link: The author's icon link.
		"""

		member = ctx.author

		if not embed_name:
			return await ctx.send(f"**Please, inform an `embed_name` to put the values in, {member.mention}!**")

		if len(embed_name) > 30:
			return await ctx.send(f"**Please, inform a `embed_name` witihin 1-30 characters, {member.mention}!**")

		if not name:
			return await ctx.send(f"**Please, inform a `name` for the author field, {member.mention}!**")

		if len(name) > 30:
			return await ctx.send(f"**Please, inform a `name` witihin 1-30 characters, {member.mention}!**")

		if not icon_link:
			return await ctx.send(f"**Please, inform an `icon_url` for the author field, {member.mention}!**")

		if len(icon_link) > 200:
			return await ctx.send(f"**Please, inform an `icon_link` witihin 1-30 characters, {member.mention}!**")

		if not await self.embed_exists(embed_name):
			return await ctx.send(f"**Embed `{embed_name}` doesn't exist, {member.mention}!**")

		confirmation = await self.reaction_confirmation(ctx, member, ', '.join([name, icon_link]))
		if not confirmation:
			return

		mycursor, db = await the_database()
		await mycursor.execute("SELECT embed_name from EmbedAuthor WHERE embed_name = %s", (embed_name,))
		exists = await mycursor.fetchall()

		if exists:
			await mycursor.execute("UPDATE EmbedAuthor SET name = %s, icon_link = %s WHERE embed_name = %s", (name, icon_link, embed_name))
			await db.commit()
			await mycursor.close()
			await ctx.send(f"**Updated `author` for {embed_name}!**")
		else:
			await mycursor.execute("INSERT INTO EmbedAuthor (embed_name, name, icon_link) VALUES (%s, %s, %s)", (embed_name, name, icon_link))
			await db.commit()
			await mycursor.close()
			await ctx.send(f"**Inserted `author` for {embed_name}!**")

	@edit.command()
	async def title(self, ctx, embed_name: str = None, *, title: str = None) -> None:
		""" Sets the title for the given saved embed. 
		:param embed_name: The name of the embed to insert.
		:param title: The embed title.
		"""

		member = ctx.author

		if not embed_name:
			return await ctx.send(f"**Please, inform an `embed_name` to put the values in, {member.mention}!**")

		if len(embed_name) > 30:
			return await ctx.send(f"**Please, inform a `embed_name` witihin 1-30 characters, {member.mention}!**")

		if not title:
			return await ctx.send(f"**Please, inform a `title` for the embed, {member.mention}!**")

		if len(title) > 30:
			return await ctx.send(f"**Please, inform a `title` witihin 1-30 characters, {member.mention}!**")

		if not await self.embed_exists(embed_name):
			return await ctx.send(f"**Embed `{embed_name}` doesn't exist, {member.mention}!**")

		confirmation = await self.reaction_confirmation(ctx, member, title.title())
		if not confirmation:
			return

		mycursor, db = await the_database()
		await mycursor.execute("SELECT embed_name from EmbedTitle WHERE embed_name = %s", (embed_name))
		exists = await mycursor.fetchall()

		if exists:
			await mycursor.execute("UPDATE EmbedTitle SET title = %s WHERE embed_name = %s", (title, embed_name))
			await db.commit()
			await mycursor.close()
			await ctx.send(f"**Updated `title` for {embed_name}!**")
		else:
			await mycursor.execute("INSERT INTO EmbedTitle (embed_name, title) VALUES (%s, %s)", (embed_name, title.title()))
			await db.commit()
			await mycursor.close()
			await ctx.send(f"**Inserted `title` for {embed_name}!**")

	@edit.command()
	async def description(self, ctx, embed_name: str = None, *, description_text: str = None) -> None:
		""" Sets the description for the given saved embed. 
		:param embed_name: The name of the embed to insert.
		:param description_text: The embed description.
		"""

		member = ctx.author

		if not embed_name:
			return await ctx.send(f"**Please, inform an `embed_name` to put the values in, {member.mention}!**")

		if len(embed_name) > 30:
			return await ctx.send(f"**Please, inform a `embed_name` witihin 1-30 characters, {member.mention}!**")

		if not description_text:
			return await ctx.send(f"**Please, inform a `description_text` for the embed, {member.mention}!**")

		if len(description_text) > 500:
			return await ctx.send(f"**Please, inform a `description_text` witihin 1-500 characters, {member.mention}!**")

		if not await self.embed_exists(embed_name):
			return await ctx.send(f"**Embed `{embed_name}` doesn't exist, {member.mention}!**")

		confirmation = await self.reaction_confirmation(ctx, member, description_text)
		if not confirmation:
			return

		mycursor, db = await the_database()
		await mycursor.execute("SELECT embed_name from EmbedDescription WHERE embed_name = %s", (embed_name,))
		exists = await mycursor.fetchall()
		if exists:
			await mycursor.execute("UPDATE EmbedDescription SET description_text = %s WHERE embed_name = %s", (description_text, embed_name))
			await db.commit()
			await mycursor.close()
			await ctx.send(f"**Updated `description` for {embed_name}!**")
		else:
			await mycursor.execute("INSERT INTO EmbedDescription (embed_name, description_text) VALUES (%s, %s)", (embed_name, description_text))
			await db.commit()
			await mycursor.close()
			await ctx.send(f"**Inserted `description` for {embed_name}!**")

	@edit.command()
	async def thumbnail(self, ctx, embed_name: str = None, icon_link: str =  None) -> None:
		""" Sets the thumbnail for the given saved embed. 
		:param embed_name: The name of the embed to insert.
		:param icon_link: The icon link for the thumbnail.
		"""

		member = ctx.author

		if not embed_name:
			return await ctx.send(f"**Please, inform an `embed_name` to put the values in, {member.mention}!**")

		if len(embed_name) > 30:
			return await ctx.send(f"**Please, inform a `embed_name` witihin 1-30 characters, {member.mention}!**")

		if not icon_link:
			return await ctx.send(f"**Please, inform a `icon_link` for the thumbnail field, {member.mention}!**")

		if len(icon_link) > 200:
			return await ctx.send(f"**Please, inform a `icon_link` witihin 1-200 characters, {member.mention}!**")

		if not await self.embed_exists(embed_name):
			return await ctx.send(f"**Embed `{embed_name}` doesn't exist, {member.mention}!**")

		confirmation = await self.reaction_confirmation(ctx, member, icon_link)
		if not confirmation:
			return

		mycursor, db = await the_database()
		await mycursor.execute("SELECT embed_name FROM EmbedThumbnail WHERE embed_name = %s", (embed_name,))

		exists = await mycursor.fetchall()
		if exists:
			await mycursor.execute("UPDATE EmbedThumbnail SET icon_link = %s WHERE embed_name = %s", (icon_link, embed_name))
			await db.commit()
			await mycursor.close()
			await ctx.send(f"**Updated `thumbnail` for {embed_name}!**")
		else:
			await mycursor.execute("INSERT INTO EmbedThumbnail (embed_name, icon_link) VALUES (%s, %s)", (embed_name, icon_link))
			await db.commit()
			await mycursor.close()
			await ctx.send(f"**Inserted `thumbnail` for {embed_name}!**")

	@edit.command()
	async def image(self, ctx, embed_name: str = None, image_link: str = None) -> None:
		""" Sets the image for the given saved embed. 
		:param embed_name: The name of the embed to insert.
		:param image_link: The embed image.
		"""

		member = ctx.author

		if not embed_name:
			return await ctx.send(f"**Please, inform an `embed_name` to put the values in, {member.mention}!**")

		if len(embed_name) > 30:
			return await ctx.send(f"**Please, inform a `embed_name` witihin 1-30 characters, {member.mention}!**")

		if not image_link:
			return await ctx.send(f"**Please, inform a `image_link` for the image field, {member.mention}!**")

		if len(image_link) > 200:
			return await ctx.send(f"**Please, inform a `image_link` witihin 1-200 characters, {member.mention}!**")

		if not await self.embed_exists(embed_name):
			return await ctx.send(f"**Embed `{embed_name}` doesn't exist, {member.mention}!**")

		confirmation = await self.reaction_confirmation(ctx, member, image_link)
		if not confirmation:
			return

		mycursor, db = await the_database()
		await mycursor.execute("SELECT embed_name FROM EmbedImage WHERE embed_name = %s", (embed_name,))
		exists = await mycursor.fetchall()
		if exists:
			await mycursor.execute("UPDATE EmbedImage SET image_link = %s WHERE embed_name = %s", (image_link, embed_name))
			await db.commit()
			await mycursor.close()
			await ctx.send(f"**Updated `image` for {embed_name}!**")
		else:
			await mycursor.execute("INSERT INTO EmbedImage (embed_name, image_link) VALUES (%s, %s)", (embed_name, image_link))
			await db.commit()
			await mycursor.close()
			await ctx.send(f"**Inserted `image` for {embed_name}!**")

	@edit.command()
	async def color(self, ctx, embed_name: str = None, hex_color: str = None) -> None:
		""" Sets the color for the given saved embed. 
		:param embed_name: The name of the embed to insert.
		:param hex_color: The embed color.
		"""

		member = ctx.author

		if not embed_name:
			return await ctx.send(f"**Please, inform an `embed_name` to put the values in, {member.mention}!**")

		if len(embed_name) > 30:
			return await ctx.send(f"**Please, inform a `embed_name` witihin 1-30 characters, {member.mention}!**")

		if not hex_color:
			return await ctx.send(f"**Please, inform a `hex_color` for the author field, {member.mention}!**")

		if len(hex_color) > 7:
			return await ctx.send(f"**Please, inform a `hex_color` witihin 1-7 characters, {member.mention}!**")

		if not await self.embed_exists(embed_name):
			return await ctx.send(f"**Embed `{embed_name}` doesn't exist, {member.mention}!**")

		confirmation = await self.reaction_confirmation(ctx, member, hex_color)
		if not confirmation:
			return

		mycursor, db = await the_database()
		await mycursor.execute("SELECT embed_name from EmbedColor WHERE embed_name = %s", (embed_name,))
		exists = await mycursor.fetchall()
		if exists:
			await mycursor.execute("UPDATE EmbedColor SET hex_color = %s WHERE embed_name = %s", (hex_color, embed_name))
			await db.commit()
			await mycursor.close()
			await ctx.send(f"**Updated `color` for {embed_name}!**")
		else:
			await mycursor.execute("INSERT INTO EmbedColor (embed_name, hex_color) VALUES (%s, %s)", (embed_name, hex_color))
			await db.commit()
			await mycursor.close()
			await ctx.send(f"**Inserted `color` for {embed_name}!**")

	@edit.command()
	async def footer(self, ctx, embed_name: str = None, icon_link: str = None, *, text: str = None) -> None:
		""" Sets the footer for the given saved embed. 
		:param embed_name: The name of the embed to insert.
		:param icon_link: The link for the footer icon.
		:param text: The text for the footer.
		"""

		member = ctx.author

		if not embed_name:
			return await ctx.send(f"**Please, inform an `embed_name` to put the values in, {member.mention}!**")

		if len(embed_name) > 30:
			return await ctx.send(f"**Please, inform a `embed_name` witihin 1-30 characters, {member.mention}!**")

		if not icon_link:
			return await ctx.send(f"**Please, inform a `icon_link` for the footer field, {member.mention}!**")

		if len(icon_link) > 200:
			return await ctx.send(f"**Please, inform a `icon_link` witihin 1-200 characters, {member.mention}!**")

		if not text:
			return await ctx.send(f"**Please, inform a `text` for the footer field, {member.mention}!**")

		if len(text) > 30:
			return await ctx.send(f"**Please, inform a `text` witihin 1-30 characters, {member.mention}!**")

		if not await self.embed_exists(embed_name):
			return await ctx.send(f"**Embed `{embed_name}` doesn't exist, {member.mention}!**")

		confirmation = await self.reaction_confirmation(ctx, member, ', '.join([icon_link, text]))
		if not confirmation:
			return

		mycursor, db = await the_database()
		await mycursor.execute("SELECT embed_name FROM EmbedFooter WHERE embed_name = %s", (embed_name,))
		exists = await mycursor.fetchall()
		if exists:
			await mycursor.execute("UPDATE EmbedFooter SET text = %s, icon_link = %s WHERE embed_name = %s", (text, icon_link, embed_name))
			await db.commit()
			await mycursor.close()
			await ctx.send(f"**Updated `footer` for {embed_name}!**")
		else:
			await mycursor.execute("INSERT INTO EmbedFooter (embed_name, text, icon_link) VALUES (%s, %s, %s)", (embed_name, text, icon_link))
			await db.commit()
			await mycursor.close()
			await ctx.send(f"**Inserted `footer` for {embed_name}!**")

	@edit.command()
	async def timestamp(self, ctx, embed_name: str = None, yes_no: str = None) -> None:
		""" Sets the timestamp for the given saved embed. 
		:param embed_name: The name of the embed to insert.
		:param yes_no: If you want the embed to have a timestamp.
		"""

		member = ctx.author

		if not embed_name:
			return await ctx.send(f"**Please, inform an `embed_name` to put the values in, {member.mention}!**")

		if len(embed_name) > 30:
			return await ctx.send(f"**Please, inform a `embed_name` witihin 1-30 characters, {member.mention}!**")

		if not yes_no:
			return await ctx.send(f"**Please, inform a `yes_no` for the footer field, {member.mention}!**")

		if yes_no.lower() not in ['yes', 'no']:
			return await ctx.send(f"**Please, answer either `yes` or `no`, {member.mention}!**")

		if not await self.embed_exists(embed_name):
			return await ctx.send(f"**Embed `{embed_name}` doesn't exist, {member.mention}!**")


		confirmation = await self.reaction_confirmation(ctx, member, yes_no.title())

		if not confirmation:
			return

		mycursor, db = await the_database()
		await mycursor.execute("SELECT embed_name FROM EmbedTimestamp WHERE embed_name = %s", (embed_name,))
		exists = await mycursor.fetchall()
		if exists:
			await mycursor.execute("UPDATE EmbedTimestamp SET yes_no = %s WHERE embed_name = %s", (yes_no, embed_name))
			await db.commit()
			await mycursor.close()
			await ctx.send(f"**Inserted `image` for {embed_name}!**")
		else:
			await mycursor.execute("INSERT INTO EmbedTimestamp (embed_name, yes_no) VALUES (%s, %s)", (embed_name, yes_no.lower()))
			await db.commit()
			await mycursor.close()
			await ctx.send(f"**Inserted `image` for {embed_name}!**")

	@edit.command()
	async def field(self, ctx, embed_name: str = None, field_name: str =  None, field_value: str = None, field_inline: str = 'no') -> None:
		""" Inserts a text field for the given saved embed. 
		:param embed_name: The name of the embed.
		:param field_name: The embed's field name.
		:param field_value: The embed's field value.
		:param field_inline: Whether the embed will be inline or not (yes/no).
		"""

		member = ctx.author

		if not embed_name:
			return await ctx.send(f"**Please, inform an `embed_name` to put the values in, {member.mention}!**")

		if len(embed_name) > 30:
			return await ctx.send(f"**Please, inform a `embed_name` witihin 1-30 characters, {member.mention}!**")

		if not field_name:
			return await ctx.send(f"**Please, inform a `field_name` for the embed, {member.mention}!**")

		if len(field_name) > 50:
			return await ctx.send(f"**Please, inform a `field_name` witihin 1-50 characters, {member.mention}!**")

		if not field_value:
			return await ctx.send(f"**Please, inform a `field_value` for the embed, {member.mention}!**")

		if len(field_value) > 500:
			return await ctx.send(f"**Please, inform a `field_value` witihin 1-500 characters, {member.mention}!**")

		if not field_inline:
			return await ctx.send(f"**Please, inform a `field_inline` for the text field, {member.mention}!**")

		if field_inline.lower() not in ['yes', 'no']:
			return await ctx.send(f"**Please, answer either `yes` or `no`, {member.mention}!**")

		if not await self.embed_exists(embed_name):
			return await ctx.send(f"**Embed `{embed_name}` doesn't exist, {member.mention}!**")

		confirmation = await self.reaction_confirmation(ctx, member, f"Name: {field_name} | Value: {field_value}")
		if not confirmation:
			return
		mycursor, db = await the_database()
		await mycursor.execute("""
			INSERT INTO EmbedFields (embed_name, field_name, field_value, field_inline) 
			VALUES (%s, %s, %s, %s)""", (embed_name, field_name, field_value, field_inline))
		await db.commit()
		await mycursor.close()
		await ctx.send(f"**Inserted `text_field` for {embed_name}!**")


	# Prompts
	async def prompt_index(self, ctx: commands.Context, member: discord.Member) -> Union[int, None]:
		""" Prompts the user for an index.
		:param ctx: The context.
		:param member: The member that is gonna be prompted. """


		def check(m) -> bool:
			if m.author.id == member.id and msg.channel.id == ctx.channel.id:
				if len(m.content.strip()) <= 2:
					if m.content.strip().isdigit():
						if int(m.content.strip()) > 0 and int(m.content.strip()) <= 25:
							return True
						else:
							self.client.loop.create_task(ctx.send(f"**The index has to be between 1-25, {member.mention}!**"))	
							return False
					else:
						self.client.loop.create_task(ctx.send(f"**The index `MUST` be an integer value, {member.mention}!**"))	
						return False
				else:
					self.client.loop.create_task(ctx.send(f"**The index can have a maximum lenght of 2, {member.mention}!**"))
					return False

			else:
				return False


		msg = await ctx.send(f"**Inform the index of the text field that you want to delete, {member.mention}. (It starts at 1)**")

		try:
			m = await self.client.wait_for('message', timeout=60, check=check)
			content = m.content
		except asyncio.TimeoutError:
			await msg.edit(content="**Timeout!**")
			return None
		else:
			return int(content)


	# Confirmation
	async def reaction_confirmation(self, ctx: commands.Context, member: discord.Member, value: str) -> bool:
		""" Prompts the user confirmation for something. """
		try:
			embed = discord.Embed(
				title="__Confirmation__",
				description=f"{member.mention}, do you confirm this action to be done to `{value}`?",
				color=discord.Color.orange(),
				timestamp=ctx.message.created_at,
				)
			msg = await ctx.send(embed=embed)
			embed.set_footer(text="60 seconds to answer!", icon_url=member.guild.icon_url)

			await msg.add_reaction('✅')
			await msg.add_reaction('❌')

			r, _ = await self.client.wait_for('reaction_add', timeout=60,
				check=lambda r, u: r.message.id == msg.id and u.id == member.id and \
				str(r.emoji) in ['✅', '❌']
			)
		except asyncio.TimeoutError:
			embed.title="__Confirmatiou timed-out!__"
			embed.description = '',
			color=discord.Color.red()
			await msg.edit(embed=embed)
			return False

		else:
			emoji = str(r.emoji)
			if emoji == '✅':
				embed.title = "__Successfully confirmed!__"
				embed.description = f"Action to the value `{value}` has been confirmed!"
				embed.color=discord.Color.green()
				await msg.edit(embed=embed)
				return True
			elif emoji == '❌':
				embed.title="Refused!__"
				embed.description = f"Action to the value `{value}` has not been confirmed!"
				embed.color=discord.Color.red()
				await msg.edit(embed=embed)
				return False

	@commands.command()
	async def embed_info(self, ctx) -> None:
		""" Shows an embedded message containing a description of the embed system. """

		def read_text() -> str:
			# print(__name__)
			# print(__file__)
			with open('./texts/embed_system.txt', 'r') as f:
				lines = f.read()
				return lines

		embed = discord.Embed(
			title="__Information about the embed system.__",
			description=read_text(),
			color=ctx.author.color,
			timestamp=ctx.message.created_at
		)
		embed.set_image(
			url="https://cdn.discordapp.com/attachments/777886760721055781/779817191675133972/unknown.png"
		)
		embed.set_footer(text="Example embed above")
		await ctx.send(embed=embed)

class SortEmbed:
	""" A class for sorting embed fields with the given data. """

	def __init__(self, fields: Dict[str, List[str]]) -> None:
		""" Class initializing method. 
		:param fields: A dictionary containing data that needs to be sorted. """

		self.fields = fields


	async def sort_embed_fields(self) -> discord.Embed:
		""" Sorts all fields in order to form an embed. """

		# Initial embed
		embed = discord.Embed()

		# Tries to add each fields one by one

		if author := self.fields.get('EmbedAuthor'):
			embed = await self.sort_embed_author(embed, author)
		if color := self.fields.get('EmbedColor'):
			embed = await self.sort_embed_color(embed, color)
		if description := self.fields.get('EmbedDescription'):
			embed = await self.sort_embed_description(embed, description)
		if footer := self.fields.get('EmbedFooter'):
			embed = await self.sort_embed_footer(embed, footer)
		if image := self.fields.get('EmbedImage'):
			embed = await self.sort_embed_image(embed, image)
		if thumbnail := self.fields.get('EmbedThumbnail'):
			embed = await self.sort_embed_thumbnail(embed, thumbnail)
		if timestamp := self.fields.get('EmbedTimestamp'):
			embed = await self.sort_embed_timestamp(embed, timestamp)
		if title := self.fields.get('EmbedTitle'):
			embed = await self.sort_embed_title(embed, title)
		if fields := self.fields.get('EmbedFields'):
			embed = await self.sort_embed_text_fields(embed, fields)

		# Returns the embed containing the available fields
		return embed

	async def sort_embed_author(self, embed: discord.Embed, values: List[str]) -> discord.Embed:
		""" Sorts the embed author. 
		:param values: The list of values to sort from. """

		try:
			embed.set_author(
				name=values[0][1],
				icon_url=values[0][2]
			)
		except:
			pass
		finally:
			return embed

	async def sort_embed_color(self, embed: discord.Member, values: List[str]) -> discord.Embed:
		""" Sorts the embed color. 
		:param values: The list of values to sort from. """

		try:
			color = values[0][1].replace('#', '')
			embed.color = discord.Color(value=int(color, 16))
		except:
			pass
		finally:
			return embed

	async def sort_embed_description(self, embed: discord.Member, values: List[str]) -> discord.Embed:
		""" Sorts the embed description. 
		:param values: The list of values to sort from. """

		try:
			embed.description = values[0][1]
		except:
			pass
		finally:
			return embed

	async def sort_embed_footer(self, embed: discord.Member, values: List[str]) -> discord.Embed:
		""" Sorts the embed footer. 
		:param values: The list of values to sort from. """

		try:
			embed.set_footer(
				text=values[0][1],
				icon_url=values[0][2],
			)
		except:
			pass
		finally:
			return embed

	async def sort_embed_image(self, embed: discord.Member, values: List[str]) -> discord.Embed:
		""" Sorts the embed image. 
		:param values: The list of values to sort from. """

		try:
			embed.set_image(
				url=values[0][1]
			)
		except:
			pass
		finally:
			return embed

	async def sort_embed_thumbnail(self, embed: discord.Member, values: List[str]) -> discord.Embed:
		""" Sorts the embed thumbnail. 
		:param values: The list of values to sort from. """

		try:
			embed.set_thumbnail(
				url=values[0][1]
			)
		except:
			pass
		finally:
			return embed

	async def sort_embed_timestamp(self, embed: discord.Member, values: List[str]) -> discord.Embed:
		""" Sorts the embed timestamp. 
		:param values: The list of values to sort from. """

		try:
			if values[0][1] == 'yes':
				embed.timestamp=datetime.utcnow()
		except:
			pass
		finally:
			return embed

	async def sort_embed_title(self, embed: discord.Member, values: List[str]) -> discord.Embed:
		""" Sorts the embed title. 
		:param values: The list of values to sort from. """

		try:
			embed.title=values[0][1]
		except:
			pass
		finally:
			return embed


	async def sort_embed_text_fields(self, embed: discord.Member, values: List[List[str]]) -> discord.Embed:
		""" Sorts the embed fields. 
		:param values: The list of values to sort from. """

		for field in values:
			try:
				embed.add_field(
					name=field[1],
					value=field[2],
					inline=True if field[3].lower() == 'yes' else False
				)
			except:
				pass

		return embed

def setup(client) -> None:
	""" Cog's setup function. """

	client.add_cog(EmbedManagement(client))