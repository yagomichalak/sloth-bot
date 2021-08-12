import discord
from discord.ext import commands
from extra.slothclasses.player import Player
from extra.slothclasses.view import HugView, BootView, KissView, SlapView, HoneymoonView
from extra import utils
from extra.prompt.menu import ConfirmButton

class RolePlay(commands.Cog):

    def __init__(self, client) -> None:
        self.client  = client


    @commands.command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def hug(self, ctx, *, member: discord.Member = None) -> None:
        """ Hugs someone.
        :param member: The member to hug.
        
        * Cooldown: 2 minutes """
        
        author = ctx.author
        if author.id == member.id:
            self.client.get_command('hug').reset_cooldown(ctx)
            return await ctx.send(f"**You can't hug yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Hug Prompt__",
            description=f"Do you really wanna hug {member.mention}, {author.mention}?",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_footer(text=f"Requested by {author}", icon_url=author.avatar.url)
        view = HugView(member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)

    @commands.command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def boot(self, ctx, *, member: discord.Member = None) -> None:
        """ Boots/kicks someone.
        :param member: The member to kick.
        
        * Cooldown: 2 minutes
        
        Ps: It doesn't KICK the person from the server. """
        
        author = ctx.author
        if author.id == member.id:
            self.client.get_command('boot').reset_cooldown(ctx)
            return await ctx.send(f"**You can't boot yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Boot Prompt__",
            description=f"Where do you wanna kick {member.mention}, {author.mention}?",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_footer(text=f"Requested by {author}", icon_url=author.avatar.url)
        view = BootView(member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)
    
    @commands.command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def kiss(self, ctx, *, member: discord.Member = None) -> None:
        """ Kisses someone.
        :param member: The member to kiss.
        
        * Cooldown: 2 minutes """

        author = ctx.author
        if author.id == member.id:
            self.client.get_command('kiss').reset_cooldown(ctx)
            return await ctx.send(f"**You can't kiss yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Kiss Prompt__",
            description=f"Select the kind of kiss you want to give {member.mention}, {author.mention}.",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_footer(text=f"Requested by {author}", icon_url=author.avatar.url)
        view = KissView(self.client, member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)

    @commands.command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def slap(self, ctx, *, member: discord.Member = None) -> None:
        """ Slaps someone.
        :param member: The member to slap.
        
        * Cooldown: 2 minutes """

        author = ctx.author
        if author.id == member.id:
            self.client.get_command('slap').reset_cooldown(ctx)
            return await ctx.send(f"**You can't slap yourself, {author.mention}!**")

        embed = discord.Embed(
            title="__Slap Prompt__",
            description=f"Select the kind of slap you want to give {member.mention}, {author.mention}.",
            color=author.color,
            timestamp=ctx.message.created_at
        )
        embed.set_footer(text=f"Requested by {author}", icon_url=author.avatar.url)
        view = SlapView(self.client, member=author, target=member, timeout=60)
        await ctx.send(embed=embed, view=view)

    @commands.command()
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def honeymoon(self, ctx) -> None:
        """ Celebrates a honey moon with your partner.
        
        Benefits: It heals the couple, protects and rests all skills
        cooldowns and change class cooldown. """

        member = ctx.author

        SlothClass = self.client.get_cog('SlothClass')

        member_marriage = await SlothClass.get_user_marriage(member.id)
        if not member_marriage['partner']:
            self.client.get_command('honeymoon').reset_cooldown(ctx)
            return await ctx.send(f"**You don't have a partner, you can't have a honeymoon by yourself, {member.mention}!** 😔")

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

        embed.set_author(name=partner, icon_url=partner.avatar.url, url=partner.avatar.url)
        embed.set_footer(text=f"Requested by {member}", icon_url=member.avatar.url)

        # Honeymoon setup view
        view = HoneymoonView(member=member, target=member, timeout=300)
        await ctx.send(content=f"{member.mention}, {partner.mention}", embed=embed, view=view)

        await view.wait()

        if not view.value:
            return await utils.disable_buttons(view)

        # Check user currency
        user_currency = await SlothClass.get_user_currency(member.id)
        if user_currency[1] < 1500:
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

        member_marriage = await SlothClass.get_user_marriage(member.id)
        if member_marriage['honeymoon']:
            return await ctx.send(f"**You already had your honeymoon, {member.mention}!**")

        await SlothClass.update_user_money(member.id, -1500) # Updates user money
        await SlothClass.update_marriage_content(member.id)

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
            # Protects
            await SlothClass.insert_skill_action(
                user_id=member.id, skill_type="divine_protection", skill_timestamp=current_ts,
                target_id=partner.id
            )
            await SlothClass.insert_skill_action(
                user_id=partner.id, skill_type="divine_protection", skill_timestamp=current_ts,
                target_id=member.id
            )
            # Resets skills cooldown
            await SlothClass.update_user_skills_ts(member.id, current_ts)
            await SlothClass.update_user_skills_ts(partner.id, current_ts)
            # Resets Change-Sloth-Class cooldown
            ten_days = current_ts - 864000
            await SlothClass.update_change_class_ts(member.id, ten_days)
            await SlothClass.update_change_class_ts(partner.id, ten_days)

        except Exception as e:
            print('Honeymoon error', e)

        await ctx.send(content=f"{member.mention}, {partner.mention}", embed=final_embed)


def setup(client):
    client.add_cog(RolePlay(client))