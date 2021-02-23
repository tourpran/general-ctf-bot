import datetime
import re
import discord
from discord.ext import tasks, commands
# from datetime import *
import dateparser # pip install dateparser
import requests
from colorama import Fore, Style
import sys
import asyncio

sys.path.append("..")

CURRENT_CTFS = []	# list of objects of class CTF
SHARED_LOCK = None	# mutex
IST = datetime.timedelta(hours=5, minutes=30)

class Challenge:
	def __init__(self, channel, is_solvable):
		self._is_solved = False
		self.time_taken = -1
		self._solved_by = ''
		self._is_solvable = is_solvable
		self._channel = channel

	def get_channel(self):
		return self._channel

	def get_chall_name(self):
		return self._channel.name
	
	def is_solved(self):
		return self._is_solved and self._is_solvable
	
	def get_solved_by(self):
		return self._solved_by
	
	def mark_solved(self, solver_name):
		if self._is_solvable and (not self._is_solved):
			self._is_solved = True
			self._solved_by = solver_name
			return True
		return False

	def __str__(self):
		msg = f"{self.get_chall_name()}"
		if not self._is_solvable:
			return ''
		else:
			if self._is_solved:
				msg = f"{msg} solved by {self._solved_by}"
			else:
				msg = f"{msg} **NOT SOLVED** yet!"
		return f'```{msg}```'

class CTF:
	def __init__(self, cat_ob, ctf_start=None, ctf_end=None):
		self._ctf_start = ctf_start
		self._ctf_end = ctf_start
		self._is_live = True
		self._challenges = []
		self._category = cat_ob
	
	def get_category(self):
		return self._category
	
	def __str__(self):
		return f"{self._category.name} : {', '.join(i.get_chall_name() for i in self._challenges)}"
	
	def get_ctf_name(self):
		return self._category.name
	
	def get_ctf_start(self):
		return self._ctf_start
	
	def get_ctf_end(self):
		return self._ctf_end
	
	def solve_challenge(self, channel_ob, solver_name):
		chall_ob = self.get_challenge(channel_ob)
		if not chall_ob:
			return False
		return chall_ob.mark_solved(solver_name)
	
	def has_challenge(self, channel):
		for i in self._challenges:
			if i.get_channel() == channel:
				return True
		return False
	
	def has_challenge_by_name(self, name):
		for i in self._challenges:
			if i.get_chall_name() == name:
				return True
		return False

	def get_challenge(self, channel) -> Challenge:
		for i in self._challenges:
			if i.get_channel() == channel:
				return i
		return None
	
	def get_all_challenges(self):
		return self._challenges

	def get_solved_challenges(self):
		return list(filter(lambda i: i.is_solved(), self._challenges))
	
	def get_unsolved_challenges(self):
		return list(filter(lambda i: not i.is_solved(), self._challenges))

	def add_challenge(self, channel, is_solvable) -> bool:
		# check chall if already added
		if self.has_challenge(channel):
			return False
		
		new_chall = Challenge(channel, is_solvable)
		self._challenges.append(new_chall)
		return True
	
	def is_live(self):
		return self._is_live

	def end_ctf(self):
		self._is_live = False


headers = {
	'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0',
}

client = commands.Bot(command_prefix='-')

client.remove_command('help')

challenges_solved = ":triangular_flag_on_post:**SOLVED CHALLENGES**"
category_info = ""

def read_token():
    with open("token.txt","r") as f:
        lines = f.readlines()
        return lines[0].strip()

token = read_token()
@client.event
async def on_ready():
	await client.change_presence(status=discord.Status.idle, activity=discord.Game('Listening to -'))
	print("Ready")

@client.command()
async def topteams(ctx):
	leaderboards = ""
	year = str(datetime.datetime.today().year)
	top = f"https://ctftime.org/api/v1/top/"
	r = requests.get(top, headers=headers)
	top_data = (r.json())[year]
	for team in range(10):
		rank = team + 1
		teamname = top_data[team]['team_name']
		score = str(round(top_data[team]['points'], 4))
		if team != 9:
			leaderboards += f"{rank} -> {teamname}: {score}\n"
		else:
			leaderboards += f"{rank} -> {teamname}: {score}\n"
	await ctx.send(f":triangular_flag_on_post:  __**{year} CTFtime Leaderboards**__```ini\n{leaderboards}```")

@client.command()
async def over(ctx):
	global category_info
	if str(ctx.channel) == "main":
		# global challenges_solved
		challenges_solved = []
		ctf_ob = get_ctf_from_context(ctx)
		if not ctf_ob:
			await ctx.send("Can't call over from a non-ctf channel!")
			return
		# async with SHARED_LOCK:
		challenges_solved = list(map(str, ctf_ob.get_solved_challenges()))
		CURRENT_CTFS.remove(ctf_ob)
		await ctx.send(''.join(challenges_solved))
		await ctx.send(f"Hope you won the ctf. \n**CTF OVER - {ctf_ob.get_ctf_name()}**")
		challenges_solved = ":triangular_flag_on_post:**SOLVED CHALLENGES**"
	else:
		await ctx.send("Cant do it 404 !!")

@client.command()
async def help(ctx):
	msg = '''**COMMANDS:**```
addchall - adds the challenge you name [-addchall challname]
all      - shows all the solved challenges [-all]
clean    - obviously cleans the messages [-clean amount]
create   - create a new CTF to win [-create ctfname]
help     - Shows this message [-help]
over     - mark the ctf over once the ctf is over [-over]
solved   - mark the challenge solved in the respective channel only [-solved]
stop     - dont bother with this [...]
topteams - top teams of the world [-topteams]
setcreds - set creds [-setcreds url login password]
upcoming - upcoming N ctfs [-upcoming N=3]```'''
	await ctx.send(msg)

@client.command(usage='Need ctf name. Type `-help` to see usage', aliases=["newctf"])
async def create(ctx, *args):
	if (not args) or (not args[0]):
		await ctx.send("Need ctf name. Type `-help` to see usage")
		return
	arg2 = args[0]
	if str(ctx.channel) == "_bot_query":
		global category_info
		name = arg2
		for i in CURRENT_CTFS:
			if i.get_ctf_name().lower() == name:
				# todo : send a failure message : "CTF already exists!"
				await ctx.send("CTF already exists!")
				return
		category_obj = await ctx.guild.create_category(arg2)
		ctf_ob = CTF(category_obj)
		CURRENT_CTFS.append(ctf_ob)
		# category = discord.utils.get(ctx.guild.categories, name=name)
		chan_ob = await ctx.guild.create_text_channel("main", category=category_obj)  
		ctf_ob.add_challenge(chan_ob, False)
		title, start, end = get_ctf_info(arg2)
		if title:
			embedVar = discord.Embed(title=title, description=f"Starts: {start}, Ends: {end}", color=0x00ff00)
			msg = await ctx.send(embed=embed)
			msg.pin()
		category_info = arg2
		embedVar = discord.Embed(title="", description=f"Kill the CTF. Channel created {category_info}", color=0x00ff00)
		await ctx.send(embed=embedVar) 
	else:
		await ctx.send("Go to bot query !!")

@client.command(aliases=["add"])
async def addchall(ctx, *args):
	if (not args) or (not args[0]):
		await ctx.send("Need challenge name. Type `-help` to see usage")
	challname = args[0]
	if str(ctx.channel) == "main":
		global category_info 
		name = challname
		ctf_ob = get_ctf_from_context(ctx)
		if not ctf_ob:
			# should never happen
			await ctx.send("Can't add challenge from a non-ctf context!")
			return
		if ctf_ob.has_challenge_by_name(challname):
			await ctx.send("Sorry! Challenge Exists.")
			return
		category = ctf_ob.get_category()
		channel_ob = await ctx.guild.create_text_channel(name , category=category)
		ctf_ob.add_challenge(channel_ob, True)
		embedVar = discord.Embed(title="", description=f"challenge created {name}", color=0x00ff00)
		await ctx.send(embed=embedVar)
	else:
		await ctx.send("Go to main !!")

def get_ctf_info(ctf_name):
	r = requests.get("https://ctftime.org/api/v1/events/", headers=headers, params=str(1337))
	upcoming_data = r.json()
	for ctf in range(len(upcoming_data)):
		ctf_title = upcoming_data[ctf]["title"]
		ctf_start = dateparser.parse(upcoming_data[ctf]["start"])
		ctf_end = dateparser.parse(upcoming_data[ctf]["finish"])
		ctf_start = ctf_start + IST
		ctf_end = ctf_end + IST
		ctf_start = ctf_start.strftime('%a %b %d, %Y %I:%M:%S %p')
		ctf_end = ctf_end.strftime('%a %b %d, %Y %I:%M:%S %p')
		if ctf_name in ctf_title:
			return ctf_title, ctf_start, ctf_end
	return None, None, None

@client.command()
async def upcoming(ctx, *args):
	linkupcoming = "https://ctftime.org/api/v1/events/"
	N = 3
	if args and args[0].isdigit():
		N = int(args[0])
	r = requests.get(linkupcoming, headers=headers, params=str(N))
	upcoming_data = r.json()
	data = []
	for ctf in range(len(upcoming_data)):
		ctf_title = upcoming_data[ctf]["title"]
		ctf_start = dateparser.parse(upcoming_data[ctf]["start"])
		ctf_end = dateparser.parse(upcoming_data[ctf]["finish"])
		ctf_start = ctf_start + IST
		ctf_end = ctf_end + IST
		ctf_start = ctf_start.strftime('%a %b %d, %Y %I:%M:%S %p')
		ctf_end = ctf_end.strftime('%a %b %d, %Y %I:%M:%S %p')
		# (ctf_start, ctf_end) = (upcoming_data[ctf]["start"].replace("T", " ").split("+", 1)[0] + " UTC", upcoming_data[ctf]["finish"].replace("T", " ").split("+", 1)[0] + " UTC")
		# (ctf_start, ctf_end) = (re.sub(":00 ", " ", ctf_start), re.sub(":00 ", " ", ctf_end))
		dur_dict = upcoming_data[ctf]["duration"]
		ctf_weight = float(upcoming_data[ctf]['weight'])
		(ctf_hours, ctf_days) = (str(dur_dict["hours"]), str(dur_dict["days"]))
		ctf_link = upcoming_data[ctf]["url"]
		ctf_image = upcoming_data[ctf]["logo"]
		ctf_format = upcoming_data[ctf]["format"]
		ctf_place = ["Online", "Onsite"][int(upcoming_data[ctf]["onsite"])]
		# if ctf_place == False:
		#     ctf_place = "Online"
		# else:
		#     ctf_place = "Onsite"

		embed = discord.Embed(title=ctf_title, description=ctf_link, color=int("ffffff", 16))
		if ctf_image != '':
		    embed.set_thumbnail(url=ctf_image)
		else:
		    embed.set_thumbnail(url='https://ctftime.org/static/images/ct/logo.svg')

		embed.add_field(name='Weight', value=str(ctf_weight), inline=True)
		embed.add_field(name="Duration", value=((ctf_days + " days, ") + ctf_hours) + " hours", inline=True)
		embed.add_field(name="Format", value=(ctf_place + " ") + ctf_format, inline=True)
		embed.add_field(name="Timeframe", value=(ctf_start + " -> ") + ctf_end, inline=True)
		# await ctx.channel.send(embed=embed)
		data.append([ctf_weight, embed])
	
	data.sort(key=lambda i: i[0], reverse=True)
	for i in data[:N]:
		await ctx.channel.send(embed=i[1])
		
@client.command()
async def all(ctx):
	# list of all solved challenges
	if str(ctx.channel) == "main":
		# global challenges_solved
		ctf_ob = get_ctf_from_context(ctx)
		if not ctf_ob:
			await ctx.send("Can't execute `all` from a non-ctf channel!")
			return
		challenges_solved = []
		for i in ctf_ob.get_all_challenges():
			m = str(i)
			if i.is_solved():
				m = m.replace(ctf_ob.get_ctf_name()+'-', '')
			challenges_solved.append(m)
		# challenges_solved = list(filter(lambda i: i, map(str, ctf_ob.get_all_challenges())))
		if not challenges_solved:
			challenges_solved = ['** No Challenges Added **']
		await ctx.send(''.join(challenges_solved))
	else:
		await ctx.send("Hmm... Go to main !!")

@client.command()
async def solved(ctx):
	# if str(ctx.channel) == "main":
	# 	await ctx.send("Cant solve main dude !!")
	# 	return
	ctf_ob = get_ctf_from_context(ctx)
	if not ctf_ob:
		await ctx.send("Tried to call `solved` on a non-ctf channel")
		return
	channel = ctx.channel
	# author = str(ctx.author)[:-5]
	author = ctx.author.name
	# async with SHARED_LOCK:
	if not ctf_ob.solve_challenge(channel, author):
		await ctx.send("Tried to call `solved` on a non-solvable channel")
		return
	# notify all channels
	cached_mention = channel.mention
	for i in ctf_ob.get_all_challenges():
		if i.get_channel().name != "main":
			continue
		# await ctx.send(f"@{author} solved `{i.get_chall_name()}` :tada: :tada:")
		await i.get_channel().send(f"{author} solved {cached_mention} :tada: :tada:")
	# global challenges_solved
	# challenges_solved += f"```{channel} solved by {author}```"
	# post a message to "main" channel that X is solved by Y
	await ctx.send("Good Job !!")
	category = discord.utils.get(ctx.guild.categories, name="solved-challenges")
	if not category:
		category = await ctx.guild.create_category('solved-challenges')
	await ctx.channel.edit(syncpermissoins=True, category=category, name=f"{ctf_ob.get_ctf_name()}-{channel.name}")

@client.command()
async def clean(ctx, amount=5):
	await ctx.channel.purge(limit=amount)

@client.command()
async def setcreds(ctx, *args):
	if (not args) or len(args) != 3 or not (args[0] and args[1] and args[2]):
		await ctx.send("Need ctf url, login and password. See `-help`")
		return
	ctf_ob = get_ctf_from_context(ctx)
	if not ctf_ob:
		# should never happen
		await ctx.send("Can't add challenge from a non-ctf context!")
		return
	url, login, password = args
	pinned = await ctx.message.channel.pins()
	for pin in pinned:
		if "CTF credentials set." in pin.content:
			# Look for previously pinned credntials, and remove them if they exist.
			await pin.unpin()
	msg = await ctx.send(f"{url}\n```Login: {login}\nPassword: {password}```")
	await msg.pin()

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid command. See `-help`")

@client.command()
async def stop(ctx):
	if str(ctx.author) in ['tourpran#2362', 'x0r19x91#0705']:
		await ctx.send("Bye i am going to sleep now !!")
		await ctx.bot.logout()
	else:
		await ctx.send("Sorry dude! I listen to tourpran and x0r19x91 only.")

def get_current_category(ctx):
	return ctx.channel.category

# helper routine
def get_ctf_from_context(ctx):
	channel_name = ctx.channel
	# category = discord.utils.get(ctx.guild.categories, name=channel_name)
	cat = get_current_category(ctx)
	if not cat:
		return None
	category = cat.name
	ob = None
	for i in CURRENT_CTFS:
		if ctx.channel in [j.get_channel() for j in i.get_all_challenges()]:
			ob = i
			break
	if ob:
		return ob

client.run(token)
# SHARED_LOCK = asyncio.Lock()