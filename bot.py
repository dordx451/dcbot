import discord
from discord.ext import commands
import sqlite3
import random
import string

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize DB
conn = sqlite3.connect("keys.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS keys (
    key TEXT PRIMARY KEY,
    used INTEGER DEFAULT 0
)''')
conn.commit()

# Helper to generate random keys
def generate_key(length=24):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Admin-only decorator
def is_admin():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)

@bot.command()
@is_admin()
async def genkey(ctx, amount: int = 1):
    keys = []
    for _ in range(amount):
        key = generate_key()
        keys.append(key)
        c.execute("INSERT OR IGNORE INTO keys (key) VALUES (?)", (key,))
    conn.commit()
    await ctx.send("Generated keys:\n" + "\n".join(keys))

@bot.command()
async def redeem(ctx, key: str):
    c.execute("SELECT used FROM keys WHERE key = ?", (key,))
    row = c.fetchone()
    if not row:
        await ctx.send("❌ Invalid key.")
    elif row[0] == 1:
        await ctx.send("⚠️ Key already used.")
    else:
        c.execute("UPDATE keys SET used = 1 WHERE key = ?", (key,))
        conn.commit()
        await ctx.send("✅ Key redeemed. Welcome!")

@bot.command()
@is_admin()
async def revoke(ctx, key: str):
    c.execute("DELETE FROM keys WHERE key = ?", (key,))
    conn.commit()
    await ctx.send(f"❌ Key {key} revoked.")

bot.run("YOUR_BOT_TOKEN")
