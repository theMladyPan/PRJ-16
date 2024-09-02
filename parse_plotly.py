import numpy
import plotly.graph_objs as go
from plotly.subplots import make_subplots
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
    filter={},
    sort=[('_id', -1)]
)

log.info(f"Last document: {last_doc}") 

# load aggregation from js file:
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

# Extract the data
# time is in format '2024-07-25T00:54:51', convert it to datetime
x = [datetime.strptime(doc['time']['datetime'], "%Y-%m-%dT%H:%M:%S").timestamp() for doc in data]
y = [doc['T1']["t"] for doc in data]
z = [doc['S'] for doc in data]

# Create 3D scatter plot using Plotly
fig = go.Figure(data=[go.Scatter3d(
    x=x,
    y=y,
    z=z,
    mode='markers',
    marker=dict(
        size=5,
        color=z,  # Set color to the z values
        colorscale='Viridis',  # Choose a colorscale
        opacity=0.8
    )
)])

# fig.update_layout(
#     scene=dict(
#         xaxis_title='Time',
#         yaxis_title='Temperature',
#         zaxis_title='S14'
#     ),
#     margin=dict(l=0, r=0, b=0, t=0)  # Adjust margins for a clean look
# )
# Set the layout to use orthogonal (orthographic) projection
fig.update_layout(
    scene=dict(
        xaxis_title='Time',
        yaxis_title='Temperature',
        zaxis_title='S14',
        camera=dict(
            projection=dict(
                type='orthographic'  # Set projection to orthographic
            )
        )
    ),
    margin=dict(l=0, r=0, b=0, t=0)  # Adjust margins for a clean look
)

fig.show()
fig.show()
