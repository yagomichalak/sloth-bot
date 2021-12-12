import os
from dotenv import load_dotenv
load_dotenv()

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
    "NSFW is forbidden": """This applies to, among others, pornographic, gore, violent, foul, offensive content/conversations. They will not be tolerated in either VCs, text channels and DMs.
This rule also applies to user profiles (avatar, banner, status, about me etc).""",

    "Be respectful": """Discrimination on the grounds of race, nationality, religion, gender, or sexual orientation is forbidden.
Do not insult other users.
Do not troll.
Do not harass other users.
Do not swear mindlessly.
Do not make people feel uncomfortable, or otherwise bother them in any unwanted way.
This rule applies to both activity on the server and dms.""",

    "Avoid Controversy": """As the Language Sloth is an international server of educational nature, we have people from all over the world here. To avoid unnecessary conflicts, topics considered controversial are only allowed in the Debate Club.
This applies to, among others, politics, religion, self-harm, suicide, gender identity, sexual orientation.
This rule also applies to user profiles.""",

    "Advertising is forbidden": """Advertising Discord servers or self-promoting via text/voice channels or dms is not allowed. If you would like to get permission, get in touch with our Staff.""",

    "Do not dox": "Do not share other users' personal information without their consent.",

    "Do not spam": """Do not flood or spam text channels.
Do not spam react in messages.
Do not ping staff members repeatedly without a reason.
Do not mic spam/earrape/use soundboards in voice channels.""",

    "Do not impersonate others": "Do not impersonate other users or Staff members.",

    "Do not beg": """Do not ask to be granted roles such as moderator, teacher or event manager. You may apply for those roles in <#729454413290143774> 
Repeatedly begging the Staff for things may result in warnings or a ban."""

}

different_class_roles = {
    "programming": [
        "python", "html", "html and css",
        "html & css", "c#", "csharp", "c++", "c",
        "c plus plus", "css", "mysql", "apache", "javascript",
        "js", "cobol", "java", "go", "golang", "fluter",
        "typescript", "ts", "js and ts", "lua",
        "javascript and typescript", "sql", "programming",
        "computer science", "cs50", "cs", "web dev",
        "web development", "comp sci", "cyber security",
        "security", "haskell"
    ],
    "conlangs": [
        "esperanto", "toki pona"
    ],
    "hindi-urdu": [
        "hindi", "urdu", "hindustani", "hindi-urdu"
    ],
    "south asian languages": [
        "bengali", "tamil", "punjabi" 
    ],
    "balkan languages": [
        "croatian", "serbian", "bosnian"
    ],
    "sign languages": [
        "sign language", "sign languages", "asl",
        "fsl", "bsl"
    ],
    "portuguese": [
        "brazilian portuguese", "portuguese from brazil", 
        "portuguese", "angolan portuguese",
        "portuguese from angola", "portuguese from portugal", 
        "portuguese portuguese", "português", "portugués",
        "portugais"
    ],
    "english": [
        "english", "inglés", "inglês", "anglais",
        "angielski", "englisch", "ingleze",
        "ingilizce", "inggris", "영어", "الإنكليزية" ,"الإنكليزِيَّة" ,"الإنجليزية",
        "AL-إنجليزية", "الإنكليزية-Al", "الإنكليزِيَّة-AL", "AL-إنجليزية",
        "AL-الإنكليزية", "A-الإنكليزيَّة", "AL-إنكليزيَّة", "английский",
        "انگلیسی"
    ],
    "german": [
        "almanca", "allemand", "aléman", "jerman", "deutsch", "آلمانی",
        "ألماني", "德语", 'niemiecki', 'немецкий'
    ],
    "french": [
        "fransızca","francés", "francês", "français", "فرانسه"
    ],
    "italian": [
        "ايطالى", "اللغة الايطالية"
    ],
    "spanish": [
        "ispanyolca", "espagnol", "spanisch", "español", "hiszpański",
        "espanhol"
    ],
    "dutch": [
        "felemenkçe", "holländisch", "néerlandais"
    ],
    "russian": [
        "rusça" ,"russo" ,"russe" ,"russisch" 
    ],
    "mandarin": [
        "mandarín", "chinese"
    ],
    "cantonese": [
        "粤语"
    ],
    "japanese": [
        "japonês", "japonais" ,"japanisch", "japonés", "日本語"
    ],
    "korean": [
        "한국어"
    ], 
    "celtic": [
        "irish"
    ], 
    "filipino": [
        "tagalog"
    ], 
    "cebuano-bisaya": [
        "cebuano", "bisaya", "cebuano/bisaya"
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
    "discord_certified_moderator": ["badge_discord_certified_moderator.png", (745, 10)],
    "staff": ['badge_discord_partnered.png', (745, 530)]
}

banned_links = [
    'https://gfycat.com/pleasedflickeringhectorsdolphin',
    'https://gfycat.com/readygiftedgopher',
    'https://gfycat.com/infantileyearlyauklet',
    'https://thumbs.gfycat.com/InfantileYearlyAuklet-mobile.mp4',
    'https://gfycat.com/shamefulscarcedowitcher',
    'https://gfycat.com/fastickyinvisiblerail',
    'https://gfycat.com/wetangryflamingo',
    'https://giant.gfycat.com/TartAdolescentBird.mp4',
    'https://giant.gfycat.com/LeafyRashAmethystgemclam.mp4',
    'https://cdn.discordapp.com/attachments/787762360353947669/834568503121150042/LinedNaturalIndianrhinoceros.mp4',
    'https://cdn.discordapp.com/attachments/816038154389553272/839387573474557982/video0_1.mp4',
    'https://giant.gfycat.com/HarmfulThankfulFrigatebird.mp4',
    'https://thumbs.gfycat.com/AccurateFlatJuliabutterfly-mobile.mp4',
    'https://images-ext-2.discordapp.net/external/pMKck-5kRztOUwD0aJZjEWBABNRKausATegghw1f77U/https/giant.gfycat.com/RevolvingPassionateCirriped.mp4',
    'https/giant.gfycat.com/RevolvingPassionateCirriped.mp4',
    'https://gfycat.com/forthrightagonizingamericantoad',
    'https://thumbs.gfycat.com/SamePlumpDwarfrabbit-mobile.mp4/',
    'https://gfycat.com/educatedrawkitty',
    'https://gfycat.com/glassunfitcricket',
    'https://giant.gfycat.com/WeirdShadowyGoa.mp4',
    'https://gfycat.com/someaggravatingindochinahogdeer',
    'https://giant.gfycat.com/ImportantThankfulIceblueredtopzebra.mp4',
]

patreon_roles = {
        int(os.getenv('SLOTH_SUPPORTER_ROLE_ID')): ["**Thanks! {member.mention} just became a `Sloth Supporter`**", "**Hey! Thank you for helping our community, you will now receive :leaves: 300 ŁŁ monthly, you'll have access to exclusive content from our events.**", """Hello there Supporter! it's finally PayDay! you just received your monthly **300** :leaves: in your account!
You can check it with the command "z!status" or "z!profile", check our website to learn what to spend it with!""", 300],

        int(os.getenv('SLOTH_NATION_ROLE_ID')): ["**Thank you, {member.mention}, for joining the `Sloth Nation`!**", "**Hey! Thank you for helping our community, you will now receive :leaves: 2000 ŁŁ monthly, you'll have access to exclusive content from our events.**", """Yay! Hello nation, it's that time of the month! you just received your monthly **2.000** :leaves: in your account!
You can check it with the command "z!status" or "z!profile", check our website to learn what to spend it on! """, 2000],



        int(os.getenv('SLOTH_NAPPER_ROLE_ID')): ["**Wowie! {member.mention} joined the `Sloth Napper`!  <:zslothsleepyuwu:695420722419466371>**", "**Hey! Thank you for helping our community, you will now receive :leaves: 3500 ŁŁ monthly, you'll have access to exclusive content from our events.**", """Cheers! not to wake you up or anything, but you've just received your monthly **3.500** :leaves: in your account!
You can check it with the command "z!status" or "z!profile", check our website to learn what to spend it with!""", 3500],



        int(os.getenv('SLOTH_EXPLORER_ROLE_ID')): ["**Hype! {member.mention} joined the `Sloth Explorer`!  <:zslothvcool:695411944332460053> **", "**Hey! Thank you for helping our community, you will now receive :leaves: 5000 ŁŁ monthly, you'll have access to exclusive content from our events.**", """Hurray! It's that time of the month for you Sloth Explorers! We have added ***5.000*** :leaves: to your Bank Account!
You can check it with the command "z!status" or "z!profile", check our website to learn what to spend it with!""", 5000],



        int(os.getenv('ASTROSLOTH_ROLE_ID')): ["**Hype! {member.mention} is now the highest rank, `Astrosloth`!  <:zslothvcool:695411944332460053> **", "**Hey! Thank you for helping our community, you will now receive :leaves: 10000 ŁŁ monthly, you'll have access to exclusive content from our events.**", """Hip-Hip a Payment is order for our **AstroSloths**, you've just received your monthly **10.000** :leaves: in your account!
You can check it with the command "z!status" or "z!profile", check our website to learn what to spend it with!""", 10000]



}