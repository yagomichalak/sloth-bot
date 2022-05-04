from extra.prompt.menu import ConfirmButton
import discord
from discord.ext import commands
from .player import Player, Skill
from mysqldb import the_database
from extra.menu import ConfirmSkill
from extra.select import WarriorUserItemSelect
from extra.view import BasicUserCheckView
from extra import utils
import os
from datetime import datetime
import random
from typing import List, Union

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID', 123))


class Warrior(Player):

    emoji = '<:Warrior:839498018792800286>'

    def __init__(self, client) -> None:
        self.client = client

    @commands.command(aliases=['ko', 'knock-out', 'knock_out', 'knock'])
    @Player.poisoned()
    @Player.skill_on_cooldown()
    @Player.skills_locked()
    @Player.user_is_class('warrior')
    @Player.skill_mark()
    async def hit(self, ctx, target: discord.Member = None) -> None:
        """ Knocks someone out, making them unable to use their skills for 24 hours.
        :param target: The target member. """

        attacker = ctx.author

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{attacker.mention}, you can only use this command in {self.bots_txt.mention}!**")

        attacker_fx = await self.get_user_effects(attacker)

        if 'knocked_out' in attacker_fx:
            return await ctx.send(f"**{attacker.mention}, you can't use your skill, because you are knocked-out!**")

        if not target:
            return await ctx.send(f"**Please, inform a target member, {attacker.mention}!**")

        if attacker.id == target.id:
            return await ctx.send(f"**{attacker.mention}, you cannot knock yourself out!**")

        if target.bot:
            return await ctx.send(f"**{attacker.mention}, you cannot knock out a bot!**")

        target_sloth_profile = await self.get_sloth_profile(target.id)
        if not target_sloth_profile:
            return await ctx.send(f"**You cannot knock out someone who doesn't have an account, {attacker.mention}!**")

        if target_sloth_profile[1] == 'default':
            return await ctx.send(f"**You cannot knock out someone who has a `default` Sloth class, {attacker.mention}!**")

        target_fx = await self.get_user_effects(target)

        if 'protected' in target_fx:
            return await ctx.send(f"**{attacker.mention}, {target.mention} is protected, you can't knock them out!**")

        if 'knocked_out' in target_fx:
            return await ctx.send(f"**{attacker.mention}, {target.mention} is already knocked out!**")

        confirmed = await ConfirmSkill(f"**{attacker.mention}, are you sure you want to knock {target.mention} out?**").prompt(ctx)
        if not confirmed:
            return await ctx.send("**Not knocking them out, then!**")

        if ctx.invoked_with == 'mirror':
            mirrored_skill = await self.get_skill_action_by_user_id_and_skill_type(user_id=attacker.id, skill_type='mirror')
            if not mirrored_skill:
                return await ctx.send(f"**Something went wrong with this, {attacker.mention}!**")
        else:
            _, exists = await Player.skill_on_cooldown(skill=Skill.ONE).predicate(ctx)

        try:
            current_timestamp = await utils.get_timestamp()
            # Don't need to store it, since it is forever
            await self.insert_skill_action(
                user_id=attacker.id, skill_type="hit", skill_timestamp=current_timestamp,
                target_id=target.id, channel_id=ctx.channel.id
            )
            if ctx.invoked_with != 'mirror':
                if exists:
                    await self.update_user_skill_ts(attacker.id, Skill.ONE, current_timestamp)
                else:
                    await self.insert_user_skill_cooldown(attacker.id, Skill.ONE, current_timestamp)
            # Updates user's skills used counter
            await self.update_user_skills_used(user_id=attacker.id)

            hit_embed = await self.get_hit_embed(
                channel=ctx.channel, perpetrator_id=attacker.id, target_id=target.id)
            await ctx.send(embed=hit_embed)
        except Exception as e:
            print(e)
            return await ctx.send(f"**Something went wrong and your `Hit` skill failed, {attacker.mention}!**")
        else:
            if 'reflect' in target_fx:
                await self.reflect_attack(ctx, attacker, target, 'hit')

    @commands.command(aliases=['crush', 'break'])
    @Player.poisoned()
    @Player.skills_used(requirement=5)
    @Player.skill_on_cooldown(skill=Skill.TWO)
    @Player.skills_locked()
    @Player.user_is_class('warrior')
    @Player.skill_mark()
    async def smash(self, ctx, target: discord.Member = None) -> None:
        """ Has a 50% change of breaking someone's Divine Protection shield.
        :param target: The target who you are trying to smash the protection. """

        attacker = ctx.author

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{attacker.mention}, you can only use this command in {self.bots_txt.mention}!**")

        attacker_fx = await self.get_user_effects(attacker)

        if 'knocked_out' in attacker_fx:
            return await ctx.send(f"**{attacker.mention}, you can't use your skill, because you are knocked-out!**")

        if not target:
            return await ctx.send(f"**Please, inform a target member, {attacker.mention}!**")

        if attacker.id == target.id:
            return await ctx.send(f"**{attacker.mention}, you cannot do it on yourself!**")

        if target.bot:
            return await ctx.send(f"**{attacker.mention}, you cannot do it on a bot!**")

        target_sloth_profile = await self.get_sloth_profile(target.id)
        if not target_sloth_profile:
            return await ctx.send(f"**You cannot do it on someone who doesn't have an account, {attacker.mention}!**")

        if target_sloth_profile[1] == 'default':
            return await ctx.send(f"**You cannot do it on someone who has a `default` Sloth class, {attacker.mention}!**")

        target_fx = await self.get_user_effects(target)

        if 'protected' not in target_fx:
            return await ctx.send(f"**{attacker.mention}, {target.mention} doesn't have a protection!**")

        user = await self.get_user_currency(attacker.id)
        if user[1] < 50:
            return await ctx.send(f"**You don't have `50łł` to use this skill, {attacker.mention}!**")

        confirmed = await ConfirmSkill(f"**{attacker.mention}, are you sure you want to smash {target.mention}'s Divine Protection shield for `50łł`?**").prompt(ctx)
        if not confirmed:
            return await ctx.send("**Not hacking them, then!**")

        _, exists = await Player.skill_on_cooldown(skill=Skill.TWO).predicate(ctx)

        current_timestamp = await utils.get_timestamp()
        # Upate user's money
        await self.client.get_cog('SlothCurrency').update_user_money(attacker.id, -50)
        # # Update attacker's second skill timestamp
        if exists:
            await self.update_user_skill_ts(user_id=attacker.id, skill=Skill.TWO, new_skill_ts=current_timestamp)
        else:
            await self.insert_user_skill_cooldown(ctx.author.id, Skill.TWO, current_timestamp)
        # Updates user's skills used counter
        await self.update_user_skills_used(user_id=attacker.id)

        # Calculates chance of smashing someone's Divine Protection shield
        if random.random() <= 0.5:
            try:
                await self.delete_skill_action_by_target_id_and_skill_type(target.id, 'divine_protection')
            except Exception as e:
                print(e)
                await ctx.send(f"**For some reason I couldn't smash their protection shield, {attacker.mention}!**")

            else:
                smash_embed = await self.get_smash_embed(
                channel=ctx.channel, perpetrator_id=attacker.id, target_id=target.id)
                await ctx.send(embed=smash_embed)
                if 'reflect' in target_fx and 'protected' in attacker_fx:
                    await self.delete_skill_action_by_target_id_and_skill_type(attacker.id, 'divine_protection')
                    await self.reflect_attack(ctx, attacker, target, 'smash')
        else:
            await ctx.send(f"**You had a `50%` chance of smashing {target.mention}'s Divine Protection shield, but you missed it, {attacker.mention}!**")

    async def check_knock_outs(self) -> None:

        """ Check on-going knock-outs and their expiration time. """

        knock_outs = await self.get_expired_knock_outs()
        for ko in knock_outs:
            await self.delete_skill_action_by_target_id_and_skill_type(ko[3], 'hit')

            channel = self.bots_txt

            await channel.send(
                content=f"<@{ko[0]}>",
                embed=discord.Embed(
                    description=f"**<@{ko[3]}> got better from <@{ko[0]}>'s knock-out! 🤕**",
                    color=discord.Color.red()))

    async def get_hit_embed(self, channel, perpetrator_id: int, target_id: int) -> discord.Embed:
        """ Makes an embedded message for a knock-out action.
        :param channel: The context channel.
        :param perpetrator_id: The ID of the perpetrator of the knock-out.
        :param target_id: The ID of the target of the knock-out. """

        timestamp = await utils.get_timestamp()

        hit_embed = discord.Embed(
            title="Someone was Knocked Out!",
            timestamp=datetime.fromtimestamp(timestamp)
        )
        hit_embed.description = f"**<@{perpetrator_id}> knocked <@{target_id}> out!** 😵"
        hit_embed.color = discord.Color.green()

        hit_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Warrior.png")
        hit_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)

        return hit_embed

    async def get_smash_embed(self, channel, perpetrator_id: int, target_id: int) -> discord.Embed:
        """ Makes an embedded message for a smash action.
        :param channel: The context channel.
        :param perpetrator_id: The ID of the perpetrator of the smash action.
        :param target_id: The ID of the target of the smash action. """

        timestamp = await utils.get_timestamp()

        smash_embed = discord.Embed(
            title="Someone just got Vulnerable!",
            timestamp=datetime.fromtimestamp(timestamp)
        )
        smash_embed.description = f"**<@{perpetrator_id}> smashed <@{target_id}>'s' Divine Protection shield; it's gone!** 🚫"
        smash_embed.color = discord.Color.green()

        smash_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Warrior.png")
        smash_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)

        return smash_embed

    @commands.command(aliases=['ripoff', 'rip', 'shred'])
    @Player.poisoned()
    @Player.skills_used(requirement=20)
    @Player.skill_on_cooldown(Skill.THREE, seconds=172800)
    @Player.skills_locked()
    @Player.user_is_class('warrior')
    @Player.skill_mark()
    async def rip_off(self, ctx, target: discord.Member = None) -> None:
        """ Will rip off an item of your choice of your target.
        :param target: The target member.
        
        * Cooldown: 2 days.
        * Price: Half of the price of your target's ripped-off item

        Ps: 
        - The menu containing the target's items will appear when using this command on them.
        - You will only see up to 25 items of your target, the first 25 items.
        - If an item is ripped-off, it's removed permanently from the member's inventory.
        """

        attacker = ctx.author

        if ctx.channel.id != self.bots_txt.id:
            return await ctx.send(f"**You can only use this skill in {self.bots_txt.mention}, {attacker.mention}!**")

        attacker_fx = await self.get_user_effects(attacker)
        if 'knocked_out' in attacker_fx:
            return await ctx.send(f"**You can't use this skills because you are knocked-out, {attacker.mention}!**")
    
        if not target:
            return await ctx.send(f"**Please, inform a target, {attacker.mention}!**")

        if attacker.id == target.id:
            return await ctx.send(f"**{attacker.mention}, you cannot do it on yourself!**")

        if target.bot:
            return await ctx.send(f"**{attacker.mention}, you cannot do it on a bot!**")

        target_sloth_profile = await self.get_sloth_profile(target.id)
        if not target_sloth_profile:
            return await ctx.send(f"**You cannot do it on someone who doesn't have an account, {attacker.mention}!**")

        if target_sloth_profile[1] == 'default':
            return await ctx.send(f"**You cannot do it on someone who has a `default` Sloth class, {attacker.mention}!**")

        target_fx = await self.get_user_effects(target)
        if 'protected' in target_fx:
            return await ctx.send(f"**You cannot attack {target.mention} because they are protected, {attacker.mention}!**")

        SlothCurrency = self.client.get_cog('SlothCurrency')

        target_items = await SlothCurrency.get_user_registered_items(target.id)       
        if not target_items:
            return await ctx.send(f"**{target.mention} doesn't have any items to rip off, {attacker.mention}!**")

        view = BasicUserCheckView(attacker)
        view.add_item(WarriorUserItemSelect(target_items[:25]))
        await ctx.send(f"**{target.display_name}**'s items:", view=view)
        await view.wait()
        if not hasattr(view, 'selected_item'):
            return await ctx.send(f"**Timeout, {attacker.mention}!**")
        
        item = view.selected_item
        cost = int(item[6]/2)
        confirm_view = ConfirmButton(attacker, timeout=60)
        await ctx.send(embed=discord.Embed(
            title="__Confirm__",
            description=f"**Do you really wanna rip off {target.mention}'s `{item[4]}` item for the cost of `{cost}łł`, {attacker.mention}?**",
            color=discord.Color.green()), view=confirm_view
        )
        await confirm_view.wait()
        if confirm_view.value is None or not confirm_view.value:
            return await ctx.send(f"**Not doing it, then!**")

        _, exists = await Player.skill_on_cooldown(skill=Skill.THREE, seconds=172800).predicate(ctx)

        attacker_currency = await self.get_user_currency(attacker.id)
        if attacker_currency[1] < cost:
            return await ctx.send(f"**You don't have {item[6]}łł to rip off the {item[4]} item, {attacker.mention}!**")

        await self.client.get_cog('SlothCurrency').update_user_money(attacker.id, -cost)
        try:
            current_timestamp = await utils.get_timestamp()
            # Don't need to store it, since it is forever
            if exists:
                await self.update_user_skill_ts(attacker.id, Skill.THREE, current_timestamp)
            else:
                await self.insert_user_skill_cooldown(attacker.id, Skill.THREE, current_timestamp)
            # Updates user's skills used counter
            await self.update_user_skills_used(user_id=attacker.id)
            await SlothCurrency.remove_user_item(target.id, item[4])

        except Exception as e:
            print(e)
            return await ctx.send(f"**Something went wrong and your `Rip Off` skill failed, {attacker.mention}!**")
        else:
            rip_off_embed = await self.get_rip_off_embed(
                channel=ctx.channel, perpetrator_id=attacker.id, target_id=target.id, item=item)
            await ctx.send(embed=rip_off_embed)


    async def get_rip_off_embed(self, channel, perpetrator_id: int, target_id: int, item: List[Union[str, int]]) -> discord.Embed:
        """ Makes an embedded message for a rip off skill.
        :param channel: The context channel.
        :param perpetrator_id: The ID of the perpetrator of the rip off skill.
        :param target_id: The ID of the target of the rip off skill.
        :param item: The item. """

        timestamp = await utils.get_timestamp()

        rip_off_embed = discord.Embed(
            title="Someone just lost an Item!",
            description=f"**<@{perpetrator_id}> ripped of <@{target_id}>'s {item[4]} item that was worth `{item[6]}łł`!** <:warrior_scratch:869221184925995079>",
            color=discord.Color.green(),
            timestamp=datetime.fromtimestamp(timestamp),
            url=f"https://thelanguagesloth.com/shop/{item[7]}"
        )
        
        rip_off_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Warrior.png")
        rip_off_embed.set_image(url=f"https://thelanguagesloth.com/media/{item[3]}")
        rip_off_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)

        return rip_off_embed


    @commands.command(aliases=['disorient', 'disorientate'])
    @Player.poisoned()
    @Player.skills_used(requirement=50)
    @Player.skill_on_cooldown(skill=Skill.FOUR, seconds=172800)
    @Player.skills_locked()
    @Player.user_is_class('warrior')
    @Player.skill_mark()
    @Player.not_ready()
    async def poison(self, ctx, target: discord.Member = None) -> None:
        """ Poisons someone so they get dizzy, disoriented to the point
        they can barely use skills, Social, Currency and RolePlay commands.
        :param target: The member to poison.

        • Delay = 2 days
        • Cost = 100łł  """

        attacker = ctx.author

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{attacker.mention}, you can only use this command in {self.bots_txt.mention}!**")

        attacker_fx = await self.get_user_effects(attacker)

        if 'knocked_out' in attacker_fx:
            return await ctx.send(f"**{attacker.mention}, you can't use your skill, because you are knocked-out!**")

        if not target:
            return await ctx.send(f"**Please, inform a target member, {attacker.mention}!**")

        if attacker.id == target.id:
            return await ctx.send(f"**{attacker.mention}, you cannot lock your own skills!**")

        if target.bot:
            return await ctx.send(f"**{attacker.mention}, you cannot use this skill on a bot!**")

        target_sloth_profile = await self.get_sloth_profile(target.id)
        if not target_sloth_profile:
            return await ctx.send(f"**You cannot lock someone who doesn't have an account, {attacker.mention}!**")

        if target_sloth_profile[1] == 'default':
            return await ctx.send(f"**You cannot wire someone who has a `default` Sloth class, {attacker.mention}!**")

        target_fx = await self.get_user_effects(target)

        if 'protected' in target_fx:
            return await ctx.send(f"**{attacker.mention}, {target.mention} is protected, you can't lock their skills!**")

        if 'poison' in target_fx:
            return await ctx.send(f"**{attacker.mention}, {target.mention} is already poisoned!**")

        user_currency = await self.get_user_currency(attacker.id)
        if user_currency[1] < 100:
            return await ctx.send(f"**You don't have 100łł to use this skill, {attacker.mention}!**")

        confirmed = await ConfirmSkill(f"**{attacker.mention}, are you sure you want to poison {target.mention} for `100łł`?**").prompt(ctx)
        if not confirmed:
            return await ctx.send("**Not locking their skills, then!**")

        _, exists = await Player.skill_on_cooldown(skill=Skill.FOUR, seconds=172800).predicate(ctx)

        try:
            current_timestamp = await utils.get_timestamp()
            await self.insert_skill_action(
                user_id=attacker.id, skill_type="poison", skill_timestamp=current_timestamp,
                target_id=target.id, channel_id=ctx.channel.id
            )
            if exists:
                await self.update_user_skill_ts(attacker.id, Skill.FOUR, current_timestamp)
            else:
                await self.insert_user_skill_cooldown(ctx.author.id, Skill.FOUR, current_timestamp)
            # Updates user's skills used counter
            await self.update_user_skills_used(user_id=attacker.id)
            await self.client.get_cog('SlothCurrency').update_user_money(attacker.id -100)

        except Exception as e:
            print(e)
            return await ctx.send(f"**For some reason I couldn't poison your target, {attacker.mention}!**")

        else:
            poison_embed = await self.get_poison_embed(
                channel=ctx.channel, perpetrator_id=attacker.id, target_id=target.id)
            await ctx.send(embed=poison_embed)
            if 'reflect' in target_fx:
                await self.reflect_attack(ctx, attacker, target, 'poison')


    async def get_poison_embed(self, channel, perpetrator_id: int, target_id: int, item: List[Union[str, int]]) -> discord.Embed:
        """ Makes an embedded message for a poison.
        :param channel: The context channel.
        :param perpetrator_id: The ID of the perpetrator of the poison skill.
        :param target_id: The ID of the target of the poison skill.
        :param item: The item. """

        timestamp = await utils.get_timestamp()

        poison_embed = discord.Embed(
            title="Someone just got Poisoned!",
            description=f"**<@{perpetrator_id}> poisoned <@{target_id}> so they are not dizzy and disoriented! 💀**",
            color=discord.Color.green(),
            timestamp=datetime.fromtimestamp(timestamp)
        )
        
        poison_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Warrior.png")
        poison_embed.set_image(url='https://c.tenor.com/Qf37BPPRfIcAAAAC/poison-poisoning.gif')
        poison_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)

        return poison_embed