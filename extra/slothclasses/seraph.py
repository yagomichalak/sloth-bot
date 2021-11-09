import discord
from discord.ext import commands
from .player import Player, Skill
from mysqldb import the_database
from extra.menu import ConfirmSkill
from extra import utils
import os
from datetime import datetime
import random
from typing import List, Optional

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))


class Seraph(Player):

    emoji = '<:Seraph:839498018998976563>'

    @commands.command(aliases=['dp', 'divine', 'protection'])
    @Player.poisoned()
    @Player.skill_on_cooldown()
    @Player.skills_locked()
    @Player.user_is_class('seraph')
    @Player.skill_mark()
    async def divine_protection(self, ctx, target: discord.Member = None) -> None:
        """ Gives a Divine Protection shield to a member, so they are protected against
        attacks for 24 hours.
        :param target: The target member. (Optional)
        PS: If target not provided, you are the target. """


        perpetrator = ctx.author

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{perpetrator.mention}, you can only use this command in {self.bots_txt.mention}!**")

        perpetrator_fx = await self.get_user_effects(perpetrator)

        if 'knocked_out' in perpetrator_fx:
            return await ctx.send(f"**{perpetrator.mention}, you can't use your skill, because you are knocked-out!**")

        if not target:
            target = perpetrator

        if target.bot:
            return await ctx.send(f"**You cannot protect a bot, {perpetrator.mention}!**")

        target_sloth_profile = await self.get_sloth_profile(target.id)
        if not target_sloth_profile:
            return await ctx.send(f"**You cannot protect someone who doesn't have an account, {perpetrator.mention}!**")

        if target_sloth_profile[1] == 'default':
            return await ctx.send(f"**You cannot protect someone who has a `default` Sloth class, {perpetrator.mention}!**")

        target_fx = await self.get_user_effects(target)

        if 'protected' in target_fx:
            return await ctx.send(f"**{target.mention} is already protected, {perpetrator.mention}!**")

        confirmed = await ConfirmSkill(f"**{perpetrator.mention}, are you sure you want to use your skill, to protect {target.mention}?**").prompt(ctx)
        if not confirmed:
            return await ctx.send("**Not protecting anyone, then!**")

        if ctx.invoked_with == 'mirror':
            mirrored_skill = await self.get_skill_action_by_user_id_and_skill_type(user_id=perpetrator.id, skill_type='mirror')
            if not mirrored_skill:
                return await ctx.send(f"**Something went wrong with this, {perpetrator.mention}!**")
        else:
            _, exists = await Player.skill_on_cooldown(skill=Skill.ONE).predicate(ctx)

        current_timestamp = await utils.get_timestamp()
        await self.insert_skill_action(
            user_id=perpetrator.id, skill_type="divine_protection", skill_timestamp=current_timestamp,
            target_id=target.id, channel_id=ctx.channel.id
        )
        if ctx.invoked_with != 'mirror':
            if exists:
                await self.update_user_skill_ts(perpetrator.id, Skill.ONE, current_timestamp)
            else:
                await self.insert_user_skill_cooldown(perpetrator.id, Skill.ONE, current_timestamp)

        # Updates user's skills used counter
        await self.update_user_skills_used(user_id=perpetrator.id)
        divine_protection_embed = await self.get_divine_protection_embed(
            channel=ctx.channel, perpetrator_id=perpetrator.id, target_id=target.id)
        await ctx.send(embed=divine_protection_embed)
            

    @commands.command()
    @Player.poisoned()
    @Player.skills_used(requirement=5)
    @Player.skill_on_cooldown(skill=Skill.TWO)
    @Player.skills_locked()
    @Player.user_is_class('seraph')
    @Player.skill_mark()
    async def reinforce(self, ctx) -> None:
        """ Gets a 50% chance of reinforcing all of their protected people's Divine Protection shield,
        by making it last for one more day and a 45% chance of getting a protection for themselves too
        (in case they don't have one already). """

        perpetrator = ctx.author

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{perpetrator.mention}, you can only use this command in {self.bots_txt.mention}!**")

        perpetrator_fx = await self.get_user_effects(perpetrator)

        if 'knocked_out' in perpetrator_fx:
            return await ctx.send(f"**{perpetrator.mention}, you can't use your skill, because you are knocked-out!**")

        # Gets all active Divine Protection shields from the user
        shields = await self.get_skill_action_by_user_id_and_skill_type(user_id=perpetrator.id, skill_type='divine_protection', multiple=True)
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

        _, exists = await Player.skill_on_cooldown(skill=Skill.TWO).predicate(ctx)

        current_timestamp = await utils.get_timestamp()

        # Upate user's money
        await self.client.get_cog('SlothCurrency').update_user_money(perpetrator.id, -50)
        # Update perpetrator's second skill timestamp
        if exists:
            await self.update_user_skill_ts(user_id=perpetrator.id, skill=Skill.TWO, new_skill_ts=current_timestamp)
        else:
            await self.insert_user_skill_cooldown(ctx.author.id, Skill.TWO, current_timestamp)
        # Updates user's skills used counter
        await self.update_user_skills_used(user_id=perpetrator.id)

        # Calculates chance (50%) of reinforcing the shields of the targets
        n1 = random.random()
        if n1 <= 0.5:
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
            await ctx.send(f"**You had a `50%` chance of reinforcing all active Divine Protection shields, but you missed it, {perpetrator.mention}!**")

        # Checks whether the perpetrator already has a Divien Protection shield
        if 'protected' not in perpetrator_fx:
            n2 = random.random()
            # Calculates the chance (45%) of getting a shield for the perpetrator
            if n2 <= 0.45:
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
                await ctx.send(f"**You had a `45%` chance of getting a Divine Protection shield for yourself, but you missed it, {perpetrator.mention}!**")

    async def check_protections(self) -> None:
        """ Check on-going protections and their expiration time. """

        divine_protections = await self.get_expired_protections()
        for dp in divine_protections:
            await self.delete_skill_action_by_target_id_and_skill_type(dp[3], 'divine_protection')

            channel = self.bots_txt

            await channel.send(
                content=f"<@{dp[0]}>, <@{dp[3]}>",
                embed=discord.Embed(
                    description=f"**<@{dp[3]}>'s `Divine Protection` from <@{dp[0]}> just expired!**",
                    color=discord.Color.red()))

    async def reinforce_shields(self, perpetrator_id: int, increment: Optional[int] = 86400) -> None:
        """ Reinforces all active Divine Protection shields.
        :param perpetrator_id: The ID of the perpetrator of those shields.
        :param increment: The amount to increment. Default = 1 day """

        mycursor, db = await the_database()
        await mycursor.execute("""
            UPDATE SlothSkills SET skill_timestamp = skill_timestamp + %s WHERE user_id = %s
            AND skill_type = 'divine_protection'""", (increment, perpetrator_id))
        await db.commit()
        await mycursor.close()

    async def reinforce_shield(self, user_id: int, increment: Optional[int] = 86400) -> None:
        """ Reinforces a specific active Divine Protection shield.
        :param user_id: The ID of the user.
        :param increment: The amount to increment. Default = 1 day """

        mycursor, db = await the_database()
        await mycursor.execute("""
        UPDATE SlothSkills SET skill_timestamp = skill_timestamp + %s WHERE target_id = %s
        AND skill_type = 'divine_protection'""", (increment, user_id))
        await db.commit()
        await mycursor.close()

    async def get_expired_protections(self) -> None:
        """ Gets expired divine protection skill actions. """

        the_time = await utils.get_timestamp()
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

        timestamp = await utils.get_timestamp()

        divine_embed = discord.Embed(
            title="A Divine Protection has been executed!",
            timestamp=datetime.fromtimestamp(timestamp)
        )
        divine_embed.description = f"🛡️ <@{perpetrator_id}> protected <@{target_id}> from attacks for 24 hours! 🛡️"
        divine_embed.color = discord.Color.green()

        divine_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Seraph.png")
        divine_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)

        return divine_embed

    async def get_reinforce_shields_embed(self, channel, perpetrator_id: int, shields_len: int) -> discord.Embed:
        """ Makes an embedded message for a shield reinforcement action.
        :param channel: The context channel.
        :param perpetrator_id: The ID of the perpetrator of the shield reinforcement.
        :param shields_len: The amount of active shields that the perpetrator have. """

        timestamp = await utils.get_timestamp()

        reinforce_shields_embed = discord.Embed(
            title="A Shield Reinforcement has been executed!",
            timestamp=datetime.fromtimestamp(timestamp)
        )
        reinforce_shields_embed.description = f"🛡️ <@{perpetrator_id}> reinforced `{shields_len}` active shields; now they have more 24 hours of duration! 🛡️💪"
        reinforce_shields_embed.color = discord.Color.green()

        reinforce_shields_embed.set_author(name='50% of chance', url=self.client.user.display_avatar)
        reinforce_shields_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Seraph.png")
        reinforce_shields_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)

        return reinforce_shields_embed

    async def get_self_shield_embed(self, channel, perpetrator_id: int) -> discord.Embed:
        """ Makes an embedded message for a shield reinforcement action.
        :param channel: The context channel.
        :param perpetrator_id: The ID of the perpetrator of the shield reinforcement.
        :param shields_len: The amount of active shields that the perpetrator have. """

        timestamp = await utils.get_timestamp()

        self_shield_embed = discord.Embed(
            title="A Divine Protection shield has been Given!",
            timestamp=datetime.fromtimestamp(timestamp)
        )
        self_shield_embed.description = f"🛡️ <@{perpetrator_id}> got a shield for themselves for reinforcing other shields! 🛡️💪"
        self_shield_embed.color = discord.Color.green()

        self_shield_embed.set_author(name='45% of chance', url=self.client.user.display_avatar)
        self_shield_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Seraph.png")
        self_shield_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)

        return self_shield_embed

    @commands.command()
    @Player.poisoned()
    @Player.skills_used(requirement=20)
    @Player.skill_on_cooldown(skill=Skill.THREE)
    @Player.skills_locked()
    @Player.user_is_class('seraph')
    @Player.skill_mark()
    async def heal(self, ctx, target: discord.Member = None) -> None:
        """ Heals a member from all debuffs.
        :param target: The member from whom to remove the debuffs.
        PS: If target not provided, the target is you.

        * Skill cost: 100łł.
        * Cooldown: 1 day. """

        perpetrator = ctx.author

        if ctx.channel.id != self.bots_txt.id:
            return await ctx.send(f"**{perpetrator.mention}, you can only use this command in {self.bots_txt.mention}!**")

        perpetrator_fx = await self.get_user_effects(perpetrator)

        if 'knocked_out' in perpetrator_fx:
            return await ctx.send(f"**{perpetrator.mention}, you can't use your skill, because you are knocked-out!**")

        if not target:
            target = perpetrator

        if target.bot:
            return await ctx.send(f"**You cannot heal a bot, {perpetrator.mention}!**")

        target_sloth_profile = await self.get_sloth_profile(target.id)
        if not target_sloth_profile:
            return await ctx.send(f"**You cannot protect someone who doesn't have an account, {perpetrator.mention}!**")

        if target_sloth_profile[1] == 'default':
            return await ctx.send(f"**You cannot protect someone who has a `default` Sloth class, {perpetrator.mention}!**")


        effects = await self.get_user_effects(target)
        debuffs = [fx for fx, values in effects.items() if values['debuff']]

        if not debuffs:
            return await ctx.send(f"**{target.mention} doesn't have any active debuff, {perpetrator.mention}!**")

        user = await self.get_user_currency(perpetrator.id)
        if user[1] < 100:
            return await ctx.send(f"**You don't have `100łł` to use this skill, {perpetrator.mention}!**")

        confirm = await ConfirmSkill(f"**Do you really want to heal {target.mention} from all debuffs, {perpetrator.mention}?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not doing it then, {perpetrator.mention}!**")

        _, exists = await Player.skill_on_cooldown(Skill.THREE).predicate(ctx)

        await self.client.get_cog('SlothCurrency').update_user_money(perpetrator.id, -100)

        current_ts = await utils.get_timestamp()
        if exists:
            await self.update_user_skill_ts(perpetrator.id, Skill.THREE, current_ts)
        else:
            await self.insert_user_skill_cooldown(perpetrator.id, Skill.THREE, current_ts)

        debuffs_removed = await self.remove_debuffs(member=target, debuffs=debuffs)

        heal_embed = await self.make_heal_embed(target=target, perpetrator=perpetrator, debuffs_removed=debuffs_removed)
        await ctx.send(embed=heal_embed)

        
    async def remove_debuffs(self, member: discord.Member, debuffs: List[str]) -> int:
        """ Removes all debuffs from a member.
        :param member: The member from whom to remove the debuffs.
        :param debuffs: A list of debuffs to remove. """

        debuffs_removed = 0
        for debuff in debuffs:
            try:
                if debuff == 'hacked':  
                    debuffs_removed += 1

                if debuff == 'knocked_out':  
                    debuffs_removed += 1

                if debuff == 'wired':  
                    debuffs_removed += 1

                if debuff == 'frogged':
                    debuffs_removed += 1

                if debuff == 'munk':
                    await member.edit(nick=member.display_name.replace('Munk', '').strip())
                    debuffs_removed += 1

                if debuff == 'sabotaged':
                    debuffs_removed += 1

                if debuff == 'locked':
                    debuffs_removed += 1

                if debuff == 'poisoned':
                    debuffs_removed += 1

            except Exception as e:
                print(e)
                continue
        
        await self.delete_debuff_skill_action_by_target_id(member.id)
        return debuffs_removed

    async def make_heal_embed(self, target: discord.Member, perpetrator: discord.Member, debuffs_removed: int) -> discord.Embed:
        """ Makes an embedded message for a heal skill action.
        :param target: The member that was healed.
        :param perpetrator: The person who healed them.
        :param debuffs_removed: The amount of debuffs removed """

        parsed_time = await utils.parse_time()
        heal_embed = discord.Embed(
            title="__Someone just got healed__!",
            description=f"{target.mention} just got healed from `{debuffs_removed}` bad effect(s)!",
            color=target.color,
            timestamp=parsed_time
        )

        heal_embed.set_thumbnail(url=target.display_avatar)
        heal_embed.set_image(url="https://cdn3.iconfinder.com/data/icons/role-playing-game-5/340/magic_game_rpg_human_healing_heal-512.png")
        heal_embed.set_author(name=perpetrator, url=perpetrator.display_avatar, icon_url=perpetrator.display_avatar)
        heal_embed.set_footer(text=perpetrator.guild.name, icon_url=perpetrator.guild.icon.url)

        return heal_embed
        

    @commands.command(aliases=['conceive_grace', 'give_grace', 'provide_grace'])
    @Player.poisoned()
    @Player.skills_used(requirement=50)
    @Player.skill_on_cooldown(skill=Skill.FOUR)
    @Player.skills_locked()
    @Player.user_is_class('seraph')
    @Player.skill_mark()
    @Player.not_ready()
    async def attain_grace(self, ctx, member: Optional[discord.Member] = None) -> None:
        """ Tries with a 10% chance of success to attain the grace from the deity
         so the person, who must be honeymoon'd receives a baby to take care of, 
         together with their spouse.
        :param member: The member to attain the grace to. [Optional][Default=You]
        
        PS: Don't forget to feed your baby, that's crucial and vital.

        • Delay = 1 day
        • Cost = 500łł  """

        pass