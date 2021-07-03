
z!eval
import discord
message = """
https://discord.gg/njVQKPBs"""

async def check_invite_guild(msg, guild):
    '''
    Checks whether it's a guild invite or not
    '''

    invite = 'discord.gg/'
    start_index = msg.index(invite)
    end_index = start_index + 11
    invite_hash = ''
    for c in msg[end_index:]:
        if c == ' ':
            break

        invite_hash += c

    for char in ['!', '@', '.', '(', ')', '[', ']', '#', '?', ':', ';', '`', '"', "'", ',', '{', '}']:
        invite_hash = invite_hash.replace(char, '')

    invite = invite + invite_hash
    print(invite)
    print()
    inv_code = discord.utils.resolve_invite(invite)
    print('inv code', inv_code)
    guild_inv = discord.utils.get(await guild.invites(), code=inv_code)
    if guild_inv:
        return True
    else:
        return False

something = await check_invite_guild(message, ctx.guild)
print(something)