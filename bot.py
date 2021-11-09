import discord
import asyncio

import time
import random, re
from collections import defaultdict
import time
import openai





client = discord.Client()

with open('ApiKey.txt') as f:
    openai.api_key  = f.readline()

with open('BotKey.txt') as f:
    BotKey =  f.readline()




@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))

client.channel_dict={}

client.oldtime = 5
client.last_sender =""
client.sender_list = dict()
client.last_sent = ""


@client.event
async def on_message(message):
	#if message.author == client.user:
	#	return



	#ignore DMs
	if str(message.channel.type) == "private":
		return


	#keep track of conversations across channels and servers
	if message.channel.id in client.channel_dict:
		message_list = client.channel_dict[message.channel.id]
	else:
		message_list = []
		client.channel_dict[message.channel.id] = message_list


	client.last_sender = message.author

	if len(message.content) > 1:
		message_list.append(message)


	#if we remember too much of discord history then it'll consume too many tokens
	if len(message_list)>6:
		message_list.pop(0)
	
	#random 1% chance to talk
	if(random.random() < 0.01):
		await talk(message,message_list)
	#otherwise talk if it's mentioned
	for x in message.mentions:
		if(x==client.user):
			await talk(message,message_list)
	
async def talk(message,messagelist):
	
	#a basic spam filter to preven a single person spamming the bot over and over and draining the tokens
	if time.time() - client.oldtime < 10 and client.last_sender == message.author:
		return
	#another general spam filter so two people can't do the above
	if time.time() - client.oldtime < 3:
		return

	client.oldtime = time.time()
	
	#GPT3 prompt
	prompt="Continue the following online chat. " + client.user.name + " is a witty and cynical chatbot.\n\n"


	#format the message for the prompt and clear out numbers and other garbage that will confuse the AI
	for msg in messagelist:
		prompt += msg.author.display_name+": "+msg.clean_content+"\n"
	prompt += client.user.name+":"
	prompt = prompt.encode('ascii', 'ignore').decode()#remove weird ascii characters

	prompt2 = prompt.replace(":"," ")
	prompt2 = prompt2.replace(">"," ")
	prompt2 = prompt2.replace("<"," ")
	numbers = [int(word) for word in prompt2.split() if word.isdigit()]
	for i in numbers:
		if i > 1000000:
			prompt = prompt.replace(str(i),"")
	#emoji names appear along with IDs - filter out the IDs


	prompt = prompt.replace(">","")
	prompt = prompt.replace("<","")
	#emoji are alos surounded by <> remove those too

	print(prompt)
	response = openai.Completion.create(engine="davinci-instruct-beta", prompt=prompt, stop=["\n"], temperature=0.8, max_tokens=100,presence_penalty=0.9,frequency_penalty=0)
	if len(response["choices"][0]["text"]) < 1:
		print("empty")#sometimes response comes back blank - trying to print blank message to discord causes an exception
		return
	print(response["choices"][0]["text"])
	await message.channel.send(response["choices"][0]["text"])




#start the bot
loop = asyncio.get_event_loop()
loop.create_task(client.start(BotKey))
loop.run_forever()
