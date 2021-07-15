import discord
from discord.ext import commands, tasks, menus
from mysqldb import the_database
from typing import Union, List, Any, Dict
from extra.customerrors import MissingRequiredSlothClass, ActionSkillOnCooldown, SkillsUsedRequirement, CommandNotReady
from extra.menu import ConfirmSkill, prompt_message, prompt_number
from extra.slothclasses.player import Skill
from extra import utils
import os

from extra.slothclasses import agares, cybersloth, merchant, metamorph, munk, prawler, seraph, warrior, db_commands
classes: Dict[str, object] = {
    'agares': agares.Agares, 'cybersloth': cybersloth.Cybersloth,
    'merchant': merchant.Merchant, 'metamorph': metamorph.Metamorph,
    'munk': munk.Munk, 'prawler': prawler.Prawler,
    'seraph': seraph.Seraph, 'warrior': warrior.Warrior
}

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))


class SlothClass(*classes.values(), db_commands.SlothClassDatabaseCommands):
    """ A category for the Sloth Class system. """

    def __init__(self, client) -> None:
        """ Class initializing method. """

        self.client = client
        super(SlothClass, self).__init__(client)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """ Tells when the cog is ready to use. """

        self.bots_txt = await self.client.fetch_channel(bots_and_commands_channel_id)
        self.check_skill_actions.start()
        print("SlothClass cog is online")

    @tasks.loop(minutes=1)
    async def check_skill_actions(self):
        """ Checks all skill actions and events. """

        await self.try_to_run(self.check_steals)
        await self.try_to_run(self.check_protections)
        await self.try_to_run(self.check_transmutations)
        await self.try_to_run(self.check_shop_potion_items)
        await self.try_to_run(self.check_shop_ring_items)
        await self.try_to_run(self.check_hacks)
        await self.try_to_run(self.check_knock_outs)
        await self.try_to_run(self.check_wires)
        await self.try_to_run(self.check_tribe_creations)
        await self.try_to_run(self.check_frogs)

    async def try_to_run(self, func):
        """ Tries to run a function/method and ignore failures. """

        try:
            await func()
        except:
            pass

    @commands.command(aliases=['sloth_class', 'slothclasses'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def sloth_classes(self, ctx) -> None:
        """ Shows how many people are in each Sloth Class team. """

        mycursor, db = await the_database()
        await mycursor.execute("""
            SELECT sloth_class, COUNT(sloth_class) AS sloth_count
            FROM SlothProfile
            WHERE sloth_class != 'default'
            GROUP BY sloth_class
            ORDER BY sloth_count DESC
            """)

        all_sloth_classes = await mycursor.fetchall()
        await mycursor.close()
        sloth_classes = [f"[Class]: {sc[0]:<10} | [Count]: {sc[1]}\n" for sc in all_sloth_classes]
        # print([sc for sc in sloth_classes])
        sloth_classes.append(f"``````ini\n[Class]: {'ALL':<10} | [Count]: {sum([sc[1] for sc in all_sloth_classes])}\n")
        embed = discord.Embed(
            title="__Sloth Classes__",
            description=f"```ini\n{''.join(sloth_classes)}```",
            color=ctx.author.color,
            timestamp=ctx.message.created_at,
            url='https://thelanguagesloth.com/profile/slothclass'
        )

        await ctx.send(embed=embed)


    @commands.command()
    @commands.has_permissions()
    async def get_ts(self, ctx) -> None:
        """ Gets the current timestamp (Etc/GMT)"""

        timestamp = await utils.get_timestamp()
        await ctx.send(f"**Current timestamp: `{timestamp}`**")

    @commands.command(aliases=['rsc'])
    @commands.has_permissions(administrator=True)
    async def reset_skill_cooldown(self, ctx, member: discord.Member = None) -> None:
        """ (ADMIN) Resets the action skill cooldown of the given member.
        :param member: The member to reset the cooldown (default = author). """

        if not member:
            member = ctx.author

        await self.update_user_skill_ts(member.id, Skill.ONE, None)
        return await ctx.send(f"**Action skill cooldown reset for {member.mention}!**")

    @commands.command(aliases=['my_skills'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def skills(self, ctx, member: discord.Member = None) -> None:
        """ Shows all skills for the user's Sloth class.
        :param member: The person from whom to see the skills.
        PS: If you don't inform a member, you will see your skills. """

        if not member:
            member = ctx.author

        sloth_profile = await self.get_sloth_profile(member.id)

        if not sloth_profile:
            component = discord.Component()
            component.add_button(style=5, label="Create Account", emoji="🦥", url="https://thelanguagesloth.com/profile/update")
            return await ctx.send(
                embed=discord.Embed(description=f"**{member.mention}, you don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one, or in the button below!**"),
                components=[component])
        if sloth_profile[1] == 'default':
            component = discord.Component()
            component.add_button(style=5, label="Create Account", emoji="🦥", url="https://thelanguagesloth.com/profile/update")
            return await ctx.send(
                embed=discord.Embed(description=f"**{member.mention}, you don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one, or in the button below!**"),
                components=[component])

        the_class = classes.get(sloth_profile[1].lower())
        class_commands = the_class.__dict__['__cog_commands__']
        prefix = self.client.command_prefix
        cmds = []

        ctx.author = member
        for c in class_commands:
            if c.hidden:
                continue
            elif c.parent:
                continue
            elif not c.checks:
                continue
            elif not [check for check in c.checks if check.__qualname__ == 'Player.skill_mark.<locals>.real_check']:
                continue
            
            try:
                await c.can_run(ctx)
                cmds.append(f"{prefix}{c.qualified_name:<18} [Ready to use]")
            except commands.CommandError as e:
                if isinstance(e, ActionSkillOnCooldown):
                    cmds.append(f"{prefix}{c.qualified_name:<18} [On cooldown]")
                elif isinstance(e, SkillsUsedRequirement):
                    cmds.append(f"{prefix}{c.qualified_name:<18} [Requires {e.skills_required} used skills]")
                elif isinstance(e, CommandNotReady):
                    cmds.append(f"{prefix}{c.qualified_name:<18} [Not Ready]")
                continue
            except Exception as e:
                continue

        cmds_text = '\n'.join(cmds)

        emoji = user_class.emoji if (user_class := classes.get(sloth_profile[1].lower())) else ''

        skills_embed = discord.Embed(
            title=f"__Available Skills for__: `{sloth_profile[1]}` {emoji}",
            color=member.color,
            timestamp=ctx.message.created_at
        )
        skills_embed.add_field(name=f"__Skills__:", value=f"```apache\n{cmds_text}```")
        skills_embed.set_author(name=member, icon_url=member.avatar_url)
        skills_embed.set_thumbnail(url=f"https://thelanguagesloth.com/media/sloth_classes/{sloth_profile[1]}.png")
        skills_embed.set_footer(text=ctx.guild, icon_url=ctx.guild.icon_url)
        await ctx.send(embed=skills_embed)

    @commands.command(aliases=["fx", "efx", "user_effects", "usereffects", "geteffects", "membereffects", "member_effects"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def effects(self, ctx, member: discord.Member = None) -> None:
        """ Gets all effects from a member.
        :param member: The member to get it from. """

        if not member:
            member = ctx.author

        effects = await self.get_user_effects(member)
        formated_effects = [f"__**{effect.title()}**__: {values['cooldown']}" for effect, values in effects.items()]
        
        embed = discord.Embed(
            title=f"__Effects for {member}__",
            description='\n'.join(formated_effects),
            color=member.color,
            timestamp=ctx.message.created_at,
            url=member.avatar_url
        )
        embed.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def skills_update(self, ctx) -> None:
        """ Shows the updates/current status of upcoming Sloth Class Skills. """

        member = ctx.author
        guild = ctx.guild

        embed = discord.Embed(
            title="__Sloth Class Skills Status__",
            description="🟢 - Finished;\n🟠 - Work in Progress;\n🔴 - Not Started.",
            color=member.color,
            timestamp=ctx.message.created_at,
            url="https://thelanguagesloth.com"
        )

        embed.set_thumbnail(url=guild.icon_url)
        embed.set_author(name=self.client.user, url=self.client.user.avatar_url, icon_url=self.client.user.avatar_url)
        embed.set_footer(text=f"Requested by {member}", icon_url=member.avatar_url)

        embed.add_field(name="🟢 Agares' 3rd Skill:", value="**Skill**: `Reflect`.", inline=True)
        embed.add_field(name="🟢 Cybersloth's 3rd Skill:", value="**Skill**: `Virus`.", inline=True)
        embed.add_field(name="🟢 Merchant's 3rd Skill:", value="**Skill**: `Sell Ring`.", inline=False)
        embed.add_field(name="🔴 Metamorph's 3rd Skill:", value="**Skill**: `Mirror`.", inline=True)
        embed.add_field(name="🟠 Munk's 3rd Skill:", value="**Skill**: `Create Tribe Role`.", inline=True)
        embed.add_field(name="🔴 Prawler's 3rd Skill:", value="**Skill**: `??`.", inline=False)
        embed.add_field(name="🟢 Seraph's 3rd Skill:", value="**Skill**: `Heal`.", inline=True)
        embed.add_field(name="🔴 Warrior's 3rd Skill:", value="**Skill**: `??`.", inline=True)

        await ctx.send(embed=embed)

def setup(client) -> None:
    """ Cog's setup function. """

    client.add_cog(SlothClass(client))
