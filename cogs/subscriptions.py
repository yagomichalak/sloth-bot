import discord
from discord.ext import commands, tasks
from discord.enums import EntitlementType

from extra import utils
from extra.useful_variables import patreon_roles
from itertools import cycle
import os

sloth_subscriber_role_id = int(os.getenv("SLOTH_SUBSCRIBER_ROLE_ID", 123))
on_sloth_sub_log_channel_id = int(os.getenv("ON_SLOTH_SUB_CHANNEL_ID", 123))
sloth_subscriber_sub_id = int(os.getenv("SLOTH_SUBSCRIBER_SUB_ID", 123))
teacher_role_id = int(os.getenv("TEACHER_ROLE_iD", 123))
server_id = int(os.getenv('SERVER_ID', 123))
guild_ids = [server_id]


class Subscriptions(commands.Cog):
    """ Commands and features related to the Sloth Subscribers. """

    STATUS_CYCLE = cycle(["members", "patrons", "sloth-subscribers", "teachers"])

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):

        self.change_status.start()
        print("SlothSubscriber cog is online!")

    @tasks.loop(seconds=20)
    async def change_status(self) -> None:

        next_status = next(self.STATUS_CYCLE)
        guild = self.client.get_guild(server_id)

        status_text = ""
        if next_status == "members":
            status_text = f"{len(guild.members)} members."

        elif next_status == "patrons":
            patrons = await utils.count_members(guild, patreon_roles.keys())
            status_text = f"{patrons} patrons."

        elif next_status == "sloth-subscribers":
            subs = [et for et in await guild.entitlements().flatten() if et.type == EntitlementType.application_subscription]
            status_text = f"{len(subs)} Sloth bot subs."

        elif next_status == "teachers":
            patrons = await utils.count_members(guild, [teacher_role_id])
            status_text = f"{patrons} teachers."
        
        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status_text))
    
    @commands.Cog.listener()
    async def on_entitlement_create(self, entitlement: discord.Entitlement) -> None:
        """ Handles subscriptions to the Sloth Subscriber subscription.
        :param entitlement: The entitlement/subscription. """

        if not isinstance(entitlement.type, EntitlementType):
            return
        
        guild = self.client.get_guild(server_id)
        sloth_subscriber_role = discord.utils.get(guild.roles, id=sloth_subscriber_role_id)
        member = discord.utils.get(guild.members, id=entitlement.user_id)

        # Add the Sloth Subscriber role to the member
        try:
            await member.add_roles(sloth_subscriber_role)
        except Exception:
            pass
        
        # Update the member's Golden Leaves
        try:
            SlothCurrency = self.client.get_cog("SlothCurrency")
            await SlothCurrency.update_user_premium_money(member.id, 5)
        except Exception:
            pass
        
        # Log when a member subscribes
        sloth_sub_log = self.client.get_channel(on_sloth_sub_log_channel_id)
        embed = discord.Embed(
            title="New subscriber!",
            description=f"**{member.mention} just became a `Sloth Subscriber`.**",
            color=discord.Color.green(),
        )
        embed.set_thumbnail(url=guild.display_avatar)
        await sloth_sub_log.send(embed=embed)

    @commands.Cog.listener()
    async def on_entitlement_delete(self, entitlement: discord.Entitlement) -> None:
        """ Handles subscriptions to the Sloth Subscriber subscription.
        :param entitlement: The entitlement/subscription. """

        if not isinstance(entitlement.type, EntitlementType):
            return
        
        guild = self.client.get_guild(server_id)
        sloth_subscriber_role = discord.utils.get(guild.roles, id=sloth_subscriber_role_id)
        member = discord.utils.get(guild.members, id=entitlement.user_id)
        
        # Remove the Sloth Subscriber role from the member.
        try:
            await member.remove_roles(sloth_subscriber_role)
        except Exception:
            pass

        # Log when a member subscribes
        sloth_sub_log = self.client.get_channel(on_sloth_sub_log_channel_id)
        embed = discord.Embed(
            title="We lost a subscriber!",
            description=f"**{member.mention} is no longer a `Sloth Subscriber`.**",
            color=discord.Color.red(),
        )
        embed.set_thumbnail(url=member.display_avatar)
        await sloth_sub_log.send(embed=embed)

    @commands.command(aliases=["subscriber", "sub", "slothsubscriber", "slothsub", "sloth_sub"])
    async def subscribe(self, ctx) -> None:
        """ Shows the subscription button. """

        view = discord.ui.View()
        view.add_item(discord.ui.Button(sku_id=sloth_subscriber_sub_id))
        return await ctx.send(
            f"**If you want to have access to some extra features & commands, subscribe now:**", view=view
        )


def setup(client):
    client.add_cog(Subscriptions(client))
