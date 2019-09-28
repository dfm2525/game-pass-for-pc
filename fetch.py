import requests
import re
import json
import datetime

data = requests.get(
    'https://reco-public.rec.mp.microsoft.com/channels/Reco/v8.0/lists/collection/pcgaVTaz?itemTypes=Devices&DeviceFamily=Windows.Desktop&market=US&language=EN&count=200').json()
gameids = []
for item in data['Items']:
    gameids.append(item['Id'])

output = []

idstring = (",").join(gameids)
url = f'https://displaycatalog.mp.microsoft.com/v7.0/products?bigIds={idstring}&market=US&languages=en-us&MS-CV=1234'
productData = requests.get(url).json()

with open('pcgames.json', 'r') as file:
    previousData = json.loads(file.read())

for product in productData['Products']:
    item = {}

    item['name'] = product['LocalizedProperties'][0]['ProductTitle']
    item['url'] = "https://www.microsoft.com/en-us/p/" + \
        re.sub(r'\W+', '', item['name'].replace(' ', '_')
               ).replace('_', '-').lower() + "/" + product['ProductId']
    item['releaseDate'] = product['MarketProperties'][0]['OriginalReleaseDate']
    item['id'] = product['ProductId']

    previousItem = next(
        (previous for previous in previousData if 'id' in previous and previous['id'] == item['id']), None)
    if previousItem != None and 'addedDate' in previousItem:
        item['addedDate'] = previousItem['addedDate']
    else:
        item['addedDate'] = datetime.datetime.utcnow().isoformat()

    usageData = product['MarketProperties'][0]['UsageData']
    for usage in usageData:
        if (usage['AggregateTimeSpan'] == 'AllTime'):
            item['allTimeRating'] = usage['AverageRating']
            break
    output.append(item)
# print(output)

outjson = json.dumps(output)
prevjson = json.dumps(previousData)

donestr = "done, no changes"
if outjson != prevjson:
    donestr = "done, changes found"
    with open('pcgames.json', 'w+') as out:
        out.write(json.dumps(output))

print(donestr)
