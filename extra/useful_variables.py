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
    "english": {
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

        "Do not impersonate others": """ Do not impersonate other users or Staff members. """,

        "Do not beg": """Do not ask to be granted roles such as moderator, teacher or event manager. You may apply for those roles in <#729454413290143774> 
            Repeatedly begging the Staff for things may result in warnings or a ban.""",

        "Drama": """Do your best to keep drama out of this server. Any active attempt to start drama, or refusal to end a dispute within the server, may result in consequences."""
    },
    "portuguese": {
        "NSFW (Not Safe For Work) é proibido": """Isto aplica-se, entre outros, a conteúdos/conversações pornográficas, violentas, viés (gore) e ofensivas. Tais não serão toleradas nem em VCs (Voice Chats) nem em Canais de Texto.
            Esta regra também se aplica aos avatares (PFP), nomes de usuário, e seu status do Discord.""",

        "Seja respeitoso(a)":"""A discriminação com base na etnicidade, nacionalidade, religião, sexo e/ou orientação sexual é proibida.
            Não insulte os outros membros.
            Não assedie os outros membros.
            Não xingue despropositadamente.
            Não faça com que as pessoas se sintam desconfortáveis, ou de outra forma incomodá-las de qualquer maneira indesejada.
            Esta regra aplica-se tanto à atividade no servidor como ao DMs (Direct Message).""",
        
        "Evite controvérsia":"""Como o Language Sloth é um servidor internacional de natureza educacional, aqui temos pessoas de todo o mundo. Para evitar conflitos desnecessários, os tópicos considerados controversos só serão permitidos no Clube de Debate.
            Isto aplica-se, entre outros, à política, religião, automutilação, suicídio, identidade de gênero, orientação sexual.
            Esta regra também se aplica aos avatares (PFP).""",
            
        "Publicidade é proibida":"""Não é permitida a publicidade de outros servidores Discord ou auto-publicidade via canais de texto/voz ou DMs. Se desejar obter tal autorização, entre em contacto com a nossa Staff.""",
            
        "Não faça dox":""" Não partilhe a informação pessoal de outros utilizadores sem o seu retrospectivo consentimento. """,
        
        "Não faça spam":""" Não floode ou envie spam pelos canais de texto.
            Não faça spam de reações nas mensagens.
            Não mencione os membros do pessoal repetidamente sem um motivo.
            Não faça mic spam/earrape nos canais de voz. """,
            
        "Não imite os outros":""" Não se faça passar por outros usuários ou membros do Sloth. """,
        
        "Não implore":""" Não mendigue a atribuição de cargos/cargos de moderação. Mas pode candidatar-se a estes cargos acessando aos links no <#729454413290143774>  (Nem sempre estarão disponíveis) mas implorar repetidamente a Staff pode resultar em warnings ou ban. """,
        
        "Drama" : """ Evite dramas no servidor. Qualquer tentativa de iniciar ou a recusa em encerrar um conflito, pode resultar em consequências. """
    },
    "italian":{
        "Il NSFW è vietato":""" Ciò vale anche, tra le altre cose, per conversazioni e contenuti pornografici, gore, violenti e linguaggio volgare ed offensivo. Questi argomenti non saranno tollerati né in canali vocali né in canali testuali. 
            Questa regola vale anche per foto profilo, usernames e per lo stato di discord. """,
        
        "Essere rispettosi":""" La discriminazione per motivi di razza, nazionalità, religione, genere o orientamento sessuale è vietata.
            Non insulare altri utenti.
            Non molestare altri utenti.
            Non imprecare senza considerazione.
            Non far sentire le persone a disagio e non disturbale in qualsiasi modo indesiderato.
            Questa regola è applicata sia all'attività relativa al server che a quella relativa ai messaggi privati. """,

        "Evitare polemiche e argomenti controversi":""" Poiché "Language Sloth" è un server internazionale di natura educativa, ci sono persone provenienti da tutto il mondo. Per evitare conflitti inutili,  argomenti considerati controversi sono solo permessi nel Club del Dibattiti. 
            Questo vale, tra le altre cose, per la politica, religione, autolesionismo, suicidio, identità di genere e orientamento sessuale.
            Questa è applicata anche alle foto profilo. """,

        "Pubblicizzare è vietato":""" Pubblicizzare server discord o auto-promuoversi via canali testuali e messaggi privati non è permesso. Se desideri ottenere il permesso per farlo, per favore mettiti in contatto con il nostro Staff. """,
        
        "Non rilasciare dati sensibili di altri utenti":""" Non condividere le informazioni personali degli altri utenti senza il loro consenso. """,
        
        "Non spammare":""" Non spammare o intasare dimessagi i canali testuali.
            Non spammare le emoji di reazioni nei messaggi.
            Non menzionare i membri dello staff ripetutamente senza alcun motivo.
            Non abusare tramite il proprio microfono e non commettere earrape nei canali vocali. """,
            
        "Non impersonare gli altri":""" Non impersonare gli altri utenti del server o i memebri dello Staff. """,

        "Non mendicare":""" Non chiedere di ottenere ruoli o il ruolo di moderatore. Puoi candidarti per questa posizione accedendo al link in <#729454413290143774>  Tuttavia pregare e chiedere ripetutamente il ruolo allo Staff può comportare warns o essere bannati dal server. """,
        
        "Dramma":""" Fai del tuo meglio per lasciare il dramma fuori da questo server. Qualsiasi tentativo di iniziare un dramma, o il rifiuto di porre fine a una disputa all’interno del server, potrebbe avere conseguenze. """
    },
    "arabic":{
        "ممنوع NSFW":""" 
            وهذا ينطبق ،على <المحتوى / المحادثات>: الإباحية ، الدموية ، العنيفة ، الكراهية ، المسيئة.
            لن يتم التسامح معها في أي من القنوات الصوتية أو القنوات النصية.
            تنطبق هذه القاعدة أيضًا على صور الملف الشخصي وأسماء المستخدمين وحالة الديسكورد. """,
        
        "كن محترما":"""
            يحظر التمييز على أساس العرق أو الجنسية أو الدين أو الجنس أو التوجه الجنسي.
            لا تهين المستخدمين الآخرين.
            لا تضايق المستخدمين الآخرين.
            لا تسب او تشتم بلا مبالاة.
            لا تجعل الناس يشعرون بعدم الارتياح ، أو تزعجهم بأي طريقة أخرى غير مرغوب فيها.
            تنطبق هذه القاعدة على كل من النشاط على السيرفير و المحادثات والرسائل الخاص. """,
        
        "تجنب الجدل":"""
            نظرًا لأن Language Sloth هو سيرفير دولي ذو طبيعة تعليمية ، فلدينا أشخاص من جميع أنحاء العالم هنا. لتجنب النزاعات غير الضرورية ، لا يُسمح بالمواضيع التي تعتبر مثيرة للجدل إلا في نادي المناقشة "Debate club".
            وهذا ينطبق  على السياسة والدين وإيذاء النفس والانتحار والهوية الجنسية والتوجه الجنسي.
            تنطبق هذه القاعدة أيضًا على صور الملف الشخصي. """,
        
        "يمنع الاعلان.":""" 
            لا يُسمح بالإعلانات أو الترويج الذاتي عبر القنوات النصية / الصوتية أو المحادثات والرسائل الخاصه. 
            إذا كنت ترغب في الحصول على إذن ، فاتصل بفريق العمل الخاص بنا. """,
        
        "لاتقم  بـ  Doxxing":""" 
            لا تشارك المعلومات الشخصية للمستخدمين الآخرين  دون موافقتهم  مثل الاسم الحقيقي 
            وعنوان المنزل ومكان العمل والهاتف والمعلومات المالية الخ. """,
        
        "لا تقم ب Spam":""" 
            لا تغمر قنوات الدردشة برسائل spam.
            لا تقم ب سبام للتفاعل على الرسائل.
            لا تقم بمنشن للمشرفين بشكل متكرر بدون سبب.
            لا للميكروفون المزعج غير المرغوب فيه/ لا للصراخ والازعاج الصوتي الذي يؤذي الاذن. """,
        
        "لا تنتحل شخصية الآخرين":""" لا تنتحل صفة مستخدمين أوالمشرفين. """,
        
        "لا تتسول": """ لا يطلب منحك الأدوار / أدوار الوسيط. يمكنك التقدم لشغل هذه الوظائف عن طريق الوصول إلى الرابط <#729454413290143774> 
            في  ولكن التسول المتكرر للمشرفين  قد يؤدي إلى تحذيرات أو حظر. """,
        
        "Drama": """Do your best to keep drama out of this server. Any active attempt to start drama, or refusal to end a dispute within the server, may result in consequences."""
    },
    "turkish":{
        "NSFW yasaktır":""" Bu kural pornografik, vahşet, şiddet içeren, açık saçık, saldırgan içerik/konuşmalar için geçerlidir. Sesli kanallarda veya metin kanallarında bunlara tolerans gösterilmeyecektir.
            Bu kural aynı zamanda profil resimleri, kullanıcı adları ve discord durumu için de geçerlidir. """,

        "Saygılı olun":""" Irk, milliyet, din, cinsiyet veya cinsel yönelim temelinde ayrımcılık yapmak yasaktır.
            Diğer kullanıcılara hakaret etmeyin.
            Diğer kullanıcıları taciz etmeyin.
            Boş yere, düşüncesizce küfretmeyin.
            İnsanları rahatsız etmeyin ya da onları istenmeyen herhangi bir şekilde rahatsız etmeyin.
            Bu kural hem sunucudaki aktivitede hem de özel mesajlar(dm) için geçerlidir. """,
            
        "Tartışmadan Kaçının":""" Language Sloth, eğitim amaçlı uluslararası bir sunucu olduğundan, burada dünyanın her yerinden insanlarımız var. Gereksiz çatışmalardan kaçınmak için tartışmalı olarak kabul edilen konulara yalnızca Münazara Kulübü'nde izin verilir.
            Bu kural politika, din, kendine zarar verme, intihar, cinsiyet kimliği, cinsel yönelim için geçerlidir.
            Bu kural profil resimleri için de geçerlidir. """,
            
        "Reklam yasaktır":""" Discord sunucularının reklamını yapmak veya metin/ses kanalları veya özel mesaj yoluyla kendi tanıtımını yapmak yasaktır. İzin almak istiyorsanız, yetkililer ile iletişime geçin. """,
        
        "Dox yapmayın":""" Diğer kullanıcıların kişisel bilgilerini izinleri olmadan paylaşmayın. """,
        
        "Spamlamayın":""" Metin kanallarına flood veya spam göndermeyin.
            Mesajlara spam tepki vermeyin.
            Yetkili kullanıcıları sebepsiz yere tekrar tekrar ping atmayın.
            Ses kanallarında spam/earrape yapmayın. """,
            
        "Başkalarını taklit etmeyin":""" Diğer kullanıcıların veya Yetkililerin hesaplarını taklit etmeyin. """,
        
        "Dilenmeyin":""" Yetkili Roller/Moderatör rolü verilmesi için dilenmeyin. Bu pozisyonlara <#729454413290143774> 'daki linke girerek başvurabilirsiniz ancak personele tekrar tekrar yalvarmanız uyarı veya banlanmanız ile sonuçlanabilir. """,
        
        "Drama": """ Dramayı bu sunucudan uzak tutmak için elinizden geleni yapın. Drama başlatmaya herhangi bir eylemli kalkışma veya sunucu içindeki bir anlaşmazlığı sona erdirmeyi reddetme, sonuçlara neden olabilir. """
    },
    "russian":{
        "NSFW запрещен":""" Это относится, в частности, к порнографическому, кровавому, жестокому, непристойному, оскорбительному контенту/разговорам. Вышеперечисленное не допускаются ни в голосовых чатах, ни в текстовых каналах. 
            Это правило так же относится к изображениям профиля, никнейму пользователей и дискорд статусу.""",
            
        "Будьте вежливыми":""" Запрещена дискриминация на почве расовой, национальной, религиозной принадлежности или же сексуальной ориентации. 
            ЗАПРЕЩЕНЫ: 
            Грубые провокации и оскорбления других пользователей. 
            Злоупотребление матами/нецензурной бранью. 
            Беспокоить участников или же причинять им неудобства. 
            Правила должны быть соблюдены как на сервере, так и в личных сообщениях. """,
            
        "Избегайте споров":""" Поскольку Language Sloth является международным сервером образовательного характера, у нас есть люди со всего мира. Чтобы избежать ненужных конфликтов, спорные темы разрешены только в клубе дебатов. 
            Запрещено обсуждать политические, религиозные темы, а так же темы, касающиеся селфхарма/самоповреждения, самоубийства, гендерной идентичности, сексуальной ориентации. 
            Это правило относится и к фотографиям профиля.  """,
            
        "Реклама запрещена":""" Не допускается реклама дискорд серверов или самореклама в текстовых/голосовых каналах или в личных сообщениях. Если вы хотите получить разрешение, свяжитесь с нашим персоналом.""",
        
        "Доксинг запрещен":""" Не разглашайте личную информацию других пользователей без их согласия. """,
        
        "Не спамить":""" Запрещен спам, флуд в любых его проявлениях. 
            ЗАПРЕЩЕНО: 
            Флудить или спамить текстовые каналы. 
            Спам реакциями в сообщениях. 
            Отмечать/упоминать роли персонала без причины и неоднократно. 
            Транслировать спам звуки, музыку, громкие шумы через микрофон в голосовых каналах. """,
            
        "Не выдавайте себя за других":""" Запрещено копировать профили других пользователей или персонала. """,
        
        "Не попрошайничать":""" Не запрашивать предоставление ролей/ролей модератора. Вы можете подать заявку на эти должности, перейдя по ссылке в <#729454413290143774>. Если будете не переставая просить у персонала, это может привести к бану или к выдаче предупреждения. """,
        
        "Drama": """Do your best to keep drama out of this server. Any active attempt to start drama, or refusal to end a dispute within the server, may result in consequences."""
    }
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
        "hindi", "urdu", "hindustani", "hindi-urdu", "angrejee"
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
        "انگلیسی", "英語", "英语", "أنكليزية", "bahasa inggris"
    ],
    "german": [
        "almanca", "allemand", "aléman", "jerman", "deutsch", "آلمانی",
        "ألماني", "德语", 'niemiecki', 'немецкий'
    ],
    "french": [
        "fransızca", "francés", "francês", "français", "فرانسه", "Французский",
        "Французскии"
    ],
    "italian": [
        "ايطالى", "اللغة الايطالية", "italiano"
    ],
    "spanish": [
        "ispanyolca", "espagnol", "spanisch", "español", "hiszpański",
        "espanhol", "spanhol", "spagnolo"
    ],
    "dutch": [
        "felemenkçe", "holländisch", "néerlandais", "flemish"
    ],
    "russian": [
        "rusça" ,"russo" ,"russe" ,"russisch" 
    ],
    "mandarin": [
        "mandarín", "chinese", "bahasa mandarin"
    ],
    "cantonese": [
        "粤语"
    ],
    "japanese": [
        "japonês", "japonais" ,"japanisch", "japonés", "日本語", "giapponese", "bahasa jepang"
    ],
    "korean": [
        "한국어", "bahasa korea"
    ], 
    "celtic": [
        "irish"
    ], 
    "filipino": [
        "tagalog"
    ], 
    "cebuano-bisaya": [
        "cebuano", "bisaya", "cebuano/bisaya"
    ],
    "malay": [
        "马来文"
    ],
    "arabic": [
        "arabe", "árabe", "arabo"
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
        int(os.getenv('SLOTH_SUPPORTER_ROLE_ID', 123)): ["**Thanks! {member.mention} just became a `Sloth Supporter`**", "**Hey! Thank you for helping our community, you will now receive :leaves: 300 ŁŁ monthly, you'll have access to exclusive content from our events.**", """Hello there Supporter! it's finally PayDay! you just received your monthly **300** :leaves: in your account!
You can check it with the command "z!status" or "z!profile", check our website to learn what to spend it with!""", 300],

        int(os.getenv('SLOTH_NATION_ROLE_ID', 123)): ["**Thank you, {member.mention}, for joining the `Sloth Nation`!**", "**Hey! Thank you for helping our community, you will now receive :leaves: 2000 ŁŁ monthly, you'll have access to exclusive content from our events.**", """Yay! Hello nation, it's that time of the month! you just received your monthly **2.000** :leaves: in your account!
You can check it with the command "z!status" or "z!profile", check our website to learn what to spend it on! """, 2000],



        int(os.getenv('SLOTH_NAPPER_ROLE_ID', 123)): ["**Wowie! {member.mention} joined the `Sloth Napper`!  <:zslothsleepyuwu:695420722419466371>**", "**Hey! Thank you for helping our community, you will now receive :leaves: 3500 ŁŁ monthly, you'll have access to exclusive content from our events.**", """Cheers! not to wake you up or anything, but you've just received your monthly **3.500** :leaves: in your account!
You can check it with the command "z!status" or "z!profile", check our website to learn what to spend it with!""", 3500],



        int(os.getenv('SLOTH_EXPLORER_ROLE_ID', 123)): ["**Hype! {member.mention} joined the `Sloth Explorer`!  <:zslothvcool:695411944332460053> **", "**Hey! Thank you for helping our community, you will now receive :leaves: 5000 ŁŁ monthly, you'll have access to exclusive content from our events.**", """Hurray! It's that time of the month for you Sloth Explorers! We have added ***5.000*** :leaves: to your Bank Account!
You can check it with the command "z!status" or "z!profile", check our website to learn what to spend it with!""", 5000],



        int(os.getenv('ASTROSLOTH_ROLE_ID', 123)): ["**Hype! {member.mention} joined the `Astrosloth`!  <:zslothvcool:695411944332460053> **", "**Hey! Thank you for helping our community, you will now receive :leaves: 10000 ŁŁ monthly, you'll have access to exclusive content from our events.**", """Hip-Hip a Payment is order for our **AstroSloths**, you've just received your monthly **10.000** :leaves: in your account!
You can check it with the command "z!status" or "z!profile", check our website to learn what to spend it with!""", 10000],

        int(os.getenv('MASTERSLOTH_ROLE_ID', 123)): ["**Hype! {member.mention} is now the highest rank, `Mastersloth`!  <:zslothvcool:695411944332460053> **", "**Hey! Thank you for helping our community, you will now receive :leaves: 10000 ŁŁ monthly, you'll have access to exclusive content from our events.**", """Hehe boi, here is the monthly payment for our **MasterSloths**, you've just received your monthly **10.000** :leaves: in your account!
You can check it with the command "z!status" or "z!profile", check our website to learn what to spend it with!""", 22000]



}