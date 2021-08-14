!eval
import asyncio
async def get_embed():
    guild = ctx.guild

    keywords = ['native', 'fluent', 'learning']

    embed = discord.Embed(
        title="__Role Counting__",
        color=discord.Color.gold(),
        timestamp=ctx.message.created_at
    )
    for kw in keywords:
        the_roles = [(role, role.color) for role in guild.roles if role.name.lower().startswith(kw)]


        role_dict = {}
        for role in the_roles:

            color = str(role[1])
            if role_dict.get(color):
                role_dict[color]['roles'].append(role[0])
            else:
                role_dict[color] = {'roles':[role[0]], 'members': []}

                        
                
        for member in guild.members:
            try:
                for ccolor, values in role_dict.items():
                    for crole in values['roles']:
                        if crole in member.roles:
                            role_dict[ccolor]['members'].append(member)
            except:
                pass
            
        text_list = []
        for rcolor, values in role_dict.items():
            text_list.append(f"(**`{rcolor}`:** **Roles**: `{len(values['roles'])}` | **Users**: {len(values['members'])})")


        embed.add_field(name=f"__{kw.title()}__ ({len(the_roles)}):", value='\n'.join(text_list), inline=False)

    return embed

async with ctx.typing():
    embed = await get_embed()
    await ctx.send(embed=embed)