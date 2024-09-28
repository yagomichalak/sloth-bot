from typing import Union

import discord
from discord.ext import commands

from cogs.slothcurrency import SlothCurrency
from extra import utils
from extra.prompt.menu import ConfirmButton
from extra.slothclasses.player import Player
from extra.slothclasses.view import (BegView, BootView, DriveOverView,
                                     GiveView, HandshakeView, HighFiveView,
                                     HoneymoonView, HugView, KissView, PatView,
                                     PeekView, PunchView, SlapView, TickleView,
                                     WhisperView, YeetView, DominateView)

class RolePlay(commands.Cog):
    """ Category for roleplaying commands. """

    def __init__(self, client) -> None:
        self.client  = client
    
    def send_if_money(required_money: int = 5) -> bool:

        async def real_check(ctx) -> bool:

            author = ctx.author
            currency = await ctx.bot.get_cog("SlothCurrency").get_user_currency(author.id)
            if not currency:
                await ctx.send(f"**You don't have a Sloth Account, {author.mention}!**")
                return False

            if currency[0][1] < required_money:
                await ctx.send(f"**You don't have 5łł to use this command, {author.mention}!**")
                return False
            
            return True
        
        return commands.check(real_check)

    @commands.command()
    @Player.poisoned()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @send_if_money()
    async def hug(self, ctx, *, member: discord.Member = None) -> None:
        """ Hugs someone.
        :param member: The member to hug.
        
        * Cooldown: 2 minutes """
        
        author = ctx.author

        if not member:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member, {author.mention}!**")

        if author.id == member.id:
            self.client.get_command('hug').reset_cooldown(ctx)
            return await ctx.send(f"**You can't hug yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Hug Prompt__",
            description=f"Do you really wanna hug {member.mention}, {author.mention}?",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_author(name="This costs 5łł")
        embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)
        view = HugView(member=author, target=member, timeout=60)

        await ctx.send(embed=embed, view=view)
        await view.wait()
        if view.used:
            await self.client.get_cog('SlothCurrency').update_user_money(author.id, -5)
            # Tries to complete a quest, if possible.
            await self.client.get_cog('SlothClass').complete_quest(author.id, 14, command_name=ctx.command.name)

    @commands.command()
    @Player.poisoned()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @send_if_money()
    async def boot(self, ctx, *, member: discord.Member = None) -> None:
        """ Boots/kicks someone.
        :param member: The member to kick.
        
        * Cooldown: 2 minutes
        
        Ps: It doesn't KICK the person from the server. """
        
        author = ctx.author

        if not member:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member, {author.mention}!**")

        if author.id == member.id:
            self.client.get_command('boot').reset_cooldown(ctx)
            return await ctx.send(f"**You can't boot yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Boot Prompt__",
            description=f"Where do you wanna kick {member.mention}, {author.mention}?",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_author(name="This costs 5łł")
        embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)
        view = BootView(member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)
        await view.wait()
        if view.used:
            await self.client.get_cog('SlothCurrency').update_user_money(author.id, -5)
            # Tries to complete a quest, if possible.
            await self.client.get_cog('SlothClass').complete_quest(author.id, 14, command_name=ctx.command.name)
    
    @commands.command()
    @Player.poisoned()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @send_if_money()
    async def kiss(self, ctx, *, member: discord.Member = None) -> None:
        """ Kisses someone.
        :param member: The member to kiss.
        
        * Cooldown: 2 minutes """

        author = ctx.author

        if not member:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member, {author.mention}!**")

        if author.id == member.id:
            self.client.get_command('kiss').reset_cooldown(ctx)
            return await ctx.send(f"**You can't kiss yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Kiss Prompt__",
            description=f"Select the kind of kiss you want to give {member.mention}, {author.mention}.",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_author(name="This costs 5łł")
        embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)
        view = KissView(self.client, member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)
        await view.wait()
        if view.used:
            await self.client.get_cog('SlothCurrency').update_user_money(author.id, -5)
            # Tries to complete a quest, if possible.
            await self.client.get_cog('SlothClass').complete_quest(author.id, 14, command_name=ctx.command.name)

    @commands.command()
    @Player.poisoned()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @send_if_money()
    async def slap(self, ctx, *, member: discord.Member = None) -> None:
        """ Slaps someone.
        :param member: The member to slap.
        
        * Cooldown: 2 minutes """

        author = ctx.author

        if not member:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member, {author.mention}!**")

        if author.id == member.id:
            self.client.get_command('slap').reset_cooldown(ctx)
            return await ctx.send(f"**You can't slap yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Slap Prompt__",
            description=f"Select the kind of slap you want to give {member.mention}, {author.mention}.",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_author(name="This costs 5łł")
        embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)
        view = SlapView(self.client, member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)
        await view.wait()
        if view.used:
            await self.client.get_cog('SlothCurrency').update_user_money(author.id, -5)
            # Tries to complete a quest, if possible.
            await self.client.get_cog('SlothClass').complete_quest(author.id, 14, command_name=ctx.command.name)

    @commands.command()
    @Player.poisoned()
    @commands.cooldown(1, 240, commands.BucketType.user)
    async def honeymoon(self, ctx, partner: Union[discord.User, discord.Member] = None) -> None:
        """ Celebrates a honey moon with your partner.

        :param partner_id: The partner you want to go on a honeymoon with. (Since you can have up to 4)
        
        Benefits: It heals the couple, protects and resets all skills
        cooldowns and change class cooldown. """

        member = ctx.author

        if not partner:
            self.client.get_command('honeymoon').reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform the partner who you want to go on a honeymoon with!**")
        
        SlothClass = self.client.get_cog('SlothClass')

        member_marriage = await SlothClass.get_user_marriage(member.id, partner.id)
        if not member_marriage:
            self.client.get_command('honeymoon').reset_cooldown(ctx)
            return await ctx.send(f"**This person is not your partner, you can't have a honeymoon by yourself, {member.mention}!** 😔")

        if member_marriage['honeymoon']:
            self.client.get_command('honeymoon').reset_cooldown(ctx)
            return await ctx.send(f"**You already had a honeymoon, what are you doing, {member.mention}?**")

        partner = discord.utils.get(ctx.guild.members, id=member_marriage['partner'])
        if not partner:
            self.client.get_command('honeymoon').reset_cooldown(ctx)
            return await ctx.send(f"**It looks like your partner has left the server, {member.mention}. RIP!")

        embed = discord.Embed(
            title="__Honeymoon Setup__",
            description=f"{member.mention}, select where in the world you wanna have your honeymoon with {partner.mention}.",
            color=discord.Color.gold(),
            timestamp=ctx.message.created_at,
            url="https://travel.usnews.com/rankings/best-honeymoon-destinations/"
        )
        embed.set_thumbnail(url='https://i.pinimg.com/originals/87/35/53/873553eeb255e47b1b4b440e4302e17f.gif')

        embed.set_author(name=partner, icon_url=partner.display_avatar, url=partner.display_avatar)
        embed.set_footer(text=f"Requested by {member}", icon_url=member.display_avatar)

        # Honeymoon setup view
        view = HoneymoonView(member=member, target=member, timeout=300)
        await ctx.send(content=f"{member.mention}, {partner.mention}", embed=embed, view=view)

        await view.wait()

        if not view.value:
            return await utils.disable_buttons(view)

        # Check user currency
        user_currency = await SlothClass.get_user_currency(member.id)
        if user_currency[1] < 1500:
            self.client.get_command('honeymoon').reset_cooldown(ctx)
            return await ctx.send(f"**You don't have `1500łł` to have a honeymoon, {member.mention}!**")

        # Confirmation view

        confirm_embed = discord.Embed(
            title="__Confirmation Prompt__",
            description=f"Are you sure you wanna spend `1500łł` for having your honeymoon with {partner.mention}, {member.mention}?",
            color=discord.Color.orange(),
            timestamp=ctx.message.created_at
        )
        confirmation_view = ConfirmButton(member, 60)
        msg = await ctx.send(embed=confirm_embed, view=confirmation_view)
        await confirmation_view.wait()

        if confirmation_view.value is None:
            embed.description = "Timeout"
            embed.color = discord.Color.red()
        elif not confirmation_view.value:
            embed.description = "Canceled!"
            embed.color = discord.Color.red()
        else:
            embed.description = "Confirmed!"
            embed.color = discord.Color.green()

        # Disable buttons and updates the confirmation_view
        await utils.disable_buttons(confirmation_view)
        await msg.edit(embed=embed, view=confirmation_view)

        if not confirmation_view.value:
            return

        member_marriage = await SlothClass.get_user_marriage(member.id, partner.id)
        if member_marriage['honeymoon']:
            self.client.get_command('honeymoon').reset_cooldown(ctx)
            return await ctx.send(f"**You already had your honeymoon with this person, {member.mention}!**")

        await self.client.get_cog('SlothCurrency').update_user_money(member.id, -1500) # Updates user money
        await SlothClass.update_user_honeymoon_ts(member.id, partner.id)

        place, activity = view.place, view.activity

        final_embed = view.embed
        final_embed.clear_fields()
        final_embed.title = "__Honeymoon Time!__"
        final_embed.description = f"""
            {member.mention} and {partner.mention} went to `{place['value']}` for their honeymoon! 🍯🌛
            And arriving there, they will `{activity['name']}`. 🎉
        """
        current_ts = await utils.get_timestamp()
        try:
            # Reset effects
            member_fx = await SlothClass.get_user_effects(member)
            partner_fx = await SlothClass.get_user_effects(partner)
            await SlothClass.remove_debuffs(member=member, debuffs=member_fx)
            await SlothClass.remove_debuffs(member=partner, debuffs=partner_fx)
            # Resets skills cooldown
            await SlothClass.update_user_skills_ts(member.id)
            await SlothClass.update_user_skills_ts(partner.id)
            # Resets Change-Sloth-Class cooldown
            ten_days = current_ts - 864000
            await SlothClass.update_change_class_ts(member.id, ten_days)
            await SlothClass.update_change_class_ts(partner.id, ten_days)
            # Protects / Reinforces
            if 'protected' not in partner_fx:
                await SlothClass.insert_skill_action(
                    user_id=member.id, skill_type="divine_protection", skill_timestamp=current_ts,
                    target_id=partner.id
                )
            else:
                await SlothClass.reinforce_shield(partner.id)
            if 'protected' not in member_fx:
                await SlothClass.insert_skill_action(
                    user_id=partner.id, skill_type="divine_protection", skill_timestamp=current_ts,
                    target_id=member.id
                )
            else:
                await SlothClass.reinforce_shield(member.id)

        except Exception as e:
            print('Honeymoon error', e)

        await ctx.send(content=f"{member.mention}, {partner.mention}", embed=final_embed)

    @commands.command(aliases=['fist'])
    @Player.poisoned()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @send_if_money()
    async def punch(self, ctx, *, member: discord.Member = None) -> None:
        """ Punches someone.
        :param member: The person to punch.
        
        * Cooldown: 2 minutes """

        author = ctx.author

        if not member:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member, {author.mention}!**")

        if author.id == member.id:
            self.client.get_command('punch').reset_cooldown(ctx)
            return await ctx.send(f"**You can't punch yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Punch Prompt__",
            description=f"Where do you wanna punch {member.mention}, {author.mention}?",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_author(name="This costs 5łł")
        embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)
        view = PunchView(member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)
        await view.wait()
        if view.used:
            await self.client.get_cog('SlothCurrency').update_user_money(author.id, -5)
            # Tries to complete a quest, if possible.
            await self.client.get_cog('SlothClass').complete_quest(author.id, 14, command_name=ctx.command.name)

    @commands.command()
    @Player.poisoned()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @send_if_money()
    async def give(self, ctx, *, member: discord.Member = None) -> None:
        """ Gives someone something.
        :param member: The member to give something to.
        
        * Cooldown: 2 minutes """

        author = ctx.author

        if not member:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member, {author.mention}!**")

        if author.id == member.id:
            self.client.get_command('give').reset_cooldown(ctx)
            return await ctx.send(f"**You can't give yourself anything, {author.mention}!**")

        embed = discord.Embed(
            title="__Give Prompt__",
            description=f"What do you wanna give {member.mention}, {author.mention}?",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_author(name="This costs 5łł")
        embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)
        view = GiveView(member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)
        await view.wait()
        if view.used:
            await self.client.get_cog('SlothCurrency').update_user_money(author.id, -5)
            # Tries to complete a quest, if possible.
            await self.client.get_cog('SlothClass').complete_quest(author.id, 14, command_name=ctx.command.name)

    @commands.command(aliases=['tickling'])
    @Player.poisoned()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @send_if_money()
    async def tickle(self, ctx, *, member: discord.Member = None) -> None:
        """ Tickles someone.
        :param member: The member to tickle.
        
        * Cooldown: 2 minutes """

        author = ctx.author

        if not member:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member, {author.mention}!**")

            
        if author.id == member.id:
            self.client.get_command('tickle').reset_cooldown(ctx)
            return await ctx.send(f"**You can't tickle yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Tickling Prompt__",
            description=f"Are you sure you wanna tickle {member.mention}, {author.mention}?",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_author(name="This costs 5łł")
        embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)
        view = TickleView(member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)
        await view.wait()
        if view.used:
            await self.client.get_cog('SlothCurrency').update_user_money(author.id, -5)
            # Tries to complete a quest, if possible.
            await self.client.get_cog('SlothClass').complete_quest(author.id, 14, command_name=ctx.command.name)

    @commands.command(aliases=['throw', 'toss'])
    @Player.poisoned()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @send_if_money()
    async def yeet(self, ctx, *, member: discord.Member = None) -> None:
        """ Yeets something at someone.
        :param member: The member to yeet or to yeet something at.
        
        * Cooldown: 2 minutes """

        author = ctx.author

        if not member:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member, {author.mention}!**")

            
        if author.id == member.id:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**You can't yeet (something at) yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Yeet Prompt__",
            description=f"What do you wanna yeet, {author.mention}?",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_author(name="This costs 5łł")
        embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)
        view = YeetView(member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)
        await view.wait()
        if view.used:
            await self.client.get_cog('SlothCurrency').update_user_money(author.id, -5)
            # Tries to complete a quest, if possible.
            await self.client.get_cog('SlothClass').complete_quest(author.id, 14, command_name=ctx.command.name)

    @commands.command()
    @Player.poisoned()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @send_if_money()
    async def pat(self, ctx, *, member: discord.Member = None) -> None:
        """ Pats someone.
        :param member: The member to pat.
        
        * Cooldown: 2 minutes """

        author = ctx.author

        if not member:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member, {author.mention}!**")
            
        if author.id == member.id:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**You can't pat yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Pat Prompt__",
            description=f"Are you sure you wanna pat {member.mention}, {author.mention}?",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_author(name="This costs 5łł")
        embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)
        view = PatView(member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)
        await view.wait()
        if view.used:
            await self.client.get_cog('SlothCurrency').update_user_money(author.id, -5)
            # Tries to complete a quest, if possible.
            await self.client.get_cog('SlothClass').complete_quest(author.id, 14, command_name=ctx.command.name)

    @commands.command(aliases=['imbegging', 'imbeggin', 'beggin'])
    @Player.poisoned()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @send_if_money()
    async def beg(self, ctx, *, member: discord.Member = None) -> None:
        """ Begs someone.
        :param member: The person to beg.
        
        * Cooldown: 2 minutes """

        author = ctx.author

        if not member:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member, {author.mention}!**")

            
        if author.id == member.id:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**You can't beg yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Beg Prompt__",
            description=f"Are you sure you wanna beg {member.mention}, {author.mention}?",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_author(name="This costs 5łł")
        embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)
        view = BegView(member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)
        await view.wait()
        if view.used:
            await self.client.get_cog('SlothCurrency').update_user_money(author.id, -5)
            # Tries to complete a quest, if possible.
            await self.client.get_cog('SlothClass').complete_quest(author.id, 14, command_name=ctx.command.name)

    @commands.command()
    @Player.poisoned()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @send_if_money()
    async def whisper(self, ctx, member: discord.Member = None, *, text: str = None) -> None:
        """ Whispers to someone.
        :param member: The member to whisper to.
        :param text: The text to whisper into the member's ear. 
        
        * Cooldown: 2 minutes """

        await ctx.message.delete()
        author = ctx.author

        if not member:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member, {author.mention}!**")

            
        if author.id == member.id:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**You can't whisper to yourself, {author.mention}!**")

        if not text:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a text to whisper, {author.mention}!**")

        embed = discord.Embed(
            title="__Whisper Prompt__",
            description=f"Are you sure you wanna whisper that in {member.mention}'s ear, {author.mention}?",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_author(name="This costs 5łł")
        embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)
        view = WhisperView(member=author, target=member, text=text, timeout=60)
        await ctx.send(embed=embed, view=view)
        await view.wait()
        if view.used:
            await self.client.get_cog('SlothCurrency').update_user_money(author.id, -5)
            # Tries to complete a quest, if possible.
            await self.client.get_cog('SlothClass').complete_quest(author.id, 14, command_name=ctx.command.name)

    @commands.command()
    @Player.poisoned()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @send_if_money()
    async def handshake(self, ctx, *, member: discord.Member = None) -> None:
        """ Handshakes someone.
        :param member: The member to handshake.
        
        * Cooldown: 2 minutes """

        author = ctx.author

        if not member:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member, {author.mention}!**")

            
        if author.id == member.id:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**You can't handshake yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Handshake Prompt__",
            description=f"Are you sure you wanna handshake {member.mention}, {author.mention}?",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_author(name="This costs 5łł")
        embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)
        view = HandshakeView(member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)
        await view.wait()
        if view.used:
            await self.client.get_cog('SlothCurrency').update_user_money(author.id, -5)
            # Tries to complete a quest, if possible.
            await self.client.get_cog('SlothClass').complete_quest(author.id, 14, command_name=ctx.command.name)

    @commands.command(aliases=['hi5', 'h5', 'high_five', 'highestfive', 'highest_five', 'hf'])
    @Player.poisoned()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @send_if_money()
    async def highfive(self, ctx, *, member: discord.Member = None) -> None:
        """ High fives someone.
        :param member: The member to highfive.
        
        * Cooldown: 2 minutes """

        author = ctx.author

        if not member:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member, {author.mention}!**")

            
        if author.id == member.id:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**You can't high five yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Highfive Prompt__",
            description=f"Are you sure you wanna high five {member.mention}, {author.mention}?",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_author(name="This costs 5łł")
        embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)
        view = HighFiveView(member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)
        await view.wait()
        if view.used:
            await self.client.get_cog('SlothCurrency').update_user_money(author.id, -5)
            # Tries to complete a quest, if possible.
            await self.client.get_cog('SlothClass').complete_quest(author.id, 14, command_name=ctx.command.name)

    @commands.command()
    @Player.poisoned()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @send_if_money()
    async def peek(self, ctx, *, member: discord.Member = None) -> None:
        """ Peeks at someone.
        :param member: The member to peek at.
        
        * Cooldown: 2 minutes """

        author = ctx.author

        if not member:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member, {author.mention}!**")
            
        if author.id == member.id:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**You can't peek at yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Peek Prompt__",
            description=f"Are you sure you wanna peek at {member.mention}, {author.mention}?",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_author(name="This costs 5łł")
        embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)
        view = PeekView(member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)
        await view.wait()
        if view.used:
            await self.client.get_cog('SlothCurrency').update_user_money(author.id, -5)
            # Tries to complete a quest, if possible.
            await self.client.get_cog('SlothClass').complete_quest(author.id, 14, command_name=ctx.command.name)

    @commands.command(aliases=['driveover', 'run_over', 'runover'])
    @Player.poisoned()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @send_if_money()
    async def drive_over(self, ctx, *, member: discord.Member = None) -> None:
        """ Drivers over someone.
        :param member: The member to drive over.
        
        * Cooldown: 2 minutes """

        author = ctx.author

        if not member:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member, {author.mention}!**")

            
        if author.id == member.id:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**You can't drive over yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Drive Over Prompt__",
            description=f"Are you sure you wanna drive over {member.mention}, {author.mention}?",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_author(name="This costs 5łł")
        embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)
        view = DriveOverView(member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)
        await view.wait()
        if view.used:
            await self.client.get_cog('SlothCurrency').update_user_money(author.id, -5)
            # Tries to complete a quest, if possible.
            await self.client.get_cog('SlothClass').complete_quest(author.id, 14, command_name=ctx.command.name)

    @commands.command(aliases=["dom"])
    @Player.poisoned()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @send_if_money()
    async def dominate(self, ctx, *, member: discord.Member = None) -> None:
        """ Dominates someone.
        :param member: The member to dominate.
        
        * Cooldown: 2 minutes """

        author = ctx.author

        if not member:
            self.client.get_command(ctx.command.name).reset_cooldown(ctx)
            return await ctx.send(f"**Please, inform a member, {author.mention}!**")

        if author.id == member.id:
            self.client.get_command('dominate').reset_cooldown(ctx)
            return await ctx.send(f"**You can't dominate yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Dominate Prompt__",
            description=f"Do you really want to dominate {member.mention}, {author.mention}?",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_author(name="This costs 5łł")
        embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)
        view = DominateView(self.client, member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)
        await view.wait()
        if view.used:
            await self.client.get_cog('SlothCurrency').update_user_money(author.id, -5)
            # Tries to complete a quest, if possible.
            await self.client.get_cog('SlothClass').complete_quest(author.id, 14, command_name=ctx.command.name)


def setup(client):
    client.add_cog(RolePlay(client))