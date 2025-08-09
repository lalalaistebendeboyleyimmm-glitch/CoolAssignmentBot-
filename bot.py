import discord
from discord.ext import commands, tasks
from discord.utils import get
import aiohttp
import random
import datetime
import requests
import asyncio

# ----------- Ayarlar -------------

BOT_PREFIX = "!"
HF_API_TOKEN = "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"  # Hugging Face API Token (açık olarak)
HF_MODEL = "moonshotai/Kimi-K2-Instruct:featherless-ai"  # Yeni model

GIPHY_API_KEY = "MDOJrTXyYtlmckUaQKWLXLTHKZr8USNy"  # Giphy API key

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

warns = {}
start_time = datetime.datetime.now(datetime.timezone.utc)

# ----------- Yardımcı Fonksiyonlar -------------

async def fetch_gif_url(keyword):
    url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q={keyword}&limit=10&rating=pg-13"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data["data"]:
                    gif = random.choice(data["data"])
                    return gif["images"]["original"]["url"]
    return None

def query_hf_chat(messages):
    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {
        "model": HF_MODEL,
        "messages": messages
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"HuggingFace API Error {response.status_code}: {response.text}")
        return None

# ----------- Event & Komutlar -------------

@bot.event
async def on_ready():
    print(f"{bot.user} is ready to serve you, senpai~ 💕")
    uptime_task.start()

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    await ctx.send(f"Hai~ {ctx.author.mention} senpai~ I kicked {member.mention} just for you 💖 Reason: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    await ctx.send(f"Yes, {ctx.author.mention} senpai~ I banned {member.mention} as you wished~ 💕 Reason: {reason}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"Done, senpai~ I cleaned {amount} messages for you~ ✨ Arigatou for letting me help~")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member):
    role = get(ctx.guild.roles, name="Muted")
    if not role:
        await ctx.send("Senpai~ I couldn't find a role called 'Muted' 😢 Please create it first~")
        return
    await member.add_roles(role)
    await ctx.send(f"Hai~ {ctx.author.mention} senpai~ I muted {member.mention} so they stay quiet for you 💞")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    role = get(ctx.guild.roles, name="Muted")
    if role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f"Yatta~! {ctx.author.mention} senpai~ {member.mention} can speak again now 💖")
    else:
        await ctx.send(f"Uhm~ {member.mention} wasn't muted, senpai~ 😳")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"Slowmode set to {seconds} seconds, senpai~ I'll keep things calm~ 💤")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("Yes, senpai~ The channel is now locked~ No one can disturb you~ (≧◡≦)")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("Yatta~ Channel unlocked, senpai~ You can chat freely again~ 💕")

@bot.command()
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, member: discord.Member, *, new_nick):
    await member.edit(nick=new_nick)
    await ctx.send(f"Hai~ {member.mention} now has a new nickname, senpai~ So cute~ 💖")

@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    user_id = member.id
    warns[user_id] = warns.get(user_id, 0) + 1
    await ctx.send(f"{member.mention} has been warned, senpai~ Please behave~ ({warns[user_id]} warnings) ❤️ Reason: {reason}")

@bot.command()
async def warnings(ctx, member: discord.Member):
    user_id = member.id
    count = warns.get(user_id, 0)
    await ctx.send(f"{member.mention} has {count} warning(s), senpai~ Be careful~ (｡•́︿•̀｡)")

@bot.command()
async def hug(ctx, member: discord.Member):
    url = await fetch_gif_url("anime hug")
    if url:
        await ctx.send(f"*Hugs {member.mention} tightly, senpai~* 💖 You’re so special~ (≧◡≦)\n{url}")
    else:
        await ctx.send(f"*Hugs {member.mention} tightly, senpai~* 💖 You’re so special~ (≧◡≦)")

@bot.command()
async def pat(ctx, member: discord.Member):
    url = await fetch_gif_url("anime pat")
    if url:
        await ctx.send(f"*Pat pat~ {member.mention}, senpai!* 💕\n{url}")
    else:
        await ctx.send(f"*Pat pat~ {member.mention}, senpai!* 💕")

@bot.command()
async def blush(ctx):
    await ctx.send("U-uhm~ I-I'm blushing, senpai~ 😳")

@bot.command()
async def say(ctx, *, message):
    await ctx.send(f"Senpai told me to say: {message}~ Hai~ (◕‿◕)")

@bot.command()
async def gif(ctx, *, keyword):
    url = await fetch_gif_url(keyword)
    if url:
        await ctx.send(f"Here you go, senpai~ (≧◡≦) {url}")
    else:
        await ctx.send(f"Sorry, senpai~ I couldn't find any gifs for '{keyword}' 😢")

@bot.command()
async def userinfo(ctx, member: discord.Member):
    embed = discord.Embed(title=f"{member}", color=discord.Color.purple())
    try:
        embed.set_thumbnail(url=member.avatar.url)
    except:
        pass
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d"))
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d"))
    embed.set_footer(text="Senpai~ Here's your info~ 💖")
    await ctx.send(embed=embed)

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"{guild.name} Server Info", color=discord.Color.blue())
    try:
        embed.set_thumbnail(url=guild.icon.url)
    except:
        pass
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Owner", value=str(guild.owner))
    region = getattr(guild, "region", None)
    embed.add_field(name="Region", value=str(region) if region else "Unknown")
    embed.add_field(name="Created At", value=guild.created_at.strftime("%Y-%m-%d"))
    embed.set_footer(text="Senpai~ Hope you like it~ (≧◡≦)")
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong~ {latency}ms, senpai~ I’m so fast! 💨")

@tasks.loop(seconds=60)
async def uptime_task():
    pass

@bot.command()
async def uptime(ctx):
    delta = datetime.datetime.now(datetime.timezone.utc) - start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    await ctx.send(f"Senpai~ I've been awake for {hours}h {minutes}m {seconds}s~ (◕‿◕)")

@bot.command()
async def senpaihelp(ctx):
    help_text = """
**Senpai Help Menu~ 💕**

**Admin Commands:**
- `!kick @member [reason]` - Kick a member
- `!ban @member [reason]` - Ban a member
- `!clear <amount>` - Delete messages
- `!mute @member` - Mute a member
- `!unmute @member` - Unmute a member
- `!slowmode <seconds>` - Set slowmode
- `!lock` - Lock channel
- `!unlock` - Unlock channel
- `!nick @member <new_nick>` - Change nickname
- `!warn @member [reason]` - Warn a member
- `!warnings @member` - Show warnings count

**Fun & Roleplay:**
- `!hug @member` - Hug someone~ 💖
- `!pat @member` - Pat someone~ 💕
- `!blush` - Make me blush~ 😳
- `!say <message>` - Make me say something
- `!gif <keyword>` - Find a gif

**Info Commands:**
- `!userinfo @member` - Get user info
- `!serverinfo` - Get server info
- `!ping` - Pong! Check latency
- `!uptime` - How long I've been awake

**Chat with me by mentioning or saying 'senpai' in your message!**

"""
    await ctx.send(help_text)

# ----------- Hata Yönetimi -------------

@kick.error
@ban.error
@clear.error
@mute.error
@unmute.error
@warn.error
@slowmode.error
@lock.error
@unlock.error
@nick.error
async def perms_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"Senpai~ You don't have permission to do that! 😣")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"Uhm~ I think you gave me wrong arguments, senpai~ 😳")
    else:
        await ctx.send(f"Something went wrong, senpai~ Please try again later~")

# ----------- Chatbot entegrasyonu -------------

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    if bot.user in message.mentions or "senpai" in message.content.lower():
        chat_history = [
            {"role": "system", "content": (
                "You are a cute, obedient anime girl assistant named SenpaiBot. "
                "You speak politely and affectionately, using some Japanese honorifics but not excessively. "
                "Always keep a gentle and submissive tone."
            )}
        ]
        chat_history.append({"role": "user", "content": message.content})

        def hf_call():
            response = query_hf_chat(chat_history)
            if response and "choices" in response and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"]
            else:
                return "Sorry, senpai~ something went wrong... (｡•́︿•̀｡)"

        reply = await asyncio.to_thread(hf_call)
        await message.channel.send(reply)

bot.run("MTQwMzQ3OTMzODQ0NzQwOTMxNQ.GlLftQ.Dl-RsN8uqSYgYu5Q2_r6kBNG2XjLElc1YufCK8")