import discord
from discord.ext import commands
from mysqldb2 import *
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import requests

shop_channels = [695975820744851507, 702911629725139074, 702911832150638684, 702914308677304330, 709000588792430602, 709038291453870080]
afk_channel_id = 581993624569643048
booster_role_id = 588752954266222602
level_badges = {'level_10': 10}

gauth = GoogleAuth()
# gauth.LocalWebserverAuth()
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    # This is what solved the issues:
    gauth.GetFlow()
    gauth.flow.params.update({'access_type': 'offline'})
    gauth.flow.params.update({'approval_prompt': 'force'})

    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:

    # Refresh them if expired
    gauth.Refresh()
else:

    # Initialize the saved creds
    gauth.Authorize()

# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")

drive = GoogleDrive(gauth)


class SlothCurrency(commands.Cog):
    '''
    Sloth Currency commands.
    '''

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("SlothCurrency cog is online!")
        await self.download_update()
        #await self.text_download_update()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not await self.check_table_exist():
            return

        user_info = await self.get_user_activity_info(message.author.id)
        if not user_info:
            return await self.insert_user_server_activity(message.author.id, 1)

        await self.update_user_server_messages(message.author.id, 1)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        if not await self.check_table_exist():
            return

        epoch = datetime.utcfromtimestamp(0)
        the_time = (datetime.utcnow() - epoch).total_seconds()

        user_info = await self.get_user_activity_info(member.id)
        if not user_info:
            return await self.insert_user_server_activity(member.id, 0, the_time)

        if not before.channel:
            return await self.update_user_server_timestamp(member.id, the_time)

        if not after.channel and not before.channel.id == afk_channel_id:
            old_time = user_info[0][3]
            addition = the_time - old_time
            await self.update_user_server_time(member.id, addition)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):        
        # Checks if it wasn't a bot's reaction
        if payload.member.bot:
            return
        
        # Takes off the reaction in the shop channel
        if payload.channel_id in shop_channels:
            guild = self.client.get_guild(payload.guild_id)
            channel = discord.utils.get(guild.channels, id=payload.channel_id)
        
            msg = await channel.fetch_message(payload.message_id)
            await msg.remove_reaction(payload.emoji.name, payload.member)        

        # Checks if it was a reaction within the shop's channel
        if not payload.channel_id in shop_channels:
            return

        epoch = datetime.utcfromtimestamp(0)
        the_time = (datetime.utcnow() - epoch).total_seconds()
        user = await self.get_user_currency(payload.user_id)
        if not user:
            await self.insert_user_currency(payload.user_id, the_time - 61)

        old_time = await self.get_user_currency(payload.member.id)
        if not the_time - old_time[0][2] >= 60:
            return await payload.member.send(
                f"**You're on a cooldown, try again in {round(60 - (the_time - old_time[0][2]))} seconds!**",
                delete_after=10)

        registered_items = await self.get_registered_items()
        for ri in registered_items:
            if ri[4] == payload.message_id:
                if str(payload.emoji) == ri[5]:
                    user_have_item = await self.check_user_have_item(payload.user_id, ri[2])
                    if user_have_item:
                        return await payload.member.send(
                            f"**You already have the item: __{ri[2]}__ in your inventory!**")
                    else:
                        return await self.try_to_buy_item(payload.user_id, ri[1], ri[2], ri[3], payload.guild_id,
                                                          the_time)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        member = discord.utils.get(self.client.get_guild(payload.guild_id).members, id=payload.user_id)
        if member.bot:
            return

    # In-game commands
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def react(self, ctx, mid: discord.Message = None, reaction=None):
        '''
        (ADM) Makes the bot react onto a message.
        :param mid: The message ID.
        :param reaction: The reaction to add.
        '''
        await ctx.message.delete()
        if not reaction:
            return await ctx.send("**Inform a reaction!**", delete_after=3)
        if not mid:
            return await ctx.send("**Inform a message id!**", delete_after=3)
        await mid.add_reaction(reaction)

    @commands.command()
    async def inventory(self, ctx, member: discord.Member = None):
        '''
        Shows the member's item inventory.
        :param member: The member to show.
        '''
        await ctx.message.delete()
        if not member:
            member = discord.utils.get(ctx.guild.members, id=ctx.author.id)

        user_items = await self.get_user_items(member.id)

        inventory = discord.Embed(title=f"{member.name}'s Inventory",
                                  description="All of your items gathered in one place.",
                                  colour=member.color, timestamp=ctx.message.created_at)
        inventory.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        inventory.set_thumbnail(url=member.avatar_url)
        for item in user_items:
            inventory.add_field(name=f"**{item[1]}**", value=f"**{item[2]}**", inline=True)
        return await ctx.send(embed=inventory)

    @commands.command()
    async def equip(self, ctx, *, item_name: str = None):
        '''
        Equips an item.
        :param item_name: The item to equip.
        '''
        await ctx.message.delete()
        if not item_name:
            return await ctx.send("**Inform an item to equip!**", delete_after=3)

        user_items = await self.get_user_items(ctx.author.id)
        for item in user_items:
            if str(item[1]) == item_name.title():
                if await self.check_user_can_equip(ctx.author.id, item_name.title()):
                    await self.update_user_item_info(ctx.author.id, item_name, 'equipped')
                    return await ctx.send(f"**{ctx.author.mention} equipped __{item_name.title()}__!**", delete_after=3)
                else:
                    return await ctx.send(f"**You already have a __{item[3]}__ item equipped!**", delete_after=3)
        else:
            return await ctx.send(f"**You don't have an item named __{item_name.title()}__!**", delete_after=3)

    @commands.command()
    async def unequip(self, ctx, *, item_name: str = None):
        '''
        Unequips an item.
        :param item_name: The item to unequip
        '''
        await ctx.message.delete()
        if not item_name:
            return await ctx.send("**Inform an item to unequip!**", delete_after=3)

        user_items = await self.get_user_items(ctx.author.id)
        for item in user_items:
            if item[1] == item_name.title():
                if await self.check_user_can_unequip(ctx.author.id, item_name.lower()):
                    await self.update_user_item_info(ctx.author.id, item_name.title(), 'unequipped')
                    return await ctx.send(f"**{ctx.author.mention} unequipped __{item_name.title()}__!**",
                                          delete_after=3)
                else:
                    return await ctx.send(f"**The item __{item_name}__ is already unequipped!**", delete_after=3)
        else:
            return await ctx.send(f"**You don't have an item named __{item_name.title()}__!**", delete_after=3)

    # Database commands
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_user_items(self, ctx):
        '''
        (ADM) Creates the UserItems table.
        '''
        await ctx.message.delete()
        mycursor, db = await the_data_base2()
        await mycursor.execute(
            "CREATE TABLE UserItems (user_id bigint, item_name VARCHAR(30), enable VARCHAR(10), item_type VARCHAR(10))")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table *UserItems* created!**", delete_after=3)

    @commands.has_permissions(administrator=True)
    @commands.command(hidden=True)
    async def drop_table_user_items(self, ctx):
        '''
        (ADM) Drops the UserItems table.
        '''
        await ctx.message.delete()
        mycursor, db = await the_data_base2()
        await mycursor.execute("DROP TABLE UserItems")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table *UserItems* dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_user_items(self, ctx):
        '''
        (ADM) Resets the UserItems table.
        '''
        await ctx.message.delete()
        mycursor, db = await the_data_base2()
        await mycursor.execute("DROP TABLE UserItems")
        await db.commit()
        await mycursor.execute(
            "CREATE TABLE UserItems (user_id bigint, item_name VARCHAR(30), enable VARCHAR(10), item_type VARCHAR(10))")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table *UserItems* reseted!**", delete_after=3)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_member(self, ctx, member: discord.Member = None, *, item_name: str = None):
        '''
        (ADM) Gives a member an item.
        :param member: The member to give the item.
        :param item_name: The name of the item.
        '''
        if not member:
            return await ctx.send("**Inform a member!**", delete_after=3)

        if not item_name:
            return await ctx.send("**Inform an item to add!**", delete_after=3)

        spec_item = await self.get_specific_register_item(item_name)
        if len(spec_item) == 0:
            return await ctx.send(f"**The item: __{item_name.title()}__ doesn't exist!**", delete_after=3)

        user_have_item = await self.get_user_specific_item(member.id, item_name)
        if len(user_have_item) == 0:
            await self.insert_user_item(member.id, item_name, 'unequipped', spec_item[0][1].lower())
            return await ctx.send(f"**{item_name.title()} given to {member.name}!**", delete_after=3)
        else:
            return await ctx.send(f"**{member.name} already have that item!**", delete_after=3)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def remove_member_item(self, ctx, member: discord.Member = None, *, item_name: str = None):
        '''
        (ADM) Removes an item from the member.
        :param member: The member to remove the item.
        :param item_name: The name of the item.
        '''
        if not member:
            return await ctx.send("**Inform a member!**", delete_after=3)

        if not item_name:
            return await ctx.send("**Inform an item to remove!**", delete_after=3)

        user_have_item = await self.get_user_specific_item(member.id, item_name)
        if len(user_have_item) != 0:
            await self.remove_user_item(member.id, item_name)
            return await ctx.send(f"**{item_name.title()} taken from {member.name}!**", delete_after=3)
        else:
            return await ctx.send(f"**{member.name} doesn't have that item!**", delete_after=3)

    async def insert_user_item(self, user_id: int, item_name: str, enable: str, item_type: str):
        mycursor, db = await the_data_base2()
        await mycursor.execute("INSERT INTO UserItems (user_id, item_name, enable, item_type) VALUES (%s, %s, %s, %s)",
                               (user_id, item_name.title(), enable, item_type.lower()))
        await db.commit()
        await mycursor.close()

    async def remove_user_item(self, user_id: int, item_name: str):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"DELETE FROM UserItems WHERE item_name = '{item_name}' and user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    async def update_user_item_info(self, user_id: int, item_name: str, enable: str):
        mycursor, db = await the_data_base2()
        await mycursor.execute(
            f"UPDATE UserItems SET enable = '{enable}' WHERE user_id = {user_id} and item_name = '{item_name}'")
        await db.commit()
        await mycursor.close()

    async def get_user_items(self, user_id: int):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"SELECT * FROM UserItems WHERE user_id = {user_id} ORDER BY user_id")
        item_system = await mycursor.fetchall()
        await mycursor.close()
        return item_system

    async def get_user_specific_type_item(self, user_id, item_type):
        mycursor, db = await the_data_base2()
        await mycursor.execute(
            f"SELECT * FROM UserItems WHERE user_id = {user_id} and item_type = '{item_type}' and enable = 'equipped'")
        spec_type_items = await mycursor.fetchall()
        if len(spec_type_items) != 0:
            registered_item = await self.get_specific_register_item(spec_type_items[0][1])
            return f'./sloth_custom_images/{item_type}/{registered_item[0][0]}'
        else:
            default_item = f'./sloth_custom_images/{item_type}/base_{item_type}.png'
            return default_item

    async def check_user_can_equip(self, user_id, item_name: str):
        mycursor, db = await the_data_base2()
        item_type = await self.get_specific_register_item(item_name)
        await mycursor.execute(
            f"SELECT * FROM UserItems WHERE user_id = {user_id} and item_type = '{item_type[0][1]}' and enable = 'equipped'")
        equipped_item = await mycursor.fetchall()

        if len(equipped_item) != 0 and len(item_type) != 0:
            return False
        else:
            return True

    async def check_user_can_unequip(self, user_id, item_name: str):
        mycursor, db = await the_data_base2()
        await mycursor.execute(
            f"SELECT * FROM UserItems WHERE user_id = {user_id} and item_name = '{item_name.lower()}' and enable = 'unequipped'")
        unequipped_item = await mycursor.fetchall()
        await mycursor.close()

        if len(unequipped_item) != 0:
            return False
        else:
            return True

    async def get_user_specific_item(self, user_id: int, item_name: str):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"SELECT * FROM UserItems WHERE user_id = {user_id} and item_name = '{item_name}'")
        item_system = await mycursor.fetchall()
        await mycursor.close()
        return item_system

    # Register Items
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_register_items(self, ctx):
        '''
        (ADM) Creates the RegisteredItems table.
        '''
        await ctx.message.delete()
        mycursor, db = await the_data_base2()
        await mycursor.execute(
            "CREATE TABLE RegisteredItems (image_name VARCHAR(50),item_type VARCHAR(10), item_name VARCHAR(30), item_price int, message_ref bigint, reaction_ref VARCHAR(50))")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table *RegisteredItems* created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_register_items(self, ctx):
        '''
        (ADM) Drops the RegisteredItems table.
        '''
        await ctx.message.delete()
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"DROP TABLE RegisteredItems")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table *RegisteredItems* dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_register_items(self, ctx):
        '''
        (ADM) Resets the RegisteredItems table.
        '''
        await ctx.message.delete()
        mycursor, db = await the_data_base2()
        await mycursor.execute("DROP TABLE RegisteredItems")
        await db.commit()
        await mycursor.execute(
            "CREATE TABLE RegisteredItems (image_name VARCHAR(50),item_type VARCHAR(10), item_name VARCHAR(30), item_price int, message_ref bigint, reaction_ref VARCHAR(50))")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table *RegisteredItems* reseted!**", delete_after=3)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def show_registered(self, ctx):
        '''
        (ADM) Shows all the registered items in the shop.
        '''
        await ctx.message.delete()
        mycursor, db = await the_data_base2()
        await mycursor.execute("SELECT * FROM RegisteredItems")
        registered_items = await mycursor.fetchall()
        await mycursor.close()
        embed = discord.Embed(title="Registered Items", description="All registered items and their info",
                              colour=discord.Colour.dark_green(), timestamp=ctx.message.created_at)
        for ri in registered_items:
            embed.add_field(name=f"{ri[2]}",
                            value=f"**File:** {ri[0]} | **Type:** {ri[1]} | **Price:** {ri[3]}łł | **Reaction:** {ri[5]} |**Message ID:** {ri[4]}",
                            inline=False)
        return await ctx.send(embed=embed)

    async def get_registered_items(self):
        mycursor, db = await the_data_base2()
        await mycursor.execute("SELECT * FROM RegisteredItems")
        registered_items = await mycursor.fetchall()
        await mycursor.close()
        return registered_items

    async def get_specific_register_item(self, item_name: str):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"SELECT * FROM RegisteredItems WHERE item_name = '{item_name}'")
        item = await mycursor.fetchall()
        await mycursor.close()
        return item

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def remove_registered_item(self, ctx, *, item_name: str = None):
        '''
        (ADM) Removes a registered item from the shop system.
        :param item_name: The name of the item to remove.
        '''
        await ctx.message.delete()
        if not item_name:
            return await ctx.send("**Inform an item name!**", delete_after=3)

        have_spec_item = await self.get_specific_register_item(item_name.title())
        if len(have_spec_item) != 0:
            await self.delete_registered_item(item_name.title())
            return await ctx.send(f"**{item_name.title()} deleted from the system!**", delete_after=3)
        else:
            return await ctx.send("**Item not found in the system!**", delete_after=3)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def register_item(self, ctx, mid: discord.Message = None, reactf=None, image_name: str = None, item_type: str = None, item_price: int = None, *, item_name: str = None):
        '''
        (ADM) Registers an item to the sloth shop.
        :param mid: The message ID of the image from which people will buy the item.
        :param reactf: The reaction that will trigger the buying process of that item.
        :param image_name: The name of the image item that will be shown in the user's inventory.
        :param item_type: The type of item; head, hand, body, bg...
        :param item_price: The price of the item
        :param item_name: The origin name of the image item that is in the system.
        '''

        # print(reactf)
        if not mid:
            return await ctx.send("**Specify the message id!**", delete_after=3)
        elif not reactf:
            if not len(reactf) <= 50:
                return await ctx.send("**Specify a shorter reaction!** (max=50)", delete_after=3)
            else:
                return await ctx.send("**Specify the reaction!**", delete_after=3)
        elif not image_name:
            if not len(item_name) <= 50:
                return await ctx.send("**Specify a shorter item name! (max=50)**", delete_after=3)
            else:
                return await ctx.send("**Specify the image name!**", delete_after=3)
        elif not item_type:
            if not len(item_type) <= 10:
                return await ctx.send("**Specify a shorter item type name!**", delete_after=3)
            else:
                return await ctx.send("**Specify the item type!**", delete_after=3)

        elif not item_price:
            return await ctx.send("**Specify the item price!**", delete_after=3)
        elif not item_name:
            if not len(item_name) <= 30:
                return await ctx.send("**Specify a shorter item name! (max=30)**", delete_after=3)
            else:
                return await ctx.send("**Specify the item name!**", delete_after=3)

        await self.insert_registered_item(mid.id, reactf, image_name, item_type, item_price, item_name)
        await mid.add_reaction(reactf)
        return await ctx.send(f"**Item __{item_name.title()}__ successfully registered!**", delete_after=3)

    async def insert_registered_item(self, mid: int, reactf, image_name: str, item_type: str, item_price: int,
                                     item_name: str):
        mycursor, db = await the_data_base2()
        await mycursor.execute(
            "INSERT INTO RegisteredItems (image_name, item_type, item_name, item_price, message_ref, reaction_ref) VALUES (%s, %s, %s, %s, %s, %s)",
            (image_name, item_type.lower(), item_name.title(), item_price, mid, reactf))
        await db.commit()
        await mycursor.close()

    async def delete_registered_item(self, item_name: str):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"DELETE FROM RegisteredItems WHERE item_name = '{item_name}'")
        await db.commit()
        await mycursor.close()

    async def check_user_have_item(self, user_id: int, item_name: str):

        user_items = await self.get_user_specific_item(user_id, item_name)
        # print(user_items)
        if user_items:
            return True
        else:
            return False

    # Table UserCurrency
    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_user_currency(self, ctx):
        '''
        (ADM) Creates the UserCurrency table.
        '''
        await ctx.message.delete()
        mycursor, db = await the_data_base2()
        await mycursor.execute("CREATE TABLE UserCurrency (user_id bigint, user_money bigint, last_purchase_ts bigint, user_classes bigint default 0, user_class_reward bigint default 0, user_hosted bigint default 0, user_lotto bigint default null)")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table *UserCurrency* created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_user_currency(self, ctx):
        '''
        (ADM) Drops the UserCurrency table.
        '''
        await ctx.message.delete()
        mycursor, db = await the_data_base2()
        await mycursor.execute("DROP TABLE UserCurrency")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table *UserCurrency* dropped!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_user_currency(self, ctx):
        '''
        (ADM) Resets the UserCurrency table.
        '''
        await ctx.message.delete()
        mycursor, db = await the_data_base2()
        await mycursor.execute("DROP TABLE UserCurrency")
        await db.commit()
        await mycursor.execute("CREATE TABLE UserCurrency (user_id bigint, user_money bigint, last_purchase_ts bigint, user_classes bigint default 0, user_class_reward bigint default 0, user_hosted bigint default 0, user_lotto bigint default null)")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table *UserCurrency* reseted!**", delete_after=3)


    @commands.command()
    async def profile(self, ctx, member: discord.Member = None):
        '''
        Shows the member's profile with their custom sloth.
        :param member: The member to see the profile. (Optional)
        '''
        await ctx.message.delete()
        if not member:
            member = ctx.author

        user_info = await self.get_user_currency(member.id)
        if not user_info:
            if ctx.author.id == member.id:
                epoch = datetime.utcfromtimestamp(0)
                the_time = (datetime.utcnow() - epoch).total_seconds()
                await self.insert_user_currency(member.id, the_time - 61)
                user_info = await self.get_user_currency(member.id)
            else:
                return await ctx.send(f"**{member} doesn't have a profile yet!**", delete_after=3)

        small = ImageFont.truetype("built titling sb.ttf", 45)
        background = Image.open(await self.get_user_specific_type_item(member.id, 'background'))
        sloth = Image.open(await self.get_user_specific_type_item(member.id, 'sloth'))
        body = Image.open(await self.get_user_specific_type_item(member.id, 'body'))
        hand = Image.open(await self.get_user_specific_type_item(member.id, 'hand'))
        foot = Image.open(await self.get_user_specific_type_item(member.id, 'foot'))
        head = Image.open(await self.get_user_specific_type_item(member.id, 'head'))
        hud = Image.open(await self.get_user_specific_type_item(member.id, 'hud'))
        #badge = Image.open(await self.get_user_specific_type_item(member.id, 'badge'))
        pfp = await self.get_user_pfp(member)
        background.paste(sloth, (0, 0), sloth)
        background.paste(body, (0, 0), body)
        background.paste(head, (0, 0), head)
        background.paste(foot, (0, 0), foot)
        background.paste(hand, (0, 0), hand)
        background.paste(hud, (0, 0), hud)
        #background.paste(badge, (1, -10), badge)
        # Checks if user is a booster
        booster_role = discord.utils.get(ctx.guild.roles, id=booster_role_id)
        if booster_role in member.roles:
            badge2 = Image.open("sloth_custom_images/badge/nitroboost.png")
            background.paste(badge2, (10, 5), badge2)

        # Checks if the user has a level badge
        user_level = await self.get_specific_user(member.id)
        for key, value in reversed(list(level_badges.items())):
            if user_level[0][2] >= value:
                level_badge = Image.open(f"sloth_custom_images/badge/{key}.png")
                background.paste(level_badge, (65, 5), level_badge)
                break
        else:
            pass

        # Tries to print the user's profile picture
        try:
            background.paste(pfp, (201, 2), pfp)
        except Exception:
            pass

        draw = ImageDraw.Draw(background)
        draw.text((310, 5), f"{member}", (255, 255, 255), font=small)
        draw.text((80, 525), f"{user_info[0][1]}", (255, 255, 255), font=small)
        background.save('profile.png', 'png', quality=90)
        return await ctx.send(file=discord.File('profile.png'))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_money(self, ctx, member: discord.Member = None, money: int = None):
        '''
        (ADM) Adds money to a member.
        :param member: The member to add money to.
        :param money: The amount of money to add.
        '''
        if not member:
            return await ctx.send("**Inform a member!**", delete_after=3)
        elif not money:
            return await ctx.send("**Inform an amount of money!**", delete_after=3)

        await self.update_user_money(member.id, money)
        return await ctx.send(f"**{money} added to {member.name}'s bank account!**", delete_after=5)

    async def get_user_currency(self, user_id: int):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"SELECT * FROM UserCurrency WHERE user_id = {user_id}")
        user_currency = await mycursor.fetchall()
        await mycursor.close()
        return user_currency

    async def try_to_buy_item(self, user_id: int, item_type: str, item_name: str, to_pay: int, guild_id: int,
                              the_time: int):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"SELECT * FROM UserCurrency WHERE user_id = {user_id}")
        user_info = await mycursor.fetchall()
        member = discord.utils.get(self.client.get_guild(guild_id).members, id=user_id)
        if user_info[0][1] >= to_pay:
            await self.insert_user_item(user_id, item_name, 'unequipped', item_type)
            await self.update_user_money(user_id, - to_pay)
            await self.update_user_purchase_ts(member.id, the_time)
            shop_embed = discord.Embed(title="Shop Communication",
                                       description=f"**You just bought a __{item_name}__!**",
                                       colour=discord.Color.green(), timestamp=datetime.utcnow())
            await member.send(embed=shop_embed)
        else:
            shop_embed = discord.Embed(title="Shop Communication",
                                       description=f"**You don't have money for that! You need more `{to_pay - user_info[0][1]}łł` in order to buy it!**",
                                       colour=discord.Color.green(), timestamp=datetime.utcnow())
            return await member.send(embed=shop_embed)

    async def insert_user_currency(self, user_id: int, the_time: int):
        mycursor, db = await the_data_base2()
        await mycursor.execute("INSERT INTO UserCurrency (user_id, user_money, last_purchase_ts) VALUES (%s, %s, %s)",
                               (user_id, 0, the_time))
        await db.commit()
        await mycursor.close()

    async def update_user_money(self, user_id: int, money: int):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"UPDATE UserCurrency SET user_money = user_money + {money} WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    async def update_user_purchase_ts(self, user_id: int, the_time: int):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"UPDATE UserCurrency SET last_purchase_ts = {the_time} WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    async def update_user_lotto_ts(self, user_id: int, the_time: int):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"UPDATE UserCurrency SET user_lotto = {the_time} WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    # Google Drive commands
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def download_update(self, ctx=None):
        '''
        (ADM) Downloads all shop images from the Google Drive.
        '''
        if ctx:
            await ctx.message.delete()
        '''
        Downloads all shop images from the GoogleDrive and stores in the bot's folder
        :param ctx:
        :return:
        '''
        all_folders = {"background": "1V8l391o3-vsF9H2Jv24lDmy8e2erlHyI",
                       "sloth": "16DB_lNrnrmvxu2E7RGu01rQGQk7z-zRy",
                       "body": "1jYvG3vhL32-A0qDYn6lEG6fk_GKYDXD7",
                       "hand": "1ggW3SDVzTSY5b8ybPimCsRWGSCaOBM8d",
                       "hud": "1-U6oOphdMNMPhPAjRJxJ2E6KIzIbewEh",
                       "badge": "1k8NRfwwLzIY5ALK5bUObAcrKr_eUlfjd",
                       "foot": "1Frfra1tQ49dKM6Dg4DIbrfYbtXadv9zj",
                       "head": "1Y9kSOayw4NDehbqfmvPXKZLrXnIjeblP"
                       }

        categories = ['background', 'sloth', 'body', 'hand', 'hud', 'badge', 'foot', 'head']
        for category in categories:
            try:
                os.makedirs(f'./sloth_custom_images/{category}')
                print(f"{category} folder made!")
            except FileExistsError:
                pass

        for folder, folder_id in all_folders.items():
            files = drive.ListFile({'q': "'%s' in parents and trashed=false" % folder_id}).GetList()
            download_path = f'./sloth_custom_images/{folder}'
            for file in files:
                isFile = os.path.isfile(f"{download_path}/{file['title']}")
                # print(isFile)
                if not isFile:
                    # print(f"\033[34mItem name:\033[m \033[33m{file['title']:<35}\033[m | \033[34mID: \033[m\033[33m{file['id']}\033[m")
                    output_file = os.path.join(download_path, file['title'])
                    temp_file = drive.CreateFile({'id': file['id']})
                    temp_file.GetContentFile(output_file)
                    # print(f"File '{file['title']}' downloaded!")

        if ctx:
            return await ctx.send("**Download update is done!**", delete_after=5)

    # Google Drive commands
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def text_download_update(self, ctx=None):
        '''
        (ADM) Downloads all texts from the GoogleDrive and stores in the bot's folder
        '''
        if ctx:
            await ctx.message.delete()
        all_text_folders = {"turkic": "1A9rKufw30sJMdDbOa7zzobV2vblxc0UP",
                            "uralic": "1lFOmnjSNE1zfxabjai5xQSgqOrjo3h0t",
                            "unafiliated": "1bjYU4-oTRhnMDLiboCCkQecQ64FVx39C",
                            "iranian": "18kvxdgyAWbNA9oEpzxGVkEF0JiSPSj4U",
                            "celtic": "1djjTF6UrXWHI5-q7B_juqmtNvRC7-Rvf",
                            "baltic": "15crfEoB-LQSavwVgU7elO-BqqvtrGO-W",
                            "germanic": "1szJMzbF7hRk7BwicUTSi-_lnvlDVt99j",
                            "slavic": "1ntr2NclwgQjhULH9wwrnRSezdsyvG3g2",
                            "random": "1_gBiliWPrCj5cLpChQfg9QRnj8skQVHM",
                            "asian": "1xXJLWXD3l31gpfKaC1oBLGaX5EMVFZ3u",
                            "semitic": "12TKyqHLNhY4VohFWpgN6FjtPQPGNuuNK",
                            "romance": "1n-E6RbHnAm9jzavnN50txHj3Qezz0T1Y",
                            "indian": "1k1xv0uDgfxBhVOOgCiTK0GVbJ_Oz6OtC"
                            }

        text_categories = ["turkic", "uralic", "unafiliated", "iranian", "celtic", "baltic", "germanic", "slavic",
                           "random", "asian", "semitic", "romance", "indian"]
        for t_category in text_categories:
            try:
                os.makedirs(f'./texts/{t_category}')
                print(f"{t_category} folder made!")
            except FileExistsError:
                pass

        for folder, folder_id in all_text_folders.items():
            files = drive.ListFile({'q': "'%s' in parents and trashed=false" % folder_id}).GetList()
            download_path = f'./texts/{folder}'
            for file in files:
                isFile = os.path.isfile(f"{download_path}/{file['title']}")
                if not isFile:
                    output_file = os.path.join(download_path, file['title'])
                    temp_file = drive.CreateFile({'id': file['id']})
                    temp_file.GetContentFile(output_file)
        if ctx:
            return await ctx.send("**Download update is done!**")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def list_folder(self, ctx, image_suffix: str = None, item_name: str = None):
        '''
        (ADM) Lists a shop image folder from Google Drive.
        :param image_suffix: The image/folder category.

        '''
        await ctx.message.delete()
        all_folders = {"background": "1V8l391o3-vsF9H2Jv24lDmy8e2erlHyI",
                       "sloth": "16DB_lNrnrmvxu2E7RGu01rQGQk7z-zRy",
                       "body": "1jYvG3vhL32-A0qDYn6lEG6fk_GKYDXD7",
                       "hand": "1ggW3SDVzTSY5b8ybPimCsRWGSCaOBM8d",
                       "hud": "1-U6oOphdMNMPhPAjRJxJ2E6KIzIbewEh",
                       "badge": "1k8NRfwwLzIY5ALK5bUObAcrKr_eUlfjd",
                       "foot": "1Frfra1tQ49dKM6Dg4DIbrfYbtXadv9zj",
                       "head": "1Y9kSOayw4NDehbqfmvPXKZLrXnIjeblP"}

        if not image_suffix:
            for folder, folder_id in all_folders.items():
                files = drive.ListFile({'q': "'%s' in parents and trashed=false" % folder_id}).GetList()
                print(f"\033[35mCategory:\033[m {folder}")
                for file in files:
                    print(
                        f"\033[34mItem name:\033[m \033[33m{file['title']:<35}\033[m | \033[34mID: \033[m\033[33m{file['id']}\033[m")
        else:

            for key, item in all_folders.items():
                if image_suffix == key:
                    embed = discord.Embed(title=f"Category: {image_suffix}", colour=discord.Colour.dark_green(),
                                          timestamp=ctx.message.created_at)
                    files = drive.ListFile({'q': "'%s' in parents and trashed=false" % item}).GetList()
                    print(f"\033[35mCategory:\033[m {image_suffix}")
                    for file in files:
                        embed.add_field(name=f"Name: {file['title']}", value=f"ID: {file['id']}", inline=False)
                        print(
                            f"\033[34mItem name:\033[m \033[33m{file['title']:<35}\033[m | \033[34mID: \033[m\033[33m{file['id']}\033[m")
                    return await ctx.send(embed=embed)
            else:
                return await ctx.send("**Category not found!**", delete_after=3)

    # UserServerActivity

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_server_activity(self, ctx):
        '''
        (ADM) Creates the UserServerActivity table.
        '''
        await ctx.message.delete()
        mycursor, db = await the_data_base2()
        await mycursor.execute(
            "CREATE TABLE UserServerActivity (user_id bigint, user_messages bigint, user_time bigint, user_timestamp bigint DEFAULT NULL)")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table *UserServerActivity* created!**", delete_after=3)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_server_activity(self, ctx):
        '''
        (ADM) Drops the UserServerActivity table.
        '''
        await ctx.message.delete()
        mycursor, db = await the_data_base2()
        await mycursor.execute("DROP TABLE UserServerActivity")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table *UserServerActivity* dropped!**", delete_after=3)

    async def insert_user_server_activity(self, user_id: int, add_msg: int, new_ts: int = None):
        mycursor, db = await the_data_base2()
        await mycursor.execute(
            "INSERT INTO UserServerActivity (user_id, user_messages, user_time, user_timestamp) VALUES (%s, %s, %s, %s)",
            (user_id, add_msg, 0, new_ts))
        await db.commit()
        await mycursor.close()

    async def get_user_activity_info(self, user_id: int):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"SELECT * FROM UserServerActivity WHERE user_id = {user_id}")
        user_info = await mycursor.fetchall()
        await mycursor.close()
        return user_info

    async def update_user_server_messages(self, user_id: int, add_msg: int):
        mycursor, db = await the_data_base2()
        await mycursor.execute(
            f"UPDATE UserServerActivity SET user_messages = user_messages + {add_msg} WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    async def update_user_server_time(self, user_id: int, add_time: int):
        mycursor, db = await the_data_base2()
        await mycursor.execute(
            f"UPDATE UserServerActivity SET user_time = user_time + {add_time} WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()

    async def update_user_server_timestamp(self, user_id: int, new_ts: int):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"UPDATE UserServerActivity SET user_timestamp = {new_ts} WHERE user_id = {user_id}")
        await db.commit()
        await mycursor.close()


    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_server_activity(self, ctx):
        '''
        (ADM) Resets the UserServerActivity table.
        '''
        await ctx.message.delete()
        mycursor, db = await the_data_base2()
        await mycursor.execute("DROP TABLE UserServerActivity")
        await db.commit()
        await mycursor.execute(
            "CREATE TABLE UserServerActivity (user_id bigint, user_messages bigint, user_time bigint, user_timestamp bigint DEFAULT NULL)")
        await db.commit()
        await mycursor.close()
        return await ctx.send("**Table *UserServerActivity* reseted!**", delete_after=3)

    @commands.command()
    async def status(self, ctx, member: discord.Member = None):
        '''
        Shows the member's time and message status.
        :param member: The member to show the status. (Optional)
        '''
        await ctx.message.delete()
        if not member:
            member = ctx.author

        if not await self.check_table_exist():
            return await ctx.send("**It looks like this command is on maintenance!**", delete_after=3)

        user_info = await self.get_user_activity_info(member.id)
        if not user_info and member.id == ctx.author.id:
            # await self.insert_user_server_activity(member.id, 1)
            return self.status(ctx, member)
        elif not user_info and not member.id == ctx.author.id:
            return await ctx.send("**Member not found in the system!**", delete_after=3)

        m, s = divmod(user_info[0][2], 60)
        h, m = divmod(m, 60)
        embed = discord.Embed(title=f"{member.name}'s Status", colour=member.color,
                              timestamp=ctx.message.created_at)
        embed.add_field(name=f"__**Messages sent:**__", value=f"{user_info[0][1]}", inline=False)
        embed.add_field(name=f"__**Time spent on voice channels:**__",
                        value=f"{h:d} hours, {m:02d} minutes and {s:02d} seconds", inline=False)
        embed.set_thumbnail(url=member.avatar_url)
        return await ctx.send(embed=embed)

    async def check_table_exist(self):
        mycursor, db = await the_data_base2()
        await mycursor.execute(f"SHOW TABLE STATUS LIKE 'UserServerActivity'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False

        else:
            return True

    @commands.command()
    async def exchange(self, ctx):
        '''
        Exchange your status into leaves (łł)
        '''
        await ctx.message.delete()
        user_info = await self.get_user_activity_info(ctx.author.id)
        if not user_info:
            return await ctx.send("**You have nothing to exchange!**", delete_after=3)
        user_found = await self.get_user_currency(ctx.author.id)
        if not user_found:
            epoch = datetime.utcfromtimestamp(0)
            the_time = (datetime.utcnow() - epoch).total_seconds()
            await self.insert_user_currency(ctx.author.id, the_time - 61)

        user_message = user_info[0][1]
        user_time = user_info[0][2]
        member_id = ctx.author.id
        cmsg, message_times = self.convert_messages(member_id, user_message)
        ctime, time_times = self.convert_time(member_id, user_time)


        await self.update_user_server_messages(member_id, -message_times * 50)
        await self.update_user_money(member_id, cmsg)

        await self.update_user_server_time(member_id, -time_times * 1800)
        await self.update_user_money(member_id, ctime)


        embed = discord.Embed(title="Exchange", colour=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_author(name=ctx.author, url=ctx.author.avatar_url)
        if not cmsg == ctime == 0:
            if cmsg > 0:
                embed.add_field(name="__**Messages:**__",
                                value=f"Exchanged `{message_times * 50}` messages for `{cmsg}`łł;", inline=False)
            if ctime > 0:
                embed.add_field(name="__**Time:**__",
                                value=f"Exchanged `{(time_times * 1800) / 60}` minutes for `{ctime}`łł;", inline=False)
            return await ctx.send(embed=embed)
        else:
            return await ctx.send("**You have nothing to exchange!**", delete_after=3)

    def convert_messages(self, member_id, user_message: int, money: int = 0, times: int = 0):
        messages_left = user_message
        exchanged_money = money
        while True:
            if user_message >= 50:
                times += 1
                messages_left -= 50
                exchanged_money += 3
                #return await self.convert_messages(member_id, messages_left, exchanged_money, times)
            else:
                #await self.update_user_server_messages(member_id, -times * 50)
                #await self.update_user_money(member_id, exchanged_money)
                return exchanged_money, times

    def convert_time(self, member_id, user_time: int, money: int = 0, times: int = 0):
        time_left = user_time
        exchanged_money = money
        while True:
            if time_left >= 1800:
                times += 1
                time_left -= 1800
                exchanged_money += 3
                #return await self.convert_time(member_id, time_left, exchanged_money, times)
            else:
                #await self.update_user_server_time(member_id, -times * 1800)
                #await self.update_user_money(member_id, exchanged_money)
                return exchanged_money, times

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_message(self, ctx, member: discord.Member = None, add_message: int= None):
        '''
        (ADM) Adds messages to the member's status.
        :param member: The member to add the messages to.
        :param add_message: The amount of messages to add.
        '''
        if not add_message:
            return await ctx.send(f"**Inform an amount of messages to add!**", delete_after=3)
        if not member:
            member = ctx.author
        await self.update_user_server_messages(member.id, add_message)
        return await ctx.send(f"Added {add_message} messages to {member}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_time(self, ctx, member: discord.Member = None, add_time: int = None):
        '''
        (ADM) Adds time to the member's status.
        :param member: The member to add time to.
        :param add_time: The amount of time to add. (in secs)
        '''
        if not add_time:
            return await ctx.send(f"**Inform an amount of seconds to add!**", delete_after=3)
        if not member:
            member = ctx.author
        await self.update_user_server_time(member.id, add_time)
        return await ctx.send(f"Added {add_time} seconds to {member}")

    @commands.command()
    async def transfer(self, ctx, member: discord.Member = None, money: int = None):
        '''
        Transfers money from one member to another member.
        :param member: The member to transfer the money to.
        :param money: The amount of money to transfer.
        '''
        if not member:
            return await ctx.send('**Inform the member!**', delete_after=3)
        elif member.id == ctx.author.id:
            return await ctx.send("**You can't transfer money to yourself!**", delete_after=3)
        elif not money:
            return await ctx.send('**Inform the amount of money to trasnfer!**', delete_after=3)
        elif not int(money) > 0:
            return await ctx.send('**Inform value bigger than 0!**', delete_after=3)

        the_user = await self.get_user_currency(ctx.author.id)
        target_user = await self.get_user_currency(member.id)
        if not the_user:
            return await ctx.send("**You don't have a bank account yet, type z!bank to open your account!**", delete_after=10)
        elif not target_user:
            return await ctx.send(f"**{member} does not have a bank account yet!**", delete_after=5)

        if the_user[0][1] >= int(money):
            await self.update_user_money(member.id, money)
            await self.update_user_money(ctx.author.id, -money)
            await ctx.send(f"**{ctx.author.mention} transferred {money}łł to {member.mention}!**")
        else:
            await ctx.send(f"You don't have {money}łł!")

    async def get_user_pfp(self, member):
        im = Image.open(requests.get(member.avatar_url, stream=True).raw)

        thumb_width = 59

        def crop_center(pil_img, crop_width, crop_height):
            img_width, img_height = pil_img.size
            return pil_img.crop(((img_width - crop_width) // 2,
                                 (img_height - crop_height) // 2,
                                 (img_width + crop_width) // 2,
                                 (img_height + crop_height) // 2))

        def crop_max_square(pil_img):
            return crop_center(pil_img, min(pil_img.size), min(pil_img.size))

        def mask_circle_transparent(pil_img, blur_radius, offset=0):
            offset = blur_radius * 2 + offset
            mask = Image.new("L", pil_img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)

            result = pil_img.copy()
            result.putalpha(mask)

            return result

        im_square = crop_max_square(im).resize((thumb_width, thumb_width), Image.LANCZOS)
        im_thumb = mask_circle_transparent(im_square, 4)
        #im_thumb.save('png/user_pfp.png', 'png', quality=90)
        return im_thumb
    
    async def get_specific_user(self, user_id: int):
        mycursor, db = await the_data_base3()
        await mycursor.execute(f"SELECT * FROM MembersScore WHERE user_id = {user_id}")
        member = await mycursor.fetchall()
        await mycursor.close()
        return member

def setup(client):
    client.add_cog(SlothCurrency(client))
