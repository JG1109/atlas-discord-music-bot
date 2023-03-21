from discord.ext import commands
import discord
# from discord.utils import find
# from discord import Interaction
from wavelink.ext import spotify
import wavelink
from config import TOKEN, CLIENT_ID, CLIENT_SECRET
# import datetime
# import asyncio
import random

# set up bot client
# intents and command prefix
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents, case_insensitive=True)
file = discord.File('./resrcs/help_thumbnail-1.png',
                    filename='help_thumbnail-1.png')
# spotifyLogo = "./resrcs/help_thumbnail-1.png"
# global vars
last = 0
context = None


# start the bot and connect the node
@bot.event
async def on_ready():
  await bot.change_presence(activity=discord.Activity(
    type=discord.ActivityType.listening, name="Ricky's Whisper"))
  print("Bot client is ready")
  bot.loop.create_task(node_connect())


# check if ready
@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
  print(f"Node {node.identifier} is ready")


# node connection
async def node_connect():
  await bot.wait_until_ready()
  await wavelink.NodePool.create_node(bot=bot,
                                      host='lavalink.devamop.in',
                                      port=443,
                                      password='DevamOP',
                                      https=True,
                                      spotify_client=spotify.SpotifyClient(
                                        client_id=CLIENT_ID,
                                        client_secret=CLIENT_SECRET))


# greeting message when invited
@bot.event
async def on_guild_join(guild):
  for channel in guild.text_channels:
    if channel.permissions_for(guild.me).send_messages:
      # send an joining embed
      embed = discord.Embed(title="Atlas is here", color=0x3E54AC)
      # embed.set_thumbnail(url=spotifyLogo)
      embed.set_thumbnail(url='attachment://help_thumbnail-1.png')
      embed.add_field(name="",
                      value="Please use `.cmds` to see all commands",
                      inline=False)
      await channel.send(embed=embed)


# buttons
class List_Panel(discord.ui.View):

  def __init__(self, vc, ctx, last):
    super().__init__()
    self.vc = vc
    self.ctx = ctx
    self.last = last

  @discord.ui.button(label="<<", style=discord.ButtonStyle.blurple)
  async def head_page(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
    queue = self.vc.queue.copy()
    if len(queue) > 10:
      self.last = 10
    else:
      self.last = len(queue)
    em = discord.Embed(title="Playlist", color=0xBFACE2)
    for i in range(self.last):
      em.add_field(name="",
                   value=str(i + 1) + ". " + queue[i].title,
                   inline=False)
    self.last -= 1
    await interaction.message.edit(embed=em, view=self)
    # no response to the above interaction
    await interaction.response.defer()

  @discord.ui.button(label="<", style=discord.ButtonStyle.blurple)
  async def prev_page(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
    queue = self.vc.queue.copy()
    if self.last - 9 > 0:
      em = discord.Embed(title="Playlist", color=0xBFACE2)
      for i in range(self.last - 19, self.last - 9):
        em.add_field(name="",
                     value=str(i + 1) + ". " + queue[i].title,
                     inline=False)
        if self.last - i == 10:
          self.last = i
          break
      await interaction.message.edit(embed=em, view=self)
    # no response to the above interaction
    await interaction.response.defer()

  @discord.ui.button(label=">", style=discord.ButtonStyle.blurple)
  async def next_page(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
    queue = self.vc.queue.copy()
    if self.last + 1 < len(queue):
      em = discord.Embed(title="Playlist", color=0xBFACE2)
      for i in range(self.last + 1, len(queue)):
        em.add_field(name="",
                     value=str(i + 1) + ". " + queue[i].title,
                     inline=False)
        if i - self.last == 10:
          self.last = i
          break
      await interaction.message.edit(embed=em, view=self)
    # no response to the above interaction
    await interaction.response.defer()

  @discord.ui.button(label=">>", style=discord.ButtonStyle.blurple)
  async def tail_page(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
    queue = self.vc.queue.copy()
    self.last = len(queue) - 1
    for i in range(self.last, 0, -1):
      if i % 10 == 0:
        start = i
        self.last = start + 9
        break
    em = discord.Embed(title="Playlist", color=0xBFACE2)
    for i in range(start, len(queue)):
      em.add_field(name="",
                   value=str(i + 1) + ". " + queue[i].title,
                   inline=False)
    await interaction.message.edit(embed=em, view=self)
    # no response to the above interaction
    await interaction.response.defer()


# embed setting
def embed(vc):
  em = discord.Embed(title="Now playing",
                     description=vc.track.title,
                     color=0x655DBB)
  # em.add_field(name="Duration", value=f"`{str(datetime.timedelta(seconds=vc.track.length))}`")
  # em.add_field(name="Video", value=f"[Click Me]({str(vc.track.uri)})")
  return em


# play queued audios
@bot.event
async def on_wavelink_track_end(player: wavelink.Player, track: wavelink.Track,
                                reason):
  # channel = player.channel
  guild = player.guild
  vc: player = guild.voice_client
  # init loop, if loop enabled
  # play the same track again
  try:
    vc.loop ^= True
  except Exception:
    setattr(vc, "loop", False)
  if vc.loop:
    return await vc.play(track)
  # play next audio in queue
  next_audio = player.queue.get()
  await player.play(next_audio)
  await context.send(embed=embed(vc))


# helping method: list all commands
@bot.command()
async def cmds(ctx):
  embed = discord.Embed(title="Helping Desk", color=0x3E54AC)
  # embed.set_thumbnail(url=spotifyLogo)
  embed.set_thumbnail(url='attachment://help_thumbnail-1.png')
  embed.add_field(name="Play song or playlist",
                  value=".play [song name / Spotify URL]",
                  inline=False)
  embed.add_field(name="Skip current song",
                  value=".skip [multiple skips coming soon]",
                  inline=False)
  embed.add_field(name="Display current playlist", value=".list", inline=False)
  embed.add_field(name="Shuffle playlist", value=".shuffle", inline=False)
  embed.add_field(name="Stop playing (will unlist all songs)",
                  value=".stop",
                  inline=False)
  embed.add_field(name="Loop a song", value=".loop", inline=False)
  embed.add_field(name="Clear messages",
                  value=".clear [amount (default is 5)]",
                  inline=False)
  embed.add_field(name="Leave the channel", value=".leave", inline=False)
  await ctx.send(file=file, embed=embed)


# search and play audio
@bot.command()
async def play(ctx: commands.Context, *, search: str):
  global context
  context = ctx
  # if user is not in a channel
  if not getattr(ctx.author.voice, "channel", None):
    em = discord.Embed(color=0x3E54AC)
    em.add_field(name="", value="Please be in a channel first")
    return await ctx.send(embed=em)
  # join if not inside a vc (voice channel)
  if not ctx.voice_client:
    vc: wavelink.Player = await ctx.author.voice.channel.connect(
      cls=wavelink.Player)
    # intro = await wavelink.YouTubeTrack.search(query="D4C | JoJo 3D Animation「ジョジョの奇妙な冒険」", return_first=True)
    # await vc.play(intro)
    # deafen the bot when joining a channel
    await ctx.guild.change_voice_state(channel=ctx.author.voice.channel,
                                       self_mute=False,
                                       self_deaf=True)
  else:
    vc: wavelink.Player = ctx.voice_client
  # play
  if vc.queue.is_empty and not vc.is_playing():
    try:
      # YouTube tracks
      if search[0:25] != "https://open.spotify.com/":
        track = await wavelink.YouTubeTrack.search(query=search,
                                                   return_first=True)
        await vc.play(track)
        await ctx.send(embed=embed(vc))
      # Spotify tracks or playlists
      else:
        decoded = spotify.decode_url(search)
        if decoded:
          # single track
          if decoded['type'] is spotify.SpotifySearchType.track:
            track = await spotify.SpotifyTrack.search(query=search,
                                                      return_first=True)
            await vc.play(track)
            await ctx.send(embed=embed(vc))
          # playlist
          if decoded['type'] is spotify.SpotifySearchType.playlist:
            iffirst = True
            first_track = None
            added = 0
            async for track in spotify.SpotifyTrack.iterator(
                query=search, partial_tracks=True):
              if iffirst:
                first_track = track
                iffirst = False
              else:
                vc.queue.put(track)
                added += 1
                # print(f"Track {added} added")
            em = discord.Embed(color=0xBFACE2)
            em.add_field(name="", value=f"{added} songs added to playlist")
            await ctx.send(embed=em)
            await vc.play(first_track)
            await ctx.send(embed=embed(vc))
        else:
          em = discord.Embed(color=0xDF2E38)
          em.add_field(name="", value="Invalid URL")
          await ctx.send(embed=em)
    except Exception as e:
      em = discord.Embed(color=0xDF2E38)
      em.add_field(name="", value="Bad Request (Invalid URL or name)")
      await ctx.send(embed=em)
      return print(e)
  else:
    try:
      # YouTube tracks
      if search[0:25] != "https://open.spotify.com/":
        track = await wavelink.YouTubeTrack.search(query=search,
                                                   return_first=True)
        vc.queue.put(track)
        em = discord.Embed(color=0xBFACE2)
        em.add_field(name="", value=f"Added {track.title} to queue")
        await ctx.send(embed=em)
      # Spotify tracks or playlists
      else:
        decoded = spotify.decode_url(search)
        if decoded:
          # single track
          if decoded['type'] is spotify.SpotifySearchType.track:
            track = await spotify.SpotifyTrack.search(query=search,
                                                      return_first=True)
            vc.queue.put(track)
            em = discord.Embed(color=0xBFACE2)
            em.add_field(name="", value=f"Added {track.title} to queue")
            await ctx.send(embed=em)
          # playlist
          if decoded['type'] is spotify.SpotifySearchType.playlist:
            added = 0
            async for track in spotify.SpotifyTrack.iterator(
                query=search, partial_tracks=True):
              vc.queue.put(track)
              added += 1
              # print(f"Track {added} added")
            em = discord.Embed(color=0xBFACE2)
            em.add_field(name="", value=f"{added} songs added to playlist")
            await ctx.send(embed=em)
        else:
          em = discord.Embed(color=0xDF2E38)
          em.add_field(name="", value="Invalid URL")
          await ctx.send(embed=em)
    except Exception as e:
      em = discord.Embed(color=0xDF2E38)
      em.add_field(name="",
                   value="Bad Request (Invalid input or Internal error)")
      await ctx.send(embed=em)
      return print(e)
  # break the loop to play the audio added
  # vc.ctx = ctx
  # setattr(vc, "loop", False)


# skip current audio
@bot.command()
async def skip(ctx: commands.Context, amount=1):
  # if user is not in a channel
  if not getattr(ctx.author.voice, "channel", None):
    em = discord.Embed(color=0x3E54AC)
    em.add_field(name="", value="Please be in a channel first")
    return await ctx.send(embed=em)
  # join if not inside a vc (voice channel)
  if not ctx.voice_client:
    vc: wavelink.Player = await ctx.author.voice.channel.connect(
      cls=wavelink.Player)
  else:
    vc: wavelink.Player = ctx.voice_client
  # stop and play next
  if vc.queue.is_empty:
    em = discord.Embed(color=0x3E54AC)
    em.add_field(name="", value="No music in queue...")
    return await ctx.send(embed=em)
  if vc.is_playing():
    # skip number of songs
    # stop to reach the end of current track
    await vc.stop()
    # play next audio in queue
    # next_audio = vc.queue.get()
    # await vc.play(next_audio)
    # await ctx.send(embed=embed(vc))


# shuffle playlist
@bot.command()
async def shuffle(ctx: commands.Context):
  if not getattr(ctx.author.voice, "channel", None):
    em = discord.Embed(color=0x3E54AC)
    em.add_field(name="", value="Please be in a channel first")
    return await ctx.send(embed=em)
  if not ctx.voice_client:
    em = discord.Embed(color=0xBFACE2)
    em.add_field(name="", value="Music is not playing...")
    await ctx.send(embed=em)
  else:
    vc: wavelink.Player = ctx.voice_client
  # shuffle
  queue = []
  # clear the current queue
  pos = set()
  for _ in range(vc.queue.count):
    queue.append(vc.queue.pop())
  # randomly re-add
  for q in queue:
    while True:
      add_pos = random.randint(0, len(queue))
      if add_pos not in pos:
        vc.queue.put_at_index(add_pos, q)
        pos.add(add_pos)
        break
  # add reaction
  await ctx.message.add_reaction('👌')


# pause the audio
@bot.command()
async def pause(ctx: commands.Context):
  if not getattr(ctx.author.voice, "channel", None):
    em = discord.Embed(color=0x3E54AC)
    em.add_field(name="", value="Please be in a channel first")
    return await ctx.send(embed=em)
  if not ctx.voice_client:
    em = discord.Embed(color=0xBFACE2)
    em.add_field(name="", value="Music is not playing...")
    await ctx.send(embed=em)
  else:
    vc: wavelink.Player = ctx.voice_client
  # pause
  await vc.pause()
  await ctx.send("Music paused")


# resume the audio
@bot.command()
async def resume(ctx: commands.Context):
  if not getattr(ctx.author.voice, "channel", None):
    em = discord.Embed(color=0x3E54AC)
    em.add_field(name="", value="Please be in a channel first")
    return await ctx.send(embed=em)
  if not ctx.voice_client:
    em = discord.Embed(color=0xBFACE2)
    em.add_field(name="", value="Music is not playing...")
    await ctx.send(embed=em)
  else:
    vc: wavelink.Player = ctx.voice_client
  # pause
  await vc.resume()


# stop the audio
@bot.command()
async def stop(ctx: commands.Context):
  if not getattr(ctx.author.voice, "channel", None):
    em = discord.Embed(color=0x3E54AC)
    em.add_field(name="", value="Please be in a channel first")
    return await ctx.send(embed=em)
  if not ctx.voice_client:
    em = discord.Embed(color=0xBFACE2)
    em.add_field(name="", value="Music is not playing...")
    await ctx.send(embed=em)
  else:
    vc: wavelink.Player = ctx.voice_client
  # pause
  vc.queue.reset()
  await vc.stop()


# clear messages
@bot.command()
async def clear(ctx: commands.Context, amount=5):  # default is 5
  await ctx.channel.purge(limit=amount)


# disconnect the bot client
@bot.command()
async def leave(ctx: commands.Context):
  if not getattr(ctx.author.voice, "channel", None):
    em = discord.Embed(color=0x3E54AC)
    em.add_field(name="", value="Please be in a channel first")
    return await ctx.send(embed=em)
  if not ctx.voice_client:
    em = discord.Embed(color=0xBFACE2)
    em.add_field(name="", value="Music is not playing...")
    await ctx.send(embed=em)
  else:
    vc: wavelink.Player = ctx.voice_client
  # pause
  await ctx.message.add_reaction('👋')
  await vc.disconnect()


# loop setting
@bot.command()
async def loop(ctx: commands.Context):
  if not getattr(ctx.author.voice, "channel", None):
    em = discord.Embed(color=0x3E54AC)
    em.add_field(name="", value="Please be in a channel first")
    return await ctx.send(embed=em)
  if not ctx.voice_client:
    em = discord.Embed(color=0xBFACE2)
    em.add_field(name="", value="Music is not playing...")
    await ctx.send(embed=em)
  else:
    vc: wavelink.Player = ctx.voice_client
  # loop
  try:
    vc.loop ^= True
  except Exception:
    setattr(vc, "loop", False)
  if vc.loop:
    em = discord.Embed(color=0xBFACE2)
    em.add_field(name="", value="Loop Enabled")
    await ctx.send(embed=em)
  else:
    em = discord.Embed(color=0xBFACE2)
    em.add_field(name="", value="Loop Disabled")
    await ctx.send(embed=em)


# queue
@bot.command()
async def list(ctx: commands.Context):
  if not getattr(ctx.author.voice, "channel", None):
    em = discord.Embed(color=0x3E54AC)
    em.add_field(name="", value="Please be in a channel first")
    return await ctx.send(embed=em)
  if not ctx.voice_client:
    em = discord.Embed(color=0xBFACE2)
    em.add_field(name="", value="Music is not playing...")
    await ctx.send(embed=em)
  else:
    vc: wavelink.Player = ctx.voice_client
  # check emptyness
  if vc.queue.is_empty:
    em = discord.Embed(color=0xBFACE2)
    em.add_field(name="", value="Playlist is empty")
    return await ctx.send(embed=em)
  #
  em = discord.Embed(title="Playlist", color=0xBFACE2)
  queue = vc.queue.copy()  # an array copy of queue

  global last
  for i, q in enumerate(queue):
    em.add_field(name="", value=str(i + 1) + ". " + q.title, inline=False)
    if i == 9:
      last = i
      break
  if last == 0:
    last = len(queue) - 1

  view = List_Panel(vc, ctx, last)

  await ctx.send(embed=em, view=view)


# launch bot
bot.run(TOKEN)
