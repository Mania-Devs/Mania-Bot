from nextcord.ext import commands
from replit import db
import nextcord, os, neversleep, time

neversleep.awake("https://Mania-Bot-v2.jmstng.repl.co")

TOKEN = os.environ['TOKEN']

intents = nextcord.Intents().all()

bot = commands.Bot(command_prefix="=", activity=nextcord.Game(name="=help"), intents=intents)

@bot.event
async def on_ready():
	print("Online!")

async def err(context, error):
	err = nextcord.Embed(title="Oops!", description=f"Something went wrong. If the issue persists, try contacting a member with <@&879827013370773576>.\n\n__Verbose Error__:\n{error}", color=0xFF0000)
	err.set_thumbnail(url="https://cdn.discordapp.com/attachments/806923554121580576/806986785825812/image0.gif")
	await context.send(embed=err)

class Verification(commands.Cog):
	@commands.has_permissions(administrator=True)
	@commands.command()
	async def setregister(self, ctx, channel=None):
		if channel == None:
			db["register"] = ctx.channel.id
			await ctx.send(embed=nextcord.Embed(title="Success!", description="This is the channel where people register themselves now.", color=0x00FF00))
		else:
			try:
				db["register"] = channel[2:-1]
				await ctx.send(embed=nextcord.Embed(title="Success!", description=f"{channel} is the channel where people register themselves now.", color=0x00FF00))
			except:
				await ctx.send("That's not a valid channel.")
				
	@setregister.error
	async def setregisterErr(self, ctx, e):
		if isinstance(e, commands.MissingPermissions):
			await ctx.send("You can't use that. You lack Administrator permissions.")
	
	@commands.command()
	async def register(self, ctx, *, name):
		if ctx.channel.id != db["register"]:
			await ctx.send(f"This isn't the place for that. Head over to <#{db['register']}> to register.")
		else:
			await ctx.author.edit(nick=name, roles=[ctx.message.guild.get_role(879825651106971718)])
			await ctx.send(embed=nextcord.Embed(title="Success!", description=f"Server Nickname successfully changed to `{name}`", color=0x00FF00))
			
	@commands.command(aliases=["rename"])
	async def reregister(self, ctx, *, name):
		await ctx.author.edit(nick=name)
		await ctx.send(embed=nextcord.Embed(title="Success!", description=f"Server Nickname successfully changed to `{name}`", color=0x00FF00))
	
	@register.error
	async def registerErr(self, ctx, e):
		if isinstance(e, commands.MissingRequiredArgument):
			await ctx.send("You forgot to write your name!")
		else:
			await err(ctx, e)
	
	@reregister.error
	async def reregisterErr(self, ctx, e):
		if isinstance(e, commands.MissingRequiredArgument):
			await ctx.send("You forgot to write your name!")
		else:
			await err(ctx, e)
			
class Tournament(commands.Cog):
	@commands.has_role("RM Staff")
	@commands.command()
	async def start(self, ctx, spots:int, force=None):
		if db["tourneyspots"] and not force:
			await ctx.send("Are you sure you want to start a new tournament?\nThe previous one hasn't filled up yet!\nCall `=start <spots> 1` to force a new tournament.")
		else:
			db["tourneyspots"] = spots
			db["tourneyplayers"] = []
			await ctx.send(embed=nextcord.Embed(title="Success!", description=f"A tournament was called with `{spots}` open seats.", color=0x00FF00))

	@start.error
	async def startErr(self, ctx, e):
		if isinstance(e, commands.errors.BadArgument):
			await ctx.send("That wasn't a number.")
		else:
			await err(ctx, e)
	
	@commands.has_role("RM Staff")
	@commands.command()
	async def end(self, ctx):
		lineup = ""
		for c, i in enumerate(db["tourneyplayers"]):
			lineup += f"{c+1}. <@{i}>\n"
		channel = bot.get_channel(886224983272075325)
		await channel.send("<@&879827013370773576>", embed=nextcord.Embed(title=f"Tournament Lineup ({len(db['tourneyplayers'])})", description=f"Here is the final lineup:\n{lineup}"))

	@commands.command()
	async def join(self, ctx):
		if ctx.channel.id == 886021349057900586:
			if db["tourneyspots"] > 0:
				if ctx.author.id not in db["tourneyplayers"]:
					db["tourneyspots"] -= 1
					db["tourneyplayers"].append(ctx.author.id)
					await ctx.send(embed=nextcord.Embed(title="Success!", description="You joined the tournament.", color=0x00FF00))
					if db["tourneyspots"] == 0:
						lineup = ""
						for c, i in enumerate(db["tourneyplayers"]):
							lineup += f"{c+1}. <@{i}>\n"
						channel = bot.get_channel(886224983272075325)
						await channel.send("<@&879827013370773576>", embed=nextcord.Embed(title=f"Tournament Lineup ({len(db['tourneyplayers'])})", description=f"Here is the final lineup:\n{lineup}"))
				else:
					await ctx.send("You've already joined this tournament.")
			else:
				await ctx.send("Sorry, there aren't any spots left.")
		else:
			await ctx.send("Join the tournament in <#886021349057900586>")

	@commands.has_role("RM Staff")
	@commands.command()
	async def remove(self, ctx, member):
		db["tourneyplayers"].remove(int(member[3:-1]))
		db["tourneyspots"] += 1
		await ctx.send(embed=nextcord.Embed(title="Success!", description=f"{member} was removed from the tournament list.", color=0x00FF00))

	@commands.command()
	async def leave(self, ctx):
		db["tourneyplayers"].remove(ctx.author.id)
		db["tourneyspots"] += 1
		await ctx.send(embed=nextcord.Embed(title="Success!", description="You have left the tournament.", color=0x00FF00))

class Utility(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		db["mutes"] = {}

	@commands.command()
	async def mute(self, ctx, member: commands.MemberConverter, length):
			db["mutes"][member.id] = [str(length), str(time.time()), list(member.roles)]
			await ctx.channel.send(embed=nextcord.Embed(title="Success!", description=f"{member.mention} was successfully muted for {length} seconds.", color=0x00FF00))
			while int(time.time()) - int(db["mutes"][member.id][1]) < int(db["mutes"][member.id][0]):
				member.edit(roles=[nextcord.utils.get(member.guild.roles, "Muted")])
			member.edit(roles=db["mutes"][member.id][2])
			await ctx.channel.send(embed=nextcord.Embed(title="Success!", description=f"{member.mention} was successfully unmuted after {length} seconds.", color=0x00FF00))
	
	@mute.error
	async def muteErr(self, ctx, e):
		if isinstance(e, [TypeError]):
			await ctx.send("Is that even a person?")
		else:
			await err(ctx, e)
		
bot.add_cog(Verification(bot))
bot.add_cog(Tournament(bot))
bot.add_cog(Utility(bot))

bot.run(TOKEN)