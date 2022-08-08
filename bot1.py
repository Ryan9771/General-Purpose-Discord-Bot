import discord
import os
import random
from replit import db
from keep_alive import keep_alive
from funcs import *
from lists import *

# ------------

# TODO: Add specific response commands

# ------------

# DESC: The discord client
class client(discord.Client):

  # DESC: Displays a message to the console when the bot is online
  async def on_ready(self):
    await self.change_presence(activity=discord.Game(name="on discord"))
    print("The bot has connected! We have logged in as {0.user}".format(self))

  # --------

  # DESC: Deals with responding back on certain message commands
  async def on_message(self, message):
    if (message.author == self.user):
      return

    # ------

    # DESC: General purpose function to send message on channels
    def doRespond(callback):
      async def result(message):
        await message.channel.send(callback(message.content))
      return result

    # DESC: General purpose function to perform non-send await operations 
    def doAction(callback):
      async def result(message):
        await callback(message)
      return result

    # ------

    # DESC: User specific commands
    if (message.content.startswith("&wipe")):
      if (str(message.author) == "Boi#6581"):
        lim = int(message.content.split(" ")[1]) + 1
        await message.channel.purge(limit = lim)
      else:
        await message.channel.send("Ok")

    # ------------

    # Commands
    cmd_responses = {
      "&8ball" : doRespond(lambda _ : random.choice(eight_ball)),
      "&clear" : doAction(clear_specific),
      "&conv" : doRespond(convertTemp),
      "&forecast" : doRespond(getForecast),
      "&hello" : doRespond(lambda _ : "hello " + str(message.author)[:-5]),
      "&hi" : doRespond(lambda _ : "hi " + str(message.author)[:-5]),
      "&remind" : doAction(reminder),
      "&search" : doRespond(search),
      "&temp" : doRespond(getWeather),
      "&timer" : doAction(timer)
      # "&weuro" : doAction(getScores)
    }

    # Exact
    ext_responses = {
      "hi bot" : (lambda _ : "hi " + str(message.author)[:-5]),
      "hello bot" : (lambda _ : "hello " + str(message.author)[:-5]),
      "good bot" : (lambda _ : "Thank you " + str(message.author)[:-5]),
      "bonk" : (lambda _ : "https://i.redd.it/xc0om3j75ne51.jpg"),
      "no u" : (lambda _ : "no u"),
      "i love you" : (lambda _ : "I love you too " + str(message.author)[:-5]),
      "i love you bot" : (lambda _ : "I love you too " + str(message.author)[:-5]),
      "love you bot" : (lambda _ : "I love you too " + str(message.author)[:-5]),
      "yo bot" : (lambda _ : random.choice(yo_msgs)),
      "thank you bot" : (lambda _ : random.choice(welcome_msgs)),
      "right bot?" : (lambda _ : random.choice(right_msgs))
    }

    # Container words
    cnt_responses = {
      "hmm" : (lambda _ : random.choice(["hmm", "interesting", "very interesting"])),
    }

    
    # Message Parser
    message_sent = False

    # Including replit database for commands
    phrs = cmd_responses.copy()
    if "phrases" in db.keys():
      phrs.update(db["phrases"])

    # DESC: Listing Commands
    if (message.content.startswith("&help")):
      await message.channel.send(getCmds(phrs))
      message_sent = True


    # DESC: User can add a custom phrase to say
    elif (message.content.startswith("&add")):
      try:
        seps = message.content.split(" ", 2)
        assert seps[1].startswith("&")
        if seps[1] in phrs.keys():
          await message.channel.send("That command already exists!")
          return
        elif "phrases" in db.keys():
          phrs = db["phrases"]
          phrs[seps[1]] = seps[2]
          db["phrases"] = phrs
        else:
          db["phrases"] = {seps[1] : doRespond(lambda _ : seps[2])}
        await message.channel.send(random.choice(completed_msgs))
      except:
        await message.channel.send(f"{random.choice(generic_error_msgs)}\n**Try Format**: &add &<command> Your phrase\n**Example**: &add &sayHi Hi there!")
      message_sent = True


    # DESC: A user with 'admin' or 'mod' role can delete an added key
    elif message.content.startswith("&del"):
      if any(role in ["Admins", "Mod"] for role in map(str,message.author.roles)):
        seps = message.content.split(" ", 1)
        try:
          assert seps[1].startswith("&")
          if (seps[1] in phrs.keys()) and (seps[1] not in cmd_responses.keys()):
            phrs = db["phrases"]
            phrs.pop(seps[1])
            db["phrases"] = phrs
            await message.channel.send(random.choice(completed_msgs))
          elif seps[1] not in phrs.keys():
            await message.channel.send("The command has to be existing.\nTo see the list of commands, enter *&help*")
          elif seps[1] in cmd_responses.keys():
            await message.channel.send("Well, don't think you have perms for that I'm afraid 😪")
          else:
            raise ValueError
        except:
          await message.channel.send(f"{random.choice(generic_error_msgs)}\n**Try Format**: &del &<existing command>\n**Example**: &del &something")
      else:
        await message.channel.send("You do not have the perms for this I'm afraid 😪")
      message_sent = True
    
    # DESC: Commands Parser -> Processes commands that start with '&'
    elif (message.content.startswith("&")):
      for cmd, rsp in phrs.items():
        if message.content.startswith(cmd):
          print(cmd_responses)
          if cmd in cmd_responses.keys():
            await rsp(message)
          else:
            await message.channel.send(rsp)
          message_sent = True
          break


    # DESC: Exact Match Messages
    elif message.content.lower() in ext_responses.keys():
      message_sent = True
      await message.channel.send(ext_responses[message.content.lower()](message.content))


    # DESC: Containing Word Messages
    else:
      split_words = message.content.split(" ")
      for wrd in split_words:
        if wrd.lower() in cnt_responses.keys():
          message_sent = True
          await message.channel.send(cnt_responses[wrd](message.content))
          break

    # If no commands were executed, bot has a 98% probability of sending a random message
    if (not message_sent):
      if (random.randint(0, 100) > 98):
        await message.channel.send(random.choice(random_phrases))


  
# MAIN
MyClient = client()
keep_alive()
MyClient.run(os.environ['TOKEN'])
