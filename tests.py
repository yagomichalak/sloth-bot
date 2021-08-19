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

{"fields":[{"name":"  Channels are places in our server where people can talk about different topics.","value":"Now, select your language roles from the roles list and access your channels!","inline":false}],"title":"Now that you've joined Everyday Languages, make your presence known and say hello! :wave:","description":"It's fantastic to see you here! Don't forget to get your roles then come say hi to us. We are ecstatic about getting to know you!","thumbnail":{"url":"https://www.everydaylanguages.org/2.png"},"image":{"url":"https://cdn.discord.me/server/8d1c330e420c2e4380fa80dfa4d3c658e09b6db2895b152bd67b0b91ee8dfa6c/articles/article_0257f3942d5c37b7a353f340ee737049cdbf507becb0bfcf5f6a9aa33a0a122d.jpg"},"author":{"name":"Language Role Selection","icon_url":"https://www.everydaylanguages.org/8.png"},"color":14937549,"footer":{"icon_url":"https://www.everydaylanguages.org/Discord.png","text":"Everyday Languages "}}


edl!eval

embed = discord.Embed(
    title="Now that you've joined Everyday Languages, make your presence known and say hello! :wave:",
    description="It's fantastic to see you here! Don't forget to get your roles then come say hi to us. We are ecstatic about getting to know you!",
    color=14937549
)
embed.add_field(name="Channels are places in our server where people can talk about different topics.", value="Now, select your language roles from the roles list and access your channels!")
embed.set_author(name='Language Role Selection', icon_url="https://www.everydaylanguages.org/8.png")
embed.set_image(url="https://cdn.discord.me/server/8d1c330e420c2e4380fa80dfa4d3c658e09b6db2895b152bd67b0b91ee8dfa6c/articles/article_0257f3942d5c37b7a353f340ee737049cdbf507becb0bfcf5f6a9aa33a0a122d.jpg")
embed.set_thumbnail(url="https://www.everydaylanguages.org/2.png")
embed.set_footer(text="Everyday Languages", icon_url="https://www.everydaylanguages.org/Discord.png")
await ctx.send(embed=embed)