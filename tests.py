# !eval
# import asyncio
# async def get_embed():
#     guild = ctx.guild

#     keywords = ['native', 'fluent', 'learning']

#     embed = discord.Embed(
#         title="__Role Counting__",
#         color=discord.Color.gold(),
#         timestamp=ctx.message.created_at
#     )
#     for kw in keywords:
#         the_roles = [(role, role.color) for role in guild.roles if role.name.lower().startswith(kw)]


#         role_dict = {}
#         for role in the_roles:

#             color = str(role[1])
#             if role_dict.get(color):
#                 role_dict[color]['roles'].append(role[0])
#             else:
#                 role_dict[color] = {'roles':[role[0]], 'members': []}

                        
                
#         for member in guild.members:
#             try:
#                 for ccolor, values in role_dict.items():
#                     for crole in values['roles']:
#                         if crole in member.roles:
#                             role_dict[ccolor]['members'].append(member)
#             except:
#                 pass
            
#         text_list = []
#         for rcolor, values in role_dict.items():
#             text_list.append(f"(**`{rcolor}`:** **Roles**: `{len(values['roles'])}` | **Users**: {len(values['members'])})")


#         embed.add_field(name=f"__{kw.title()}__ ({len(the_roles)}):", value='\n'.join(text_list), inline=False)

#     return embed

# async with ctx.typing():
#     embed = await get_embed()
#     await ctx.send(embed=embed)

# 2 ====
# edl!eval

# view= discord.ui.View()
# view.add_item(discord.ui.Select(placeholder='Native languages', options=[
#     discord.SelectOption(label='Native English', emoji='🇬🇧'),
#     discord.SelectOption(label='Native Swedish', emoji='🇸🇪'),
#     discord.SelectOption(label='Native German', emoji='🇩🇪'),
#     ], min_values=0))
# view.add_item(discord.ui.Select(placeholder='Fluent languages', options=[
#     discord.SelectOption(label='Fluent English', emoji='🇬🇧'),
#     discord.SelectOption(label='Fluent Swedish', emoji='🇸🇪'),
#     discord.SelectOption(label='Fluent German', emoji='🇩🇪'),
#     ], min_values=0))
# view.add_item(discord.ui.Select(placeholder='Learning languages', options=[
#     discord.SelectOption(label='Learning English', emoji='🇬🇧'),
#     discord.SelectOption(label='Learning Swedish', emoji='🇸🇪'),
#     discord.SelectOption(label='Learning German', emoji='🇩🇪'),
#     ], min_values=0))

# embed = discord.Embed(
#     title="__Germanic Languages__",
#     color=discord.Color.gold()
# )
# await ctx.send(embed=embed, view=view)


# z!eval

# embed = discord.Embed(
# title="Nitro", description="Expires in 46 hours", color=int('36393F', 16))
# space = '\u2800 '*8
# embed.set_author(name="A WILD GIFT APPEARS")
# view = discord.ui.View(timeout=None)
# class MyButton(discord.ui.Button):
#     def __init__(self) -> None:
#         super().__init__(style=discord.ButtonStyle.success, label=f"{space}ACCEPT{space}", custom_id="nitro_id")

#     async def callback(self, interaction: discord.Interaction) -> None:
#         await interaction.response.send_message(f"{interaction.user.mention}\nhttps://c.tenor.com/Z6gmDPeM6dgAAAAM/dance-moves.gif")

# view.add_item(MyButton())
# embed.set_thumbnail(url="https://pbs.twimg.com/media/EmSIbDzXYAAb4R7.png")
# await ctx.send(embed=embed, view=view)

"""
UPDATE UserCurrency AS OG,
     (SELECT user_id, user_money FROM UserCurrency WHERE user_id = 814130010260373515) T
    SET OG.user_money = OG.user_money + T.user_money
 WHERE OG.user_id = 754678627265675325;

"""

"""
UPDATE TribeMember AS OG,
    (SELECT member_id, tribe_role FROM TribeMember WHERE member_id =  657561152951156777) T
SET OG.tribe_role = T.tribe_role, T.tribe_role = 'Owner'
WHERE OG.member_id = 647452832852869120
"""
"""
SELECT * FROM TribeMember AS OG, (SELECT member_id, tribe_role FROM TribeMember T WHERE T.member_id = 657561152951156777) T WHERE OG.member_id = 647452832852869120
"""


"""
SELECT OG.member_id, OG.tribe_role FROM TribeMember AS OG, (SELECT member_id, tribe_role FROM TribeMember WHERE member_id = 657561152951156777) T WHERE OG.member_id = 647452832852869120;
"""

"""
UPDATE TribeMember OG 
    JOIN (
           SELECT owner_id, member_id, tribe_role
           FROM TribeMember
           WHERE member_id in (657561152951156777, 647452832852869120)
          ) T
    ON T.owner_id = OG.owner_id
    SET OG.tribe_role = T.tribe_role, T.tribe_role = 'Owner' 
    WHERE OG.member_id in (657561152951156777, 647452832852869120)
"""

"""
```mysql
UPDATE TribeMember as GL, (
    SELECT owner_id, member_id, tribe_role
    FROM TribeMember
    WHERE member_id = %s
) OG, (
    SELECT owner_id, member_id, tribe_role
    FROM TribeMember
    WHERE member_id = %s
) T
SET GL.tribe_role = ( 
    CASE 
        WHEN GL.member_id = %s THEN T.tribe_role
        WHEN GL.member_id = %s THEN OG.tribe_role
    END
)
WHERE GL.member_id in (%s, %s);
```
"""


"""

UPDATE TribeMember as OG
    JOIN TribeMember as T ON OG.member_id = T.
    SET OG.tribe_role = T.tribe_role, T.tribe_role = 'Owner';
"""


# SELECT USA.user_id, USA.user_time
# FROM UserServerActivity USA
# LEFT JOIN SlothProfile SP ON SP.user_id = USA.user_id
# WHERE SP.user_id IS NULL;


# SELECT USA.user_id, round(USA.user_time/60/60) FROM UserServerActivity USA LEFT JOIN SlothProfile SP ON SP.user_id = USA.user_id WHERE SP.user_id IS NULL AND round(USA.user_time/60/60) >= 3000 ORDER BY USA.user_time DESC;

# UPDATE UserServerActivity USA LEFT JOIN SlothProfile SP ON SP.user_id = USA.user_id SET USA.user_time = 0 WHERE SP.user_id IS NULL AND round(USA.user_time/60/60) >= 0;


# import re

# text: str = 'niiiiiiiiceee work'
# text: str = 'cool words'

# # found = re.findall(r'[<]?[a]?:[!_\-\w]+:[0-9]{0,18}[>]?', text)


# regexes: list[str] = [
#     re.compile(r'go{2,99}d wo{1,99}r[!_\-\w]s{0,99}', text),
#     re.compile(r'co{2,99}l wo{1,99}r[!_\-\w]s{0,99}', text),
#     re.compile(r'n[!_\-\w]{1,99}c[!_\-\w]{1,99} wo{1,99}r[!_\-\w]s{0,99}', text)
# ]

# for regex in regexes:
#     print(regex)
#     print()







# cases = [
#     # Upper horizontal
#     [(0, 0), (0, 1), (0, 2)],
#     # Middle horizontal
#     [(1, 0), (1, 1), (1, 2)],
#     # Bottom horizontal
#     [(2, 0), (2, 1), (2, 2)],

#     # Upper vertical
#     [(0, 0), (1, 0), (2, 0)],
#     # Middle vertical
#     [(1, 0), (1, 1), (1, 2)],
#     # Bottom vertical
#     [(2, 0), (2, 1), (2, 2)],

#     # Right diagonal
#     [(0, 0), (1, 1), (2, 2)],
#     # Left diagonal
#     [(0, 2), (1, 1), (2, 0)],

# ]

# you = [
#     (0, 0), (2, 0), (0, 1), (2, 2), (0, 2)
# ]


# # print(set([0, 0]))

# for case in cases:
#     if len(inter := set(you).intersection(set(case))) >= 3:
#         print('You won with: ', case)
#         break


# import enum


# class QuestEnum(enum.Enum):

#     one = 'test1'
#     twice = 'test2'
#     three = 'test3'
#     four = 'test4'
#     five = 'test5'
#     six = 'test6'


# print(QuestEnum.__dict__['_member_names_'][1-1])


# roles = ['Native French', 'Studying French', 'Music Club', 'Fluent English', 'Fluent Portuguese']
# t_role = 'Native French'


# language_roles = [r for r in roles if r.lower().startswith(('native', 'fluent', 'studying'))]
# language = t_role.lower().strip('native').strip('fluent').strip('studying').strip()

# print([lr for lr in language_roles if language.lower() in lr.lower()])
# print(language in language_roles)
# # print([])







# z!create_table_sloth_analytics
# z!create_table_data_bumps
# z!create_table_scheduled_events
# z!create_table_user_dr_vc_ts
# z!create_table_dynamic_rooms
# z!create_table_language_room
# z!create_table_premium_vc
# z!create_table_galaxy_vc
# z!create_table_user_vc_ts
# z!create_table_cursed_member
# z!create_table_duolingo_profile
# z!create_table_event_rooms
# z!create_table_giveaways
# z!create_table_giveaway_entries
# z!create_table_member_reminder
# z!create_table_queues
# z!create_table_slothboard
# z!create_table_user_timezones
# z!create_table_voice_channel_activity
# z!create_table_member_score
# z!create_table_user_currency
# z!create_table_user_items
# z!create_table_server_activity
# z!create_table_fake_accounts
# z!create_table_bypass_firewall
# z!create_table_firewall
# z!create_table_moderated_nicknames
# z!create_table_mutedmember
# z!create_table_user_infractions
# z!create_table_watchlist
# z!create_table_applications
# z!create_table_case_counter
# z!create_table_open_channels
# z!create_table_selection_menu
# z!create_table_sloth_skills
# z!create_table_skills_cooldown
# z!create_table_user_tribe
# z!create_table_tribe_member
# z!create_table_tribe_role
# z!create_table_sloth_profile
# z!create_table_user_babies
# z!create_table_user_pets
# z!create_table_stealth_status
# z!create_table_selection_menu








# import requests
# import json
# import os

# the_member = {}
# headers = {
#     'Authorization': f"Bot {os.getenv('TOKEN')}",
#     'Content-Type': 'application/json',
# }
# params = {
#     'limit': 40
# }
# endpoint = f'https://discord.com/api/v10/guilds/{guild.id}/members/{author.id}'
# response = requests.get(endpoint, headers=headers, params=params)
# if response.status_code == 200:
#     the_member = json.loads(response.text)
        

# print(the_member)

z!eval
message = "Goodnight. Smiley face"

voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients, guild=ctx.guild)

# Checks if the bot is in a voice channel
if not voice_client:
    await voice.channel.connect()
    voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients, guild=ctx.guild)

# Checks if the bot is in the same voice channel that the user

# Plays the song
if not voice_client.is_playing():
    tts = gTTS(text=message, lang=language)
    tts.save(f'tts/audio.mp3')
    audio_source = discord.FFmpegPCMAudio('tts/audio.mp3')
    voice_client.play(audio_source, after=lambda e: print('finished playing the tts!'))