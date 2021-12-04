import discord
from discord.app.commands import slash_command, Option
from discord.ext import commands, menus
from discord.member import VoiceState
from discord.utils import escape_mentions
from mysqldb import *
from external_cons import the_drive
from PIL import Image, ImageDraw, ImageFont
import os

import shutil
import asyncio
import aiohttp
from io import BytesIO
import glob
from itertools import cycle

from extra.menu import InventoryLoop
from typing import List, Dict, Tuple, Union, Optional

from extra.slothclasses.player import Player
from extra.useful_variables import level_badges, flag_badges
from extra.gif_manager import GIF
from extra import utils

from extra.currency.useritems import UserItemsTable
from extra.currency.userserveractivity import UserServerActivityTable, UserVoiceSystem
from extra.currency.usercurrency import UserCurrencyTable

shop_channels = [
int(os.getenv('BACKGROUND_ITEMS_CHANNEL_ID')), int(os.getenv('HAND_ITEMS_CHANNEL_ID')),
int(os.getenv('CLOTHES_ITEMS_CHANNEL_ID')), int(os.getenv('LIMITED_EDITION_ITEMS_CHANNEL_ID')),
int(os.getenv('HEAD_ITEMS_CHANNEL_ID')), int(os.getenv('LEG_ITEMS_CHANNEL_ID')),
int(os.getenv('PATREONS_CHANNEL_ID'))
]

booster_role_id = int(os.getenv('BOOSTER_ROLE_ID'))
guild_ids = [int(os.getenv('SERVER_ID'))]

currency_cogs: List[commands.Cog] = [
    UserItemsTable, UserServerActivityTable, UserCurrencyTable,
    UserVoiceSystem
]


class SlothCurrency(*currency_cogs):
    """ Sloth Currency commands. """

    def __init__(self, client) -> None:
        """ Class init method. """

        self.client = client

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Tells when the cog is ready to go. """

        print("SlothCurrency cog is online!")

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        """ Updates the user's message counter and gives them XP. """

        if not message.guild:
            return

        if message.author.bot:
            return
        if not await self.check_user_server_activity_table_exists():
            return

        user_info = await self.get_user_activity_info(message.author.id)
        if not user_info:
            return await self.insert_user_server_activity(message.author.id, 1)

        effects = await self.client.get_cog('SlothClass').get_user_effects(message.author)
        if 'sabotaged' not in effects:
            await self.update_user_server_messages(message.author.id, 1)


    # In-game commands
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def react(self, ctx, mid: discord.Message = None, reaction=None):
        """ (ADM) Makes the bot react onto a message.
        :param mid: The message ID.
        :param reaction: The reaction to add. """

        await ctx.message.delete()
        if not reaction:
            return await ctx.send("**Inform a reaction!**", delete_after=3)
        if not mid:
            return await ctx.send("**Inform a message id!**", delete_after=3)
        await mid.add_reaction(reaction)

    @commands.command(aliases=['inv'])
    @Player.poisoned()
    async def inventory(self, ctx, member: discord.Member = None) -> None:
        """ Shows the member's item inventory.
        :param member: The member to show. """

        await ctx.message.delete()
        if not member:
            member = discord.utils.get(ctx.guild.members, id=ctx.author.id)

        user_items = await self.get_user_items(member.id)

        if not user_items:
            return await ctx.send(f"**You don't have items to show, {ctx.author.mention}!**")

        the_menu = menus.MenuPages(source=InventoryLoop(user_items, member), clear_reactions_after=True)
        await the_menu.start(ctx)

    @commands.command()
    @Player.poisoned()
    async def equip(self, ctx, *, item_name: str = None) -> None:
        """ Equips an item.
        :param item_name: The item to equip. """

        item_name = escape_mentions(item_name)

        await ctx.message.delete()
        if not item_name:
            return await ctx.send("**Inform an item to equip!**", delete_after=3)

        if user_item := await self.get_user_item(ctx.author.id, item_name.title()):
            if await self.check_user_can_equip(ctx.author.id, item_name.title()):
                await self.update_user_item_info(ctx.author.id, item_name, 'equipped')
                return await ctx.send(f"**{ctx.author.mention} equipped __{item_name.title()}__!**", delete_after=3)
            else:
                return await ctx.send(f"**You already have a __{user_item[3]}__ item equipped!**", delete_after=3)
        else:
            return await ctx.send(f"**You don't have an item named __{item_name.title()}__!**", delete_after=3)

    @commands.command()
    @Player.poisoned()
    async def unequip(self, ctx, *, item_name: str = None) -> None:
        """ Unequips an item.
        :param item_name: The item to unequip """

        item_name = escape_mentions(item_name)

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


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_member(self, ctx, member: discord.Member = None, *, item_name: str = None) -> None:
        """ (ADM) Gives a member an item.
        :param member: The member to give the item.
        :param item_name: The name of the item. """

        item_name = escape_mentions(item_name)

        if not member:
            return await ctx.send("**Inform a member!**", delete_after=3)

        if not item_name:
            return await ctx.send("**Inform an item to add!**", delete_after=3)

        user_has_item = await self.get_user_specific_item(member.id, item_name.title())
        if not user_has_item:
            if (shop_item := await self.get_shop_item(item_name)):
                await self.insert_user_item(member.id, item_name, 'unequipped', shop_item[5], str(shop_item[3]).replace('registered_items/', ''))
                return await ctx.send(f"**{item_name.title()} given to {member.name}!**", delete_after=3)
            else:
                return await ctx.send(f"**This item doesn't exist, {ctx.author.mention}!**")
        else:
            return await ctx.send(f"**{member.name} already has that item!**", delete_after=3)

    async def get_shop_item(self, item_name: str) -> List[Union[str, int]]:
        """ Gets a specific item from the shop.
        :param item_name: The name of the item to get. """

        mycursor, db = await the_django_database()
        await mycursor.execute("SELECT * FROM shop_shopitem WHERE item_name = %s", (item_name,))
        item = await mycursor.fetchone()
        await mycursor.close()
        return item

    async def get_shop_items(self) -> List[List[Union[str, int]]]:
        """ Gets all items from the shop. """

        mycursor, db = await the_django_database()
        await mycursor.execute("SELECT * FROM shop_shopitem")
        items = await mycursor.fetchall()
        await mycursor.close()
        return items


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def remove_member_item(self, ctx, member: discord.Member = None, *, item_name: str = None) -> None:
        """ (ADM) Removes an item from the member.
        :param member: The member to remove the item.
        :param item_name: The name of the item. """

        item_name = escape_mentions(item_name)

        if not member:
            return await ctx.send("**Inform a member!**", delete_after=3)

        if not item_name:
            return await ctx.send("**Inform an item to remove!**", delete_after=3)

        user_has_item = await self.get_user_specific_item(member.id, item_name)
        if len(user_has_item) != 0:
            await self.remove_user_item(member.id, item_name)
            return await ctx.send(f"**{item_name.title()} taken from {member.name}!**", delete_after=3)
        else:
            return await ctx.send(f"**{member.name} doesn't have that item!**", delete_after=3)


    async def check_user_has_item(self, user_id: int, item_name: str) -> bool:
        """ Checks whether the user has an item.
        :param user_id: The ID of the user to check.
        :param item_name: The name of the item to check. """

        user_item = await self.get_user_specific_item(user_id, item_name)
        if user_item:
            return True
        else:
            return False

    async def send_hacked_image(self, answer: discord.PartialMessageable, author: discord.Member, member: discord.Member) -> None:
        """ Makes and sends a hacked image.
        :param answer: The answerable object.
        :param author: The author of the action.
        :param member: The member who was hacked. """

        SlothClass = self.client.get_cog('SlothClass')

        try:
            # Gets original skill action and the attacker
            skill_action = await SlothClass.get_skill_action_by_target_id_and_skill_type(member.id, 'hack')
            skill_action = skill_action[0] if skill_action else '??'
            hacker = self.client.get_user(skill_action)
            # Makes the Hacked image and saves it
            big = ImageFont.truetype("built titling sb.ttf", 80)
            background = Image.open('sloth_custom_images/background/hacked.png').convert('RGBA')
            draw = ImageDraw.Draw(background)
            draw.text((350, 300), f"Hacked by {hacker}", font=big, fill=(0, 0, 0))
            file_path = f'media/temporary/hacked_{member.id}.png'
            background.save(file_path, 'png', quality=90)
        except Exception as e:
            print(e)
            return await answer(f"**{author.mention}, something went wrong with it!**")
        else:
            await answer(file=discord.File(file_path))
            # await asyncio.sleep(0.5)
            return os.remove(file_path)

    async def send_frogged_image(self, answer: discord.PartialMessageable, author: discord.Member, member: discord.Member, knocked_out: bool = False) -> None:
        """ Makes and sends a frogged image.
        :param answer: The answerable object.
        :param author: The author of the action.
        :param member: The member who was frogged.
        :param knocked_out: Whether the user is knocked out"""

        SlothClass = self.client.get_cog('SlothClass')
        try:
            # Gets original skill action and the attacker
            skill_action = await SlothClass.get_skill_action_by_target_id_and_skill_type(member.id, 'frog')
            skill_action = skill_action[0] if skill_action else '??'
            metamorph = self.client.get_user(skill_action)
            # Makes the Hacked image and saves it
            big = ImageFont.truetype("built titling sb.ttf", 80)
            background = None

            if knocked_out:
                background = Image.open('sloth_custom_images/background/frogged_ko.png').convert('RGBA')
            else:
                background = Image.open('sloth_custom_images/background/frogged.png').convert('RGBA')

            draw = ImageDraw.Draw(background)
            draw.text((170, 170), f"{metamorph}", font=big, fill=(39, 126, 205))
            file_path = f'media/temporary/frogged_{member.id}.png'
            background.save(file_path, 'png', quality=90)
        except Exception as e:
            print(e)
            return await answer(f"**{author.mention}, something went wrong with it!**")
        else:
            await answer(file=discord.File(file_path))
            # await asyncio.sleep(0.5)
            return os.remove(file_path)

    @commands.command(name="profile")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @Player.poisoned()
    async def _profile_command(self, ctx, member: discord.Member = None):
        """ Shows the member's profile with their custom sloth.
        :param member: The member to see the profile. (Optional) """

        await self._profile(ctx, member)

    @slash_command(name="profile", guild_ids=guild_ids)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @Player.poisoned()
    async def _profile_slash(self, ctx, member: Option(discord.Member, description="The member to show the info; [Default=Yours]", required=False)) -> None:
        """ Shows the member's profile with their custom sloth. """

        await ctx.defer()
        await self._profile(ctx, member)

    async def _profile(self, ctx, member: discord.Member = None):
        """ Shows the member's profile with their custom sloth.
        :param member: The member to see the profile. (Optional) """

        answer = None
        if isinstance(ctx, commands.Context):
            answer = ctx.send
        else:
            answer = ctx.respond

        author = ctx.author

        if not member:
            member = author
            
        user_info = await self.get_user_currency(member.id)
        sloth_profile = await self.client.get_cog('SlothClass').get_sloth_profile(member.id)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(style=5, label="Create Account", emoji="🦥", url="https://thelanguagesloth.com/profile/update"))

        if not user_info or not sloth_profile:
            if author.id == member.id:
                return await answer( 
                    embed=discord.Embed(description=f"**{member.mention}, you don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one, or in the button below!**"),
                    view=view)
            else:
                return await answer(f"**{member} doesn't have an account yet!**", delete_after=3)

        if sloth_profile[1].lower() == 'default':
            if author.id == member.id:
                return await answer( 
                    embed=discord.Embed(description=f"**{member.mention}, you don't have a Sloth class yet. Click [here](https://thelanguagesloth.com/profile/slothclass) to choose one, or in the button below!**"),
                    view=view)
                    
            else:
                return await answer(f"**{member} has a default Sloth class, I cannot show their profile!**")
                
        SlothClass = self.client.get_cog('SlothClass')
        effects = await SlothClass.get_user_effects(member=member)

        # Checks whether user is frogged
        if 'frogged' in effects:
            ko = 'knocked_out' in effects
            return await self.send_frogged_image(answer, author, member, ko)

        # Checks whether user is hacked
        if 'hacked' in effects:
            await self.send_hacked_image(answer, author, member)
            if author.id != member.id:
                await SlothClass.check_virus(ctx=ctx, target=member)
            return

        small = ImageFont.truetype("built titling sb.ttf", 45)
        background = Image.open(await self.get_user_specific_type_item(member.id, 'background'))

        # Checks whether user is transmutated
        sloth = None
        if await SlothClass.has_effect(effects, 'transmutated'):
            sloth = Image.open(f"./sloth_custom_images/sloth/transmutated_sloth.png")
        else:
            sloth = Image.open(f"./sloth_custom_images/sloth/{sloth_profile[1].title()}.png")

        # Gets an item image for each equippable slot
        body = Image.open(await self.get_user_specific_type_item(member.id, 'body'))
        hand = Image.open(await self.get_user_specific_type_item(member.id, 'hand'))
        foot = Image.open(await self.get_user_specific_type_item(member.id, 'foot'))
        head = Image.open(await self.get_user_specific_type_item(member.id, 'head'))
        hud = Image.open(await self.get_user_specific_type_item(member.id, 'hud'))
        
        # Pastes all item images
        pfp = await utils.get_user_pfp(member)
        background.paste(sloth, (0, 0), sloth)
        background.paste(body, (0, 0), body)
        background.paste(head, (0, 0), head)
        background.paste(foot, (0, 0), foot)
        background.paste(hand, (0, 0), hand)
        background.paste(hud, (0, 0), hud)

        # Checks if user is a booster
        booster_role = discord.utils.get(ctx.guild.roles, id=booster_role_id)
        if booster_role in member.roles:
            if flag_badge := flag_badges.get('discord_server_booster'):
                file_path = f"./sloth_custom_images/badge/{flag_badge[0]}"
                if os.path.isfile(file_path):
                    booster_badge = Image.open(file_path).resize((50, 50)).convert('RGBA')
                    background.paste(booster_badge, flag_badge[1], booster_badge)

        # Pastes all flag badges that the user has
        flags = await utils.get_member_public_flags(member)
        for flag in flags:
            if flag_badge := flag_badges.get(flag):
                file_path = f"./sloth_custom_images/badge/{flag_badge[0]}"
                if os.path.isfile(file_path):
                    flag_image = Image.open(file_path).resize((50, 50)).convert('RGBA')
                    background.paste(flag_image, flag_badge[1], flag_image)

        # Checks whether user has level badges
        user_level = await self.client.get_cog('SlothReputation').get_specific_user(member.id)
        for key, value in reversed(list(level_badges.items())):
            if user_level[0][2] >= key:
                file_path = f"sloth_custom_images/badge/{value[0]}.png"
                if os.path.isfile(file_path):
                    level_badge = Image.open(file_path)
                    background.paste(level_badge, value[1], level_badge)
                    break

        # Tries to print the user's profile picture
        try:
            background.paste(pfp, (201, 2), pfp)
        except Exception:
            pass

        draw = ImageDraw.Draw(background)
        draw.text((310, 5), f"{str(member)[:10]}", (255, 255, 255), font=small)
        draw.text((80, 525), f"{user_info[0][1]}", (255, 255, 255), font=small)
        file_path = f'media/temporary/profile_{member.id}.png'
        background.save(file_path, 'png', quality=90)

        all_effects = {key: value for (key, value) in effects.items() if value.get('has_gif')}
        async with ctx.typing():

            if all_effects:
                try:
                    gif_file_path = await self.make_gif_image(user_id=member.id, all_effects=all_effects)
                    await answer(file=discord.File(gif_file_path))

                except Exception as e:
                    print(e)
                    pass
                finally:
                    os.remove(file_path)
                    os.remove(gif_file_path)
            else:
                try:
                    await answer(file=discord.File(file_path))
                except:
                    pass
                finally:
                    os.remove(file_path)

    async def make_gif_image(self, user_id: int, all_effects: Dict[str, Dict[str, Union[List[str], Tuple[int]]]]) -> str:
        """ Makes a gif image out a profile image.
        :param user_id: The ID of the user for whom to make the GIF.
        :param all_effects: All effects that the user currently has. """

        gif_file_path = f'media/temporary/profile_{user_id}.gif'

        try:
            profile = Image.open(f'media/temporary/profile_{user_id}.png').convert('RGBA')
            gif = GIF(image=profile, frame_duration=40)
            path = 'media/effects'

            # Gets all frames of each effect and resize them properly, respectively.
            for effect in all_effects:
                full_path = f"{path}/{effect}"
                # Checks whether the effect folder exists
                if os.path.isdir(full_path):
                    # Gets all frame images from the folder
                    for i in range(len(glob.glob(f"{full_path}/*.png"))):
                        frame = Image.open(f"{full_path}/{effect}_{i+1}.png")  # convert('RGBA') # remove this convert later
                        # Checs whether frame has to be resized
                        if all_effects[effect]['resize']:
                            frame = frame.resize(all_effects[effect]['resize']).convert('RGBA')
                        # Appends to its respective frame list
                        all_effects[effect]['frames'].append(frame)

            # Loops through the frames based on the amount of frames of the longest effect.
            longest_gif = max([len(frames['frames']) for frames in all_effects.values()])

            for efx in all_effects.keys():
                all_effects[efx]['frames'] = cycle(all_effects[efx]['frames'])

            for i in range(longest_gif):
                # Gets a frame of each effect in each iteration of the loop
                base = gif.new_frame()
                await asyncio.sleep(0)
                for efx, value in all_effects.items():
                    # print(all_effects[efx]['cords'])
                    cords = all_effects[efx]['cords']
                    frame = next(all_effects[efx]['frames'])
                    # print(efx, frame)
                    base.paste(frame, cords, frame)
                    gif.add_frame(base)

                if i >= 400:
                    break

            else:
                gif.export(gif_file_path)

        except Exception as e:
            print(e)
            pass
        finally:
            return gif_file_path

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_money(self, ctx, member: discord.Member = None, money: int = None) -> None:
        """ (ADM) Adds money to a member.
        :param member: The member to add money to.
        :param money: The amount of money to add. """

        if not member:
            return await ctx.send("**Inform a member!**", delete_after=3)
        elif not money:
            return await ctx.send("**Inform an amount of money!**", delete_after=3)

        await self.update_user_money(member.id, money)
        return await ctx.send(f"**{money} added to {member.name}'s bank account!**", delete_after=5)

    # Google Drive commands
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def download_update(self, ctx=None, rall: str = 'no'):
        """ (ADM) Downloads all shop images from the Google Drive. """

        if ctx:
            await ctx.message.delete()

        drive = await the_drive()

        if rall.lower() == 'yes':
            try:
                shutil.rmtree('./sloth_custom_images')
            except Exception:
                pass

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
                    try:
                        output_file = os.path.join(download_path, file['title'])
                        temp_file = drive.CreateFile({'id': file['id']})
                        temp_file.GetContentFile(output_file)
                    except:
                        pass
                    # print(f"File '{file['title']}' downloaded!")

        if ctx:
            return await ctx.send("**Download update is done!**", delete_after=5)

    # Google Drive commands
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def text_download_update(self, ctx=None, rall: str = 'no'):
        """ (ADM) Downloads all texts from the GoogleDrive and stores in the bot's folder. """

        if rall.lower() == 'yes':
            try:
                shutil.rmtree('./texts')
            except Exception as e:
                pass

        drive = await the_drive()

        all_text_folders = {"languages": "1_gBiliWPrCj5cLpChQfg9QRnj8skQVHM"}

        text_categories = ["languages"]

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
                    try:
                        output_file = os.path.join(download_path, file['title'])
                        temp_file = drive.CreateFile({'id': file['id']})
                        temp_file.GetContentFile(output_file)
                    except:
                        pass
        if ctx:
            return await ctx.send("**Download update is done!**")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def list_folder(self, ctx, image_suffix: str = None, item_name: str = None):
        """ (ADM) Lists a shop image folder from Google Drive.
        :param image_suffix: The image/folder category. """

        await ctx.message.delete()
        all_folders = {"background": "1V8l391o3-vsF9H2Jv24lDmy8e2erlHyI",
                       "sloth": "16DB_lNrnrmvxu2E7RGu01rQGQk7z-zRy",
                       "body": "1jYvG3vhL32-A0qDYn6lEG6fk_GKYDXD7",
                       "hand": "1ggW3SDVzTSY5b8ybPimCsRWGSCaOBM8d",
                       "hud": "1-U6oOphdMNMPhPAjRJxJ2E6KIzIbewEh",
                       "badge": "1k8NRfwwLzIY5ALK5bUObAcrKr_eUlfjd",
                       "foot": "1Frfra1tQ49dKM6Dg4DIbrfYbtXadv9zj",
                       "head": "1Y9kSOayw4NDehbqfmvPXKZLrXnIjeblP"}

        drive = await the_drive()

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
                    embed = discord.Embed(title=f"Category: {image_suffix}", color=discord.Color.dark_green(),
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


    async def exchange(self, ctx, cmsg, message_times, ctime, time_times):
        """ Exchange your status into leaves (łł).
        :param ctx: The context of the command.
        :param cmsg: The amount of leaves gotten from messages.
        :param message_times: The amount of loops it took to get to the messages result.
        :param ctime: The amount of leaves gotten from time.
        :param time_times: The amount of loops it took to get to the time result. """
        
        embed = discord.Embed(title="Exchange", color=ctx.author.color, timestamp=ctx.message.created_at)
        embed.set_author(name=ctx.author, url=ctx.author.display_avatar)
        if cmsg > 0:
            embed.add_field(name="__**Messages:**__",
                            value=f"Exchanged `{message_times * 100}` messages for `{cmsg}`łł;", inline=False)
        if ctime > 0:
            embed.add_field(name="__**Time:**__",
                            value=f"Exchanged `{(time_times * 3600) / 60}` minutes for `{ctime}`łł;", inline=False)
        return await ctx.send(embed=embed)


    async def convert_messages(self, user_message: int) -> List[int]:
        """ Converts the user's message counter to leaves.
        :param user_message: The message counter the user has. """

        messages_left = user_message
        exchanged_money = times = 0

        while True:
            if messages_left >= 100:
                times += 1
                messages_left -= 100
                exchanged_money += 4
                await asyncio.sleep(0)
                continue
            else:
                
                return exchanged_money, times

    async def convert_time(self, user_time: int) -> List[int]:
        """ Converts the user's time counter to leaves.
        :param user_time: The amount of time in seconds the user has. """

        time_left = user_time
        exchanged_money = times = 0

        while True:
            if time_left >= 1800:
                times += 1
                time_left -= 1800
                exchanged_money += 4
                await asyncio.sleep(0)
                continue
            else:
                return exchanged_money, times

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_message(self, ctx, member: discord.Member = None, add_message: int = None):
        """ (ADM) Adds messages to the member's status.
        :param member: The member to add the messages to.
        :param add_message: The amount of messages to add. """

        if not add_message:
            return await ctx.send(f"**Inform an amount of messages to add!**", delete_after=3)
        if not member:
            member = ctx.author
        await self.update_user_server_messages(member.id, add_message)
        return await ctx.send(f"Added {add_message} messages to {member}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def add_time(self, ctx, member: discord.Member = None, add_time: int = None):
        """ (ADM) Adds time to the member's status.
        :param member: The member to add time to.
        :param add_time: The amount of time to add. (in secs) """

        if not add_time:
            return await ctx.send(f"**Inform an amount of seconds to add!**", delete_after=3)
        if not member:
            member = ctx.author
        await self.update_user_server_time(member.id, add_time)
        return await ctx.send(f"Added {add_time} seconds to {member}")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @Player.poisoned()
    async def transfer(self, ctx, member: discord.Member = None, money: int = None):
        """ Transfers money from one member to another member.
        :param member: The member to transfer the money to.
        :param money: The amount of money to transfer.
        
        * Cooldown: 10 secs. """

        if not member:
            return await ctx.send('**Inform the member!**', delete_after=3)
        elif member.id == ctx.author.id:
            return await ctx.send("**You can't transfer money to yourself!**", delete_after=3)
        elif not money:
            return await ctx.send('**Inform the amount of money to transfer!**', delete_after=3)
        elif not int(money) > 0:
            return await ctx.send('**Inform value bigger than 0!**', delete_after=3)

        the_user = await self.get_user_currency(ctx.author.id)
        target_user = await self.get_user_currency(member.id)
        if not the_user:
            view = discord.ui.View()
            view.add_item(discord.ui.Button(style=5, label="Create Account", emoji="🦥", url="https://thelanguagesloth.com/profile/update"))
            return await ctx.send( 
                embed=discord.Embed(description=f"**{member.mention}, you don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one, or in the button below!**"),
                view=view)
        elif not target_user:
            return await ctx.send(f"**{member} does not have a bank account yet!**", delete_after=5)

        if the_user[0][1] < int(money):
            return await ctx.send(f"You don't have {money}łł!")


        SlothClass = self.client.get_cog('SlothClass')

        wired_user = await SlothClass.get_skill_action_by_target_id_and_skill_type(
            target_id=ctx.author.id, skill_type='wire')

        if wired_user:
            siphon_percentage = 35
            cybersloth_money = round((money*siphon_percentage)/100)
            await self.update_user_money(member.id, money-cybersloth_money)
            await self.update_user_money(ctx.author.id, -money)
            await self.update_user_money(wired_user[0], cybersloth_money)
            description: str = f"{ctx.author.mention} tried to transfer `{money}łł` to {member.mention}, "\
                f"and <@{wired_user[0]}> siphoned off `{siphon_percentage}%` of it; `{cybersloth_money}łł`! "\
                f"So {member.mention} actually got `{money-cybersloth_money}łł`!"

            await ctx.send(
                content=f"{ctx.author.mention}, {member.mention}, <@{wired_user[0]}>",
                embed=discord.Embed(
                    title="__Intercepted Transfer__",
                    description=description,
                    color=ctx.author.color,
                    timestamp=ctx.message.created_at)
            )

        else:
            await self.update_user_money(member.id, money)
            await self.update_user_money(ctx.author.id, -money)
            await ctx.send(f"**{ctx.author.mention} transferred {money}łł to {member.mention}!**")


    @commands.command(aliases=["farming_status", "farmingstatus", "farm", "farmstatus", "farmstats", "farm_status", "farm_stats"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def farming(self, ctx, member: discord.Member = None) -> None:
        """ Checks the farming status of a specific member.
        :param member: The member of the checking. """

        author: discord.Member = ctx.author
        if not member:
            member = author

        embed = discord.Embed(
            title="__Farm Checking__",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_footer(text=f"Requested by: {author}", icon_url=author.display_avatar)

        user_activity = await self.get_user_activity_info(member.id)
        user_activity = user_activity[0][3] if user_activity else None

        member_voice: VoiceState = member.voice
        vc: discord.VoiceChannel = member_voice.channel if member_voice else None
        smute, mute = member_voice.mute if member_voice else False, member_voice.self_mute if member_voice else False
        sdeaf, deaf = member_voice.deaf if member_voice else False, member_voice.self_deaf if member_voice else False

        embed.description = """
        🍃 - Farming
        <:vc:914947524178116649> - Joined VC Timestamp
        """

        alts = await self.client.get_cog('Moderation').get_fake_accounts(member.id)
        alts_list: List[int] = []
        for alt in alts:
            alts_list.append(alt[0])
            alts_list.append(alt[1])

        alts = list(set(alts_list))
        try:
            alts.remove(member.id)
        except ValueError:
            pass

        vc_members: List[int] = len([m for m in vc.members if not m.bot if m.id not in alts]) if vc else 0
        is_farming = True if vc and not mute and not deaf and not smute and not sdeaf and vc_members > 1 else False

        embed.add_field(
            name="__Checking__:",
            value= f"**Member:** {member.mention}\n" \
            f"<:server_muted:914943052156665919> `{smute}` | <:muted:914943036931326054> `{mute}`\n" \
            f"<:server_deafened:914943091599880203> `{sdeaf}` | <:deafened:914943073119772683> `{deaf}`\n" \
            f"🍃 `{is_farming}` ({vc.mention if vc else '`No VC`'})\n" \
            f"<:vc:914947524178116649> `{user_activity}` ({f'<t:{user_activity}:R>' if user_activity else '`None`'})" \
        , inline=False)

        embed.set_thumbnail(url=member.display_avatar)

        await ctx.send(embed=embed)

    @commands.command(aliases=['balance', 'bal', 'fric'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def money(self, ctx, member: Optional[Union[discord.Member, discord.User]] = None) -> None:
        """ Shows the user's money.
        :param member: The member from whom to show the money. [Optional][Default = You] """

        if not member:
            member = ctx.author

        user_currency = await self.get_user_currency(member.id)
        if not user_currency:
            return await ctx.send(f"**User doesn't have a Sloth Account, {ctx.author.mention}!**")

        embed = discord.Embed(
            description=f"**{member.mention}'s money: {user_currency[0][1]} 🍃**",
            color=member.color
        )
        await ctx.send(embed=embed)





def setup(client):
    client.add_cog(SlothCurrency(client))
