import discord
from discord.ext import commands
from .player import Player, Skill
from mysqldb import the_database
from extra.menu import ConfirmSkill
from extra import utils
import os
from datetime import datetime
import random

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))


class Warrior(Player):

    emoji = '<:Warrior:839498018792800286>'

    def __init__(self, client) -> None:
        self.client = client

    @commands.command(aliases=['ko', 'knock-out', 'knock_out', 'knock'])
    @Player.skill_on_cooldown()
    @Player.user_is_class('warrior')
    @Player.skill_mark()
    async def hit(self, ctx, target: discord.Member = None) -> None:
        """ Knocks someone out, making them unable to use their skills for 24 hours.
        :param target: The target member. """

        attacker = ctx.author

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{attacker.mention}, you can only use this command in {self.bots_txt.mention}!**")

        if await self.is_user_knocked_out(attacker.id):
            return await ctx.send(f"**{attacker.mention}, you can't use your skill, because you are knocked-out!**")

        if not target:
            return await ctx.send(f"**Please, inform a target member, {attacker.mention}!**")

        if attacker.id == target.id:
            return await ctx.send(f"**{attacker.mention}, you cannot knock yourself out!**")

        if target.bot:
            return await ctx.send(f"**{attacker.mention}, you cannot knock out a bot!**")

        target_currency = await self.get_user_currency(target.id)
        if not target_currency:
            return await ctx.send(f"**You cannot knock out someone who doesn't have an account, {attacker.mention}!**")

        if target_currency[7] == 'default':
            return await ctx.send(f"**You cannot knock out someone who has a `default` Sloth class, {attacker.mention}!**")

        if await self.is_user_protected(target.id):
            return await ctx.send(f"**{attacker.mention}, {target.mention} is protected, you can't knock them out!**")

        if await self.is_user_knocked_out(target.id):
            return await ctx.send(f"**{attacker.mention}, {target.mention} is already knocked out!**")

        confirmed = await ConfirmSkill(f"**{attacker.mention}, are you sure you want to knock {target.mention} out?**").prompt(ctx)
        if not confirmed:
            return await ctx.send("**Not knocking them out, then!**")

        _, exists = await Player.skill_on_cooldown(skill=Skill.ONE).predicate(ctx)

        try:
            current_timestamp = await utils.get_timestamp()
            # Don't need to store it, since it is forever
            await self.update_user_is_knocked_out(target.id, 1)
            await self.insert_skill_action(
                user_id=attacker.id, skill_type="hit", skill_timestamp=current_timestamp,
                target_id=target.id, channel_id=ctx.channel.id
            )
            if exists:
                await self.update_user_skill_ts(attacker.id, Skill.ONE, current_timestamp)
            else:
                await self.insert_user_skill_cooldown(ctx.author.id, Skill.ONE, current_timestamp)
            # Updates user's skills used counter
            await self.update_user_skills_used(user_id=attacker.id)

            hit_embed = await self.get_hit_embed(
                channel=ctx.channel, perpetrator_id=attacker.id, target_id=target.id)
            msg = await ctx.send(embed=hit_embed)
        except Exception as e:
            print(e)
            return await ctx.send(f"**Something went wrong and your `Hit` skill failed, {attacker.mention}!**")

    @commands.command(aliases=['crush', 'break'])
    @Player.skills_used(requirement=5)
    @Player.skill_on_cooldown(skill=Skill.TWO)
    @Player.user_is_class('warrior')
    @Player.skill_mark()
    async def smash(self, ctx, target: discord.Member = None) -> None:
        """ Has a 50% change of breaking someone's Divine Protection shield.
        :param target: The target who you are trying to smash the protection. """

        attacker = ctx.author

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{attacker.mention}, you can only use this command in {self.bots_txt.mention}!**")

        if await self.is_user_knocked_out(attacker.id):
            return await ctx.send(f"**{attacker.mention}, you can't use your skill, because you are knocked-out!**")

        if not target:
            return await ctx.send(f"**Please, inform a target member, {attacker.mention}!**")

        if attacker.id == target.id:
            return await ctx.send(f"**{attacker.mention}, you cannot do it on yourself!**")

        if target.bot:
            return await ctx.send(f"**{attacker.mention}, you cannot do it on a bot!**")

        target_currency = await self.get_user_currency(target.id)
        if not target_currency:
            return await ctx.send(f"**You cannot do it on someone who doesn't have an account, {attacker.mention}!**")

        if target_currency[7] == 'default':
            return await ctx.send(f"**You cannot do it on someone who has a `default` Sloth class, {attacker.mention}!**")

        if not await self.is_user_protected(target.id):
            return await ctx.send(f"**{attacker.mention}, {target.mention} doesn't have a protection!**")

        user = await self.get_user_currency(attacker.id)
        if not user[1] >= 50:
            return await ctx.send(f"**You don't have `50łł` to use this skill, {attacker.mention}!**")

        confirmed = await ConfirmSkill(f"**{attacker.mention}, are you sure you want to smash {target.mention}'s Divine Protection shield for `50łł`?**").prompt(ctx)
        if not confirmed:
            return await ctx.send("**Not hacking them, then!**")

        _, exists = await Player.skill_on_cooldown(skill=Skill.TWO).predicate(ctx)

        current_timestamp = await utils.get_timestamp()
        # Upate user's money
        await self.update_user_money(attacker.id, -50)
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
                await self.update_user_protected(target.id, 0)
                await self.delete_skill_action_by_target_id_and_skill_type(target.id, 'divine_protection')
            except Exception as e:
                print(e)
                await ctx.send(f"**For some reason I couldn't smash their protection shield, {attacker.mention}!**")

            else:
                smash_embed = await self.get_smash_embed(
                channel=ctx.channel, perpetrator_id=attacker.id, target_id=target.id)
                await ctx.send(embed=smash_embed)
        else:
            await ctx.send(f"**You had a `50%` chance of smashing {target.mention}'s Divine Protection shield, but you missed it, {attacker.mention}!**")

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

    async def update_user_is_knocked_out(self, user_id: int, is_it: int) -> None:
        """ Updates the user's protected state.
        :param user_id: The ID of the member to update.
        :param is_it: Whether it's gonna be set to true or false. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE SlothProfile SET knocked_out = %s WHERE user_id = %s", (is_it, user_id))
        await db.commit()
        await mycursor.close()

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
        hit_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

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
        smash_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

        return smash_embed

    @commands.command()
    @Player.skills_used(requirement=20)
    @Player.skill_on_cooldown(Skill.THREE)
    @Player.user_is_class('warrior')
    @Player.skill_mark()
    @Player.not_ready()
    async def unknown(self, ctx, target: discord.Member = None) -> None:
        """ Unknown skill, that is TBD. """

        pass