import discord
from discord import embeds
from discord.ext import commands
from .player import Player, Skill
from mysqldb import the_database
from extra.menu import ConfirmSkill
from extra import utils
import os
from datetime import datetime

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))


class Cybersloth(Player):

    emoji = '<:Cybersloth:839498017823916082>'

    def __init__(self, client) -> None:
        self.client = client

    @commands.command(aliases=['eb', 'energy', 'boost'])
    @Player.skill_on_cooldown()
    @Player.user_is_class('cybersloth')
    @Player.skill_mark()
    async def hack(self, ctx, target: discord.Member = None) -> None:
        """ Hacks a member, making them unable to check their z!info and z!profile for 24hrs.
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
            return await ctx.send(f"**{attacker.mention}, you cannot hack yourself!**")

        if target.bot:
            return await ctx.send(f"**{attacker.mention}, you cannot hack a bot!**")

        target_sloth_profile = await self.get_sloth_profile(target.id)
        if not target_sloth_profile:
            return await ctx.send(f"**You cannot hack someone who doesn't have an account, {attacker.mention}!**")

        if target_sloth_profile[1] == 'default':
            return await ctx.send(f"**You cannot hack someone who has a `default` Sloth class, {attacker.mention}!**")

        target_fx = await self.get_user_effects(target)

        if 'protected' in target_fx:
            return await ctx.send(f"**{attacker.mention}, {target.mention} is protected, you can't hack them!**")

        if 'hacked' in target_fx:
            return await ctx.send(f"**{attacker.mention}, {target.mention} is already hacked!**")

        confirmed = await ConfirmSkill(f"**{attacker.mention}, are you sure you want to hack {target.mention}?**").prompt(ctx)
        if not confirmed:
            return await ctx.send("**Not hacking them, then!**")

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
                user_id=attacker.id, skill_type="hack", skill_timestamp=current_timestamp,
                target_id=target.id, channel_id=ctx.channel.id
            )
            if ctx.invoked_with != 'mirror':
                if exists:
                    await self.update_user_skill_ts(attacker.id, Skill.ONE, current_timestamp)
                else:
                    await self.insert_user_skill_cooldown(attacker.id, Skill.ONE, current_timestamp)
            # Updates user's skills used counter
            await self.update_user_skills_used(user_id=attacker.id)
            hack_embed = await self.get_hack_embed(
                channel=ctx.channel, perpetrator_id=attacker.id, target_id=target.id)
            await ctx.send(embed=hack_embed)
        except Exception as e:
            print(e)
            return await ctx.send(f"**Something went wrong and your `Hack` skill failed, {attacker.mention}!**")
        else:
            if 'reflect' in target_fx:
                await self.reflect_attack(ctx, attacker, target, 'hack')

    @commands.command()
    @Player.skills_used(requirement=5)
    @Player.skill_on_cooldown(skill=Skill.TWO)
    @Player.user_is_class('cybersloth')
    @Player.skill_mark()
    async def wire(self, ctx, target: discord.Member = None) -> None:
        """ Wires someone so if they buy a potion or transfer money to someone,
        it siphons off up to 35% of the value amount.
        :param target: The person who you want to wire. """

        attacker = ctx.author

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{attacker.mention}, you can only use this command in {self.bots_txt.mention}!**")

        attacker_fx = await self.get_user_effects(attacker)

        if 'knocked_out' in attacker_fx:
            return await ctx.send(f"**{attacker.mention}, you can't use your skill, because you are knocked-out!**")

        if not target:
            return await ctx.send(f"**Please, inform a target member, {attacker.mention}!**")

        if attacker.id == target.id:
            return await ctx.send(f"**{attacker.mention}, you cannot wire yourself!**")

        if target.bot:
            return await ctx.send(f"**{attacker.mention}, you cannot wire a bot!**")

        target_sloth_profile = await self.get_sloth_profile(target.id)
        if not target_sloth_profile:
            return await ctx.send(f"**You cannot wire someone who doesn't have an account, {attacker.mention}!**")

        if target_sloth_profile[1] == 'default':
            return await ctx.send(f"**You cannot wire someone who has a `default` Sloth class, {attacker.mention}!**")

        target_fx = await self.get_user_effects(target)

        if 'protected' in target_fx:
            return await ctx.send(f"**{attacker.mention}, {target.mention} is protected, you can't wire them!**")

        if 'wired' in target_fx:
            return await ctx.send(f"**{attacker.mention}, {target.mention} is already wired!**")

        confirmed = await ConfirmSkill(f"**{attacker.mention}, are you sure you want to wire {target.mention}?**").prompt(ctx)
        if not confirmed:
            return await ctx.send("**Not wiring them, then!**")

        _, exists = await Player.skill_on_cooldown(skill=Skill.TWO).predicate(ctx)

        try:
            current_timestamp = await utils.get_timestamp()
            await self.insert_skill_action(
                user_id=attacker.id, skill_type="wire", skill_timestamp=current_timestamp,
                target_id=target.id, channel_id=ctx.channel.id
            )
            if exists:
                await self.update_user_skill_ts(attacker.id, Skill.TWO, current_timestamp)
            else:
                await self.insert_user_skill_cooldown(ctx.author.id, Skill.TWO, current_timestamp)
            # Updates user's skills used counter
            await self.update_user_skills_used(user_id=attacker.id)

        except Exception as e:
            print(e)
            return await ctx.send(f"**For some reason I couldn't wire your target, {attacker.mention}!**")

        else:
            wire_embed = await self.get_wire_embed(
                channel=ctx.channel, perpetrator_id=attacker.id, target_id=target.id)
            await ctx.send(embed=wire_embed)
            if 'reflect' in target_fx:
                await self.reflect_attack(ctx, attacker, target, 'wire')

    async def check_hacks(self) -> None:

        """ Check on-going hacks and their expiration time. """

        hacks = await self.get_expired_hacks()
        for h in hacks:
            await self.delete_skill_action_by_target_id_and_skill_type(h[3], 'hack')

            channel = self.bots_txt

            await channel.send(
                content=f"<@{h[0]}>",
                embed=discord.Embed(
                    description=f"**<@{h[3]}> updated his firewall so <@{h[0]}>'s hacking has no effect anymore! 💻**",
                    color=discord.Color.red()))

    async def check_wires(self) -> None:

        """ Check on-going wires and their expiration time. """

        wires = await self.get_expired_wires()
        for w in wires:
            await self.delete_skill_action_by_target_id_and_skill_type(w[3], 'wire')

            channel = self.bots_txt

            await channel.send(
                content=f"<@{w[0]}>",
                embed=discord.Embed(
                    description=f"**<@{w[0]}> lost connection with <@{w[3]}> and the wire doesn't seem to work anymore! 🔌**",
                    color=discord.Color.red()))

    async def get_hack_embed(self, channel: discord.TextChannel, perpetrator_id: int, target_id: int,) -> discord.Embed:
        """ Makes an embedded message for a hacking skill action.
        :param channel: The context channel.
        :param perpetrator_id: The ID of the perpetrator of the hacking.
        :param target_id: The ID of the target of the hacking. """

        timestamp = await utils.get_timestamp()

        hack_embed = discord.Embed(
            title="Someone just got Hacked and lost Control of Everything!",
            timestamp=datetime.fromtimestamp(timestamp)
        )
        hack_embed.description = f"**<@{perpetrator_id}> hacked <@{target_id}>!** <a:hackerman:652303204809179161>"
        # hack_embed.description=f"**<@{perpetrator_id}> hacked <@{attacker_id}>!** <a:hackerman:802354539184259082>"
        hack_embed.color = discord.Color.green()

        hack_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Cybersloth.png")
        hack_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)

        return hack_embed

    async def get_wire_embed(self, channel: discord.TextChannel, perpetrator_id: int, target_id: int,) -> discord.Embed:
        """ Makes an embedded message for a wire skill action.
        :param channel: The context channel.
        :param perpetrator_id: The ID of the perpetrator of the wiring.
        :param target_id: The ID of the target of the wiring. """

        timestamp = await utils.get_timestamp()

        wire_embed = discord.Embed(
            title="Someone has been wired up!",
            timestamp=datetime.fromtimestamp(timestamp)
        )
        wire_embed.description = f"**<@{perpetrator_id}> wired <@{target_id}>!** 🔌"
        wire_embed.color = discord.Color.green()
        wire_embed.set_image(url='https://i.pinimg.com/originals/8f/e1/d1/8fe1d171c2cfc5b7cc5f6b022d2a51b1.gif')
        wire_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Cybersloth.png")
        wire_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)

        return wire_embed


    @commands.command()
    @Player.skills_used(requirement=20)
    @Player.skill_on_cooldown(skill=Skill.THREE)
    @Player.user_is_class('cybersloth')
    @Player.skill_mark()
    async def virus(self, ctx) -> None:
        """ Makes all people that you hacked infect other people that look onto their profiles.
        
        * Skill Cost: 150łł
        * Cooldown: 2 days. """

        attacker = ctx.author

        if ctx.channel.id != bots_and_commands_channel_id:
            return await ctx.send(f"**{attacker.mention}, you can only use this command in {self.bots_txt.mention}!**")

        attacker_fx = await self.get_user_effects(attacker)

        if 'knocked_out' in attacker_fx:
            return await ctx.send(f"**{attacker.mention}, you can't use your skill, because you are knocked-out!**")

        hacks = await self.get_user_target_hacks(attacker.id)
        if not hacks:
            return await ctx.send(f"**You don't have any active hack, {attacker.mention}!**")

        user_currency = await self.get_user_currency(attacker.id)
        if user_currency[1] < 150:
            return await ctx.send(f"**You don't have 150łł to use this skill, {attacker.mention}!**")

        # Update `content` of active hacks to `virus`
        confirm = await ConfirmSkill(f"**Are you sure you want to spend `150łł` to use this skill, {attacker.mention}?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not doing it then, {attacker.mention}!**")

        _, exists = await Player.skill_on_cooldown(skill=Skill.THREE).predicate(ctx)
        current_ts = await utils.get_timestamp()
        try:
            await self.update_hacks_content(attacker_id=attacker.id)
            await self.update_user_money(attacker.id, -150)
            if exists:
                await self.update_user_skill_ts(attacker.id, Skill.THREE, current_ts)
            else:
                await self.insert_user_skill_cooldown(attacker.id, Skill.THREE, current_ts)
            # Updates user's skills used counter
            await self.update_user_skills_used(user_id=attacker.id)
        except Exception as e:
            print(e)
            await ctx.send(f"**It looks like something went wrong with this skill, {attacker.mention}!**")
        else:
            contagious_embed = await self.get_contagious_hack(ctx.channel, attacker.id, len(hacks))
            await ctx.send(embed=contagious_embed)
            
    
    async def update_hacks_content(self, attacker_id: int) -> None:
        """ Updates all content fields of hacks executed by a specific user.
        :param attacker_id: The ID of the attacker. """

        mycursor, db = await the_database()
        await mycursor.execute("UPDATE SlothSkills SET content = 'virus' WHERE user_id = %s", (attacker_id,))
        await db.commit()
        await mycursor.close()

    async def check_virus(self, ctx: commands.Context, target: discord.Member) -> None:
        """ Checks if the target member has a contagious virus in their hack.
        :param ctx: The context of the command.
        :param target: The target member. """

        answer: discord.PartialMessageable = None
        if isinstance(ctx, commands.Context):
            answer = ctx.send
        else:
            answer = ctx.respond

        infected = ctx.author

        hack = await self.get_skill_action_by_target_id_and_skill_type(target.id, skill_type='hack')
        if hack[8] != 'virus' or hack[0] == infected.id:
            return

        effects = await self.get_user_effects(infected)
        if 'hacked' in effects:
            return

        if 'protected' in effects:
            return

        if 'reflect' in effects:
            attacker = await discord.utils.get(ctx.guild.members, id=hack[0])
            await self.reflect_attack(ctx, attacker, target, 'hack')
        
        try:
            current_timestamp = await utils.get_timestamp()
            # Don't need to store it, since it is forever
            await self.insert_skill_action(
                user_id=hack[0], skill_type="hack", skill_timestamp=current_timestamp,
                target_id=infected.id, channel_id=ctx.channel.id, content="virus"
            )            

        except Exception as e:
            print('Failed virus', e)
        else:
            virus_embed = await self.get_virus_embed(
                channel=ctx.channel, perpetrator_id=hack[0], target_id=target.id, infected_id=infected.id)
            await answer(embed=virus_embed)

    async def get_contagious_hack(self, channel: discord.TextChannel, perpetrator_id: int, lenhacks) -> discord.Embed:
        """ Makes an embedded message for a virus infection skill action.
        :param channel: The context channel.
        :param perpetrator_id: The ID of the perpetrator of the initial hack.
        :param lenhacks: The length of the list of hacks the user has. """

        timestamp = await utils.get_timestamp()

        contagious_embed = discord.Embed(
            title="Viruses are Everywhere!",
            timestamp=datetime.fromtimestamp(timestamp)
        )
        contagious_embed.description = f"**<@{perpetrator_id}> just made his `{lenhacks}` active hacks contagious, beware!** ⚜️"
        contagious_embed.color = discord.Color.green()


        contagious_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Cybersloth.png")
        contagious_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)

        return contagious_embed

        

    async def get_virus_embed(self, channel: discord.TextChannel, perpetrator_id: int, target_id: int, infected_id: int) -> discord.Embed:
        """ Makes an embedded message for a virus infection skill action.
        :param channel: The context channel.
        :param perpetrator_id: The ID of the perpetrator of the initial hack.
        :param target_id: The ID of the target of the hack.
        :param infected_id: The ID of the infected member of the hack. """

        timestamp = await utils.get_timestamp()

        wire_embed = discord.Embed(
            title="Someone has been infected by a hacking!",
            timestamp=datetime.fromtimestamp(timestamp)
        )
        wire_embed.description = f"**<@{infected_id}> got infected by <@{perpetrator_id}>'s virus through <@{target_id}>!** ⚜️"
        wire_embed.color = discord.Color.green()
        
        wire_embed.set_image(url='https://media1.tenor.com/images/df4840a6e3ddd163fd5cef6d678a57aa/tenor.gif?itemid=9991524')
        wire_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Cybersloth.png")
        wire_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)

        return wire_embed

    
    @commands.command()
    @Player.skills_used(requirement=50)
    @Player.skill_on_cooldown(skill=Skill.FOUR, seconds=172800)
    @Player.user_is_class('cybersloth')
    @Player.skill_mark()
    @Player.not_ready()
    async def lock(self, ctx, target: discord.Member = None) -> None:
        """ Locks someone else's set of skills until they complete a Quest.
        :param target: The member for whom to lock the skills.
        
        • Delay = 2 days
        • Cost = 150łł  """

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

        if 'lock' in target_fx:
            return await ctx.send(f"**{attacker.mention}, {target.mention} already has their skills locked!**")

        user_currency = await self.get_user_currency(attacker.id)
        if user_currency[1] < 150:
            return await ctx.send(f"**You don't have 150łł to use this skill, {attacker.mention}!**")

        confirmed = await ConfirmSkill(f"**{attacker.mention}, are you sure you want to lock {target.mention}'s skills for `150łł`?**").prompt(ctx)
        if not confirmed:
            return await ctx.send("**Not locking their skills, then!**")

        _, exists = await Player.skill_on_cooldown(skill=Skill.FOUR, seconds=172800).predicate(ctx)

        try:
            current_timestamp = await utils.get_timestamp()
            await self.insert_skill_action(
                user_id=attacker.id, skill_type="lock", skill_timestamp=current_timestamp,
                target_id=target.id, channel_id=ctx.channel.id
            )
            if exists:
                await self.update_user_skill_ts(attacker.id, Skill.FOUR, current_timestamp)
            else:
                await self.insert_user_skill_cooldown(ctx.author.id, Skill.FOUR, current_timestamp)
            # Updates user's skills used counter
            await self.update_user_skills_used(user_id=attacker.id)

        except Exception as e:
            print(e)
            return await ctx.send(f"**For some reason I couldn't lock your target's skills, {attacker.mention}!**")

        else:
            wire_embed = await self.get_lock_embed(
                channel=ctx.channel, perpetrator_id=attacker.id, target_id=target.id)
            await ctx.send(embed=wire_embed)
            if 'reflect' in target_fx:
                await self.reflect_attack(ctx, attacker, target, 'lock')


    async def get_lock_embed(self, channel: discord.TextChannel, perpetrator_id: int, target_id: int,) -> discord.Embed:
        """ Makes an embedded message for a lock skill action.
        :param channel: The context channel.
        :param perpetrator_id: The ID of the perpetrator of the lock.
        :param target_id: The ID of the target of the lock. """

        timestamp = await utils.get_timestamp()

        wire_embed = discord.Embed(
            title="Someone's Skills got Locked Up!",
            timestamp=datetime.fromtimestamp(timestamp)
        )
        wire_embed.description = f"**<@{perpetrator_id}> locked up <@{target_id}>'s set of skills until they finish a Quest!** 🔒"
        wire_embed.color = discord.Color.green()
        wire_embed.set_image(url='https://c.tenor.com/EDnuqsLISREAAAAS/close-the-door-the-invisible-man.gif')
        wire_embed.set_thumbnail(url="https://thelanguagesloth.com/media/sloth_classes/Cybersloth.png")
        wire_embed.set_footer(text=channel.guild, icon_url=channel.guild.icon.url)

        return wire_embed