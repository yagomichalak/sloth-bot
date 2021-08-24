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

class Message:
    content: str

message = Message
message.content = 'dsadd https://cdn.discordapp.com/attachments/ads asda'
message.attachments = []

print('Content: ', message.content)
print('Attachments: ', message.attachments)

content = message.content.split()

attachment_root = 'https://cdn.discordapp.com/attachments/'
import discord
discord_attachments = [att for att in message.content.split() if att.startswith(attachment_root)]
for datt in discord_attachments:
    print(datt)
    try:
        fake_attachment = {"url": datt, "content_type": "image"}
        message.attachments.append(fake_attachment)
        content.remove(datt)
    except Exception as e:
        print('hehe', e)

message.content = ' '.join(content).strip() if content else None

print('New content: ', message.content)
print('New attachments: ', message.attachments)