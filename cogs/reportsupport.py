# import.standard
from collections import defaultdict
import time
import asyncio
from asyncio import Lock
import os
import subprocess
import re
from typing import List, Optional
import requests

# import.thirdparty
import httpx
import anthropic
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

# variables.anthropic #
api_key = str(os.getenv('ANTHROPIC_API_KEY', 'abc'))

# variables.textchannel #
reportsupport_channel_id = int(os.getenv('REPORT_CHANNEL_ID', 123))
mod_log_id = int(os.getenv('MOD_LOG_CHANNEL_ID', 123))
ban_appeals_channel_id: int = os.getenv("BAN_APPEALS_CHANNEL_ID", 123)

# variables.role #
moderator_role_id = int(os.getenv('MOD_ROLE_ID', 123))
senior_role_id = int(os.getenv('SENIOR_MOD_ROLE_ID', 123))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID', 123))
lesson_management_role_id = int(os.getenv('LESSON_MANAGEMENT_ROLE_ID', 123))
analyst_debugger_role_id: int = int(os.getenv('ANALYST_DEBUGGER_ROLE_ID', 123)) # used by temp check command
timedout_role_id = int(os.getenv('TIMEDOUT_ROLE_ID', 123)) # used by temp check command
allowed_roles = [int(os.getenv('OWNER_ROLE_ID', 123)), admin_role_id, moderator_role_id]

report_support_classes: List[commands.Cog] = [
    ApplicationsTable, Verify, OpenChannels
]

class ReportSupport(*report_support_classes):
    """ A cog related to the system of reports and some other things. """

    def __init__(self, client) -> None:

        self.client = client
        self.db = DatabaseCore()
        self.conversation_history = {}
        self.send_summary = {}
        self.mod_appeared = {}
        self.max_ai_responses = {}
        self.last_message_time = defaultdict(float)
        self.active_channels = set()
        self.active_channels_lock = Lock()
        self.owner_role_id: int = int(os.getenv('OWNER_ROLE_ID', 123))
        self.mayu_id: int = int(os.getenv('MAYU_ID', 123))
        self.prisca_id: int = int(os.getenv('PRISCA_ID', 123))
        self.cache = {}
        self.report_cache = {}
        self.bot_cache = {}

    @commands.Cog.listener()
    async def on_ready(self) -> None:

        self.client.add_view(view=ApplyView(self.client))
        self.client.add_view(view=PremiumView(self.client))
        self.client.add_view(view=ReportView(self.client))
        self.check_inactive_cases.start()
        print('ReportSupport cog is online!')

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

    @commands.command()
    @utils.is_allowed([analyst_debugger_role_id], throw_exc=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def check(self, ctx: commands.Context) -> None:
        """ Temporary command for checking cases and timeouts. """

        guild = self.client.get_guild(server_id)

        # Look for people who completed their timeout time 
        role = guild.get_role(timedout_role_id)
        members = role.members

        for member in members:
            try:
                timeout_time = member.communication_disabled_until
                if timeout_time == None:
                    await member.remove_roles(role)
            except Exception as e:
                print(e)
                continue

        # Look inactive case rooms to delete
        current_ts = await utils.get_timestamp()
        inactive_cases = await self.get_inactive_cases(current_ts)

        for inactive_case in inactive_cases:
            channel = discord.utils.get(guild.channels, id=inactive_case[1])

            if channel:
                try:
                    await channel.delete()
                except Exception as e:
                    print(f"Failed at deleting the {channel}: {str(e)}")
            await self.remove_user_open_channel(inactive_case[0])

        emoji = "<:patao:1261308730918572163>"
        await ctx.send(emoji)

    def split_into_chunks(self, text: str, max_length: int) -> List[str]:
        """Splits text into chunks of a specified maximum length, respecting word boundaries."""
        max_length = min(max_length, 2000)  # Discord messages are limited to 2000 chars
        chunks = []
        
        while len(text) > max_length:
            # Find the last newline or space within the max_length limit
            split_index = text.rfind('\n', 0, max_length)
            if split_index == -1:  # If no newline, try to split by space
                split_index = text.rfind(' ', 0, max_length)
            if split_index == -1:  # If no space, hard split at max_length
                split_index = max_length

            # Append the chunk and update the remaining text
            chunks.append(text[:split_index].strip())
            text = text[split_index:].strip()

        # Append the remaining text as the last chunk
        if text:
            chunks.append(text)

        return chunks

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
            
            # Initiate the user_id variable
            user_id = 0
            
            # Grabs the channel ID
            channel_id = message.channel.id

            # Initialize the channel conversation history
            if all(channel_id not in d for d in 
                (
                self.mod_appeared,
                self.conversation_history,
                self.send_summary,
                self.max_ai_responses,)
                ):
                    self.conversation_history[channel_id] = []
                    self.max_ai_responses[channel_id] = []
                    self.send_summary[channel_id] = False
                    self.mod_appeared[channel_id] = False
            
            current_ts = await utils.get_timestamp()
            case_channel_aliases = ("general", "role", "case")
            report_channel_aliases = ("user", "staff")

            if channel.name.startswith(case_channel_aliases):
                await self.update_case_timestamp(channel.id, current_ts)
            
            if channel.name.startswith(report_channel_aliases):
                await asyncio.sleep(1) # Add a delay to avoid race conditions
                await self.update_case_timestamp(channel.id, current_ts)
                
                # Handles messages in report channels and forwards them to Claude
                # Ignore bot's own messages
                if message.author == self.client.user:
                    return

                # Add the user's message to the conversation history
                self.conversation_history[channel_id].append((f"{message.author}: {message.content}", time.time()))
                
                # Add the message time to the time history variable
                self.last_message_time[channel_id] = time.time()
                
                async with self.active_channels_lock:
                    # Start monitoring for multiple messages sent
                    if channel_id not in self.active_channels:
                        self.active_channels.add(channel_id)

                    # Verify if a mod/admin has sent a message
                    # This will be later used to stop the Claude AI from sending messages
                    if any(role.id in [moderator_role_id, admin_role_id] for role in message.author.roles):
                        user_id = message.author.id
                        self.mod_appeared[channel_id] = True

                        # Verify if the message is pinging the Sloth Bot
                        for user in message.mentions:
                            # Once a mod appears on the channel (aka mentions the sloth bot)
                            # The AI will send a recap of the report case on the mod's DM
                            if user.id == self.client.application_id:
                                await asyncio.sleep(1)
                
                                # Fetch and format conversation history
                                messages = "\n".join(
                                    msg if isinstance(msg, str) else msg[0]  # Extract the message text from the tuple
                                    for msg in self.conversation_history[channel_id]
                                )
                
                                messages += """
                                            Compile a brief and clear summary of the report in English, regardless of the original language.
                                            Example output:
                                            **Summary of Report:**  
                                            - **User Reported:**   
                                            - **Reason:** 
                                            - **Evidence Provided:** (Summarized details or mention if missing)  
                                            - **Time of Incident:** (Extracted from the conversation)  
                                            - **Additional Notes:** (Any relevant context, such as prior offenses)  
                                            - **Recommended Action:**
                                            """
                
                                # Send messages to Claude API
                                response = await self.get_claude_response(messages)
                
                                # Send Claude response to mod's DM
                                if user := self.client.get_user(user_id):
                                    response_chunks = self.split_into_chunks(response, 2000)
                                    for chunk in response_chunks:
                                        try:
                                            await user.send(f"{chunk}")
                                        except Exception as e:
                                            print(f"Failed to send DM: {e}")

                                # Stop monitoring each instance to make space for a new one
                                self.active_channels.remove(channel_id)
                    
                    # Start a task for inactivity monitoring
                    asyncio.create_task(self.monitor_channel_inactivity(channel_id, user_id))

    async def monitor_channel_inactivity(self, channel_id: int, user_id: int):
        """Monitor a channel for inactivity and send data to Claude API."""
        async with self.active_channels_lock:
            while not self.mod_appeared[channel_id] and len(self.max_ai_responses[channel_id]) < 2:
                # Wait for 1 second to check for inactivity
                await asyncio.sleep(1)
                
                time_diff = time.time() - self.last_message_time[channel_id]
                
                # Will verify if multiple messages have been sent in less than 10 seconds
                if time_diff > 5:  # No messages for 10 seconds

                    # Fetch and format conversation history
                    messages = "\n".join(
                        msg if isinstance(msg, str) else msg[0]
                        for msg in self.conversation_history[channel_id]
                    )

                    # Send messages to Claude API
                    response = await self.get_claude_response(messages)
                    
                    # Add AI response to the history
                    self.conversation_history[channel_id].append(f"Assistant: {response}")

                    # Add AI response count to the max AI responses sent
                    self.max_ai_responses[channel_id].append(1)

                    # Send response back to the channel
                    if channel := self.client.get_channel(channel_id):
                        response_chunks = self.split_into_chunks(response, 2000)
                        for chunk in response_chunks:
                            await channel.send(f"{chunk}")

                    # Stop monitoring each instance to make space for a new one
                    self.active_channels.remove(channel_id)
                    break
                
    async def handle_ban_appeal(self, message: discord.Message, payload) -> None:
        """ Handles ban appeal applications.
        :param guild: The server in which the application is running.
        :param payload: Data about the staff member who is opening the application. """

        emoji = str(payload.emoji)
        if emoji == '✅':
            # Gets the ban appeal app and does the magic
            if not (app := await self.get_application_by_message(payload.message_id)):
                return

            try:
                user = discord.Object(app[1])
                await message.guild.unban(user)
            except discord.NotFound:
                pass
            finally:
                await self.delete_application(message.id)
                await message.add_reaction('❤️‍🩹')

        elif emoji == '❌':
            # Tries to delete the ban appeal app from the db, in case it is registered
            app = await self.get_application_by_message(payload.message_id)
            if app and not app[3]:
                await self.delete_application(payload.message_id)


                app_channel = self.client.get_channel(self.ban_appeals_channel_id)
                app_msg = await app_channel.fetch_message(payload.message_id)
                await app_msg.add_reaction('🚫')

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

    # Sends the report information to Claude AI and sends a response on the chat for the user
    async def get_claude_response(self, prompt: str) -> str:
        """Fetches a response from Claude 3 using the Anthropic API."""
        client = anthropic.Anthropic()  # Initialize the Anthropic client
        
        with open('./extra/random/texts/other/report.txt', 'r') as file:
            content = file.readlines()
        
        # Send request to Claude API
        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0,
                system=f"""{content}""",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            # Extract the text content from the TextBlock
            raw_content = ''.join(block.text for block in message.content if hasattr(block, 'text'))
            return raw_content.strip()
        
        except Exception as e:
            print(f"Error interacting with Claude: {e}")
            return "An error occurred while communicating with the AI."

    async def report_action(self, interaction: discord.Interaction, vc_name: str, reportee: str, text: str, evidence: str):
        # sourcery skip: low-code-quality
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
            senior_mod = discord.utils.get(guild.roles, id=senior_role_id)
            overwrites.update({
                moderator: discord.PermissionOverwrite(
                    read_messages=False, 
                    send_messages=False, 
                    connect=False, 
                    view_channel=False, 
                    manage_messages=False),
                senior_mod: discord.PermissionOverwrite(
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
                message = await the_channel.send(content=f"{member.mention}, {senior_mod.mention}", embed=embed)
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
                
            # Calls the function to communicate with Claude's API
            await self.call_ai(reportee, text, evidence, the_channel, language_role)
    
    async def call_ai(self, reportee: str, text: str, evidence: str, the_channel, language_role: str):
        # Prepare the AI prompt
        responseBuffer = f"""
        A user submitted a report against a user of the Language Sloth Discord server.
        You are the AI assistant that will help users initially with their reports before a mod appears.
        Their native language is {language_role}, ask if they want to discuss in their native language
        or in english.
        
        Here are the details about the report:
        - The user that is being reported: {reportee}
        - The reason for the report: {text}
        - The evidence for the report case: {evidence}

        Please respond as a helpful assistant by asking brief short follow-up questions, with a maximum of 3 questions.
        You don't want to overwhelm with questions, be precise.
        Dont' ask in what voice or text channel it occured, because the mods already know it.
        """
        
        # Initialize conversation history for this channel
        channel_id = the_channel.id
        if channel_id not in self.conversation_history:
            self.conversation_history[channel_id] = []

        # Initialize the maximum responses AI
        # This will define how many messages the AI has sent and then will stop it
        if channel_id not in self.max_ai_responses:
            self.max_ai_responses[channel_id] = []

        # Add the initial user input to the conversation history
        self.conversation_history[channel_id].append(f"User: {responseBuffer.strip()}")

        # Get response from Claude
        response = await self.get_claude_response("\n".join(self.conversation_history[channel_id]))

        # Add AI response to the history
        self.conversation_history[channel_id].append(f"Assistant: {response}")

        # Add AI response count to the max AI responses sent
        self.max_ai_responses[channel_id].append(1)

        # Send the AI response in the channel
        await the_channel.send(content=f"{response}")

    # - Report a staff member
    async def report_staff(self, interaction: discord.Interaction, reportee: str, text: str, evidence: str):
        # Calls the function to perform the report
        await self.report_action(interaction, "staff", reportee, text, evidence)

    # - Report a standard User
    async def report_someone(self, interaction: discord.Interaction, reportee: str, text: str, evidence: str):
        # Calls the function to perform the report
        await self.report_action(interaction, "user", reportee, text, evidence)

    # - Get generic help
    async def generic_help(self, interaction: discord.Interaction, type_help: str, message: str, ping: bool = True) -> None:
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
            embed = discord.Embed(title=f"{type_help.title()}!", description=message, color=discord.Color.red())

            if ping:
                await the_channel.send(content=f"{member.mention}, {moderator.mention}", embed=embed)
            else:
                await the_channel.send(content=member.mention, embed=embed)

    async def get_message_content(self, member, check, timeout: Optional[int] = 300) -> str:
        """ Gets a message content.
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
            content = message.content
            return content

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

    async def get_reaction(self, member, check, timeout: int = 300):
        try:
            reaction, _ = await self.client.wait_for('reaction_add',
            timeout=timeout, check=check)
        except asyncio.TimeoutError:
            await member.send("**Timeout! Try again.**")
            return None
        else:
            return str(reaction.emoji)

    @commands.command(aliases=['permit_case', 'allow_case', 'add_witness', 'witness', 'aw'])
    @commands.has_any_role(*allowed_roles)
    async def allow_witness(self, ctx):
        """ Allows one or more witnesses to join a case channel.
        :param members: The member(s) to allow. """

        author = ctx.author
        members = await utils.get_mentions(ctx.message)

        if not members:
            return await ctx.send("**Inform at least one witness to allow!**")

        user_channel = await self.get_case_channel(ctx.channel.id)
        if not user_channel:
            return await ctx.send(f"**This is not a case channel, {author.mention}!**")

        confirm = await Confirm(f"**Are you sure you want to allow all `{len(members)}` informed {'witnesses' if len(members) > 1 else 'witness'} in this case channel, {ctx.author.mention}?**").prompt(ctx)
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

        return await ctx.send(f"**`{allowed}` {'witnesses have' if allowed > 1 else 'witness has'} been allowed here!**")

    @commands.command(aliases=['forbid_case', 'delete_witness', 'remve_witness', 'fw'])
    @commands.has_any_role(*allowed_roles)
    async def forbid_witness(self, ctx):
        """ Forbids one or more witnesses from a case channel.
        :param members: The member(s) to forbid. """

        members = await utils.get_mentions(ctx.message)
        if not members:
            return await ctx.send("**Inform a witness to forbid!**")

        user_channel = await self.get_case_channel(ctx.channel.id)
        if not user_channel:
            return await ctx.send(f"**This is not a case channel, {ctx.author.mention}!**")

        confirm = await Confirm(f"**Are you sure you want to forbid all `{len(members)}` informed {'witnesses' if len(members) > 1 else 'witness'} from this case channel, {ctx.author.mention}?**").prompt(ctx)
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

        return await ctx.send(f"**`{forbid}` {'witnesses have' if forbid > 1 else 'witness has'} been forbidden from here!**")
            
    @commands.command(aliases=['delete_channel', 'archive', 'cc', "close_case", "end_case", "solve", "solved"])
    @commands.has_any_role(*allowed_roles)
    async def close_channel(self, ctx):
        """ (MOD) Closes a Case-Channel. """

        member: discord.Member = ctx.author

        user_channel = await self.get_case_channel(ctx.channel.id)
        if not user_channel:
            return await ctx.send(f"**What do you think that you are doing? You cannot delete this channel, {member.mention}!**")
            
        channel = discord.utils.get(ctx.guild.text_channels, id=user_channel[0][1])
        embed = discord.Embed(title="Confirmation",
            description="Are you sure that you want to delete this channel?",
            color=member.color,
            timestamp=ctx.message.created_at)
        confirmation = await ctx.send(content=member.mention, embed=embed)
        await confirmation.add_reaction('✅')
        await confirmation.add_reaction('❌')
        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=20,
                check=lambda r, u: u == member and r.message.channel == ctx.channel and str(r.emoji) in ['✅', '❌'])
        except asyncio.TimeoutError:
            embed = discord.Embed(title="Confirmation",
            description="You took too long to answer the question; not deleting it!",
            color=discord.Color.red(),
            timestamp=ctx.message.created_at)
            return await confirmation.edit(content=member.mention, embed=embed)
        else:
            if str(reaction.emoji) == '✅':
                embed.description = f"**Channel {ctx.channel.mention} is being deleted...**"
                await confirmation.edit(content=member.mention, embed=embed)
                await asyncio.sleep(3)
                await channel.delete()
                await self.remove_user_open_channel(user_channel[0][0])
                # Moderation log embed
                moderation_log = discord.utils.get(ctx.guild.channels, id=mod_log_id)
                embed = discord.Embed(
                    title='__**Case Closed**__',
                    color=discord.Color.red(),
                    timestamp=ctx.message.created_at)
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
            "Debate Manager": "Debate Managers"
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
    
    @utils.is_allowed([lesson_management_role_id], throw_exc=True)
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
