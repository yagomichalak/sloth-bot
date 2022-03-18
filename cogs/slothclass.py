import discord
from discord.ext import commands, tasks, menus
from mysqldb import the_database

from extra import utils
from extra.menu import SlothClassPagination
from extra.customerrors import ActionSkillOnCooldown, ActionSkillsLocked, SkillsUsedRequirement, CommandNotReady
from extra.slothclasses import agares, cybersloth, merchant, metamorph, munk, prawler, seraph, warrior, db_commands
from extra.slothclasses.player import Skill
from extra.slothclasses.player import Player

from typing import Union, List, Dict, Optional
import os
from random import sample, random

classes: Dict[str, object] = {
    'agares': agares.Agares, 'cybersloth': cybersloth.Cybersloth,
    'merchant': merchant.Merchant, 'metamorph': metamorph.Metamorph,
    'munk': munk.Munk, 'prawler': prawler.Prawler,
    'seraph': seraph.Seraph, 'warrior': warrior.Warrior
}

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID', 123))


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

        await self.try_to_run(self.check_reflects)
        await self.try_to_run(self.check_steals)
        await self.try_to_run(self.check_protections)
        await self.try_to_run(self.check_transmutations)
        await self.try_to_run(self.check_shop_potion_items)
        await self.try_to_run(self.check_shop_ring_items)
        await self.try_to_run(self.check_shop_egg_items)
        await self.try_to_run(self.check_hacks)
        await self.try_to_run(self.check_knock_outs)
        await self.try_to_run(self.check_wires)
        await self.try_to_run(self.check_tribe_creations)
        await self.try_to_run(self.check_frogs)
        await self.try_to_run(self.check_sabotages)
        await self.try_to_run(self.check_pet_food)
        await self.try_to_run(self.check_baby_food)

    async def try_to_run(self, func):
        """ Tries to run a function/method and ignore failures. """

        try:
            await func()
        except:
            pass

    @commands.command(aliases=['sloth_class', 'slothclasses'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @Player.poisoned()
    async def sloth_classes(self, ctx, class_name: Optional[str] = None) -> None:
        """ Shows how many people are in each Sloth Class team,
        or showed a full list with all members of the given class ordered by used skills.
        :param class_name: The class name to search members from. [Optional] """

        if class_name and class_name.lower() not in classes:
            return await ctx.send(f"**This is not a valid Sloth Class, {ctx.author.mention}!**")

        if not class_name or class_name.lower() not in classes:
            all_sloth_classes = await self.get_sloth_classes(grouped=True)
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
        else:
            selected_class = classes.get(class_name.lower())

            sloth_classes = await self.get_sloth_classes(class_name=selected_class.__name__)
            members = [f"<@{m[0]}> ({m[1]})" for m in sloth_classes]
            if members:
                additional = {
                    'sloth_class': selected_class
                }
                pages = menus.MenuPages(source=SlothClassPagination(members, **additional), clear_reactions_after=True)
                await pages.start(ctx)

    async def get_sloth_classes(self, grouped: Optional[bool] = False, class_name: Optional[str] = None) -> List[Union[str, int]]:
        """ Gets all or a specific Sloth Class, grouped or not.
        :param grouped: Whether it's gonna be grouped. [Optional]
        :param class_name: The name of the class to selected. [Optional]
        
        Ps: You can either specify grouped or the class_name. """

        mycursor, _ = await the_database()
        if grouped:
            await mycursor.execute("""
                SELECT sloth_class, COUNT(sloth_class) AS sloth_count
                FROM SlothProfile
                WHERE sloth_class != 'default'
                GROUP BY sloth_class
                ORDER BY sloth_count DESC
                """)
        elif not grouped and class_name:
            await mycursor.execute("""
            SELECT user_id, skills_used 
            FROM SlothProfile WHERE sloth_class = %s
            ORDER BY skills_used DESC""", (class_name,))


        all_sloth_classes = await mycursor.fetchall()
        await mycursor.close()
        return all_sloth_classes
        


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
    @Player.poisoned()
    async def skills(self, ctx, member: discord.Member = None) -> None:
        """ Shows all skills for the user's Sloth class.
        :param member: The person from whom to see the skills.
        PS: If you don't inform a member, you will see your skills. """

        if not member:
            member = ctx.author

        sloth_profile = await self.get_sloth_profile(member.id)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(style=5, label="Create Account", emoji="🦥", url="https://thelanguagesloth.com/profile/update"))

        if not sloth_profile:
            return await ctx.send( 
                embed=discord.Embed(description=f"**{member.mention}, you don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one, or in the button below!**"),
                view=view)
        if sloth_profile[1] == 'default':
            return await ctx.send( 
                embed=discord.Embed(description=f"**{member.mention}, you don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one, or in the button below!**"),
                view=view)

        the_class = classes.get(sloth_profile[1].lower())
        class_commands = the_class.__dict__['__cog_commands__']
        prefix = self.client.command_prefix
        cmds = []

        ctx.author = member
        for c in class_commands:
            if c.hidden or (hasattr(c, 'parent') and c.parent) or not c.checks:
                continue

            elif not [check for check in c.checks if check.__qualname__ == 'Player.skill_mark.<locals>.real_check']:
                continue
            
            try:
                await c.can_run(ctx)
                if c.qualified_name == 'mirror':
                    mirrored_skill = await self.get_skill_action_by_user_id_and_skill_type(user_id=ctx.author.id, skill_type='mirror')
                    if mirrored_skill:
                        cmds.append(f"{prefix}{c.qualified_name:<18} [Mirrored -> {mirrored_skill[8]}]")        
                        continue
                    
                cmds.append(f"{prefix}{c.qualified_name:<18} [Ready to use]")
            except commands.CommandError as e:
                if isinstance(e, ActionSkillOnCooldown):
                    cmds.append(f"{prefix}{c.qualified_name:<18} [On cooldown]")
                elif isinstance(e, ActionSkillsLocked):
                    cmds.append(f"{prefix}{c.qualified_name:<18} [Locked]")
                elif isinstance(e, SkillsUsedRequirement):
                    cmds.append(f"{prefix}{c.qualified_name:<18} [Requires {e.skills_required} used skills]")
                elif isinstance(e, CommandNotReady):
                    cmds.append(f"{prefix}{c.qualified_name:<18} [Not Ready]")
                elif isinstance(e, commands.CheckFailure):
                    if isinstance(e.errors[0], ActionSkillOnCooldown):
                        cmds.append(f"{prefix}{c.qualified_name:<18} [On cooldown]")
                        continue
                    cmds.append(f"{prefix}{c.qualified_name:<18} [Failure]")
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
        skills_embed.set_author(name=member, icon_url=member.display_avatar)
        skills_embed.set_thumbnail(url=f"https://thelanguagesloth.com/media/sloth_classes/{sloth_profile[1]}.png")
        skills_embed.set_footer(text=ctx.guild, icon_url=ctx.guild.icon.url)
        await ctx.send(embed=skills_embed)

    @commands.command(aliases=["fx", "efx", "user_effects", "usereffects", "geteffects", "membereffects", "member_effects"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @Player.poisoned()
    async def effects(self, ctx, member: discord.Member = None) -> None:
        """ Gets all effects from a member.
        :param member: The member to get it from. """

        if not member:
            member = ctx.author

        effects = await self.get_user_effects(member)
        formated_effects = [f"__**{effect.title()}**__: {values['cooldown']}" for effect, values in effects.items()]
        
        embed = discord.Embed(
            title=f"__Effects for {member}__",
            description='\n'.join(formated_effects) if formated_effects else 'No effects.',
            color=member.color,
            timestamp=ctx.message.created_at,
            url=member.display_avatar
        )
        embed.set_thumbnail(url=member.display_avatar)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @Player.poisoned()
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

        embed.set_thumbnail(url=guild.icon.url)
        embed.set_author(name=self.client.user, url=self.client.user.display_avatar, icon_url=self.client.user.display_avatar)
        embed.set_footer(text=f"Requested by {member}", icon_url=member.display_avatar)

        embed.add_field(name="🟢 Agares' 4th Skill:", value="**Skill**: `Delay`.", inline=True)
        embed.add_field(name="🟢 Cybersloth's 4th Skill:", value="**Skill**: `Lock`.", inline=True)
        embed.add_field(name="🟢 Merchant's 4th Skill:", value="**Skill**: `Sell Pet`.", inline=False)
        embed.add_field(name="🟢 Metamorph's 4th Skill:", value="**Skill**: `Reborn`.", inline=True)
        embed.add_field(name="🟠 Munk's 4th Skill:", value="**Skill**: `Get Quest`.", inline=True)
        embed.add_field(name="🟢 Prawler's 4th Skill:", value="**Skill**: `Kidnap`.", inline=False)
        embed.add_field(name="🟢 Seraph's 4th Skill:", value="**Skill**: `Attain Grace`.", inline=True)
        embed.add_field(name="🟢 Warrior's 4th Skill:", value="**Skill**: `Poison`.", inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @Player.poisoned()
    async def all_skills(self, ctx) -> None:
        """ Shows all skills available for each Sloth Class. """

        member = ctx.author

        embed = discord.Embed(
            title="__All Sloth Class Skills__",
            description="Showing all skills available for all Sloth Class, respectively.",
            color=member.color,
            timestamp=ctx.message.created_at,
            url="https://thelanguagesloth.com/profile/slothclass"
        )

        # Loops all Sloth Classes
        for name, sloth_class in classes.items():

            cog_commands = [c for c in sloth_class.__cog_commands__ if hasattr(c, 'parent') and c.parent is None]
            class_cmds = cog_commands
            skills = []

            # Loops all commands of the Sloth Class
            for cmd in class_cmds:
                if cmd.hidden or not cmd.checks:
                    continue

                # Checks if it has a skill mark on the command
                for check in cmd.checks:
                    if check.__qualname__ == 'Player.skill_mark.<locals>.real_check':
                        skills.append(f"{self.client.command_prefix}{cmd.name}")

            skills_text = '\n'.join(skills)
            embed.add_field(name=f"__({sloth_class.emoji}) {name.title()}__:", value=f"```{skills_text}```")
            embed.set_footer(text=f"Requested by {member}", icon_url=member.display_avatar)

        await ctx.send(embed=embed)

    @commands.command(aliases=["get_target"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def find_target(self, ctx) -> None:
        """ Finds a random unprotected target, who is offline. """


        author: discord.Member = ctx.author
        offline: List[int] = list({m.id for m in ctx.guild.members if m.status == discord.Status.offline})
        try: 
            offline.remove(author.id) 
        except:
            pass

        users = await self.client.get_cog('SlothCurrency').get_all_specific_leaves_users(offline)
        unprotected_users = await self.get_specific_unprotected_users([user[0] for user in users])

        embed: discord.Embed = discord.Embed(title="__Random Target__")
        scrambled_users = sorted(unprotected_users, key = lambda _: random())

        for user in scrambled_users:
            if member := ctx.guild.get_member(user[0]):
                embed.color = member.color
                embed.description = f"Your random target is: {member.mention}! (`{user[1]}` 🍃)"
                embed.set_footer(text=f"Requested by {author}", icon_url=author.display_avatar)
                embed.set_author(name=f"From {len(unprotected_users)} offline users.")
                return await ctx.reply(embed=embed)
        else:
            await ctx.send(f"**No targets found, {author.mention}!**")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def update_sloth_class(self, ctx, member: discord.Member = None, sloth_class: str = None) -> None:
        """ Updates the user's Sloth Class.
        :param member: The user to update.
        :sloth_class: The sloth class to update to. """

        if not sloth_class:
            return await ctx.send(f"**Please, type a `Sloth Class`, {member.mention}!**")

        available_classes: List[str] = ['default', *classes.keys()]

        if sloth_class.lower() not in available_classes:
            return await ctx.send(f"**Please, type a valid `Sloth Class`, {member.mention}!**\n`{', '.join(available_classes)}`")

        if sloth_class.lower() == 'default':
            sloth_class = sloth_class.lower()
        else:
            sloth_class = sloth_class.title()

        await self.update_sloth_profile_class(member.id, sloth_class)

def setup(client) -> None:
    """ Cog's setup function. """

    client.add_cog(SlothClass(client))
