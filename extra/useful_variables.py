list_of_commands = [
['• Moderation ',
'''
`|Snipe|` - Gets the last deleted message sent in the server.
`|Purge|` - Deletes a given amount of messages
`|Warn|` - Warns a member.
`|Mute|` - Mutes a member.
`|Unmute|` - Unmutes a member.
`|Tempmute|` - Temporarily mutes a member
`|Ban|` - Bans a member.
`|Unban|` - Unbans a member.
`|Softban|` - Softbans a member.
`|Hackban|` - Bans a member that is currently not in your server.
`|Logs|` - Moderation commands will be logged in a specific channel'''],
['• Social ',
'''
`|Serverinfo|` - Shows some information about the server.
`|Userinfo|` - Shows some information about a member.
`|Meme|` - Fetchs a random meme from the meme subReddit.'''],
['• General ',
'''
`|Create a Room|` - Allows the member to join a specific voice channel and automatically create a voice channel; or even asking the member about the room configurations in their dm's.
`|modrep|` - The bot sends an embedded message showing the activity of the moderators; allowing you to erase the statuses so it can start counting it again.'''],
['• Currency system ',
'''
`|points|` - A system that will give points/coins to users based on ther activity on the server; such as by sending X messages or having spent some time in the voice channels.
`|shop|` - A menu showing items that are avaiable for purchase by using those coins. (Roles are a good option for items)'''],
['• Tool ',
'''
`|count|` - Countsdown by given numerber.
`|tts|` - A text-to-speech command.
`|tr|` - Translates a message to another language, by specifying the initials of language. Ex: en for English or es for spanish.
`|ping|` - Shows the bot's ping.
`|math|` - Math operation commands; addition, subtraction, division, multiplication etc.
`|custom help command|` - A neat custom help command, that shows all the bot's available commands with their descriptions and usage.
`|members|` - Shows the current amount of members in the server.
`|status|` - The bot will show something in its status; it can be playing, streaming, watching or listening to something.'''],
['• Eval ',
'''A powerful command that basically allows you to do most Python commands from within Discord.'''],
['• Custom commands ',
'''
I'm open to new ideas, in other words, if you want a custom command designed specially for your server, having database access or not, you tell me how you want it to be done and if it's doable, I'll do it.''']
]


rules = {
    "No NSFW": "The Language Sloth is an educational community. For this reason, NSFW content will not be tolerated in either VCs or text channels. Pornographic, violent, foul, offensive, or even politically charged content/conversations are to be avoided, as they will result in punishment.",

    "Respectful Conduct": "Being intentionally disrespectful, following people, harassing over dms and using foul language are not allowed here, specially the Staff of this server.",

    "Avoid Controversy": "The following topics are not permitted on the server: Politics, Religion,Gender identity/Sexual orientation, Self-Harm or anything considered controversial. The only place where these topics are acceptable is Debate Club.",

    "No Advertising": "Advertising Discord servers or self-promoting via dm spam or voice channels without permission from our staff will result in immediate ban. If you would like to get permission, get in touch with our staff.",

    "No Doxing": "Do not share others' personal information without their consent.",

    "No Spamming": """Do not flood or spam text channels.
Do not spam react in messages.
Do not ping staff members repeatedly without a reason.
Do not mic spam/earrape in voice channels
Any of the above infractions may result in server mute or ban at the discretion of the admins/mods.""",

    "Do not impersonate others": "Do not impersonate other users or members of the staff.",

    "No Begging": "No asking to be granted roles/moderator roles. You may apply for these positions by accessing the link in #🌟announcements🌟 but repeatedly begging the staff may result in warnings or ban."

}

different_class_roles = {
    "programming": [
        "python", "html", "html and css",
        "html & css","c#", "csharp", "c++", "c",
        "c plus plus", "css", "mysql", "apache", "javascript",
        "js", "cobol", "java", "go", "golang", "fluter",
        "typescript", "ts", "js and ts", "lua",
        "javascript and typescript", "sql", "programming",
        "computer science", "cs50", "cs", "'web dev",
        "web development", "comp sci"
    ],
    "conlangs": [
        "esperanto"
    ],
    "hindustani": [
        "hindi", "urdu", "hindustani"
    ],
    "balkan languages": [
        "croatian", "serbian", "bosnian"
    ]
}


level_badges = {
    10: ['level_10', (5, 10)],
    15: ['level_15', (60, 10)],
    20: ['level_20', (110, 10)],
    25: ['level_25', (160, 10)],
}
flag_badges = {
    "discord_server_booster": ['badge_server_booster.png', (255, 10)],
    "nitro_booster": ['badge_nitro.png', (490, 10)],
    "early_supporter": ['badge_early_supporter.png', (545, 10)],
    "hypesquad_brilliance": ['badge_hypesquad_brilliance.png', (595, 10)],
    "hypesquad_balance": ['badge_hypesquad_balance.png', (595, 10)],
    "hypesquad_bravery": ['badge_hypesquad_bravery.png', (595, 10)],
    "verified_bot_developer": ['badge_bot_dev.png', (645, 10)],
    "partner": ['badge_discord_partnered.png', (695, 10)],
    "staff": ['badge_discord_partnered.png', (745, 10)],
}