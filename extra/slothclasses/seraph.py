import discord
from discord.ext import commands
from .player import Player
from mysqldb import the_database
from extra.menu import ConfirmSkill
import os
from datetime import datetime
import random

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))


class Seraph(Player):

    def __init__(self, client) -> None:
        self.client = client
        # self.bots_txt = await self.client.fetch_channel(bots_and_commands_channel_id)

    @commands.command(aliases=['dp', 'divine', 'protection'])
    @Player.skill_on_cooldown()
    @Player.user_is_class('seraph')
    @Player.skill_mark()
    async def divine_protection(self, ctx, target: discord.Member = None) -> None:
        """ Gives a Divine Protection shield to a member, so they are protected against
        attacks for 24 hours.
        :param target: The target member. (Optional)
        PS: If target not provided, you are the target. """

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{ctx.author.mention}, you can only use this command in {self.bots_txt.mention}!**")

        if await self.is_user_knocked_out(ctx.author.id):
            return await ctx.send(f"**{ctx.author.mention}, you can't use your skill, because you are knocked-out!**")

        if not target:
            target = ctx.author

        target_currency = await self.get_user_currency(target.id)
        if not target_currency:
            return await ctx.send(f"**You cannot protect someone who doesn't have an account, {ctx.author.mention}!**")

        if target_currency[7] == 'default':
            return await ctx.send(f"**You cannot protect someone who has a `default` Sloth class, {ctx.author.mention}!**")

        if await self.is_user_protected(target.id):
            return await ctx.send(f"**{target.mention} is already protected, {ctx.author.mention}!**")

        confirmed = await ConfirmSkill(f"**{ctx.author.mention}, are you sure you want to use your skill, to protect {target.mention}?**").prompt(ctx)
        if confirmed:
            await self.check_cooldown(user_id=ctx.author.id, skill_number=1)

            current_timestamp = await self.get_timestamp()
            await self.insert_skill_action(
                user_id=ctx.author.id, skill_type="divine_protection", skill_timestamp=current_timestamp,
                target_id=target.id, channel_id=ctx.channel.id
            )
            await self.update_user_protected(target.id, 1)
            await self.update_user_action_skill_ts(ctx.author.id, current_timestamp)
            # Updates user's skills used counter
            await self.update_user_skills_used(user_id=ctx.author.id)
            divine_protection_embed = await self.get_divine_protection_embed(
                channel=ctx.channel, perpetrator_id=ctx.author.id, target_id=target.id)
            await ctx.send(embed=divine_protection_embed)
        else:
            await ctx.send("**Not protecting anyone, then!**")

    @commands.command()
    @Player.skills_used(requirement=5)
    @Player.skill_on_cooldown(skill_number=2)
    @Player.user_is_class('seraph')
    @Player.skill_mark()
    # @Player.not_ready()
    async def reinforce(self, ctx) -> None:
        """ Gets a 35% chance of reinforcing all of their protected people's Divine Protection shield,
        by making it last for one more day and a 20% chance of getting a protection for themselves too
        (in case they don't have one already). """

        perpetrator = ctx.author

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{perpetrator.mention}, you can only use this command in {self.bots_txt.mention}!**")

        if await self.is_user_knocked_out(perpetrator.id):
            return await ctx.send(f"**{perpetrator.mention}, you can't use your skill, because you are knocked-out!**")

        # Gets all active Divine Protection shields from the user
        shields = await self.get_skill_action_by_user_id_and_skill_type(user_id=perpetrator.id, skill_type='divine_protection')
        if not shields:
            return await ctx.send(f"**You don't have any active shield, {perpetrator.mention}!**")

        user = await self.get_user_currency(perpetrator.id)
        if not user[1] >= 50:
            return await ctx.send(f"**You don't have `50łł` to use this skill, {perpetrator.mention}!**")

        # Confirms the use of the skill
        confirm = await ConfirmSkill(
            f"**Are you sure you want to reinforce `{len(shields)}` active Divine Protection shields for `50łł`, {perpetrator.mention}?**").prompt(ctx)
        # User confirmed the use the skill
        if not confirm:
            return await ctx.send(f"**Not reinforcing them, then, {perpetrator.mention}!**")

        await self.check_cooldown(user_id=perpetrator.id, skill_number=2)

        current_timestamp = await self.get_timestamp()

        # Upate user's money
        await self.update_user_money(perpetrator.id, -50)
        # Update perpetrator's second skill timestamp
        await self.update_user_action_skill_two_ts(user_id=perpetrator.id, current_ts=current_timestamp)
        # Updates user's skills used counter
        await self.update_user_skills_used(user_id=perpetrator.id)

        # Calculates chance (35%) of reinforcing the shields of the targets
        n1 = random.random()
        if n1 <= 0.35:
            # Tries to execute it and update the database
            try:
                # Update active Divine Protection shields' time (+1 day)
                await self.reinforce_shields(perpetrator_id=perpetrator.id)
            except Exception as e:
                print(e)
                await ctx.send(f"**For some reason I couldn't reinforce the shield(s), {perpetrator.mention}!**")
            else:
                reinforce_shields_embed = await self.get_reinforce_shields_embed(
                    channel=ctx.channel, perpetrator_id=perpetrator.id, shields_len=len(shields))
                await ctx.send(embed=reinforce_shields_embed)
        else:
            await ctx.send(f"**You had a `35%` chance of reinforcing all active Divine Protection shields, but you missed it, {perpetrator.mention}!**")

        # Checks whether the perpetrator already has a Divien Protection shield
        if not await self.is_user_protected(perpetrator.id):
            n2 = random.random()
            # Calculates the chance (20%) of getting a shield for the perpetrator
            if n2 <= 0.2:
                # Tries to execute it and update the database
                try:
                    # Give user a shield
                    await self.insert_skill_action(
                        user_id=perpetrator.id, skill_type="divine_protection", skill_timestamp=current_timestamp,
                        target_id=perpetrator.id, channel_id=ctx.channel.id
                    )

                except Exception as e:
                    print(e)
                    await ctx.send(f"**For some reason I couldn't give you a shield, {perpetrator.mention}!**")
                else:
                    self_shield_embed = await self.get_self_shield_embed(
                        channel=ctx.channel, perpetrator_id=perpetrator.id)
                    await ctx.send(embed=self_shield_embed)

            else:
                await ctx.send(f"**You had a `20%` chance of getting a Divine Protection shield for yourself, but you missed it, {perpetrator.mention}!**")

    async def check_protections(self) -> None:
        """ Check on-going protections and their expiration time. """

        divine_protections = await self.get_expired_protections()
        for dp in divine_protections:
            await self.update_user_protected(dp[3], 0)
            await self.delete_skill_action_by_target_id_and_skill_type(dp[3], 'divine_protection')

            channel = self.bots_txt

            await channel.send(
                content=f"<@{dp[0]}>, <@{dp[3]}>",
                embed=discord.Embed(
                    description=f"**<@{dp[3]}>'s `Divine Protection` from <@{dp[0]}> just expired!**",
                    color=discord.Color.red()))

    async def update_user_protected(self, user_id: int, protected: int) -> None:
        """ Updates the user's protected state.
        :param user_id: The ID of the member to update.
        :param protected: Whether it's gonna be set to true or false. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE UserCurrency SET protected = %s WHERE user_id = %s", (protected, user_id))
        await db.commit()
        await mycursor.close()

    async def reinforce_shields(self, perpetrator_id: int) -> None:
        """ Reinforces all active Divine Protection shields.
        :param perpetrator_id: The ID of the perpetrator of those shields. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE SlothSkills SET skill_timestamp = skill_timestamp + 86400 WHERE user_id = %s", (perpetrator_id,))
        await db.commit()
        await mycursor.close()

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

    async def get_reinforce_shields_embed(self, channel, perpetrator_id: int, shields_len: int) -> discord.Embed:
        """ Makes an embedded message for a shield reinforcement action.
        :param channel: The context channel.
        :param perpetrator_id: The ID of the perpetrator of the shield reinforcement.
        :param shields_len: The amount of active shields that the perpetrator have. """

        timestamp = await self.get_timestamp()

        reinforce_shields_embed = discord.Embed(
            title="A Shield Reinforcement has been executed!",
            timestamp=datetime.utcfromtimestamp(timestamp)
        )
        reinforce_shields_embed.description=f"🛡️ <@{perpetrator_id}> reinforced `{shields_len}` active shields; now they have more 24 hours of duration! 🛡️💪"
        reinforce_shields_embed.color=discord.Color.green()

        reinforce_shields_embed.set_author(name='35% of chance', url=self.client.user.avatar_url)
        reinforce_shields_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Seraph.png")
        reinforce_shields_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

        return reinforce_shields_embed

    async def get_self_shield_embed(self, channel, perpetrator_id: int) -> discord.Embed:
        """ Makes an embedded message for a shield reinforcement action.
        :param channel: The context channel.
        :param perpetrator_id: The ID of the perpetrator of the shield reinforcement.
        :param shields_len: The amount of active shields that the perpetrator have. """

        timestamp = await self.get_timestamp()

        self_shield_embed = discord.Embed(
            title="A Divine Protection shield has been Given!",
            timestamp=datetime.utcfromtimestamp(timestamp)
        )
        self_shield_embed.description=f"🛡️ <@{perpetrator_id}> got a shield for themselves for reinforcing other shields! 🛡️💪"
        self_shield_embed.color=discord.Color.green()

        self_shield_embed.set_author(name='20% of chance', url=self.client.user.avatar_url)
        self_shield_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Seraph.png")
        self_shield_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon_url)

        return self_shield_embed