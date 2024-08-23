# import.standard
import os
import random
from datetime import datetime
from typing import List, Optional, Union

# import.thirdparty
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageOps

# import.local
from extra import utils
from extra.prompt.menu import Confirm, ConfirmButton
from extra.view import UserBabyView
from mysqldb import DatabaseCore
from .player import Player, Skill

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID', 123))


class Seraph(Player):

    emoji = '<:Seraph:839498018998976563>'

    def __init__(self, client) -> None:
        self.client = client
        self.db = DatabaseCore()

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

        confirmed = await Confirm(f"**{perpetrator.mention}, are you sure you want to use your skill, to protect {target.mention}?**").prompt(ctx)
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
        confirm = await Confirm(
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
        success_rate: float = 0.5
        success_rate2: float = 0.45
        if await self.get_user_baby(perpetrator.id):
            success_rate = 1.0
            success_rate2 = 1.0
        
        if n1 <= success_rate:
            # Tries to execute it and update the database
            try:
                # Update active Divine Protection shields' time (+1 day)
                await self.reinforce_shields(perpetrator_id=perpetrator.id)
            except Exception as e:
                print(e)
                await ctx.send(f"**For some reason I couldn't reinforce the shield(s), {perpetrator.mention}!**")
            else:
                reinforce_shields_embed = await self.get_reinforce_shields_embed(
                    channel=ctx.channel, perpetrator_id=perpetrator.id, shields_len=len(shields), success_rate=success_rate)
                await ctx.send(embed=reinforce_shields_embed)
        else:
            await ctx.send(f"**You had a `50%` chance of reinforcing all active Divine Protection shields, but you missed it, {perpetrator.mention}!**")

        # Checks whether the perpetrator already has a Divien Protection shield
        if 'protected' not in perpetrator_fx:
            n2 = random.random()
            # Calculates the chance (45%) of getting a shield for the perpetrator
            if n2 <= success_rate2:
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
                        channel=ctx.channel, perpetrator_id=perpetrator.id, success_rate=success_rate2)
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

        await self.db.execute_query("""
            UPDATE SlothSkills SET skill_timestamp = skill_timestamp + %s WHERE user_id = %s
            AND skill_type = 'divine_protection'""", (increment, perpetrator_id))

    async def reinforce_shield(self, user_id: int, increment: Optional[int] = 86400) -> None:
        """ Reinforces a specific active Divine Protection shield.
        :param user_id: The ID of the user.
        :param increment: The amount to increment. Default = 1 day """

        await self.db.execute_query("""
        UPDATE SlothSkills SET skill_timestamp = skill_timestamp + %s WHERE target_id = %s
        AND skill_type = 'divine_protection'""", (increment, user_id))

    async def get_expired_protections(self) -> None:
        """ Gets expired divine protection skill actions. """

        the_time = await utils.get_timestamp()
        return await self.db.execute_query("""
            SELECT * FROM SlothSkills
            WHERE skill_type = 'divine_protection' AND (%s - skill_timestamp) >= 86400
            """, (the_time,), fetch="all")

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

        divine_embed.set_thumbnail(url="https://languagesloth.com/media/sloth_classes/Seraph.png")
        divine_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)

        return divine_embed

    async def get_reinforce_shields_embed(self, channel, perpetrator_id: int, shields_len: int, success_rate: float) -> discord.Embed:
        """ Makes an embedded message for a shield reinforcement action.
        :param channel: The context channel.
        :param perpetrator_id: The ID of the perpetrator of the shield reinforcement.
        :param shields_len: The amount of active shields that the perpetrator have.
        :param success_rate: The success rate. """

        timestamp = await utils.get_timestamp()

        reinforce_shields_embed = discord.Embed(
            title="A Shield Reinforcement has been executed!",
            timestamp=datetime.fromtimestamp(timestamp)
        )
        reinforce_shields_embed.description = f"🛡️ <@{perpetrator_id}> reinforced `{shields_len}` active shields; now they have more 24 hours of duration! 🛡️💪"
        reinforce_shields_embed.color = discord.Color.green()

        reinforce_shields_embed.set_author(name=f"{int(success_rate*100)}% of chance", url=self.client.user.display_avatar)
        reinforce_shields_embed.set_thumbnail(url="https://languagesloth.com/media/sloth_classes/Seraph.png")
        reinforce_shields_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)

        return reinforce_shields_embed

    async def get_self_shield_embed(self, channel, perpetrator_id: int, success_rate: float) -> discord.Embed:
        """ Makes an embedded message for a shield reinforcement action.
        :param channel: The context channel.
        :param perpetrator_id: The ID of the perpetrator of the shield reinforcement.
        :param shields_len: The amount of active shields that the perpetrator have.
        :param success_rate: The success rate. """

        timestamp = await utils.get_timestamp()

        self_shield_embed = discord.Embed(
            title="A Divine Protection shield has been Given!",
            timestamp=datetime.fromtimestamp(timestamp)
        )
        self_shield_embed.description = f"🛡️ <@{perpetrator_id}> got a shield for themselves for reinforcing other shields! 🛡️💪"
        self_shield_embed.color = discord.Color.green()

        self_shield_embed.set_author(name=f"{int(success_rate*100)}% of chance", url=self.client.user.display_avatar)
        self_shield_embed.set_thumbnail(url="https://languagesloth.com/media/sloth_classes/Seraph.png")
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
        debuffs = [fx for fx, values in effects.items() if values['debuff'] and fx not in ['locked', 'poisoned', 'kidnapped']]

        if not debuffs:
            return await ctx.send(f"**{target.mention} doesn't have any active debuff, {perpetrator.mention}!**")

        user = await self.get_user_currency(perpetrator.id)
        if user[1] < 100:
            return await ctx.send(f"**You don't have `100łł` to use this skill, {perpetrator.mention}!**")

        confirm = await Confirm(f"**Do you really want to heal {target.mention} from all debuffs, {perpetrator.mention}?**").prompt(ctx)
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
    async def attain_grace(self, ctx, target: Optional[discord.Member] = None) -> None:
        """ Tries with a 10% chance of success to attain the grace from the deity
         so the person, who must be honeymoon'd receives a baby to take care of, 
         together with their spouse.
        :param target: The target member to attain the grace to. [Optional][Default=You]
        
        PS: Don't forget to feed your baby, that's crucial and vital.

        • Delay = 1 day
        • Cost = 500łł  """

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{ctx.author.mention}, you can only use this command in {self.bots_txt.mention}!**")

        perpetrator = ctx.author
        perpetrator_fx = await self.get_user_effects(perpetrator)

        if 'knocked_out' in perpetrator_fx:
            return await ctx.send(f"**{perpetrator.mention}, you can't use your skill, because you are knocked-out!**")

        if not target:
            target = perpetrator

        if target.bot:
            return await ctx.send(f"**You cannot use it on a bot, {perpetrator.mention}!**")

        target_sloth_profile = await self.get_sloth_profile(target.id)
        if not target_sloth_profile:
            return await ctx.send(f"**You cannot attain the grace for someone who doesn't have an account, {perpetrator.mention}!**")

        if target_sloth_profile[1] == 'default':
            return await ctx.send(f"**You cannot attain the grace for someone who has a `default` Sloth class, {perpetrator.mention}!**")

        SlothClass = self.client.get_cog('SlothClass')
        user_baby = await SlothClass.get_user_baby(target.id)
        if user_baby:
            return await ctx.send(f"**This user already has a baby, {perpetrator.mention}!**")

        marriage = await SlothClass.get_user_marriage(target.id)
        if not marriage['partner']:
            return await ctx.send(f"**You cannot attain the grace for someone who is not married, {perpetrator.mention}!**")

        if not marriage['honeymoon']:
            return await ctx.send(f"**You cannot attain the grace for someone who is not honeymoon'd, {perpetrator.mention}!**")

        confirm = await Confirm(f"**Are you sure you want to spend `500` to try to attain the grace for {target.mention}, {perpetrator.mention}?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not doing it, then, {target.mention}!**")

        _, exists = await Player.skill_on_cooldown(skill=Skill.FOUR).predicate(ctx)

        user_currency = await self.get_user_currency(perpetrator.id)
        if user_currency[1] < 500:
            return await ctx.send(f"**{perpetrator.mention}, you don't have `500łł`!**")

        SlothCurrency = self.client.get_cog("SlothCurrency")
        await SlothCurrency.update_user_money(perpetrator.id, -500)

        emoji = '👶'

        # Calculates the chance (10%) of attaining the grace for the a member
        rn = random.random()
        attained_grace: bool = rn <= 0.10

        try:
            current_timestamp = await utils.get_timestamp()
            if attained_grace:
                target_partner_sloth_profile = await self.get_sloth_profile(marriage['partner'])
                sclass_one, sclass_two = target_sloth_profile[1], target_partner_sloth_profile[1]
                if sclass_two == 'default':
                    sclass_two = sclass_one
                baby_class = random.choice([sclass_one, sclass_two])
                await self.insert_user_baby(target.id, marriage['partner'], f"Baby {baby_class}", baby_class)
            if exists:
                await self.update_user_skill_ts(perpetrator.id, Skill.FOUR, current_timestamp)
            else:
                await self.insert_user_skill_cooldown(perpetrator.id, Skill.FOUR, current_timestamp)
                # Updates user's skills used counter
                await self.update_user_skills_used(user_id=perpetrator.id)
        except Exception as e:
            print(e)
            return await ctx.send(f"**{perpetrator.mention}, something went wrong with it, try again later!**")
        else:
            if attained_grace:
                attained_grace_embed = await self.attained_grace_embed(perpetrator=perpetrator, target=target, emoji=emoji)
                await ctx.send(embed=attained_grace_embed)
            else:
                await ctx.send(f"**You had a `10%` chance of attaining the grace for {target.mention}, but you missed it, {perpetrator.mention}!**")

                if random.random() <= 0.5:
                    await ctx.send(f"**You had a `50%` chance of getting your money back after failing your `attain grace`, and you got it, {perpetrator.mention}!** 😄")
                    await SlothCurrency.update_user_money(perpetrator.id, 500)
                else:
                    await ctx.send(f"**You had a `50%` chance of getting your money back after failing your `attain grace`, but you missed it, {perpetrator.mention}!** 😢")



    async def attained_grace_embed(self, perpetrator: int, target: int, emoji: str) -> discord.Embed:
        """ Makes an embedded message for an attain grace action.
        :param perpetrator: The member who conceived the grace.
        :param target: The member who has been received the grace.
        :param emoji: The emoji representing the skill action. """

        parsed_time = await utils.parse_time()
        attained_grace_embed = discord.Embed(
            title="__A Grace has been Attained__!",
            description=f"{target.mention} attained the grace thanks to {perpetrator.mention} and has been given a beautiful baby!",
            color=discord.Color.green(),
            timestamp=parsed_time
        )

        attained_grace_embed.set_thumbnail(url=target.display_avatar)
        attained_grace_embed.set_image(url="https://c.tenor.com/ISO7aKhQvX4AAAAC/lion-king-simba.gif")
        attained_grace_embed.set_author(name=perpetrator, url=perpetrator.display_avatar, icon_url=perpetrator.display_avatar)
        attained_grace_embed.set_footer(text=perpetrator.guild.name, icon_url=perpetrator.guild.icon.url)

        return attained_grace_embed

    @commands.group(aliases=['bb'])
    @Player.poisoned()
    @Player.kidnapped()
    async def baby(self, ctx) -> None:
        """ Command for managing and interacting with a baby.
        (Use this without a subcommand to see all subcommands available) """
        if ctx.invoked_subcommand:
            return

        prefix = self.client.command_prefix
        subcommands = [f"{prefix}{c.qualified_name}" for c in ctx.command.commands
            ]

        subcommands = '\n'.join(subcommands)
        items_embed = discord.Embed(
            title="__Subcommads__:",
            description=f"```apache\n{subcommands}```",
            color=ctx.author.color,
            timestamp=ctx.message.created_at
        )

        await ctx.send(embed=items_embed)

    @baby.command(name="choose_class", aliases=["update_class", "change_class", "cc"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _baby_choose_class(self, ctx) -> None:
        """ Chooses a class for your baby. """

        member: discord.Member = ctx.author

        user_baby = await self.get_user_baby(member.id)
        if not user_baby:
            return await ctx.send(f"**You don't even have a baby, {member.mention}!**")
        if user_baby[3].lower() != 'embryo':
            return await ctx.send(f"**You already chose a class for your baby, {member.mention}!**")
        
        embed: discord.Embed = discord.Embed(
            title="__Baby Class Selection__",
            color=member.color,
            timestamp=ctx.message.created_at
        )
        embed.set_author(name=member, icon_url=member.display_avatar)
        embed.set_thumbnail(url=member.display_avatar)
        embed.set_footer(text="3 minutes to select", icon_url=ctx.guild.icon.url)

        view: discord.ui.View = UserBabyView(member)
        msg = await ctx.send(embed=embed, view=view)
        await view.wait()
        await utils.disable_buttons(view)
        await msg.edit(view=view)

        if view.selected_baby is None:
            return

        if not view.selected_baby:
            return

        await self.update_user_baby_class(member.id, view.selected_baby.lower())
        await ctx.send(f"**Your `Embryo` is born as a `{view.selected_baby}`, {member.mention}!**")

    @baby.command(name="change_name", aliases=["name", "c_name", "update_name", "cn"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _baby_change_name(self, ctx, *, baby_name: str = None) -> None:
        """ Changes the baby's name.
        :param baby_name: The new baby name to change to.
        
        * Price: 250.
        * Character limit: 25. """

        member: discord.Member = ctx.author
        if not (user_baby := await self.get_user_baby(member.id)):
            return await ctx.send(f"**You don't even have a baby, you cannot change it's name, {member.mention}!**")

        if user_baby[2].lower() == 'Embryo':
            return await ctx.send(f"**You cannot change the name of an unhatched embryo, {member.mention}!**")

        if not baby_name:
            return await ctx.send(f"**Please, inform a name for your baby, {member.mention}!**")

        if baby_name.lower() == 'embryo':
            return await ctx.send(f"**You cannot put that name, {member.mention}!**")

        if len(baby_name) > 25:
            return await ctx.send(f"**The limit of characters for the name is 25, {member.mention}!**")

        SlothCurrency = self.client.get_cog('SlothCurrency')
        user_money = await SlothCurrency.get_user_currency(member.id)
        if user_money[0][1] < 250:
            return await ctx.send(f"**You don't have 250łł to change your baby's nickname, {member.mention}!**")

        confirm = await Confirm(f"**Are you sure you want to spend `250łł` to change your baby's name to `{baby_name}`?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not doing it then, {member.mention}!**")

        await SlothCurrency.update_user_money(member.id, -250)
        await self.update_user_baby_name(member.id, baby_name)
        await ctx.send(f"**Successfully updated your baby {user_baby[2]}'s nickname from `{user_baby[2]}` to `{baby_name}`, {member.mention}!**")


    @baby.command(name="see", aliases=["show", "display", "render"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _baby_see(self, ctx, member: Optional[Union[discord.Member, discord.User]] = None) -> None:
        """ Sees someone's baby.
        :param member: The member from whom to show the baby. [Optional][Default = You] """

        author: discord.Member = ctx.author

        if not member:
            member = author

        user_baby = await self.get_user_baby(member.id)
        if not user_baby:
            if author == member:
                return await ctx.send(f"**You don't have a baby, {member.mention}!**")
            else:
                return await ctx.send(f"**{member} doesn't have a baby, {author.mention}!**")

        # Gets the baby's parents
        parent_one: discord.Member = ctx.guild.get_member(user_baby[0])
        parent_two: discord.Member = ctx.guild.get_member(user_baby[1])
        # Gets parents' profile pictures
        p1pfp = await utils.get_user_pfp(parent_one)
        p2pfp = await utils.get_user_pfp(parent_two)

        # Makes the Baby's Image

        small = ImageFont.truetype("built titling sb.ttf", 45)
        background = Image.open(f"./sloth_custom_images/background/base_baby_background.png")
        hud = Image.open(f"./sloth_custom_images/hud/base_baby_hud.png")
        baby_class = Image.open(f"./sloth_custom_images/sloth/{user_baby[3].title()}.png").resize((470, 350))

        background.paste(hud, (0, 0), hud)
        background.paste(p1pfp, (5, 5), p1pfp)
        background.paste(p2pfp, (730, 5), p2pfp)
        background.paste(baby_class, (160, 280), baby_class)
        
        draw = ImageDraw.Draw(background)
        draw.text((320, 5), str(user_baby[2]), fill="white", font=small)
        draw.text((5, 70), f"LP: {user_baby[4]}", fill="red", font=small)
        draw.text((5, 120), f"Food: {user_baby[5]}", fill="brown", font=small)
        file_path = f"media/temporary/user_baby-{member.id}.png"
        background.save(file_path)

        # Sends the Baby's Image
        await ctx.send(file=discord.File(file_path))
        return os.remove(file_path)

    async def check_baby_food(self) -> None:
        """ Checks baby food statuses. """

        current_ts = await utils.get_timestamp()
        babies = await self.get_hungry_babies(current_ts)
        for baby in babies:
            if baby[3].lower() == 'embryo':
                continue
            
            try:
                # Checks whether baby has food
                if baby[5] >= 5:
                    # Increments LP if it needs
                    if baby[4] < 100:
                        await self.update_user_baby_lp(baby[0], 5, current_ts)
                    # Subtracts food
                    await self.update_user_baby_food(baby[0], -5, current_ts)

                else:
                    # Checks whether baby has lp
                    if baby[4] - 5 > 0: 
                        await self.update_user_baby_lp(baby[0], -5, current_ts)
                        await self.update_user_baby_food(baby[0], 0, current_ts)
                    else:
                        # Baby died
                        channel = self.bots_txt

                        await self.delete_user_baby(baby[0])

                        embed: discord.Embed = discord.Embed(
                            description=f"**Sadly, your baby `{baby[3]}` named `{baby[2]}` starved to death because you didn't feed it for a while. My deepest feelings...**",
                            color=discord.Color.red())

                        file_path = await self.make_baby_death_image(baby)
                        embed.set_image(url="attachment://user_baby_death.png")
                        # Sends the Baby's Image
                        await channel.send(content=f"<@{baby[0]}>, <@{baby[1]}>", embed=embed, file=discord.File(file_path, filename="user_baby_death.png"))
                        os.remove(file_path)
            except Exception as e:
                print('Baby death error', e)
                pass

    async def make_baby_death_image(self, baby: List[Union[int, str]]) -> str:
        """ Makes an embed for the baby's death.
        :param baby: The data from the dead baby. """
    
        medium = ImageFont.truetype("built titling sb.ttf", 60)
        background = Image.open(f"./sloth_custom_images/background/base_baby_background.png")
        baby_class = Image.open(f"./sloth_custom_images/sloth/{baby[3].lower()}.png").resize((470, 350))

        background.paste(baby_class, (160, 280), baby_class)
        draw = ImageDraw.Draw(background)
        draw.text((320, 180), "R.I.P.", fill="black", font=medium)
        draw.text((320, 230), str(baby[2]), fill="black", font=medium)
        file_path = f"media/temporary/user_baby_death-{baby[0]}.png"
        # Makes the image gray
        background = ImageOps.grayscale(background)
        # Saves image
        background.save(file_path)

        return file_path

    @baby.command(name="feed", aliases=["give_food", "f"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _baby_feed(self, ctx, leaves: str = None) -> None:
        """ Feeds your baby.
        :param leaves: The amount of leaves you want to give to your baby.

        PS: You feed your baby with leaves.
        Each leave gives 5 life points to your baby. """

        member: discord.Member = ctx.author

        if not leaves:
            return await ctx.send(f"**Please, inform an amount of leaves to feed your baby, {member.mention}!**")

        user_baby = await self.get_user_baby(member.id)
        if not user_baby:
            return await ctx.send(f"**You don't have a baby, {member.mention}!**")

        if user_baby[3] == 'Embryo':
            return await ctx.send(f"**You cannot feed an embryo, {member.mention}!**")

        try:
            leaves = int(leaves)
        except ValueError:
            return await ctx.send(f"**Please, inform a valid amount of leaves, {member.mention}!**")

        if leaves <= 0:
            return await ctx.send(f"**Please, inform an amount of leaves that is greater than 0, {member.mention}!**")

        current_ts = await utils.get_timestamp()

        food_points: int = user_baby[5]

        temp_points = temp_leaves = 0
        food_rate: int = 5 # The life points each leaf gives to the baby

        for _ in range(leaves):
            
            if food_points + food_rate <= 100:
                temp_points += food_rate
                temp_leaves += 1
                food_points += food_rate
            else:
                break

        confirm_view = ConfirmButton(member, timeout=60)
        msg = await ctx.send(
            content=f"**Are you sure you want to spend `{temp_leaves}` out of `{leaves}łł` to recover `{temp_points}fp` to your baby, {member.mention}!**",
            view=confirm_view)
        await confirm_view.wait()

        SlothCurrency = self.client.get_cog("SlothCurrency")

        user_currency = await self.get_user_currency(member.id)
        if user_currency[1] < temp_leaves:
            return await ctx.send(f"**You don't have `{temp_leaves}` leaves to feed your baby, {member.mention}!**")
        
        if confirm_view.value:
            await SlothCurrency.update_user_money(member.id, -temp_leaves)
            await self.update_user_baby_food(member.id, temp_points, current_ts)
            embed = discord.Embed(
                title="__Baby has been Fed__",
                description=f"**You just fed `{user_baby[2]}` with `{temp_leaves}łł`, now it has `{food_points}` food points, {member.mention}!**",
                color=discord.Color.green(),
                timestamp=ctx.message.created_at
            )

            embed.set_thumbnail(url=f"https://languagesloth.com/static/assets/images/sloth_classes/{user_baby[3]}.png")

            await ctx.send(embed=embed)
            # Tries to complete a quest, if possible.
            await self.client.get_cog('SlothClass').complete_quest(member.id, 12)

        await utils.disable_buttons(confirm_view)
        await msg.edit(view=confirm_view)
