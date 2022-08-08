import asyncio
import datetime
import http.client
import json
import random
import re
from replit import db
from requests_html import HTMLSession
from lists import *
import os
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service


# ----- PRE DEFINED FUNCTIONS ------


# DESC: Gets the weather from an api and returns it to the doRespond function -> &temp <country>
def getWeather(msg):
  try:
    sesh = HTMLSession()
    country = msg.split(" ")[1]
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{country}?unitGroup=metric&include=current&key={os.environ['weatherKey']}&contentType=json"
    req = sesh.get(url).json()["currentConditions"]
    temp = str(req["temp"])
    conds = req["conditions"]
    return temp + "°C and " + conds + " in " + country
  except:
    return "Hmm, i can't recognize that country\n**Example**: &temp London"


# DESC: Gets the maximum and minimum weather forecast for the specified day -> &forecast <country>
def getForecast(msg):
  try:
    sesh = HTMLSession()
    country = msg.split(" ")[1]
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{country}?unitGroup=metric&include=current&key={os.environ['weatherKey']}&contentType=json"
    req = sesh.get(url).json()["days"]
    forecastMax = str(req[0]["tempmax"]) + "°C"
    forecastMin = str(req[0]["tempmin"]) + "°C"
    return f"Forecast for today is a max temperature of {forecastMax} and a min temperature of {forecastMin}"
  except:
      return "Hmm, i can't recognize that country\n**Example**: &forecast London"


# DESC: Clears either specific user's message if they are me, or deletes their own messages with 2nd arg "me" -> &clear 10 me OR &clear 10 Someone#1234
async def clear_specific(msg):
  try:
    split_msg = msg.content.split(" ", 2)
    def delete(m):
      return (str(m.author) == split_msg[2] and str(msg.author) == "YourUsername") or (split_msg[2] == "me" and m.author == msg.author)
    await msg.channel.purge(limit=int(split_msg[1])+1, check=delete)
  except:
    await msg.channel.send(f"{random.choice(generic_error_msgs)}\n**Example**: &clear 2 me")


# PRIVATE DESC: Gets all commands in the command dictionary -> &help
def getCmds(dict):
      res = "**List of Commands** (Sorted by time added):\n"
      for key in dict.keys():
        res += key + "\n"
      return res


# DESC: Gets the matches and scores for women's euro either today or at the specified date -> &weuro OR &weuro <date of july>
async def getScores(msg):
  try:
    splits = msg.content.split(" ")
    conn = http.client.HTTPSConnection("v3.football.api-sports.io")
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': os.environ['rapidApiKey']
        }

    date = 0
    if (len(splits) == 1) or (splits[1] == ""):
      date = datetime.date.today().day
    else:
      date = int(splits[1])

    conn.request("GET", f"/fixtures?season=2021&league=743&date=2022-07-{date:02d}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    dict = json.loads(data.decode('utf-8'))
    num_res = dict["results"]

    if (num_res > 0):
      responses = dict["response"]
      time = responses[0]["fixture"]["date"][0:10]
      frmt_time = datetime.datetime.strptime(time, "%Y-%m-%d").date().strftime("%B %d, %Y")
      await msg.channel.send(f"**For {frmt_time}:**")
      for i in range(0, num_res):
        home = responses[i]["teams"]["home"]["name"][:-1]
        away = responses[i]["teams"]["away"]["name"][:-1]
        home_score = responses[i]["goals"]["home"] or 0
        away_score = responses[i]["goals"]["away"] or 0
        status = responses[i]["fixture"]["status"]["long"]
        await msg.channel.send(f"{home}  {home_score} : {away_score}  {away} - [{status}]")
    else:
      await msg.channel.send("Couldn't find any matches for that date I'm afraid")
  except:
      await msg.channel.send("**Try following**: &weuro OR &weuro <day number in July>\n**Example**: &weuro 17")


# DESC: Converts temp from c to f or f to c -> &conv <(converts to) c/f> temp
def convertTemp(msg):
  try:
    split = msg.split(" ", 2) # &conv f <degreeC>
    num = float(split[2])
    if (split[1] == 'f'):
      fahr = round(num * 1.8 + 32, 1)
      return f"{fahr} °F"
    elif split[1] == 'c':
      celsius = round((num - 32) * 5/9, 1)
      return f"{celsius} °C"
    return "Try &conv <enter letter to convert to: c/f> <temp>\n**Example**: &conv f 30 -> Converts 30°C to °F"
  except:
    return f"{random.choice(generic_error_msgs)}\n**Example**: &conv f 30 -> Converts 30°C to °F"


# PRIVATE DESC: Helper function to parse <time>h <time>m <time>s into seconds
def parseTime(strtime):
    sep = strtime.strip().split(' ')
    res = 0
    for time in sep:
        if time[-1] == 'h':
            if not (int(time[:-1]) > 11):
                res = res + int(time[:-1]) * 3600
            else:
                raise ValueError("Incorrect time format - hours must be under 12")
        elif time[-1] == 'm':
            if not (int(time[:-1]) > 59):
                res = res + int(time[:-1]) * 60
            else:
                raise ValueError("Incorrect time format - minutes must be under 60")
        elif time[-1] == 's':
            if not (int(time[:-1]) > 59):
                res = res + int(time[:-1])
            else:
                raise ValueError("Incorrect time format - seconds must be under 60")
        else:
            raise ValueError("Incorrect time format")
    return res

# DESC: Sets a countdown timer -> &timer 1h 2m 3s
async def timer(msg):
  try:
    secs = parseTime(msg.content.split(" ", 1)[1])
    await msg.channel.send(random.choice(completed_msgs))
    await asyncio.sleep(secs)
    await msg.channel.send(f"{msg.author.mention}, {random.choice(timer_end_msgs)}")
  except:
    await msg.channel.send("**Try Format**: &timer <(hours < 12)>h <(mins < 60)>m <(secs < 60)>s\n**Example**: &timer 1h2m3s")


# DESC: Reminds the user of their reminder -> &remind (1h2s) A random reminder
async def reminder(msg):
  try:
    seps = re.split(' \(|\) ', msg.content, maxsplit=2)
    assert len(seps) == 3
    assert seps[2] != ""
    secs = parseTime(seps[1])
    message = seps[2]
    await msg.channel.send("Done")
    await asyncio.sleep(secs)
    await msg.channel.send(f"{msg.author.mention}, Your reminder: {message}")
  except:
    await msg.channel.send("**Try format**: &remind (<(hours < 12)>h <(mins < 60)>m <(secs < 60)>s) <Your message>\n**Example**: &remind (1h2m3s) hello there")


# DESC: Google for short description answers -> &search mass of the sun
def search(msg):
  try:
    sesh = HTMLSession()

    query = msg.split(' ', 1)[1]
    mod_query = query.replace(' ', '+')
    
    url = f"https://www.google.com/search?q={mod_query}"
    req = sesh.get(url).html
    
    # Direct answer box (eg; mass of the sun)
    if (req.xpath('//div[@data-tts="answers"]', first=True)):
        answer = req.xpath('//div[@data-tts="answers"]', first=True).attrs["data-tts-text"]
        return answer

    # First search for card container
    elif (req.find("div.card-section", first=True)):
        card = req.find("div.card-section", first=True).find("#NotFQb", first=True)
        value = card.find("input", first=True).attrs['value']
        unit = card.find('select', first=True).xpath('//option[@selected="1"]', first=True).text
        return f"{unit}: {value}"
    
    # If no card container, then check if its currency-like box
    elif (req.xpath('//div[@data-attrid="Converter"]')):
        table = req.xpath('//div[@data-attrid="Converter"]', first=True).find('table', first=True).find('tr')[-1].find('td')
        value = table[0].find('input', first=True).attrs["value"]
        unit = table[-1].xpath('//option[@selected="1"]', first=True).text
        return f"{unit} : {value}"
    
    # Only name answers
    elif (req.find('div.Z0LcW', first=True)):
        answer = req.find('div.Z0LcW', first=True).text
        return answer
    
    # Otherwise say, search for snippet result
    elif (req.xpath('//div[@data-attrid="wa:/description"]', first=True)):
        box = req.xpath('//div[@data-attrid="wa:/description"]', first=True).find('span', first=True)
        desc = box.find('span', first=True).text
        return desc
    
    # Carousell answers
    elif (req.find('g-scrolling-carousel')):
        answer = req.find('g-scrolling-carousel', first=True).find('a', first=True).attrs["aria-label"]
        return answer
    
    else:
        raise ValueError 

  except:
    return "I can't seem to search that. Try short questions\n**Example**: &search Tallest Building in the world"


# SELENIUM -> Not currency working in replit, yet to fix

# DESC: Gets lyrics -> &lyrics The gambler home free
# async def getLyrics(ctx):
#   s = Service('/usr/local/bin/chromedriver')
#   browser = webdriver.Chrome(service = s)
#   browser.get('https://www.azlyrics.com/')


#   # Search for song
#   song = "The gambler home free"
#   search_bar = browser.find_element(By.ID, 'q')
#   search_bar.send_keys(song)
#   search_bar.send_keys(Keys.ENTER)

#   # Go to lyrics from table
#   table = browser.find_element(By.CLASS_NAME, "table-condensed")
#   results = table.find_elements(By.CSS_SELECTOR, "tr")
#   results[0].click()

#   # Retrieving lyrics
#   lyrics = browser.find_element(By.XPATH, '//div[@class="col-xs-12 col-lg-8 text-center"]').find_elements(By.TAG_NAME, "div")[11]

#   res = lyrics.get_attribute('textContent')