import numpy
from matplotlib import pyplot
from pymongo import MongoClient
import dotenv
import logging
import os
import argparse
import json
from datetime import datetime

dotenv.load_dotenv()
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Connect to the MongoDB server
client = MongoClient(os.getenv('MONGO_URI'))
db = client['prod']
col = db['PRJ-16']

last_doc = col.find_one(
    filter={
    },
    sort=[('_id', -1)]
)

log.info(f"Last document: {last_doc}") 

# load agregation from js file:
with open('s14.mongodb.js', 'r') as file:
    # Read the file contents
    js_content = file.read()
    
    # Strip out the variable assignment and the MongoDB commands
    start = js_content.find('[')
    end = js_content.rfind(']') + 1
    aggregation_pipeline_str = js_content[start:end]
    log.debug(f"Aggregation pipeline: {aggregation_pipeline_str}")

    # Parse the string as JSON
    aggregation_pipeline = json.loads(aggregation_pipeline_str)


log.info(f"Aggregation: {aggregation_pipeline}")

docs = col.aggregate(aggregation_pipeline)

# Extract the data from the cursor
data = list(docs)
log.info(f"Data length: {len(data)}")

log.info(f"Last doc: {data[-1]}")

# document template:
# {'_id': ObjectId('66a1a25b3ae660fb8a106850'), 'time': {'datetime': '2024-07-25T00:54:51'}, 'S14': {'s': 362177.0}, 'T1': {'t': 25.0}, 'hour': 0, 'temp': 25.0, 'S': 236.53779869999997}

# plot 3D data S14 in temperature and time domain
fig = pyplot.figure()
ax = fig.add_subplot(111, projection='3d')

# Extract the data
# time is in format '2024-07-25T00:54:51', convert it to datetime
x = [datetime.strptime(doc['time']['datetime'], "%Y-%m-%dT%H:%M:%S").timestamp() for doc in data]
y = [doc['T1']["t"] for doc in data]
z = [doc['S'] for doc in data]

ax.scatter(x, y, z)

ax.set_xlabel('Time')
ax.set_ylabel('Temperature')
ax.set_zlabel('S14')

pyplot.show()