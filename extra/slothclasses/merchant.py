from discord import file
from extra.prompt.menu import ConfirmButton
import discord
from discord.ext import commands, menus
from .player import Player, Skill
from mysqldb import the_database
from extra.menu import ConfirmSkill, prompt_number, OpenShopLoop
from extra import utils
import os
from typing import List, Dict, Union
from datetime import datetime
import random
from PIL import Image, ImageDraw, ImageFont

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))


class Merchant(Player):

    emoji = '<:Merchant:839498018532753468>'

    def __init__(self, client) -> None:
        self.client = client

    @commands.command(aliases=['sellpotion', 'potion'])
    @Player.skill_on_cooldown()
    @Player.user_is_class('merchant')
    @Player.skill_mark()
    async def sell_potion(self, ctx) -> None:
        """ Puts a changing-SlothClass potion for sale for the price you want.
        Ps: It costs 50łł to do it and the item remains there for 24 hours. """

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{ctx.author.mention}, you can only use this command in {self.bots_txt.mention}!**")

        member = ctx.author

        member_fx = await self.get_user_effects(member)

        if 'knocked_out' in member_fx:
            return await ctx.send(f"**{member.mention}, you can't use your skill, because you are knocked-out!**")

        if await self.get_skill_action_by_user_id_and_skill_type(member.id, 'potion'):
            return await ctx.send(f"**{member.mention}, you already have a potion in your shop!**")

        item_price = await prompt_number(self.client, ctx, f"**{member.mention}, for how much do you want to sell your changing-Sloth-class potion?**", member)
        if item_price is None:
            return

        confirm = await ConfirmSkill(f"**{member.mention}, are you sure you want to spend `50łł` to put a potion in your shop with the price of `{item_price}`łł ?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not doing it, then, {member.mention}!**")

        _, exists = await Player.skill_on_cooldown(skill=Skill.ONE).predicate(ctx)

        user_currency = await self.get_user_currency(member.id)
        if user_currency[1] < 50:
            return await ctx.send(f"**{member.mention}, you don't have `50łł`!**")

        item_emoji = '🍯'

        try:
            current_timestamp = await utils.get_timestamp()
            await self.insert_skill_action(
                user_id=member.id, skill_type="potion", skill_timestamp=current_timestamp,
                target_id=member.id, channel_id=ctx.channel.id, price=item_price, emoji=item_emoji
            )
            await self.update_user_money(member.id, -50)
            if exists:
                await self.update_user_skill_ts(member.id, Skill.ONE, current_timestamp)
            else:
                await self.insert_user_skill_cooldown(ctx.author.id, Skill.ONE, current_timestamp)
            # Updates user's skills used counter
            await self.update_user_skills_used(user_id=member.id)
            open_shop_embed = await self.get_open_shop_embed(
                channel=ctx.channel, perpetrator_id=member.id, price=item_price, item_name='changing-Sloth-class potion', emoji=item_emoji)
            await ctx.send(embed=open_shop_embed)
        except Exception as e:
            print(e)
            return await ctx.send(f"**{member.mention}, something went wrong with it, try again later!**")
        else:
            await ctx.send(f"**{member}, your item is now in the shop, check `z!sloth_shop` to see it there!**")
            

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def sloth_shop(self, ctx) -> None:
        """ Shows all class related items in the Sloth shop. """

        potions = await self.get_open_shop_items()
        if potions:
            the_menu = menus.MenuPages(source=OpenShopLoop(potions), clear_reactions_after=True)
            await the_menu.start(ctx)
        else:
            return await ctx.send(f"**There are no items in the `Sloth class shop` yet, {ctx.author.mention}!**")


    @commands.group(aliases=['buy_item', 'buyitem', 'purchase'])
    async def buy(self, ctx) -> None:
        """ Buys a specific item from a Merchant.
        (Use this without an item name to see what items you can possibly buy with this command) """
        if ctx.invoked_subcommand:
            return

        cmd = self.client.get_command('buy')
        prefix = self.client.command_prefix
        subcommands = [f"{prefix}{c.qualified_name}" for c in cmd.commands
            ]

        subcommands = '\n'.join(subcommands)
        items_embed = discord.Embed(
            title="__Subcommads__:",
            description=f"```apache\n{subcommands}```",
            color=ctx.author.color,
            timestamp=ctx.message.created_at
        )

        await ctx.send(embed=items_embed)

    @buy.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def potion(self, ctx, member: discord.Member = None) -> None:
        """ Buys a changing-Sloth-class potion from a Merchant. """

        buyer = ctx.author
        if not member:
            return await ctx.send(f"**Please, inform a `Merchant`, {buyer.mention}!**")

        if not(merchant_item := await self.get_skill_action_by_user_id_and_skill_type(member.id, 'potion')):
            return await ctx.send(
                f"**{member} is either not a `Merchant` or they don't have a potion available for purchase, {buyer.mention}!**")

        user_info = await self.get_user_currency(buyer.id)
        sloth_profile = await self.get_sloth_profile(buyer.id)
        if not user_info or not sloth_profile:
            await ctx.send(embed=discord.Embed(description=f"**{buyer.mention}, you don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one!**"))

        elif sloth_profile[1].lower() == 'default':
            await ctx.send(embed=discord.Embed(description=f"**{buyer.mention}, you don't have a Sloth class yet. Click [here](https://thelanguagesloth.com/profile/slothclass) to choose one!**"))

        elif sloth_profile[5]:
            await ctx.send(embed=discord.Embed(description=f"**{buyer.mention}, you already have a potion, you can't buy another one!**"))

        elif user_info[1] < merchant_item[7]:
            await ctx.send(embed=discord.Embed(description=f"**{buyer.mention}, the potion costs {merchant_item[7]}, but you only have {user_info[1]}łł!**"))

        else:
            confirm = await ConfirmSkill(f"**{buyer.mention}, are you sure you want to buy a `changing-Sloth-class potion` for `{merchant_item[7]}łł`?**").prompt(ctx)
            if not confirm:
                return await ctx.send(f"**Not buying it, then, {buyer.mention}!**")

            if not await self.get_skill_action_by_user_id_and_skill_type(member.id, 'potion'):
                return await ctx.send(f"**{member.mention} doesn't have a potion available for purchase, {buyer.mention}!**")

            try:
                if wired_user := await self.get_skill_action_by_target_id_and_skill_type(target_id=member.id, skill_type='wire'):

                    siphon_percentage = 35
                    cybersloth_money = round((merchant_item[7]*siphon_percentage)/100)
                    target_money = merchant_item[7] - cybersloth_money
                    await self.update_user_money(member.id, target_money)
                    await self.update_user_money(buyer.id, -merchant_item[7])
                    await self.update_user_money(wired_user[0], cybersloth_money)
                    cybersloth = self.client.get_user(wired_user[0])
                    siphon_embed = discord.Embed(
                            title="__Intercepted Purchase__",
                            description=(
                                f"{buyer.mention} bought a `changing-Sloth-class potion` from {member.mention} for `{merchant_item[7]}łł`, "
                                f"but {cybersloth.mention if cybersloth else str(cybersloth)} siphoned off `{siphon_percentage}%` of the price; `{cybersloth_money}łł`! "
                                f"So the Merhcant {member.mention} actually got `{target_money}łł`!"
                            ),
                            color=buyer.color,
                            timestamp=ctx.message.created_at)
                    if cybersloth:
                        siphon_embed.set_thumbnail(url=cybersloth.avatar.url)

                    await ctx.send(
                        content=f"{buyer.mention}, {member.mention}, <@{wired_user[0]}>",
                        embed=siphon_embed)

                else:
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

    @buy.command(aliases=['wedding', 'wedding_ring', 'weddingring'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ring(self, ctx, member: discord.Member = None) -> None:
        """ Buys a Wedding Ring from a Merchant. """

        buyer = ctx.author
        if not member:
            return await ctx.send(f"**Please, inform a `Merchant`, {buyer.mention}!**")

        if not(merchant_item := await self.get_skill_action_by_user_id_and_skill_type(member.id, 'ring')):
            return await ctx.send(
                f"**{member} is either not a `Merchant` or they don't have a ring available for purchase, {buyer.mention}!**")

        user_info = await self.get_user_currency(buyer.id)
        slothprofile = await self.get_sloth_profile(buyer.id)
        
        if not user_info:
            return await ctx.send(embed=discord.Embed(description=f"**{buyer.mention}, you don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one!**"))

        if slothprofile[1].lower() == 'default':
            return await ctx.send(embed=discord.Embed(description=f"**{buyer.mention}, you don't have a Sloth class yet. Click [here](https://thelanguagesloth.com/profile/slothclass) to choose one!**"))

        if slothprofile and slothprofile[7] == 2:
            return await ctx.send(embed=discord.Embed(description=f"**{buyer.mention}, you already have two `Wedding Rings`, you can't buy another one!**"))

        if user_info[1] < merchant_item[7]:
            return await ctx.send(embed=discord.Embed(description=f"**{buyer.mention}, the ring costs {merchant_item[7]}, but you only have {user_info[1]}łł!**"))

        confirm = await ConfirmSkill(f"**{buyer.mention}, are you sure you want to buy a `Wedding Ring` for `{merchant_item[7]}łł`?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not buying it, then, {buyer.mention}!**")

        if not await self.get_skill_action_by_user_id_and_skill_type(member.id, 'ring'):
            return await ctx.send(f"**{member.mention} doesn't have a `Wedding Ring` available for purchase, {buyer.mention}!**")

        try:
            if wired_user := await self.get_skill_action_by_target_id_and_skill_type(target_id=member.id, skill_type='wire'):

                siphon_percentage = 35
                cybersloth_money = round((merchant_item[7]*siphon_percentage)/100)
                target_money = merchant_item[7] - cybersloth_money
                await self.update_user_money(member.id, target_money)
                await self.update_user_money(buyer.id, -merchant_item[7])
                await self.update_user_money(wired_user[0], cybersloth_money)
                cybersloth = self.client.get_user(wired_user[0])
                siphon_embed = discord.Embed(
                        title="__Intercepted Purchase__",
                        description=(
                            f"{buyer.mention} bought a `Wedding Ring` from {member.mention} for `{merchant_item[7]}łł`, "
                            f"but {cybersloth.mention if cybersloth else str(cybersloth)} siphoned off `{siphon_percentage}%` of the price; `{cybersloth_money}łł`! "
                            f"So the Merhcant {member.mention} actually got `{target_money}łł`!"
                        ),
                        color=buyer.color,
                        timestamp=ctx.message.created_at)
                if cybersloth:
                    siphon_embed.set_thumbnail(url=cybersloth.avatar.url)

                await ctx.send(
                    content=f"{buyer.mention}, {member.mention}, <@{wired_user[0]}>",
                    embed=siphon_embed)

            else:
                # Updates both buyer and seller's money
                await self.update_user_money(buyer.id, - merchant_item[7])
                await self.update_user_money(member.id, merchant_item[7])

            # Gives the buyer their potion and removes the potion from the store
            await self.update_user_rings(buyer.id)
            await self.delete_skill_action_by_target_id_and_skill_type(member.id, 'ring')
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
                description=f"{buyer.mention} bought a `Wedding Ring` from {member.mention}!",
                color=discord.Color.green(),
                timestamp=ctx.message.created_at
                ))


    @commands.command()
    @Player.skills_used(requirement=5)
    @Player.skill_on_cooldown(skill=Skill.TWO)
    @Player.user_is_class('merchant')
    @Player.skill_mark()
    async def package(self, ctx) -> None:
        """ Buys a package from Dark Sloth Web and has a 35% chance of getting any equippable item from the Leaf Shop. """

        merchant = ctx.author

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{merchant.mention}, you can only use this command in {self.bots_txt.mention}!**")


        merchant_fx = await self.get_user_effects(merchant)
        if 'knocked_out' in merchant_fx:
            return await ctx.send(f"**{merchant.mention}, you can't use your skill, because you are knocked-out!**")

        confirm = await ConfirmSkill(f"**{merchant.mention}, are you sure you want to spend `50łł` to get a random package from the Dark Sloth Web?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not buying it, then!**")

        _, exists = await Player.skill_on_cooldown(skill=Skill.TWO).predicate(ctx)

        # Checks whether user has money
        user_currency = await self.get_user_currency(merchant.id)
        if user_currency[1] >= 50:
            await self.update_user_money(merchant.id, -50)
        else:
            return await ctx.send(f"**{merchant.mention}, you don't have `50łł`!**")

        current_timestamp = await utils.get_timestamp()
        if exists:
            await self.update_user_skill_ts(merchant.id, Skill.TWO, current_timestamp)
        else:
            await self.insert_user_skill_cooldown(ctx.author.id, Skill.TWO, current_timestamp)
        # Updates user's skills used counter
        await self.update_user_skills_used(user_id=merchant.id)

        if random.random() <= 0.35:
            SlothCurrency = self.client.get_cog('SlothCurrency')
            registered_items = await SlothCurrency.get_shop_items()
            random_item = random.choice(registered_items)

            # Checks whether user already has the item
            user_has_item = await SlothCurrency.check_user_has_item(user_id=merchant.id, item_name=random_item[4])
            if user_has_item:
                # Gives the user the price of the item
                await self.update_user_money(merchant.id, random_item[6])
                await ctx.send(f"**{merchant.mention}, you already have the `{random_item[4]}` item, so you got it worth of leaves instead; `{random_item[5]}łł`**")

            else:
                # Gives the user the item
                await SlothCurrency.insert_user_item(merchant.id, random_item[4], 'unequipped', random_item[5], str(random_item[3]).replace('registered_items/', ''))
                await ctx.send(f"**{merchant.mention}, you just got the `{random_item[4]}` item, which is worth `{random_item[6]}łł`**")

        else:
            await ctx.send(f"**{merchant.mention}, you had a `35%` chance of getting something from the Dark Sloth Web, it happened that today wasn't your day!**")

    async def check_shop_potion_items(self) -> None:

        """ Check on-going changing-Sloth-class potion items and their expiration time. """

        transmutations = await self.get_expired_potion_items()
        for tm in transmutations:
            await self.delete_skill_action_by_target_id_and_skill_type(tm[3], 'potion')

            channel = self.bots_txt

            await channel.send(
                content=f"<@{tm[0]}>",
                embed=discord.Embed(
                    description=f"**<@{tm[3]}>'s `changing-Sloth-class potion` has just expired! Then it's been removed from the `Sloth class shop`! 🍯**",
                    color=discord.Color.red()))

    async def check_shop_ring_items(self) -> None:

        """ Check on-going Wedding Ring items and their expiration time. """

        transmutations = await self.get_expired_ring_items()
        for tm in transmutations:
            await self.delete_skill_action_by_target_id_and_skill_type(tm[3], 'ring')

            channel = self.bots_txt

            await channel.send(
                content=f"<@{tm[0]}>",
                embed=discord.Embed(
                    description=f"**<@{tm[3]}>'s `Wedding Ring` has just expired! Then it's been removed from the `Sloth class shop`! 🍯**",
                    color=discord.Color.red()))

    # ========== Update ===========

    async def update_user_has_potion(self, user_id: int, has_it: int) -> None:
        """ Updates the user's protected state.
        :param user_id: The ID of the member to update.
        :param has_it: Whether it's gonna be set to true or false. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE SlothProfile SET has_potion = %s WHERE user_id = %s", (has_it, user_id))
        await db.commit()
        await mycursor.close()

    async def update_user_rings(self, user_id: int, increment: int = 1) -> None:
        """ Updates the user's ring counter.
        :param user_id: The ID of the member to update.
        :param increment: Incremention value. Default = 1.
        PS: Increment can be negative. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE SlothProfile SET rings = rings + %s WHERE user_id = %s", (increment, user_id))
        await db.commit()
        await mycursor.close()

    # ========== Get ===========
    async def get_ring_skill_action_by_user_id(self, user_id: int) -> Union[List[Union[int, str]], None]:
        """ Gets a ring skill action by reaction context.
        :param user_id: The ID of the user of the skill action. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM SlothSkills WHERE user_id = %s AND skill_type = 'ring'", (user_id,))
        skill_action = await mycursor.fetchone()
        await mycursor.close()
        return skill_action

    async def get_open_shop_items(self) -> List[List[Union[str, int]]]:
        """ Gets all open shop items. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM SlothSkills WHERE skill_type = 'potion' OR skill_type = 'ring'")
        potions = await mycursor.fetchall()
        await mycursor.close()
        return potions

    async def get_open_shop_embed(self, channel, perpetrator_id: int, price: int, item_name: str, emoji: str = '') -> discord.Embed:
        """ Makes an embedded message for a magic pull action.
        :param channel: The context channel.
        :param perpetrator_id: The ID of the perpetrator of the magic pulling.
        :param price: The price of the item that Merchant put into the shop.
        :param item_name: The name of the item put into the shop. """

        timestamp = await utils.get_timestamp()

        open_shop_embed = discord.Embed(
            title="A Merchant item has been put into the `Sloth Class Shop`!",
            timestamp=datetime.fromtimestamp(timestamp)
        )
        open_shop_embed.description = f"**<@{perpetrator_id}> put a `{item_name}` into the Sloth class shop, for the price of `{price}łł`!** {emoji}"
        open_shop_embed.color = discord.Color.green()

        open_shop_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Merchant.png")
        open_shop_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)

        return open_shop_embed

        
    @commands.command(aliases=["sellring", "ring"])
    @Player.skills_used(requirement=20)
    @Player.skill_on_cooldown(Skill.THREE, 36000)
    @Player.user_is_class('merchant')
    @Player.skill_mark()
    async def sell_ring(self, ctx) -> None:
        """ Puts a Wedding Ring for sale.
        
        * Skill cost: 100łł
        * Cooldown: 10 hours. """

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{ctx.author.mention}, you can only use this command in {self.bots_txt.mention}!**")

        member = ctx.author

        member_fx = await self.get_user_effects(member)

        if 'knocked_out' in member_fx:
            return await ctx.send(f"**{member.mention}, you can't use your skill, because you are knocked-out!**")

        if await self.get_skill_action_by_user_id_and_skill_type(member.id, 'ring'):
            return await ctx.send(f"**{member.mention}, you already have a ring in your shop!**")

        item_price = await prompt_number(self.client, ctx, f"**{member.mention}, for how much do you want to sell your ring?**", member)
        if item_price is None:
            return

        confirm = await ConfirmSkill(f"**{member.mention}, are you sure you want to spend `100łł` to put a ring in your shop with the price of `{item_price}`łł ?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not doing it, then, {member.mention}!**")

        _, exists = await Player.skill_on_cooldown(skill=Skill.THREE, seconds=36000).predicate(ctx)

        user_currency = await self.get_user_currency(member.id)
        if user_currency[1] < 100:
            return await ctx.send(f"**{member.mention}, you don't have `100łł`!**")

        await self.update_user_money(member.id, -100)

        item_emoji = '💍'

        try:
            current_timestamp = await utils.get_timestamp()
            await self.insert_skill_action(
                user_id=member.id, skill_type="ring", skill_timestamp=current_timestamp,
                target_id=member.id, channel_id=ctx.channel.id, price=item_price, emoji=item_emoji
            )
            if exists:
                await self.update_user_skill_ts(member.id, Skill.THREE, current_timestamp)
            else:
                await self.insert_user_skill_cooldown(ctx.author.id, Skill.THREE, current_timestamp)
            # Updates user's skills used counter
            await self.update_user_skills_used(user_id=member.id)
            open_shop_embed = await self.get_open_shop_embed(
                channel=ctx.channel, perpetrator_id=member.id, price=item_price, item_name='Wedding Ring', emoji=item_emoji)
            await ctx.send(embed=open_shop_embed)
        except Exception as e:
            print(e)
            return await ctx.send(f"**{member.mention}, something went wrong with it, try again later!**")
        else:
            await ctx.send(f"**{member}, your item is now in the shop, check `z!sloth_shop` to see it there!**")


    @commands.command()
    @commands.cooldown(1, 180, commands.BucketType.user)
    async def marry(self, ctx, suitor: discord.Member = None) -> None:
        """ Marries someone.
        :param suitor: The person to marry.
        PS: You need wedding rings to propose someone, buy one from your local Merchant.
        
        * Cost: 1000łł

        Ps: Both you and your suitor must have a sum of at least 2 rings in order to marry.
        """

        member = ctx.author

        member_marriage = await self.get_user_marriage(member.id)
        if member_marriage['partner']:
            self.client.get_command('marry').reset_cooldown(ctx)
            return await ctx.send(f"**You already have a partner, what do you think you're doing, {member.mention}?** 🤨")

        if not suitor:
            self.client.get_command('marry').reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform who you want to marry, {member.mention}!**")

        if member.id == suitor.id:
            self.client.get_command('marry').reset_cooldown(ctx)
            return await ctx.send(f"**You cannot marry yourself, {member.mention}!**")

        no_pf_view = discord.ui.View()
        no_pf_view.add_item(discord.ui.Button(style=5, label="Create Account", emoji="🦥", url="https://thelanguagesloth.com/profile/update"))

        if not (sloth_profile := await self.get_sloth_profile(member.id)):
            self.client.get_command('marry').reset_cooldown(ctx)
            return await ctx.send("You don't seem to have a Sloth Account, create one by clicking the button below:", view=no_pf_view)

        if not (target_sloth_profile := await self.get_sloth_profile(suitor.id)):
            self.client.get_command('marry').reset_cooldown(ctx)
            return await ctx.send(f"**Your suitor doesn't have a Sloth Account, tell them to create one before trying this again, {member.mention}!**")

        suitor_marriage = await self.get_user_marriage(suitor.id)
        if suitor_marriage['partner']:
            self.client.get_command('marry').reset_cooldown(ctx)
            return await ctx.send(f"**{suitor.mention} already has a partner, you savage, {member.mention}!** 😏")

        p1_rings, p2_rings = sloth_profile[7], target_sloth_profile[7]

        if p1_rings + p2_rings < 2:
            self.client.get_command('marry').reset_cooldown(ctx)
            return await ctx.send(f"**You two don't have enough rings to marry each other! The sum of your rings must be greater or equal to 2, {member.mention}!**")

        # Checks the member's money
        member_currency = await self.get_user_currency(member.id)
        if member_currency[1] < 1000:
            self.client.get_command('marry').reset_cooldown(ctx)
            return await ctx.send(f"**You don't have `1000łł` to marry {suitor.mention}, {member.mention}!**")

        # Asks confirmation
        confirm_view = ConfirmButton(member, timeout=60)
        embed = discord.Embed(
            title="__Confirmation__", color=member.color,
            description=f"**Are you sure you wanna marry {suitor.mention}, {member.mention}?**")
        await ctx.send(embed=embed, view=confirm_view)

        await confirm_view.wait()
        if confirm_view.value is None:
            self.client.get_command('marry').reset_cooldown(ctx)
            return await ctx.send(f"**{member.mention}, you took too long to answer...**")

        if not confirm_view.value:
            self.client.get_command('marry').reset_cooldown(ctx)
            return await ctx.send(f"**Not doing it then, {member.mention}!**")


        # Asks confirmation
        confirm_view = ConfirmButton(suitor, timeout=60)
        embed = discord.Embed(
            title="__Do you wanna Marry me?__", color=int('fa377d', 16), timestamp=ctx.message.created_at,
            description=f"**{suitor.mention}, {member.mention} is proposing you for `marriage`, do you accept it? 😳**"
        ).set_thumbnail(url='https://cdn.discordapp.com/emojis/738579957936029837.png?v=1')
        await ctx.send(content=suitor.mention, embed=embed, view=confirm_view)

        await confirm_view.wait()
        if confirm_view.value is None:
            return await ctx.send(f"**{suitor.mention}, you took too long to answer...**")

        if not confirm_view.value:
            return await ctx.send(f"**Not doing it then, {suitor.mention}!**")


        await self.update_user_money(member.id, -1000)
            
        # Update ring counters
        if p1_rings == 2 and p2_rings >= 1:
            await self.update_user_rings(member.id, -1)
            await self.update_user_rings(suitor.id, -1)
        elif p1_rings == 2 and p2_rings == 0:
            await self.update_user_rings(member.id, -2)
        elif p1_rings == 1:
            await self.update_user_rings(member.id, -1)
            await self.update_user_rings(suitor.id, -1)
        elif p1_rings == 0:
            await self.update_user_rings(suitor.id, -2)

        # Update marital status
        current_ts = await utils.get_timestamp()
        try:
            await self.insert_skill_action(
                user_id=member.id, skill_type='marriage', skill_timestamp=current_ts,
                target_id=suitor.id)
            filename, filepath = await self.make_marriage_image(member, suitor)
        except Exception as e:
            print(e)
            await ctx.send(f"**Something went wrong with this, {member.mention}!**")
        else:
            marriage_embed = await self.get_marriage_embed(ctx.channel, member, suitor, filename)
            await ctx.send(embed=marriage_embed, file=discord.File(filepath, filename=filename))
        finally:
            os.remove(filepath)

    @commands.command()
    @commands.cooldown(1, 180, commands.BucketType.user)
    async def divorce(self, ctx) -> None:
        """ Divorces your partner.
        
        Cost: 500łł """

        member = ctx.author

        member_marriage = await self.get_user_marriage(member.id)
        if not member_marriage['partner']:
            return await ctx.send(f"**You don't even have a partner, {member.mention}!** 😔")

        partner = discord.utils.get(ctx.guild.members, id=member_marriage['partner'])
        partner = discord.Object(id=member_marriage['partner']) if not partner else partner

        # Checks the member's money
        member_currency = await self.get_user_currency(member.id)
        if member_currency[1] < 500:
            self.client.get_command('divorce').reset_cooldown(ctx)
            return await ctx.send(f"**You don't have `500łł` to divorce <@{partner.id}>, {member.mention}!**")

        # Asks confirmation
        confirm_view = ConfirmButton(member, timeout=60)
        embed = discord.Embed(
            title="__Confirmation__", color=member.color,
            description=f"**Are you really sure you wanna divorce <@{partner.id}>, {member.mention}?**")
        await ctx.send(embed=embed, view=confirm_view)

        await confirm_view.wait()
        if confirm_view.value is None:
            return await ctx.send(f"**{member.mention}, you took too long to answer...**")

        if not confirm_view.value:
            return await ctx.send(f"**Not doing it then, {member.mention}!**")

        await self.update_user_money(member.id, -500)

        # Update marital status
        try:
            await self.delete_skill_action_by_target_id_and_skill_type(member.id, skill_type='marriage')
            await self.delete_skill_action_by_user_id_and_skill_type(member.id, skill_type='marriage')
        except Exception as e:
            print(e)
            await ctx.send(f"**Something went wrong with this, {member.mention}!**")
        else:
            divorce_embed = await self.get_divorce_embed(ctx.channel, member, partner)
            await ctx.send(content=f"<@{partner.id}>", embed=divorce_embed)

    async def get_user_marriage(self, user_id: int) -> Dict[str, Union[str, int]]:
        """ Gets the user's partner.
        :param user_id: The ID of the user. """

        kind = None

        skill_action = await self.get_skill_action_by_user_id_and_skill_type(user_id=user_id, skill_type='marriage')
        if skill_action:
            kind = 1
        else:
            skill_action = await self.get_skill_action_by_target_id_and_skill_type(target_id=user_id, skill_type='marriage')
            kind = 2

        marriage = {
            'user': None,
            'partner': None,
            'timestamp': None,
            'honeymoon': False
        }

        if not skill_action:
            return marriage

        if kind == 1:
            marriage = {'user': skill_action[0], 'partner': skill_action[3], 'timestamp': skill_action[2], "honeymoon": skill_action[8]}
        elif kind == 2:
            marriage = {'user': skill_action[3], 'partner': skill_action[0], 'timestamp': skill_action[2], "honeymoon": skill_action[8]}

        return marriage


    async def make_marriage_image(self, p1: discord.Member, p2: discord.Member) -> List[str]:

        filename = f"marriage_{p1.id}_{p2.id}.png"

        SlothCurrency = self.client.get_cog('SlothCurrency')

        medium = ImageFont.truetype("built titling sb.ttf", 60)
        background = Image.open(await SlothCurrency.get_user_specific_type_item(p1.id, 'background'))

        # Get PFPs
        pfp1 = await SlothCurrency.get_user_pfp(p1, 250)
        pfp2 = await SlothCurrency.get_user_pfp(p2, 250)


        background.paste(pfp1, (150, 200), pfp1)
        # background.paste(heart, (250, 250), heart)
        background.paste(pfp2, (400, 200), pfp2)

        # Writing names
        draw = ImageDraw.Draw(background)
        W, H = (800,600)

        w1, h1 = draw.textsize(str(p1), font=medium)
        w2, h2 = draw.textsize(str(p2), font=medium)

        draw.text(((W-w1)/2, 50), str(p1), fill="black", font=medium)
        draw.text(((W-w2)/2, 500), str(p2), fill="black", font=medium)

        filepath = f'media/temporary/{filename}'
        background.save(filepath, 'png', quality=90)
        return filename, filepath

    async def get_marriage_embed(self, channel, perpetrator: discord.Member, suitor: discord.Member, filename: str) -> discord.Embed:
        """ Makes an embedded message for a marriage action.
        :param channel: The context channel.
        :param perpetrator: The perpetrator of the proposal.
        :param suitor: The suitor. """

        timestamp = await utils.get_timestamp()

        marriage_embed = discord.Embed(
            title="A Marriage is now being Celebrated!",
            description=f"**{perpetrator.mention} has just married {suitor.mention}!** ❤️💍💍❤️",
            color=int('fa377d', 16),
            timestamp=datetime.fromtimestamp(timestamp)
        )
        
        marriage_embed.set_image(url=f"attachment://{filename}")
        marriage_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)

        return marriage_embed


    async def get_divorce_embed(self, channel, perpetrator: discord.Member, partner: Union[discord.User, discord.Member]) -> discord.Embed:
        """ Makes an embedded message for a divorce action.
        :param channel: The context channel.
        :param perpetrator: The perpetrator of the divorce.
        :param partner: The partner. """

        timestamp = await utils.get_timestamp()

        marriage_embed = discord.Embed(
            title="Oh no, a Marriage has been Ruined!",
            description=f"**{perpetrator.mention} has just divorced <@{partner.id}>!** 💔💔",
            color=int('fa377d', 16),
            timestamp=datetime.fromtimestamp(timestamp)
        )
        
        marriage_embed.set_thumbnail(url="https://media.tenor.com/images/99bba4c52c034aa6c29f51df547b6206/tenor.gif")
        marriage_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)

        return marriage_embed
        
    async def update_marriage_content(self, member_id: int) -> None:
        """ Updates marriage content to honeymoon.
        :param member_id: The ID of the member who's married. """

        mycursor, db = await the_database()
        await mycursor.execute("""
        UPDATE SlothSkills SET content = 'honeymoon' 
        WHERE user_id = %s AND skill_type = 'marriage' 
        OR target_id = %s AND skill_type = 'marriage'
        """, (member_id, member_id))
        await db.commit()
        await mycursor.close()