import fut
import datetime
import time
import os
import random
import requests

first_time = True
min_margin = 400

items = [
  {'ctype': 'training', 'asset_id': 5003075, 'buy_in': 1800, 'name': 'CAMCF'},
  {'ctype': 'training', 'asset_id': 5003076, 'buy_in': 2000, 'name': 'CFCAM'},
  # {'ctype': 'player', 'asset_id': 230666, 'buy_in': 6500, 'name': 'Gabriel Jesus'}
]
session = None
item = None

def search_and_set_price():
  print('Going to search ', item['name'])
  results = session.search(ctype=item['ctype'],assetId=item['asset_id'],page_size=50)
  min_buy_in = item['buy_in']
  for result in results:
    if result['currentBid'] < min_buy_in and result['currentBid'] != 0:
      min_buy_in = result['currentBid']
  item['buy_in'] = min_buy_in
  print('set the min buy in price is ', item['buy_in'])


def search_and_buy():
  print('Going to search and buy ', item['name'])
  results = session.search(ctype=item['ctype'],assetId=item['asset_id'],page_size=3,max_buy=item['buy_in'])
  print('Buy now count: ', len(results))
  for result in results:
    print('Buy now...', session.bid(result['tradeId'], item['buy_in'], fast=True))


def search_and_bid():
  print('Going to search and bid...', item['name'])
  results = session.search(ctype=item['ctype'],assetId=item['asset_id'],page_size=5,max_price=item['buy_in'])
  print('Bid count: ', len(results), ' and check if within 1 min')
  for result in results:
    if result['expires'] <= 60:
      print('Bid now...', session.bid(result['tradeId'], item['buy_in'], fast=True))


def clean_watchlist():
  watchlist = session.watchlist()
  print('Watchlist Count:', len(watchlist))
  for result in watchlist:
    if result['bidState'] == 'outbid':
      session.watchlistDelete(result['tradeId'])
      print('Cleaning watchlist...')

    if result['bidState'] == 'highest':
      session.sendToTradepile(result['id'])


def clean_unassigned():
  unassigned = session.unassigned()
  print('Unassigned Count:', len(unassigned))
  for result in unassigned:
    session.sendToTradepile(item_id=result['id'])


def clean_tradepile():
  relist = False
  clear = False
  print('Check the tradepile again...')
  tradepile = session.tradepile()
  print('Tradepile count:', len(tradepile))

  for result in tradepile:
    if result['tradeState'] == None:
      session.sell(result['id'], bid=result['lastSalePrice']+min_margin, buy_now=result['lastSalePrice']+min_margin+100)

    if result['tradeState'] == 'expired':
      relist = True

    if result['tradeState'] == 'closed':
      clear = True

  if relist == True:
    print('Relist some items')
    session.relist()

  if clear == True:
    print('Clear sold items')
    session.tradepileClear()


while True:
  try:
    if first_time == True:
      print('Welcome to FUT!')
      print('Login: ', datetime.datetime.now()) 
      session = fut.Core(os.environ['email'], os.environ['password'], os.environ['secret'], platform="ps4")
      print(requests.get('https://api.telegram.org/bot%s/sendMessage?text=%s&chat_id=%s' % (os.environ['telegram'], 'Login ^^', os.environ['chat_id'])))
      first_time = False
      print('   At: ', datetime.datetime.now())

    coins = session.keepalive()
    print('You have $', coins)
    tradepile_count = len(session.tradepile())
    print('Tradepile count:', tradepile_count)

    if coins <= 10000:
      print('No money...')
      time.sleep(300)
    elif tradepile_count >= 99:
      print('Tradepile nearly full...')
    else:
      item = random.choice(items)
      search_and_set_price()
      time.sleep(1)

      search_and_buy()
      time.sleep(1)

      search_and_bid()
      time.sleep(1)

      clean_watchlist()
      time.sleep(1)

    clean_unassigned()
    time.sleep(1)

    clean_tradepile()
    print('Time now is : ',datetime.datetime.now())
    print('----------------------------------------')
    time.sleep(20)

  except fut.exceptions.ExpiredSession:
    print(requests.get('https://api.telegram.org/bot%s/sendMessage?text=%s&chat_id=%s' % (os.environ['telegram'], 'Session Expired', os.environ['chat_id'])))
    first_time = True
    time.sleep(1800)
  except fut.exceptions.Captcha:
    for x in range(0, 9):
      print(requests.get('https://api.telegram.org/bot%s/sendMessage?text=%s&chat_id=%s' % (os.environ['telegram'], 'Urgent!!!', os.environ['chat_id'])))
    break
  except Exception as exception:
    print('Exception: %s' % exception)
    print(requests.get('https://api.telegram.org/bot%s/sendMessage?text=%s&chat_id=%s' % (os.environ['telegram'], 'Exception', os.environ['chat_id'])))
    break




