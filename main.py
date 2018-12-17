import fut
import datetime
import time
import os

first_time = True
asset_id = 5003076
buy_now_price = 1500
max_price = 1500
sell_min_price = 1800
sell_max_price = 1900

while True:
  try:
    if first_time == True:
      print('Welcome to FUT!')
      print('Login: ',datetime.datetime.now()) 
      session = fut.Core(os.environ['email'], os.environ['password'], os.environ['secret'], platform="ps4")
      first_time = False

    session.keepalive()
    tradepile_count = len(session.tradepile())
    print('Tradepile count:', tradepile_count)

    if tradepile_count >= 95:
      print('tradepile nearly full...')
    else:
      print('going to search...')
      results = session.search(ctype='training',category='position',assetId=asset_id,page_size=50,max_buy=buy_now_price)
      print('buy now count', len(results))
      for result in results:
        print('going buy now...')
        session.bid(result['tradeId'], buy_now_price, fast=True)
        # session.sendToTradepile(result['id'])


      results = session.search(ctype='training',category='position',assetId=asset_id,page_size=10,max_price=max_price)
      print('max price but maybe take longer time, count:', len(results))
      for result in results:
        if result['expires'] <= 60:
          print('going to bid now...')
          session.bid(result['tradeId'], max_price+100, fast=True)
          time.sleep(0.5)

      watchlist = session.watchlist()
      print('Watchlist Count:', len(watchlist))
      for result in watchlist:
        if result['bidState'] == 'outbid':
          session.watchlistDelete(result['tradeId'])
          print('cleaning watchlist...')
          time.sleep(0.5)

        if result['bidState'] == 'highest':
          session.sendToTradepile(result['id'])


    relist = False
    clear = False
    print('Check the tradepile again...')
    for result in session.tradepile():
      if result['tradeState'] == None:
        session.sell(result['id'], bid=sell_min_price, buy_now=sell_max_price)

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

    print('Time now is : ',datetime.datetime.now())
    time.sleep(5)
  except NameError:
    print('*** Session dropped ***')
    print('Login: ',datetime.datetime.now()) 
    session = fut.Core(os.environ['email'], os.environ['password'], os.environ['secret'], platform="ps4")
  # else:
    # print('Else case')
  # finally:
    # print('Must go through')
