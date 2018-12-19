import fut
import datetime
import time
import os
import random

first_time = True
min_margin = 500

items = [
  {'ctype': 'training', 'asset_id': 5003076, 'buy_in': 1500}
]

def search_and_buy(session, item):
  print('Going to search and buy...')
  results = session.search(ctype=item['ctype'],assetId=item['asset_id'],page_size=5,max_buy=item['buy_in'])
  print('Buy now count: ', len(results))
  for result in results:
    print('Going to buy now...')
    session.bid(result['tradeId'], item['buy_in'], fast=True)


def search_and_bid(session, item):
  print('Going to search and bid...')
  results = session.search(ctype=item['ctype'],assetId=item['asset_id'],page_size=5,max_price=item['buy_in'])
  print('Bid count: ', len(results), ' and check if within 1 min')
  for result in results:
    if result['expires'] <= 60:
      print('Going to bid now...')
      session.bid(result['tradeId'], item['buy_in'], fast=True)

def clean_watchlist(session):
  watchlist = session.watchlist()
  print('Watchlist Count:', len(watchlist))
  for result in watchlist:
    if result['bidState'] == 'outbid':
      session.watchlistDelete(result['tradeId'])
      print('Cleaning watchlist...')

    if result['bidState'] == 'highest':
      session.sendToTradepile(result['id'])

def clean_tradepile(session):
  relist = False
  clear = False
  print('Check the tradepile again...')
  for result in session.tradepile():
    if result['tradeState'] == None:
      for item in items:
        if result['resourceId'] == item['asset_id']:
          session.sell(result['id'], bid=item['buy_in']+min_margin, buy_now=item['buy_in']+min_margin+100)

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
      first_time = False
      print('Successfully login at ', datetime.datetime.now())

    session.keepalive()
    tradepile_count = len(session.tradepile())
    print('Tradepile count:', tradepile_count)

    if tradepile_count >= 95:
      print('Tradepile nearly full...')
    else:
      search_and_buy(session, items[0])
      time.sleep(1)

      search_and_bid(session, items[0])
      time.sleep(1)

      clean_watchlist(session)
      time.sleep(1)

    clean_tradepile(session)
    print('Time now is : ',datetime.datetime.now())
    print('----------------------------------------')
    time.sleep(5)
  except NameError:
    print('*** Session dropped ***')
    print(NameError)
    print('Login again: ',datetime.datetime.now())
    session = fut.Core(os.environ['email'], os.environ['password'], os.environ['secret'], platform="ps4")


