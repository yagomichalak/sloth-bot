# import.standard
import asyncio
import os
import subprocess
from typing import List, Optional

# import.thirdparty
import aiohttp
import discord
from discord.ext import commands, tasks

# import.local
from extra import utils
from extra.prompt.menu import Confirm
from extra.view import ApplyView, PremiumView, ReportView
from extra.reportsupport.applications import ApplicationsTable
from extra.reportsupport.openchannels import OpenChannels
from extra.reportsupport.verify import Verify
from mysqldb import DatabaseCore

# variables.webhook #
webhook_url: str = os.getenv('WEBHOOK_URL', "")

# variables.id #
server_id = int(os.getenv('SERVER_ID', 123))
dnk_id = int(os.getenv('DNK_ID', 123))

# variables.category #
case_cat_id = int(os.getenv('CASE_CAT_ID', 123))

# variables.voicechannel #
staff_vc_id = int(os.getenv('STAFF_VC_ID', 123))

# variables.textchannel #
reportsupport_channel_id = int(os.getenv('REPORT_CHANNEL_ID', 123))
mod_log_id = int(os.getenv('MOD_LOG_CHANNEL_ID', 123))
ban_appeals_channel_id: int = os.getenv("BAN_APPEALS_CHANNEL_ID", 123)

# variables.role #
moderator_role_id = int(os.getenv('MOD_ROLE_ID', 123))
staff_manager_role_id = int(os.getenv('STAFF_MANAGER_ROLE_ID', 123))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID', 123))
lesson_management_role_id = int(os.getenv('LESSON_MANAGEMENT_ROLE_ID', 123))
event_management_role_id = int(os.getenv('EVENT_MANAGER_ROLE_ID', 123))
giveaway_management_role_id = int(os.getenv('GIVEAWAY_MANAGER_ROLE_ID', 123))
allowed_roles = [int(os.getenv('OWNER_ROLE_ID', 123)), admin_role_id, moderator_role_id]
witness_roles = [lesson_management_role_id, event_management_role_id, giveaway_management_role_id]

report_support_classes: List[commands.Cog] = [
    ApplicationsTable, Verify, OpenChannels
]

class ReportSupport(*report_support_classes):
    """ A cog related to the system of reports and some other things. """

    def __init__(self, client) -> None:

        self.client = client
        self.db = DatabaseCore()
        self.owner_role_id: int = int(os.getenv('OWNER_ROLE_ID', 123))
        self.mayu_id: int = int(os.getenv('MAYU_ID', 123))

    @commands.Cog.listener()
    async def on_ready(self) -> None:

        self.client.add_view(view=ApplyView(self.client))
        self.client.add_view(view=PremiumView(self.client))
        self.client.add_view(view=ReportView(self.client))
        self.check_inactive_cases.start()
        print('[.cogs] ReportSupport cog is ready!')

    @tasks.loop(seconds=60)
    async def check_inactive_cases(self):
        """ Task that checks Dynamic Rooms expirations. """

        # Get current time
        current_ts = await utils.get_timestamp()

        # Look inactive case rooms to delete
        inactive_cases = await self.get_inactive_cases(current_ts)
        for inactive_case in inactive_cases:
            guild = self.client.get_guild(server_id)
            channel = discord.utils.get(guild.channels, id=inactive_case[1])

            if channel:
                try:
                    await channel.delete()
                except Exception as e:
                    print(f"Failed at deleting the {channel}: {str(e)}")
            await self.remove_user_open_channel(inactive_case[0])

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """ Detects when a webhook is sent from the Sloth Appeals server. """
        channel = message.channel
        category = message.channel.category if hasattr(message.channel, "category") else None

        # Initiates the session
        if channel.id == int(ban_appeals_channel_id):
            async with aiohttp.ClientSession() as session:
                # Gets the webhook
                webhook = discord.Webhook.from_url(webhook_url, session=session)
                try:
                    # Tries to fetch the message
                    await webhook.fetch_message(message.id)
                except discord.NotFound:
                    pass
                else:
                    # Adds the reactions to the message, if fetched
                    await message.add_reaction('✅')
                    await message.add_reaction('❌')
        
        category = getattr(message.channel, "category", None)
        # If the channel is part of the category of case reports
        if category and category.id == case_cat_id:

            current_ts = await utils.get_timestamp()
            case_channel_aliases = ("general", "role", "case")
            report_channel_aliases = ("user", "staff")

            if channel.name.startswith(case_channel_aliases):
                await self.update_case_timestamp(channel.id, current_ts)
                
    async def handle_ban_appeal(self, message: discord.Message, payload) -> None:
        """ Handles ban appeal applications.
        :param guild: The server in which the application is running.
        :param payload: Data about the staff member who is opening the application. """

        emoji = str(payload.emoji)
        guild = self.client.get_guild(server_id)
        
        try:
            if emoji == '✅':
            # Gets the ban appeal app and does the magic
                try:
                    app = await self.get_application_by_message(payload.message_id)
                    if not app:
                        return

                    try:
                        user = discord.Object(app[1])
                        await guild.unban(user)
                    except discord.NotFound:
                        if channel := self.client.get_channel(payload.channel_id):
                            await channel.send(f"**Let Hodja know:** User with ID {app[1]} not found in the ban list.")
                    except Exception as e:
                        if channel := self.client.get_channel(payload.channel_id):
                            await channel.send(f"**Let Hodja know:** Error unbanning user: {e}")
                    finally:
                        try:
                            await self.delete_application(message.id)
                        except Exception as e:
                            if channel := self.client.get_channel(payload.channel_id):
                                await channel.send(f"**Let Hodja know:** Error deleting application: {e}")
                        try:
                            await message.add_reaction('❤️‍🩹')
                        except Exception as e:
                            if channel := self.client.get_channel(payload.channel_id):
                                await channel.send(f"**Let Hodja know:** Error adding reaction to message: {e}")

                except Exception as e:
                    if channel := self.client.get_channel(payload.channel_id):
                        await channel.send(f"**Let Hodja know:** Error handling '✅' reaction: {e}")

            elif emoji == '❌':
            # Tries to delete the ban appeal app from the db, in case it is registered
                try:
                    app = await self.get_application_by_message(payload.message_id)
                    if not app:
                        return

                    if app and not app[3]:
                        try:
                            await self.delete_application(payload.message_id)
                        except Exception as e:
                            if channel := self.client.get_channel(payload.channel_id):
                                await channel.send(f"**Let Hodja know:** Error deleting application: {e}")

                        try:
                            app_channel = self.client.get_channel(self.ban_appeals_channel_id)
                            app_msg = await app_channel.fetch_message(payload.message_id)
                            await app_msg.add_reaction('🚫')
                        except Exception as e:
                            if channel := self.client.get_channel(payload.channel_id):
                                await channel.send(f"**Let Hodja know:** Error handling message in ban appeals channel: {e}")

                except Exception as e:
                    if channel := self.client.get_channel(payload.channel_id):
                        await channel.send(f"**Let Hodja know:** Error handling '❌' reaction: {e}")

        except Exception as e:
            if channel := self.client.get_channel(payload.channel_id):
                await channel.send(f"**Let Hodja know:** Unexpected error in handle_ban_appeal: {e}")

    async def handle_application(self, guild, payload) -> None:
        """ Handles applications.
        :param guild: The server in which the application is running.
        :param payload: Data about the staff member who is opening the application. """

        emoji = str(payload.emoji)
        if emoji == '✅':
            # Gets the app and does the magic
            if not (app := await self.get_application_by_message(payload.message_id)):
                return

            # Checks if the person has not an open interview channel already
            if not app[3]:
                # Creates an interview room with the applicant and sends their application there (you can z!close there)
                return await self.create_interview_room(guild, app)

        elif emoji == '❌':
            # Tries to delete the app from the db, in case it is registered
            app = await self.get_application_by_message(payload.message_id)
            if app and not app[3]:
                await self.delete_application(payload.message_id)

                interview_info = self.interview_info[app[2]]
                app_channel = self.client.get_channel(interview_info['app'])
                app_msg = await app_channel.fetch_message(payload.message_id)
                await app_msg.add_reaction('🔏')
                
                if applicant := discord.utils.get(guild.members, id=app[1]):
                    return await applicant.send(embed=discord.Embed(description=interview_info['message']))

    async def send_verified_selfies_verification(self, interaction: discord.Interaction) -> None:
        """ Sends a message to the user asking for them to send a selfie in order for them
        to get the verified selfies role.
        :param interaction: The interaction object. """

        guild = interaction.guild
        member = interaction.user

        def msg_check(message):
            if message.author == member and not message.guild:
                if len(message.content) <= 100:
                    return True
                else:
                    self.client.loop.create_task(member.send("**Your answer must be within 100 characters**"))
            else:
                return False

        embed = discord.Embed(
            title=f"__Verify__",
            description=f"""You have opened a verification request, if you would like to verify:\n
            **1.** Take a clear picture of yourself holding a piece of paper with today's date and time of verification, and your Discord server name written on it. Image links won't work, only image uploads!\n(You have 5 minutes to do so)"""
        )
        embed.set_footer(text=f"by {member}", icon_url=member.display_avatar)

        embed.set_image(url="https://cdn.discordapp.com/attachments/675668948473348096/911602316677906492/verify.png")

        await member.send(embed=embed)

        while True:
            msg = await self.get_message(member, msg_check, 300)
            if msg is None:
                return await member.send(f"**Timeout, you didn't answer in time, try again later!**")


            attachments = [att for att in msg.attachments if att.content_type.startswith('image')]
            if msg.content.lower() == 'quit':
                return await member.send(f"**Bye!**")

            if not attachments:
                await member.send(f"**No uploaded pic detected, send it again or type `quit` to stop this!**")
                continue

            break

        # Sends verified request to admins
        verify_embed = discord.Embed(
            title=f"__Verification Request__",
            description=f"{member} ({member.id})",
            color=member.color,
            timestamp=interaction.message.created_at
        )

        verify_embed.set_thumbnail(url=member.display_avatar)
        verify_embed.set_image(url=attachments[0])
        verify_req_channel_id = discord.utils.get(guild.text_channels, id=self.verify_reqs_channel_id)
        verify_msg = await verify_req_channel_id.send(content=member.mention, embed=verify_embed)
        await verify_msg.add_reaction('✅')
        await verify_msg.add_reaction('❌')
        # Saves
        await self.insert_application(verify_msg.id, member.id, 'verify')
        return await member.send(f"**Request sent, you will get notified here if you get accepted or declined! ✅**")

    async def report_action(self, interaction: discord.Interaction, vc_name: str, reportee: str, text: str, evidence: str):
        member = interaction.user
        guild = interaction.guild
        counter = await self.get_case_number()
        moderator = discord.utils.get(guild.roles, id=moderator_role_id)
        owner_role = discord.utils.get(guild.roles, id=self.owner_role_id)
        
        for role in member.roles:
            if role.name.startswith("Native"):
                language_role = role
                break
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False, connect=False, view_channel=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True, connect=False, view_channel=True)
        }
        
        if (vc_name == "staff"):
            staff_manager = discord.utils.get(guild.roles, id=staff_manager_role_id)
            overwrites.update({
                moderator: discord.PermissionOverwrite(
                    read_messages=False, 
                    send_messages=False, 
                    connect=False, 
                    view_channel=False, 
                    manage_messages=False),
                staff_manager: discord.PermissionOverwrite(
                    read_messages=True, 
                    send_messages=True, 
                    connect=False, 
                    view_channel=True, 
                    manage_messages=True)
            })
        else:
            overwrites.update({
                moderator: discord.PermissionOverwrite(
                    read_messages=True, 
                    send_messages=True, 
                    connect=False, 
                    view_channel=True, 
                    manage_messages=True, 
                    manage_permissions=True)
            })

        # Verifies if the user already has an open text channel
        if open_channel := await self.member_has_open_channel(member.id):
            if open_channel := discord.utils.get(guild.text_channels, id=open_channel[1]):
                embed = discord.Embed(title="Error!", description=f"**You already have an open channel! ({open_channel.mention})**", color=discord.Color.red())
                await interaction.followup.send(embed=embed, ephemeral=True)
                return False
            else:
                await self.remove_user_open_channel(member.id)
        
        # Verifies if the cases category ID is correct
        case_cat = discord.utils.get(guild.categories, id=case_cat_id)
        if not case_cat:
            print("Invalid case_cat_id")
            return
        
        # Tries to create the report case text channel
        try:
            the_channel = await guild.create_text_channel(name=f"{vc_name}-{counter[0][0]}", category=case_cat, overwrites=overwrites)
        except Exception as e:
            print(f"Error creating text channel: {e}")
            await interaction.followup.send("**Something went wrong with it, please contact an admin!**", ephemeral=True)
            raise ValueError from e
        else:
            created_embed = discord.Embed(
                title=f"Report {vc_name} room created!",
                description=f"**Go to {the_channel.mention}!**",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=created_embed, ephemeral=True)
            current_ts = await utils.get_timestamp()
            await self.insert_user_open_channel(member.id, the_channel.id, current_ts)
            await self.increase_case_number()

            # Creates the UI message with the report result and sends to the user who reported
            embed = discord.Embed(title=f"Report {vc_name}!", description=f"{member.mention}", colour=member.color)
            embed.add_field(name="Reporting:", value=f"```{reportee}```", inline=False)
            embed.add_field(name="For:", value=f"```{text}```", inline=False)
            embed.add_field(name="Evidence:", value=f"```{evidence}```", inline=False)
            
            if (vc_name == "staff"):
                message = await the_channel.send(content=f"{member.mention}, {staff_manager.mention}", embed=embed)
            else:
                message = await the_channel.send(content=f"{member.mention}, {moderator.mention}, {owner_role.mention}", embed=embed)
            
            ctx = await self.client.get_context(message)
            
            # Verifies if the reported member is on a VC at the moment
            if member.voice:
                channel = member.voice.channel
                members = member.voice.channel.members

                for id, member_in_vc in enumerate(members):
                    if member == member_in_vc:
                        del members[id]

                if not members:
                    await ctx.send(f"**{member.mention} is in the {channel.mention} voice channel alone!**")
                else:
                    await ctx.send(f"**{member.mention} is in the {channel.mention} voice channel with other {len(channel.members) - 1} members:** {', '.join([member_in_vc.mention for member_in_vc in members])}")

            else:
                await ctx.send(f"**{member.mention} is not in a VC!**")

    # - Report a staff member
    async def report_staff(self, interaction: discord.Interaction, reportee: str, text: str, evidence: str):
        # Calls the function to perform the report
        await self.report_action(interaction, "staff", reportee, text, evidence)

    # - Report a standard User
    async def report_someone(self, interaction: discord.Interaction, reportee: str, text: str, evidence: str):
        # Calls the function to perform the report
        await self.report_action(interaction, "user", reportee, text, evidence)

    # - Get generic help
    async def generic_help(self, interaction: discord.Interaction, type_help: str, desc: str, ping: bool = True) -> None:
        """ Opens a generic help channel.
        :param interaction: The interaction that generated this action.
        :param type_help: The kind of general help.
        :param message: The text message to send in the room.
        :param ping: Whether mods should be pinged for this. """

        member = interaction.user
        guild = interaction.guild

        if open_channel := await self.member_has_open_channel(member.id):
            if open_channel := discord.utils.get(guild.text_channels, id=open_channel[1]):
                embed = discord.Embed(title="Error!", description=f"**You already have an open channel! ({open_channel.mention})**", color=discord.Color.red())
                await interaction.followup.send(embed=embed, ephemeral=True)
                return False
            else:
                await self.remove_user_open_channel(member.id)

        # General help
        case_cat = discord.utils.get(guild.categories, id=case_cat_id)
        moderator = discord.utils.get(guild.roles, id=moderator_role_id)
        overwrites = {guild.default_role: discord.PermissionOverwrite(
            read_messages=False, send_messages=False, connect=False, view_channel=False),
        member: discord.PermissionOverwrite(
            read_messages=True, send_messages=True, connect=False, view_channel=True),
        moderator: discord.PermissionOverwrite(
            read_messages=True, send_messages=True, connect=False, view_channel=True, manage_messages=True)}
        try:
            the_channel = await guild.create_text_channel(name=f"{'-'.join(type_help.split())}", category=case_cat, overwrites=overwrites)
        except:
            await interaction.followup.send("**Something went wrong with it, please contact an admin!**", ephemeral=True)
            raise Exception
        else:
            created_embed = discord.Embed(
                title=f"Room for `{type_help}` created!",
                description=f"**Go to {the_channel.mention}!**",
                color=discord.Color.green())
            await interaction.followup.send(embed=created_embed, ephemeral=True)
            current_ts = await utils.get_timestamp()
            await self.insert_user_open_channel(member.id, the_channel.id, current_ts)
            embed = discord.Embed(title=f"{type_help.title()}!", description=f"{member.mention}", colour=member.color)
            embed.add_field(name="Description:", value=f"```{desc}```", inline=False)

            if ping:
                await the_channel.send(content=f"{member.mention}, {moderator.mention}", embed=embed)
            else:
                await the_channel.send(content=member.mention, embed=embed)

    async def get_message(self, member, check, timeout: Optional[int] = 300) -> discord.Message:
        """ Gets a message.
        :param member: The member to get the message from.
        :param check: The check for the event.
        :param timeout: Timeout for getting the message. [Optional] """

        try:
            message = await self.client.wait_for('message', timeout=timeout,
            check=check)
        except asyncio.TimeoutError:
            await member.send("**Timeout! Try again.**")
            return None
        else:
            return message

    @commands.command(aliases=['permit_case', 'allow_case', 'add_witness', 'witness', 'aw'])
    @commands.has_any_role(*allowed_roles)
    async def allow_witness(self, ctx):
        """ Allows one or more witnesses or roles to join a case channel.
        :param members: The member(s) or role(s) to allow. """

        author = ctx.author
        members = await utils.get_mentions(ctx.message)
        roles = await utils.get_roles(ctx.message)
        witness_r = [role for role in roles if role.id in witness_roles]

        if not members and not witness_r:
            return await ctx.send("**Inform at least one witness or role to allow!**")

        user_channel = await self.get_case_channel(ctx.channel.id)
        if not user_channel:
            return await ctx.send(f"**This is not a case channel, {author.mention}!**")

        confirm = await Confirm(f"**Are you sure you want to allow all `{len(members) + len(witness_r)}` informed {'witnesses/roles' if len(members) + len(witness_r) > 1 else 'witness/role'} in this case channel, {ctx.author.mention}?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not allowing them, then!**")

        channel = discord.utils.get(ctx.guild.channels, id=user_channel[0][1])
        allowed: int = 0

        embed = discord.Embed(
            description=f"It’s just something we’re trying to sort out and your quick input could really help us.\n{channel.mention}",
            color=author.color,
            timestamp=ctx.message.created_at
        )   

        for member in members:
            try:
                await channel.set_permissions(
                    member, read_messages=True, send_messages=True, connect=True, speak=True, view_channel=True)

                embed.set_author(name="You have been allowed as a witness.", icon_url=member.display_avatar)             
                await member.send(embed=embed)
            except Exception:
                pass
            else:
                allowed += 1

        for role in witness_r:
            try:
                await channel.set_permissions(
                    role, read_messages=True, send_messages=True, connect=True, speak=True, view_channel=True)
            except Exception:
                pass
            else:
                allowed += 1

        return await ctx.send(f"**`{allowed}` {'witnesses/roles have' if allowed > 1 else 'witness/role has'} been allowed here!**")

    @commands.command(aliases=['forbid_case', 'delete_witness', 'remove_witness', 'fw'])
    @commands.has_any_role(*allowed_roles)
    async def forbid_witness(self, ctx):
        """ Forbids one or more witnesses or roles from a case channel.
        :param members: The member(s) or role(s) to forbid. """

        members = await utils.get_mentions(ctx.message)
        roles = await utils.get_roles(ctx.message)
        witness_r = [role for role in roles if role.id in witness_roles]

        if not members and not witness_r:
            return await ctx.send("**Inform a witness or role to forbid!**")

        user_channel = await self.get_case_channel(ctx.channel.id)
        if not user_channel:
            return await ctx.send(f"**This is not a case channel, {ctx.author.mention}!**")

        confirm = await Confirm(f"**Are you sure you want to forbid all `{len(members) + len(witness_r)}` informed {'witnesses/roles' if len(members) + len(witness_r) > 1 else 'witness/role'} from this case channel, {ctx.author.mention}?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not forbidding them, then!**")

        channel = discord.utils.get(ctx.guild.channels, id=user_channel[0][1])
        forbid: int = 0
        for member in members:
            try:
                await channel.set_permissions(
                    member, read_messages=False, send_messages=False, connect=False, speak=False, view_channel=False)
            except Exception:
                pass
            else:
                forbid += 1

        for role in witness_r:
            try:
                await channel.set_permissions(
                    role, read_messages=False, send_messages=False, connect=False, speak=False, view_channel=False)
            except Exception:
                pass
            else:
                forbid += 1

        return await ctx.send(f"**`{forbid}` {'witnesses/roles have' if forbid > 1 else 'witness/role has'} been forbidden from here!**")
            
    @commands.command(aliases=['delete_channel', 'archive', 'cc', "close_case", "end_case", "solve", "solved"])
    @commands.has_any_role(*allowed_roles)
    async def close_channel(self, ctx):
        """ (MOD) Closes a Case-Channel. """

        member: discord.Member = ctx.author

        user_channel = await self.get_case_channel(ctx.channel.id)
        if not user_channel:
            return await ctx.send(f"**What do you think that you are doing? You cannot delete this channel, {member.mention}!**")
            
        channel = discord.utils.get(ctx.guild.text_channels, id=user_channel[0][1])
        case_name = channel.name
        case_number = case_name.split('-')[-1] if case_name.split('-')[-1].isdigit() else "N/A"  # Extract the case number if there is one

        embed = discord.Embed(title="Confirmation",
            description="Are you sure that you want to delete this channel?",
            color=member.color,
            timestamp=ctx.message.created_at
        )
        confirmation = await ctx.send(content=member.mention, embed=embed)
        await confirmation.add_reaction('✅')
        await confirmation.add_reaction('❌')
        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=20,
                check=lambda r, u: u == member and r.message.channel == ctx.channel and str(r.emoji) in ['✅', '❌'])
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="Confirmation",
                description="You took too long to answer the question; not deleting it!",
                color=discord.Color.red(),
                timestamp=ctx.message.created_at
            )
            return await confirmation.edit(content=member.mention, embed=embed)
        else:
            if str(reaction.emoji) == '✅':
                embed.description = f"**Channel {channel.mention} is being deleted...**"
                await confirmation.edit(content=member.mention, embed=embed)
                await asyncio.sleep(3)
                await channel.delete()
                await self.remove_user_open_channel(user_channel[0][0])

                # Moderation log embed
                moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
                embed = discord.Embed(
                    title='__**Case Closed**__',
                    color=discord.Color.red(),
                    timestamp=ctx.message.created_at
                )
                embed.add_field(name="Case Number", value=f"#{case_number}")
                embed.set_footer(text=f"Closed by {member}", icon_url=member.display_avatar)
                await moderation_log.send(embed=embed)
            else:
                embed.description = "Not deleting it!"
                await confirmation.edit(content='', embed=embed)

    # Discord methods
    async def create_interview_room(self, guild: discord.Guild, app: List[str]) -> None:
        """ Creates an interview room for the given application.
        :param guild: The server in which the interview will be.
        :param app: The applicant info. """

        applicant = discord.utils.get(guild.members, id=app[1])

        interview_info = self.interview_info.get(app[2])

        # Create Private Thread for the user
        app_parent = self.client.get_channel(interview_info['parent'])

        #delete this later
        message = None
        # message = await app_parent.send('Uncomment this in your development environment')

        txt_channel = await app_parent.create_thread(name=f"{applicant.display_name}'s-interview", message=message, auto_archive_duration=10080, reason=f"{app[2].title()} Interview Room")

        # Add permissions for the user in the interview room
        parent_channel = self.client.get_channel(interview_info['parent'])
        interview_vc = self.client.get_channel(interview_info['interview'])

        # Updates the applicant's application in the database, adding the channels ids
        await self.update_application(applicant.id, txt_channel.id, interview_vc.id, app[2])

        # Set channel perms for the user.
        await parent_channel.set_permissions(applicant, read_messages=True, send_messages=False, view_channel=True)
        await interview_vc.set_permissions(applicant, speak=True, connect=True, view_channel=True)

        application_type = app[2].title().replace('_', ' ')

        role_mapping = {
            "Teacher": "Lesson Managers",
            "Moderator": "staff Managers",
            "Event Host": "Event Managers",
            "Debate Organizer": "Debate Managers"
        }

        role_name = role_mapping.get(application_type, "Managers")

        app_embed = discord.Embed(
            title=f"{applicant.name}'s Interview",
            description=f"""
            Hello {applicant.mention}, thank you for submitting your {application_type} application. We've reviewed it and the next step is an interview to better access who you are as a person.
            Please talk to one of the {role_name} to schedule a time that works for you.""",
            color=applicant.color)

        formatted_pings = await self.format_application_pings(guild, interview_info['pings'])
        await txt_channel.send(content=f"{formatted_pings}, {applicant.mention}", embed=app_embed)
        try:
            await applicant.send(f"Your {txt_channel.mention} channel has been created, please take a look at it.")
        except:
            pass

    # In-game commands
    
    @utils.is_allowed([staff_manager_role_id, lesson_management_role_id, event_management_role_id], throw_exc=True)
    @commands.command(aliases=['ca'])
    async def close_app(self, ctx) -> None:
        """ (ADMIN) Closes an application channel. """

        member = ctx.author
        channel = ctx.channel
        guild = ctx.guild

        if not (app := await self.get_application_by_channel(channel.id)):
            return await ctx.send(f"**This is not an application channel, {member.mention}!**")

        interview_info = self.interview_info[app[2]]
        all_apps_channel = discord.utils.get(guild.text_channels, id=interview_info['app'])

        confirm = await Confirm(f"**Are you sure that you want to delete this application channel, {member.mention}?**").prompt(ctx)
        if not confirm:
            return await ctx.send(f"**Not deleting it, then, {member.mention}!**")
    
        applicant = guild.get_member(app[1])
        parent_channel = discord.utils.get(guild.text_channels, id=interview_info['parent'])
        interview_vc = discord.utils.get(guild.voice_channels, id=interview_info['interview'])
        try:
            await parent_channel.set_permissions(applicant, overwrite=None)
            await interview_vc.set_permissions(applicant, overwrite=None)
        except:
            pass
        await channel.delete()
        await self.delete_application(app[0])
        try:
            msg = await all_apps_channel.fetch_message(app[0])
            await msg.add_reaction('🔒')
        except:
            pass
    
    async def audio(self, member: discord.Member, audio_name: str) -> None:
        """ Plays an audio.
        :param member: A member to get guild context from.
        :param audio_name: The name of the audio to play. """

        # Resolves bot's channel state
        staff_vc = self.client.get_channel(staff_vc_id)
        bot_state = member.guild.voice_client

        try:
            if bot_state and bot_state.channel and bot_state.channel != staff_vc:
                await bot_state.disconnect()
                await bot_state.move_to(staff_vc)
            elif not bot_state:
                voicechannel = discord.utils.get(member.guild.channels, id=staff_vc.id)
                vc = await voicechannel.connect()

            await asyncio.sleep(2)
            voice_client: discord.VoiceClient = discord.utils.get(self.client.voice_clients, guild=member.guild)
            # Plays / and they don't stop commin' /
            if voice_client and not voice_client.is_playing():
                audio_path=f'tts/{audio_name}.mp3'
                audio_source = discord.FFmpegPCMAudio(audio_path)
                audio_duration = get_audio_duration(audio_path)
                voice_client.play(audio_source, after=lambda e: print("Finished Warning staff!"))
                await asyncio.sleep(audio_duration + 1)
                await voice_client.disconnect()
            else:
                print('couldnt play it!')

        except Exception as e:
            print(e)
            return

    @commands.command(aliases=['make_report_msg', 'reportmsg', 'report_msg', 'supportmsg', 'support_msg'])
    @commands.has_permissions(administrator=True)
    async def make_report_support_message(self, ctx) -> None:
        """ (ADM) Makes a Report-Support message. """

        premiumEmbed = discord.Embed(
            title="Language Sloth | Premium",
            description="""Support the server and get access to special privileges and features\n
<:green_dot:1338144193754955819> **Patrons:** Join full rooms, access to soundboard, own customizable permanent voice channel, receive leaves monthly (server currency), support your favorite lesson

<:green_dot:1338144193754955819> **Frog Catcher:** Join full rooms, access to gambling commands, marry up to 4 people at the same time, role that changes color, check other users infractions in the server""",
            color=0x3A9D76,
        )
        
        premiumView = PremiumView(self.client)
        await ctx.send(embed=premiumEmbed, view=premiumView)

        staffEmbed = discord.Embed(
            title="Language Sloth | Staff",
            description="""<:blue_dot:1338144172615536661> Do you like the server and want to join our family? Check out the positions below and choose the one that interests""",
            color=0x4795ce,
        )

        applyView = ApplyView(self.client)
        await ctx.send(embed=staffEmbed, view=applyView)

        reportEmbed = discord.Embed(
            title="Language Sloth | Report - Support",
            description="""<:red_dot:1338144150935044197> Get help from staff members, report issues and stay informed about the latest server updates""",
            color=0xdd3849,
        )

        reportView = ReportView(self.client)
        await ctx.send(embed=reportEmbed, view=reportView)

        self.client.add_view(view=premiumView)
        self.client.add_view(view=applyView)
        self.client.add_view(view=reportView)

def setup(client):
    client.add_cog(ReportSupport(client))

def get_audio_duration(audio_path: str) -> float:
    """Get the duration of the audio file in seconds."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    duration = float(result.stdout)
    return duration
