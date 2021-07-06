import discord
from discord.ext import commands, tasks, menus
from mysqldb import the_database
from typing import Union, List, Any, Dict
from extra.customerrors import MissingRequiredSlothClass, ActionSkillOnCooldown, SkillsUsedRequirement, CommandNotReady
from extra.menu import ConfirmSkill, prompt_message, prompt_number
from extra.slothclasses.player import Skill
from extra import utils
import os

from extra.slothclasses import agares, cybersloth, merchant, metamorph, munk, prawler, seraph, warrior
classes: Dict[str, object] = {
    'agares': agares.Agares, 'cybersloth': cybersloth.Cybersloth,
    'merchant': merchant.Merchant, 'metamorph': metamorph.Metamorph,
    'munk': munk.Munk, 'prawler': prawler.Prawler,
    'seraph': seraph.Seraph, 'warrior': warrior.Warrior
}

bots_and_commands_channel_id = int(os.getenv('BOTS_AND_COMMANDS_CHANNEL_ID'))


class SlothClass(*classes.values()):
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
            FROM UserCurrency
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

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_sloth_skills(self, ctx) -> None:
        """ (Owner) Creates the SlothSkills table. """

        if await self.table_sloth_skills_exists():
            return await ctx.send("**The `SlothSkills` table already exists!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE SlothSkills (
                user_id BIGINT NOT NULL, skill_type VARCHAR(30) NOT NULL,
                skill_timestamp BIGINT NOT NULL, target_id BIGINT DEFAULT NULL,
                message_id BIGINT DEFAULT NULL, channel_id BIGINT DEFAULT NULL,
                emoji VARCHAR(50) DEFAULT NULL, PRICE INT DEFAULT 0
            ) DEFAULT CHARSET=utf8mb4""")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Created `SlothSkills` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_sloth_skills(self, ctx) -> None:
        """ (Owner) Drops the SlothSkills table. """

        if not await self.table_sloth_skills_exists():
            return await ctx.send("**The `SlothSkills` table doesn't exist!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE SlothSkills")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Dropped `SlothSkills` table!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_sloth_skills(self, ctx) -> None:
        """ (Owner) Resets the SlothSkills table. """

        if not await self.table_sloth_skills_exists():
            return await ctx.send("**The `SlothSkills` table doesn't exist yet!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM SlothSkills")
        await db.commit()
        await mycursor.close()
        await ctx.send("**Reset `SlothSkills` table!**")

    async def table_sloth_skills_exists(self) -> bool:
        """ Checks whether the SlothSkills table exists. """

        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'SlothSkills'")
        table_info = await mycursor.fetchall()
        await mycursor.close()
        if len(table_info) == 0:
            return False
        else:
            return True

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

        user = await self.get_user_currency(member.id)

        if not user:
            component = discord.Component()
            component.add_button(style=5, label="Create Account", emoji="🦥", url="https://thelanguagesloth.com/profile/update")
            return await ctx.send(
                embed=discord.Embed(description=f"**{member.mention}, you don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one, or in the button below!**"),
                components=[component])
        if user[7] == 'default':
            component = discord.Component()
            component.add_button(style=5, label="Create Account", emoji="🦥", url="https://thelanguagesloth.com/profile/update")
            return await ctx.send(
                embed=discord.Embed(description=f"**{member.mention}, you don't have an account yet. Click [here](https://thelanguagesloth.com/profile/update) to create one, or in the button below!**"),
                components=[component])

        the_class = classes.get(user[7].lower())
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

            # if 'Player.not_ready.<locals>.real_check' in [check.__qualname__ for check in c.checks]:
            #     cmds.append(f"{prefix}{c.qualified_name:<18} [Not ready]")
            # else:
            
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

        emoji = user_class.emoji if (user_class := classes.get(user[7].lower())) else ''

        skills_embed = discord.Embed(
            title=f"__Available Skills for__: `{user[7]}` {emoji}",
            color=member.color,
            timestamp=ctx.message.created_at
        )
        skills_embed.add_field(name=f"__Skills__:", value=f"```apache\n{cmds_text}```")
        skills_embed.set_author(name=member, icon_url=member.avatar_url)
        skills_embed.set_thumbnail(url=f"https://thelanguagesloth.com/media/sloth_classes/{user[7]}.png")
        skills_embed.set_footer(text=ctx.guild, icon_url=ctx.guild.icon_url)
        await ctx.send(embed=skills_embed)


    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_skills_cooldown(self, ctx) -> None:
        """ Creates the SkillsCooldown table. """

        member = ctx.author

        if await self.table_skills_cooldown_exists():
            return await ctx.send(f"**Table `SkillsCooldown` already exists, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
        CREATE TABLE SkillsCooldown (
            user_id BIGINT NOT NULL,
            skill_one_ts BIGINT DEFAULT NULL,
            skill_two_ts BIGINT DEFAULT NULL,
            skill_three_ts BIGINT DEFAULT NULL,
            skill_four_ts BIGINT DEFAULT NULL,
            skill_five_ts BIGINT DEFAULT NULL,
            PRIMARY KEY (user_id),
            CONSTRAINT fk_skills_user_id FOREIGN KEY (user_id) REFERENCES UserCurrency (user_id) ON DELETE CASCADE ON UPDATE CASCADE
        )
        """)
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `SkillsCooldown` created, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_skills_cooldown(self, ctx) -> None:
        """ Drops the SkillsCooldown table. """

        member = ctx.author

        if not await self.table_skills_cooldown_exists():
            return await ctx.send(f"**Table `SkillsCooldown` doesn't exist, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE SkillsCooldown")
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `SkillsCooldown` dropped, {member.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_skills_cooldown(self, ctx) -> None:
        """ Resets the SkillsCooldown table. """

        member = ctx.author

        if not await self.table_skills_cooldown_exists():
            return await ctx.send(f"**Table `SkillsCooldown` doesn't exist yet, {member.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM SkillsCooldown")
        await db.commit()
        await mycursor.close()
        await ctx.send(f"**Table `SkillsCooldown` reset, {member.mention}!**")

    async def table_skills_cooldown_exists(self) -> bool:
        """ Checks whether the SkillsCooldown table exists. """

        mycursor, db = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'SkillsCooldown'")
        exists = await mycursor.fetchall()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

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

def setup(client) -> None:
    """ Cog's setup function. """

    client.add_cog(SlothClass(client))
