import discord
from discord.ext import commands

import os

sloth_subscriber_role_id = int(os.getenv("SLOTH_SUBSCRIBER_ROLE_ID", 123))
sloth_subscriber_sub_id = int(os.getenv("SLOTH_SUBSCRIBER_SUB_ID", 123))
on_sloth_sub_log_channel_id = int(os.getenv("ON_SLOTH_SUB_LOG_CHANNEL_ID", 123))
server_id = int(os.getenv('SERVER_ID', 123))
guild_ids = [server_id]

class SlothSubscriber(commands.Cog):
    """ Commands and features related to the Sloth Subscribers. """

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.look_for_due_reminders.start()
        print("SlothSubscriber cog is online!")
    
    @commands.Cog.listener()
    async def on_entitlement_create(self, entitlement: discord.Entitlement) -> None:
        """ Handles subscriptions to the Sloth Subscriber subscription.
        :param entitlement: The entitlement/subscription. """

        if entitlement.sku_id != sloth_subscriber_sub_id:
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

        if entitlement.sku_id != sloth_subscriber_sub_id:
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


def setup(client):
    client.add_cog(SlothSubscriber(client))
