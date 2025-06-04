# import.standard
import os
from itertools import cycle
from datetime import datetime

# import.thirdparty
import discord
from discord.enums import EntitlementType
from discord.ext import commands, tasks

# import.local
from extra import utils
# from extra.useful_variables import patreon_roles
from extra.slothclasses.mastersloth import Mastersloth

# variables.id
server_id = int(os.getenv('SERVER_ID', 123))
guild_ids = [server_id]

# variables.slothsubscription
sloth_subscriber_role_id = int(os.getenv("SLOTH_SUBSCRIBER_ROLE_ID", 123))
on_sloth_sub_log_channel_id = int(os.getenv("ON_SLOTH_SUB_CHANNEL_ID", 123))
sloth_subscriber_sub_id = int(os.getenv("SLOTH_SUBSCRIBER_SUB_ID", 123))
sloth_twenty_k_leaves_bundle_id = int(os.getenv("SLOTH_TWENTY_K_LEAVES_BUNDLE_ID", 123))
sloth_marriage_bundle_id = int(os.getenv("SLOTH_MARRIAGE_BUNDLE_ID", 123))
sloth_golden_leaf_id = int(os.getenv("SLOTH_GOLDEN_LEAF_ID", 123))
frog_catchers_channel_id: int = int(os.getenv("FROG_CATCHERS_CHANNEL_ID", 123))

# variables.role
teacher_role_id = int(os.getenv("TEACHER_ROLE_ID", 123))

class Subscriptions(commands.Cog):
    """ Commands and features related to the Sloth Subscribers. """

    STATUS_CYCLE = cycle(["members"])  #, "patrons", "sloth-subscribers", "teachers"])

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):

        self.change_status.start()
        print("[.cogs] SlothSubscriber cog is ready!")

    @tasks.loop(seconds=10)
    async def change_status(self) -> None:

        next_status = next(self.STATUS_CYCLE)
        guild = self.client.get_guild(server_id)

        status_text = ""
        if next_status == "members":
            status_text = f"{len(guild.members)} members."

        # elif next_status == "patrons":
        #     patrons = await utils.count_members(guild, patreon_roles.keys())
        #     status_text = f"{patrons} patrons."

        # elif next_status == "sloth-subscribers":
        #     subs = list(set([et.user_id for et in await self.client.entitlements().flatten() if et.type == EntitlementType.application_subscription]))
        #     status_text = f"{len(subs)} Sloth bot subs."

        # elif next_status == "teachers":
        #     patrons = await utils.count_members(guild, [teacher_role_id])
        #     status_text = f"{patrons} teachers."
        
        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status_text))
    
    @commands.Cog.listener()
    async def on_entitlement_create(self, entitlement: discord.Entitlement) -> None:
        """ Handles subscriptions to the Sloth Subscriber subscription.
        :param entitlement: The entitlement/subscription. """

        print("On sub: ", entitlement)
        print(datetime.now())
        
        guild = self.client.get_guild(server_id)
        sloth_subscriber_role = discord.utils.get(guild.roles, id=sloth_subscriber_role_id)
        member = discord.utils.get(guild.members, id=entitlement.user_id)

        # Add the Sloth Subscriber role to the member
        try:
            await member.add_roles(sloth_subscriber_role)
        except Exception:
            pass
        
        # Update the member's leaves and Golden Leaves
        try:
            SlothCurrency = self.client.get_cog("SlothCurrency")
            await SlothCurrency.update_user_money(member.id, 3000)
            await SlothCurrency.update_user_premium_money(member.id, 5)
        except Exception:
            pass

        # Resets all skills cooldown
        try:
            SlothClass = self.client.get_cog("SlothClass")
            await SlothClass.update_user_skills_ts(member.id)
        except Exception:
            pass

        # Log when a member subscribes
        sloth_sub_log = self.client.get_channel(on_sloth_sub_log_channel_id)
        embed = discord.Embed(
            title="New subscriber",
            description=f"**{member.mention} just became a `Sloth Subscriber`.**",
            color=discord.Color.green(),
        )
        embed.set_thumbnail(url=member.display_avatar)
        await sloth_sub_log.send(embed=embed)

    @commands.Cog.listener()
    async def on_entitlement_update(self, entitlement: discord.Entitlement) -> None:
        """ Handles subscription renewals to the Sloth Subscriber subscription.
        :param entitlement: The entitlement/subscription. """

        print("On resub: ", entitlement)
        print(datetime.now())
        
        guild = self.client.get_guild(server_id)
        sloth_subscriber_role = discord.utils.get(guild.roles, id=sloth_subscriber_role_id)
        member = discord.utils.get(guild.members, id=entitlement.user_id)

        # Add the Sloth Subscriber role to the member
        try:
            await member.add_roles(sloth_subscriber_role)
        except Exception:
            pass
        
        # Update the member's leaves and Golden Leaves
        try:
            SlothCurrency = self.client.get_cog("SlothCurrency")
            await SlothCurrency.update_user_money(member.id, 3000)
            await SlothCurrency.update_user_premium_money(member.id, 5)
        except Exception:
            pass

        # Resets all skills cooldown
        try:
            SlothClass = self.client.get_cog("SlothClass")
            await SlothClass.update_user_skills_ts(member.id)
        except Exception:
            pass

        # Log when a member subscribes
        sloth_sub_log = self.client.get_channel(on_sloth_sub_log_channel_id)
        embed = discord.Embed(
            title="Subscription Renewal!",
            description=f"**{member.mention} got their subscription renewed.**",
            color=discord.Color.yellow(),
        )
        embed.set_thumbnail(url=member.display_avatar)
        await sloth_sub_log.send(embed=embed)

    @commands.Cog.listener()
    async def on_entitlement_delete(self, entitlement: discord.Entitlement) -> None:
        """ Handles subscription cancellations to the Sloth Subscriber subscription.
        :param entitlement: The entitlement/subscription. """

        print("On unsub: ", entitlement)
        print(datetime.now())
        
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

        # Descriptive Embed
        embed = discord.Embed(
            title="__Sloth Subscriber__",
            description="For getting access to some extra features, commands and server perks.",
            color=discord.Color.green()
        )
        embed.add_field(
            name="🎲 __Gambling__",
            value="> Access to gambling commands like `z!coinflip`, `z!blackjack`, `z!whitejack`, `z!slots`, etc.",
            inline=False
        )
        embed.add_field(
            name="💍 __Polygamy & Golden Leaves__",
            value="> You'll receive `5 Golden Leaves` <:golden_leaf:1289365306413813810> per month, and you can also `marry up to 4 people` at the same time.",
            inline=False
        )
        embed.add_field(
            name="<:richsloth:701157794686042183> __Bonus Activity Exchange & Leaves__",
            value="> Receive `3000 leaves` 🍃 per month, and get twice as many leaves for exchanging your activity statuses, that is, the time you spent in the VCs and messages sent.",
            inline=False
        )
        embed.add_field(
            name="🕰️ __Cooldown Reset & Reduction__",
            value="> Reset all of your Sloth Skills automatically upon subscribing (and on subscription renewal), and reduce by `50% the cooldown` of your next skills.",
            inline=False
        )
        embed.add_field(
            name="🚨 __Check Infractions__",
            value=f"> Check other people's infractions in <#{frog_catchers_channel_id}>.",
            inline=False
        )
        embed.add_field(
            name="🦥 __Sloth Subscriber role__",
            value=f"> Get the <@&{sloth_subscriber_role_id}>, whose color can be changed once a week for `1 Golden Leaf` <:golden_leaf:1289365306413813810>.",
            inline=False
        )
        embed.add_field(
            name=f"{Mastersloth.emoji} __Mastersloth Class__",
            value=f"> Become a `Mastersloth` for `5 Golden Leaves` <:golden_leaf:1289365306413813810> and have ALL skills of the other Sloth Classes in your skill set.",
            inline=False
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/980613341858914376/1316585723570163722/image.png?ex=675b9581&is=675a4401&hm=e69b1ec43d9ff32d1a641e17925fd874715c24b4bd8f86dba3f6ba72ee9b12ec&")

        # Subscription Views
        view = discord.ui.View()
        view.add_item(discord.ui.Button(sku_id=sloth_subscriber_sub_id))
        view.add_item(discord.ui.Button(sku_id=sloth_golden_leaf_id))
        view.add_item(discord.ui.Button(sku_id=sloth_twenty_k_leaves_bundle_id))
        view.add_item(discord.ui.Button(sku_id=sloth_marriage_bundle_id))

        return await ctx.send(embed=embed, view=view)


def setup(client):
    client.add_cog(Subscriptions(client))
