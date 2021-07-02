msg = 'https://discord.gg/GWCcrurb'
invite = 'discord.gg/'
start_index = msg.index(invite)
end_index = start_index + 11
for c in msg[end_index:]:
    if c == ' ':
        break

    invite += c

inv_code = discord.utils.resolve_invite(invite)
guild_inv = discord.utils.get(await guild.invites(), code=inv_code)
if guild_inv:
    return True
else:
    return False