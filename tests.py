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
# await ctx.send(content="\u200b", embed=embed, view=view)

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