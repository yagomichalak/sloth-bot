import discord
from discord.ext import commands
from pprint import pprint
from typing import List, Any, Union, Tuple, Dict
import asyncio
from random import randint

class Game(commands.Cog):
	""" A category for a simple embedded message game. """

	def __init__(self, client) -> None:
		""""""

		self.client = client


	@commands.Cog.listener()
	async def on_ready(self) -> None:
		print("Game cog is online!")


	async def make_game_square(self, inserted: Dict[str, Tuple[int]], columns: int, rows: int, player_x: int, player_y: int, update: bool = False) -> str:
		""" Makes a game square with emojis. """

		emoji = '\u2B1B'
		# emoji = ':black_large_square:'
		
		simple_square = [[emoji for __ in range(columns)] for _ in range(rows)]
		# pprint(square)
		square = await self.make_square_border(simple_square, emoji, player_x, player_y)
		square, new_inserted = await self.put_objects(square, inserted, player_x, player_y, columns, rows, update)
		return square, new_inserted

	async def make_square_border(self, square: List[List[str]], emoji: str, player_x: int, player_y: int) -> List[List[str]]:
		""" Makes a border for the given square. """		

		blue = ':blue_square:'

		new_list = []
		for i, row in enumerate(square):
			# print(i, row.replace())
			if i == 0 or i == len(square) - 1:
				new_row = []
				for column in row:
					column = blue
					new_row.append(column)
					# square[i].replace(emoji, blue)
				new_list.append(new_row)
			else:
				new_row = row
				new_row[0] = blue
				new_row[-1] = blue
				new_list.append(new_row)


		return new_list

	async def put_objects(self, square: List[List[str]], inserted: Dict[str, Tuple[int]], player_x: int, player_y: int, columns: int, rows: int, update: bool) -> List[List[str]]:
		""" Puts all objects into the game square field. 
		:param square: The game square field. """

		# List of inserted items

		# Puts player
		player = '🐸'
		x = player_x
		y = player_y
		inserted['player'] = (x, y, player)
		
		if update:
			# Puts item
			square, item_tuple = await self.insert_item(square, columns, rows, inserted)
			inserted['item'] = item_tuple

			# Puts destiny
			square, destiny_tuple = await self.insert_destiny(square, columns, rows, inserted)
			inserted['destiny'] = destiny_tuple

		for values in inserted.values():
			x, y, emoji = values
			square[y][x] = emoji


		return square, inserted

	async def insert_item(self, square: List[List[str]], columns, rows, inserted: Dict[str, Tuple[int]]) -> Dict[str, Tuple[int]]:
		""""""

		item = '🍫'

		while True:
			rand_x = randint(1, columns-2)
			rand_y = randint(1, rows-2)
			if (rand_x, rand_y) not in inserted.values():
				square[rand_y][rand_x] = item
				return square, (rand_x, rand_y, item)



	async def insert_destiny(self, square: List[List[str]], columns, rows, inserted: Dict[str, Tuple[int]]) -> Dict[str, Tuple[int]]:
		""""""

		destiny = '👩'

		while True:
			rand_x = randint(1, columns-2)
			rand_y = randint(1, rows-2)
			if (rand_x, rand_y) not in inserted.values():
				square[rand_y][rand_x] = destiny
				return square, (rand_x, rand_y, destiny)


	@commands.command()
	@commands.cooldown(1, 3600, commands.BucketType.user)
	async def start(self, ctx) -> None:
		""" Starts the game. """

		member = ctx.author

		embed = discord.Embed(
			title="Gra",
			color=discord.Color.blue(),
			timestamp=ctx.message.created_at
		)

		columns, rows = 13, 9
		x, y = 6, 4
		inserted: Dict[str, Tuple[int]] = {'player': (x, y)}
		square, inserted = await self.make_game_square(inserted=inserted, columns=columns, rows=rows, player_x=x, player_y=y, update=True)

		msg = await ctx.send(embed=discord.Embed(title="**Opening game...**"))
		await asyncio.sleep(0.5)
		await msg.add_reaction('⬅️')
		await msg.add_reaction('➡️')
		await msg.add_reaction('⬇️')
		await msg.add_reaction('⬆️')

		while True:

			square = '\n'.join(map(lambda r: ''.join(r), square))
			embed.description=square
			await msg.edit(embed=embed)
			try:
				r, u = await self.client.wait_for('reaction_add', timeout=60,
					check=lambda r, u: u.id == member.id and r.message.id == msg.id \
					and str(r.emoji) in ['⬅️', '➡️', '⬇️', '⬆️']
				)
			except asyncio.TimeoutError:
				await msg.remove_reaction('⬅️', self.client.user)
				await msg.remove_reaction('➡️', self.client.user)
				await msg.remove_reaction('⬇️', self.client.user)
				await msg.remove_reaction('⬆️', self.client.user)
				embed.title += ' (Timeout)'
				embed.color = discord.Color.red()
				self.client.get_command('start').reset_cooldown(ctx)
				return await msg.edit(embed=embed)
			else:
				emj = str(r.emoji)

				if emj == '⬅️':
					await msg.remove_reaction(r, u)
					if x - 1 > 0:
						x -= 1
				elif emj == '➡️':
					await msg.remove_reaction(r, u)
					if x + 1 < columns - 1:
						x += 1
				elif emj == '⬇️':
					await msg.remove_reaction(r, u)
					if y + 1 < rows -1:
						y += 1

				elif emj == '⬆️':
					await msg.remove_reaction(r, u)
					if y - 1 > 0:
						y -= 1

				square, inserted = await self.make_game_square(inserted=inserted, columns=columns, rows=rows, player_x=x, player_y=y)


def setup(client) -> None:
	client.add_cog(Game(client))