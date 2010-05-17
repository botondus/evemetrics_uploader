"""Parser for cache files written on top of reverence"""

import csv
import StringIO
import datetime
import pprint

from reverence import blue

# Quick helper function to convert CCP's long date format (Windows timestamp) into a UTC datetime object.
def wintime_to_datetime(timestamp):
  return datetime.datetime.utcfromtimestamp((timestamp-116444736000000000)/10000000)

# Converts relevant cache files into CSV suitable for upload.
def parse(filepath):
  key, obj = blue.marshal.Load(open(filepath, "rb").read())
  s = StringIO.StringIO()
  w = csv.writer(s)
  if 'GetOldPriceHistory' in key or 'GetNewPriceHistory' in key:
    history = obj['lret']
    for row in history:
      w.writerow([
        wintime_to_datetime(row.historyDate).strftime("%Y-%m-%d %H:%M:%S"), 
        row.lowPrice, row.highPrice, row.avgPrice, row.volume, row.orders, key[3], key[2]   
      ])
  elif 'GetOrders' in key:
    orders = obj['lret']
    for order in (orders[0]+orders[1]):
      w.writerow([
        order.price, order.volRemaining, order.typeID, order.range, order.orderID, 
        order.volEntered, order.minVolume, order.bid, wintime_to_datetime(order.issued).strftime("%Y-%m-%d %H:%M:%S"), order.duration,
        order.stationID, order.regionID, order.solarSystemID, order.jumps, 'cache'
      ])
  else:
    print 'skipping unknown key %s' % pprint.pformat( key )
    return
  s.seek(0)
  return [ key[1], key[2], key[3], s.read(), wintime_to_datetime( obj['version'][0] ).strftime("%Y-%m-%d %H:%M:%S") ]