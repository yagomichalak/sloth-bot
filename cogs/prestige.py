# import.standard
import os
from random import choice, randrange

# import.thirdparty
from discord import slash_command
from discord.ext import commands

# variables.id
guild_ids = [int(os.getenv('SERVER_ID', 123))]

# variables.role
mod_role_id = int(os.getenv('MOD_ROLE_ID', 123))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID', 123))
owner_role_id = int(os.getenv('OWNER_ROLE_ID', 123))

class Prestige(commands.Cog, command_attrs=dict(hidden=True)):
    """ Category for prestige commands. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    @slash_command(name="dnk", guild_ids=guild_ids)
    async def _dnk(self, ctx) -> None:
        """ Tells you something about DNK. """

        await ctx.respond(f"**`Sapristi ! C'est qui ? Oui, c'est lui le plus grave et inouï keum qu'on n'a jamais ouï-dire, tandis qu'on était si abasourdi et épris de lui d'être ici affranchi lorsqu'il a pris son joli gui qui ne nie ni être suivi par une souris sur son nid ni être mis ici un beau lundi !`**")

    @slash_command(name="gabriel", guild_ids=guild_ids)
    async def _gabriel_slash(self, ctx) -> None:
        """ Tells you something about Gabriel. """

        await ctx.respond(f"**<@875915997767430214>? Il est frais et il est chaud, et quand il rap c'est que du feu**")

    @commands.command(name="gabriel", aliases=["gab", "gabi", "gbrl", "gaburierudesu", "camisa9", "atacante", "rapper"])
    async def _gabriel_command(self, ctx) -> None:
        """ Tells you something about Gabriel. """

        await ctx.message.delete()
        await ctx.send(f"**<@875915997767430214>, desculpa por interromper o seu andamento, é que eu te vi passando, você é artista?**")
        
    @commands.command(aliases=["lexi", "lèqçi", "lexis"])
    async def alexis(self, ctx) -> None:
        """ A command for telling something about Alexis. """

        await ctx.message.delete()

        sentences = [
            "**I have a really nice voice**",
            "**Best sister-in-law ever**",
            "**z!bj 50**",
            "**z!bj 5000**",
            "**I see where you're coming from**",
        ]

        await ctx.send(choice(sentences))

    @commands.command()
    async def freak(self, ctx) -> None:
        """ A command for telling something about Marceline. """

        await ctx.message.delete()
        await ctx.send("You mean missy aka Marceline")

    @commands.command()
    async def hiba(self, ctx) -> None:
        """ A command for telling something about Hiba. """

        await ctx.message.delete()
        
        sentences = [
            "<@760178072904531988> Give me attention",
            "<@760178072904531988>\nAll of these girl on some uppercase shi\nThat means they all cap\nBeing the best at whatever i do\nThat’s sounding on brand",
            "<@760178072904531988> Morning 🤨",
            "<@760178072904531988> Kant hear you",
            "<@760178072904531988> Can you move me?",
            "<@760178072904531988>\nYou wouldnt put it\nSo no point ~",
            "<@760178072904531988>\nGab\nI have a problem",
            "<@760178072904531988> mysqli_query($cnx,$req1)",
            "<@760178072904531988> Caught you there ✨",
            "<@760178072904531988> I’m restarted",
        ]

        await ctx.send(choice(sentences))

    @commands.command(aliases=["not_lime", "lemonade", "citric", "yellow_fruit"])
    async def lemon(self, ctx) -> None:
        """ A command for telling something about Lemon. """

        await ctx.message.delete()

        sentences = [
            "**Easy peasy, lemon squeezy** �",
            "**When life gives you a lemon, make it an admin!** <:lemonsloth:785872087414996992>",
            "**My greatest fear is a limenade...**"
        ]

        await ctx.send(choice(sentences))

    @commands.command(aliases=["felipe"])
    async def sousa(self, ctx) -> None:
        """ A command for telling something about Sousa. """

        await ctx.message.delete()

        sentences = [
            "If you give <@372100977060347906> a cup of coffee, he might tell you a secret...",
            "**<@372100977060347906> He's Simple, He's Dumb, He's The Pilot.**",
            "Gohan, vê se você me escuta... Não é pecado lutar pela justiça, ao contrário, é uma boa ação, pense... Existem inimigos que não são convencidos com palavras, você só tem que soltar a fúria que está dentro do seu espírito, eu sei como você se sente... Não precisa mais suportar isso Gohan... Gohan, proteja os seres vivos e as plantas desse mundo que eu tanto amei, conto com você. <@372100977060347906>"
        ]

        await ctx.send(choice(sentences))

    @commands.command(aliases=["maksiu", "maks1u", "c4tchme"])
    async def choose_right(self, ctx) -> None:
        """ A command for telling something about maksiu. """

        await ctx.message.delete()

        idkWhichOne = [
            "Oh, <@312940056115544064>. 🧠 He's found... never mind",
            "<@312940056115544064> If this were a game of 'spot the right one,' I'd say we're still playing 😈",
            "👌 ||Almost there||, but this one is playing hard to get! <@312940056115544064>",
            "u got me! 💐 from <@312940056115544064>",
            "with love to <@439110609745870870> 🇮🇹 from <@312940056115544064>"
        ]

        await ctx.send(choice(idkWhichOne))

    @commands.command(aliases=["birds"])
    async def keybirds(self, ctx) -> None:
        """ A command for telling something about Keybirds. """

        await ctx.message.delete()

        sentences = [
            "<@584699027421921280> Well, sounds like a good idea",
            "<@584699027421921280> Stina wants to go outside",
            "<@584699027421921280> I closed it and now it's closed"
            ]

        await ctx.send(choice(sentences))

    @commands.command()
    async def loral(self, ctx) -> None:
        """ A command for telling something about Loral. """

        await ctx.message.delete()
        await ctx.send("<@759049454819999776> Mans annoying")

    @commands.command()
    async def leonor(self, ctx) -> None:
        """ A command for telling something about Leonor. """

        await ctx.message.delete()
        await ctx.send("<@754678627265675325> Human brain smells like cat piss when it dries out")

    @commands.command()
    async def anis(self, ctx) -> None:
        """ A command for telling something about anis. """

        await ctx.message.delete()
        await ctx.send("<@515991382217981952> niso")

    @commands.command(aliases=["hodjapie", "kebap", "kebapguy", "onekebappls", "muazzam"])
    async def hodja(self, ctx) -> None:
        """ A command for telling something about the kebap guy, Hodja. """

        if not hasattr(self, "_last_hodja_sentence"):
            self._last_hodja_sentence = None
        
        if not hasattr(self, "_last_hodja_gif"):
            self._last_hodja_gif = None

        await ctx.message.delete()

        sentences = [
            ("**I THOUGHT YOU WERE A GIRL** <@201086628167417857>", "https://tenor.com/view/teen-angel-body-swap-transformation-transform-shapeshift-gif-20282289"),
            ("*one kebap pls* <@201086628167417857>", "https://tenor.com/view/kebap%C3%A7%C4%B1-abi-terleyen-kebap%C3%A7%C4%B1-abi-kebap-yapan-abi-terleyen-abi-terleyen-adam-gif-16683983459963325554"),
            ("**the f-ck is up yo?** <@201086628167417857>", "https://tenor.com/view/k%C4%B1l%C4%B1%C3%A7daro%C4%9Flu-gif-17522471039651255534"),
            ("*aferin* <@201086628167417857>", "https://tenor.com/view/anime-fight-anime-argue-suisei-suisei-fight-gif-4325572992682955548"),
            ("**muazzam** <@201086628167417857>", "https://tenor.com/view/christmas-christmas-tree-throw-angry-gif-15936546"),
            ("*type shi* <@201086628167417857>", "https://tenor.com/view/suit-black-man-sitting-posing-gif-27703959"),
            ("*burada demokrasi yok hocam* <@201086628167417857>", "https://tenor.com/view/1984-gif-19260546"),
            ("*my honest reaction* <@201086628167417857>", "https://tenor.com/view/my-honest-reaction-meme-meme-reaction-thugga-trying-not-to-laugh-gif-17796125959159847090"),
            ("**allahümmeyarab** <@201086628167417857>", "https://tenor.com/view/praise-allah-gif-24350702"),
            ("*haydaaa* <@201086628167417857>", "https://tenor.com/view/bruh-bruh-triggered-bruh-bttv-meme-gif-16887494"),
            ("*şeytan müzik listener* <@201086628167417857>", "https://tenor.com/view/bad-omens-artificial-suicide-the-death-of-peace-of-mind-metalcore-metal-gif-24779206"),
            ("bro like when a mf deadass says *“hojda”* like what the **ACTUAL** hell is that supposed to be. it’s *“hodja.”* it’s literally right there. not even a hard word. like it’s not some advanced quantum linguistics olympiad, it’s five damn letters. just say *“hoca”* if you’re gonna butcher it anyway. mf acting like vowels are optional and spelling is interpretive art. like imagine being so **braindead** your brain is just two neutrons drifting past each other in a fog of stupid and you somehow manage to say *“hojda”* with your whole chest like you did something.\n**I SWEAR TO GOD MFFFFFFFFFFFFFFFFFFFFFFFFF**\n**YOU HAD ONE JOB**\n**RAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA**\nlike it’s not even a typo at this point, it’s a full-blown declaration of war on phonetics. *“hojda”* sounds like a medieval cough. like some peasant sneezed in 1347 and accidentally invented that word while dying of the plague. and don’t even get me started on the smugness. mf say it like they dropping ancient wisdom. no, you're not profound. you just misspelled *“hodja”* and now i’m gonna have to sit in a dark room and rethink the future of communication.\n**RAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA**\n**YOU GOT 26 LETTERS AND STILL MADE THE WRONG CHOICE**\n**THE BAR WAS ON THE FLOOR**\n**AND YOU BROUGHT A SHOVEL**\nthis is why i got trust issues bro. someone says *“hojda”* and all my neurons just short-circuit out of sheer disappointment. like how do you even get it that wrong. i’m gonna start charging people a stupidity tax for every time i hear that nonsense. bro just log off. delete your keyboard. seek help.\n**RAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA**\n*ok, i'm calm now* <@201086628167417857>", "https://tenor.com/view/low-tier-god-gif-25175746"),
        ]

        gifs = [
            "https://tenor.com/view/yayl%C4%B1-oyuncak-yayl%C4%B1-emoji-g%C3%B6z-k%C4%B1rpan-emoji-g%C3%B6z-k%C4%B1rparak-g%C3%BClen-emoji-wink-gif-2176531366822319352",
            "https://tenor.com/view/gopher-groundhod-groundhog-eating-gopher-eating-gopher-eating-carrot-gif-26389545",
            "https://tenor.com/view/cerbervt-cerber-vtuber-gif-543256581190828359",
            "https://tenor.com/view/meme-down-syndrome-funny-tongue-action-tongue-out-meme-gif-572114404054760484",
            "https://tenor.com/view/ma%C3%A7avras1-gif-16101498646883457546",
            "https://tenor.com/view/peaky-blinders-no-fighting-no-fucking-fighting-fight-fuck-gif-16259749058826278291",
            "https://tenor.com/view/open-season-boog-elliot-sicko-mode-booty-shake-gif-15909219",
            "https://tenor.com/view/cat-one-at-a-time-ladies-aaron-if-he-was-a-cat-funny-cat-gif-565648516443483223",
            "https://tenor.com/view/qurial-bleeeh-cat-meme-qvrial-gif-27229139",
            "https://tenor.com/view/ankara-bina-%C3%A7%C3%B6l-ankara-%C3%A7%C3%B6l-ankara-kalp-gif-3276235952120258144",
            "https://tenor.com/view/orange-cat-gets-flung-and-explodes-orange-cat-funny-cat-meme-explodes-gif-10706110874965244466",
            "https://tenor.com/view/mean-cat-cat-fu-gif-23644413",
            "https://tenor.com/view/homer-the-simpsons-dance-wiggle-gif-17689048",
            "https://media.discordapp.net/attachments/780931454845583410/846535086933147689/13f.gif",
            "https://tenor.com/view/lowtiergod-low-tier-god-ltg-dale-girlboss-gif-15880573990312780020",
            "https://tenor.com/view/low-tier-god-awesome-mario-twerking-gif-23644561",
            "https://tenor.com/view/recep-ivedik-gif-17979851115064014078",
            "https://tenor.com/view/u%C4%9Fur-d%C3%BCndar-gif-21913397",
            "https://tenor.com/view/recep-ivedik-gif-20643754",
            "https://tenor.com/view/bruh-gif-23441586",
            "https://tenor.com/view/cute-anime-anime-girl-pink-hearts-gif-2859182496452245481",
            "https://tenor.com/view/funny-emo-wolf-werewolf-transform-gif-27196401",
            "https://tenor.com/view/%C3%A7okzorya-cokzorua-cokzorya-%C3%A7ok-zor-ya-%C3%A7ok-zor-ya-diyen-adam-gif-10957057876352588846",
            "https://tenor.com/view/fbi-kana-gif-7441334008951759059",
            "https://tenor.com/view/ali-ko%C3%A7-gif-18426190093325981609",
            "https://tenor.com/view/black-man-sitting-snazzy-gif-26181918",
            "https://tenor.com/view/shrek-smirk-gif-10170997843933469713",
            "https://tenor.com/view/discord-ban-appeal-gif-3829887507116417894",
            "https://tenor.com/view/homer-simpson-simpsons-kebab-gif-9043334",
            "https://tenor.com/view/khontkar-zenci-ensar-nas%C4%B1l-olunuyor-peki-rk-dance-gif-13595955285171961629",
            "https://media.discordapp.net/attachments/1107006693503684638/1202297577589194805/bruhgif.gif",
            "https://tenor.com/view/lowtiergod-ltg-excuse-me-what-huh-gif-16649578861553422481",
            "https://tenor.com/view/roblox-roblox-run-low-quality-gif-7119753476526813171",
            "https://tenor.com/view/rterahatsiz-gif-7057240225373514376",
            "https://tenor.com/view/monkey-shocked-monkey-disappointed-disappointed-monkey-gif-25631537",
            "https://tenor.com/view/transitions-kinemaster-black-guy-suit-tiktok-gif-25279479",
            "https://tenor.com/view/side-eye-dog-gif-22972113",
            "https://tenor.com/view/abdulhamit-abdul-kalam-abdulh-abdulham-abdulhami-gif-26119085",
            "https://tenor.com/view/pepe-the-frog-cave-get-inside-walk-in-gif-16937105",
            "https://tenor.com/view/bruh-bruh-triggered-bruh-bttv-meme-gif-16887494"
        ]

        chance = randrange(67)
        if chance in [3, 6, 11, 13, 16, 22, 23, 26, 36, 43, 46, 44, 53, 55, 56, 63, 66]: # don't even ask
            while True:
                gif = choice(gifs)
                if gif != self._last_hodja_gif:
                    self._last_hodja_gif = gif
                    break
            
            await ctx.send("<@201086628167417857>", delete_after=11)
            await ctx.send(gif, delete_after=11)
        elif chance == 33:
            await ctx.send("**SUPER RARE DOUBLE LAVASH KEBAP PULL!!!** <@201086628167417857>", delete_after=11)
            await ctx.send("https://tenor.com/view/ayran-gif-10772760", delete_after=11)
        else:
            while True:
                sentence, gif = choice(sentences)
                if (sentence, gif) != self._last_hodja_sentence:
                    self._last_hodja_sentence = (sentence, gif)
                    break

            await ctx.send(sentence, delete_after=11)
            if gif is not None:
                await ctx.send(gif, delete_after=11)
            
    @commands.command(aliases=["jelly", "jellyfish", "jellytimet", "jogurt", "doctor"])
    async def _jelly(self, ctx) -> None:
        """ A command for telling something about Jelly. """

        await ctx.message.delete()

        sentences = [
            "love you all from <@781007535267119138>",
            "<@781007535267119138> don't call me if you are sick, i'm busy jellying :p",
            "<@781007535267119138> I'm a doctor, not a magician",
            "be nice not mean, spread love not hate 💞",
            "<@781007535267119138> at your service, how may I help?",
            "An apple a day keeps a doctor away",
        ]

        await ctx.send(choice(sentences))


def setup(client) -> None:
    """ Cog's setup function. """

    client.add_cog(Prestige(client))
