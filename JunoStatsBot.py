#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#Coded by CamelJuno 🐪#7465

import discord
import requests
import random
import json
import base64
import string
import time
from datetime import date,datetime,timedelta

client = discord.Client()

def getJUNOGecko():
  headers = {
    'Host': 'api.coingecko.com',
    'Accept': '*/*'
  }
  a = requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=juno-network',headers=headers,timeout=10)
  if a.status_code == 200:
    z = json.loads(a.text)[0]['current_price']
    b = json.loads(a.text)[0]['market_cap']
    x = json.loads(a.text)[0]['max_supply']
    if z == None or b == None or x == None:
      getJUNOGecko()
    else:
      return z,b,x
  else:
    getJUNOGecko()

def getAPI():
  headers = {
  'Host': 'supply-api.junonetwork.io',
  'Connection': 'keep-alive'
  }
  a = requests.get('https://supply-api.junonetwork.io/',headers=headers,timeout=10)
  if a.status_code == 200:
    circulatingSupply = round(float(json.loads(a.text)['circulatingSupply']))
    return circulatingSupply
  else:
    getAPI()

def getJUNOMintscan():
  headers = {
  'Host': 'api-utility.cosmostation.io',
  'Accept': 'application/json, text/plain, */*'
  }
  a = requests.get('https://api-utility.cosmostation.io/v1//params/juno-1',headers=headers,timeout=10)
  if a.status_code == 200:
    inflation = int(float(json.loads(a.text)['Params']['minting_inflation']['inflation'])*100)
    unbondingPeriod = int(json.loads(a.text)['Params']['staking_params']['params']['unbonding_time'].replace('s',''))/86400
    maxValidators = int(json.loads(a.text)['Params']['staking_params']['params']['max_validators'])
    if inflation == None or unbondingPeriod == None or maxValidators == None:
      getJUNOMintscan()
    else:
      return inflation,unbondingPeriod,maxValidators
  else:
    getJUNOMintscan()

def getJUNOMintscanStatus():
  headers = {
  'Host': 'api-juno.cosmostation.io',
  'Accept': 'application/json, text/plain, */*'
  }
  a = requests.get('https://api-juno.cosmostation.io/v1/status',headers=headers,timeout=10)
  if a.status_code == 200:
    communityPool = int(round(float(json.loads(a.text)['community_pool'][0]['amount'])/1000000))
    currentSupply = int(round(float(json.loads(a.text)['total_circulating_tokens']['supply'][-1]['amount'])/1000000))
    totalBonded = int(round(float(json.loads(a.text)['bonded_tokens'])/1000000))
    if communityPool == None or currentSupply == None or totalBonded == None:
      getJUNOMintscanStatus()
    else:
      return communityPool,currentSupply,totalBonded
  else:
    getJUNOMintscanStatus()

def getGovernance(totalBonded):
  headers = {
  'Host': 'api.mintscan.io',
  'Accept': 'application/json, text/plain, */*'
  }
  a = requests.get('https://api.mintscan.io/v1/juno/proposals',headers=headers,timeout=10)
  if a.status_code == 200:
    proposalData = json.loads(a.text)
    activeProposals = 0
    for i in proposalData:
      if i['proposal_status'] == 'PROPOSAL_STATUS_VOTING_PERIOD':
        activeProposals = activeProposals + 1
    governanceData = ':scroll: `Active Proposals:` **'+str(activeProposals)+'**\n'
    if activeProposals > 0:
      for i in proposalData:
        if i['proposal_status'] == 'PROPOSAL_STATUS_VOTING_PERIOD':
          yesVotes = round(float(i['yes'])/1000000)
          noVotes = round(float(i['no'])/1000000)
          noVetoVotes = round(float(i['no_with_veto'])/1000000)
          abstainVotes = round(float(i['abstain'])/1000000)
          governanceData = governanceData + '> ```Proposal #'+str(i['id'])+'```:ballot_box: `Current Turnout:` **'+str(round((yesVotes+abstainVotes+noVotes+noVetoVotes)/float(totalBonded)*100,2))+'%**\n> :white_check_mark: `Yes:` **'+'{:,}'.format(yesVotes)+'**\n> :x: `No:` **'+'{:,}'.format(noVotes)+'**\n> :no_entry: `NoWithVeto:` **'+'{:,}'.format(noVetoVotes)+'**\n> :person_shrugging: `Abstain:` **'+'{:,}'.format(abstainVotes)+'**\n> :alarm_clock: `Voting End:` **'+i['voting_end_time'].replace('T',' ').split('.',1)[0]+' UTC**\n'
    return governanceData

def getBlockTime():
  headers = {
  'Host': 'api.mintscan.io',
  'Accept': 'application/json, text/plain, */*'
  }
  a = requests.get('https://api.mintscan.io/v1/juno/block/blocktime',headers=headers,timeout=10)
  if a.status_code == 200:
    return json.loads(a.text)['block_time']
  else:
    getBlockTime()

def formatIt(hello):
  suffixes = ["", "K", "M", "B", "T"]
  hello = str("{:,}".format(hello))
  commas = 0
  x = 0
  while x < len(hello):
      if hello[x] == ',':
        commas += 1
      x += 1
  return hello.split(',')[0]+'.'+hello.split(',')[1][:-1] + suffixes[commas]

def genId():
  res = ''
  for i in range(12):
    res = res+random.choice(string.digits)
  return int(res)

@client.event
async def on_ready():
  print(f'You have logged in as {client}')
  message = await client.get_channel(channelID).fetch_message(messageID)
  while(True):
    try:
      today = date.today().strftime("%B %d, %Y")
      price,marketCap,maxSupply = getJUNOGecko()
      circulatingSupply = getAPI()
      inflation,unbondingPeriod,maxValidators = getJUNOMintscan()
      communityPool,currentSupply,totalBonded = getJUNOMintscanStatus()
      governanceData = getGovernance(totalBonded)
      bondedRatio = round(float(totalBonded/currentSupply)*100,2)
      APR = 25961297.0 * (1-2) / float(totalBonded) * 6.247111/getBlockTime() * 100
      messageToBeSent = ':calendar: **'+today+'** :calendar:\n**__JUNO Stats - Update/Minute__**\n\n'
      messageToBeSent = messageToBeSent+':dollar: `Price:` **$'+str(price)+'**\n:moneybag: `Market Capitalization:` **$'+str(formatIt(marketCap))+'**\n'
      messageToBeSent = messageToBeSent+'```Supply Stats```:left_luggage: `Max Supply:` **'+'{:,}'.format(int(maxSupply))+'**\n:briefcase: `Current Supply:` **'+'{:,}'.format(currentSupply)+'**\n:recycle: `Circulating Supply:` **'+'{:,}'.format(circulatingSupply)+'**\n:classical_building: `Community Pool:` **'+'{:,}'.format(communityPool)+'**\n'
      messageToBeSent = messageToBeSent+'```Staking Stats```:trophy: `APR:` **'+str(APR)+'%**\n:printer: `Inflation:` **'+str(inflation)+'%**\n:closed_lock_with_key: `Total Bonded:` **'+'{:,}'.format(int(totalBonded))+'**\n:bar_chart: `Bonded Ratio:` **'+str(bondedRatio)+'%**\n:unlock: `Unbonding Period:` **'+str(int(unbondingPeriod))+' Days**\n:technologist: `Max Validators:` **'+str(maxValidators)+'**\n'
      messageToBeSent = messageToBeSent+'```Governance Stats```'+governanceData
      messageToBeSent = messageToBeSent+'```Resources```:lizard: `CoinGecko:` https://www.coingecko.com/en/coins/juno-network\n:test_tube: `JunoSwap:` https://junoswap.com\n:test_tube: `Osmosis:` https://info.osmosis.zone/token/JUNO\n:desktop: `Monitor:` https://monitor.bronbro.io/d/juno-stats\n:mag_right: `Mintscan:` https://www.mintscan.io/juno\n\n'
      messageToBeSent = messageToBeSent+'>>> ***Powered By <@340813726103896064>***'
      await message.edit(content=messageToBeSent)
      print('Updated on: '+str(datetime.now().strftime("%H:%M:%S")))
      time.sleep(57)
    except:
      continue

messageID = 0
channelID = 0
BOT_TOKEN = 'PLACE_AUTH_TOKEN_HERE'
client.run(BOT_TOKEN)