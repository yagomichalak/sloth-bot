from functools import partial
import discord

async def callback(button, interaction) -> None:
    member = interaction.user

    try:
        role = discord.utils.get(member.guild.roles, id=int(button.custom_id))
    except Exception as e:
        print(e)
        pass
    else:
        member_roles_ids = [r.id for r in member.roles]
        if role and role.id not in member_roles_ids:
            await member.add_roles(role)
            await interaction.response.send_message(f"**The `{role}` role was assigned to you!**", ephemeral=True)
        else:
            await member.remove_roles(role)
            await interaction.response.send_message(f"**The `{role}` role was taken away from you!**", ephemeral=True)