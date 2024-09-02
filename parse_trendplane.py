import numpy as np
import plotly.graph_objs as go
from pymongo import MongoClient
import dotenv
import logging
import os
import json
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

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

# Load aggregation from JS file
with open('s14.mongodb.js', 'r') as file:
    js_content = file.read()
    start = js_content.find('[')
    end = js_content.rfind(']') + 1
    aggregation_pipeline_str = js_content[start:end]
    aggregation_pipeline = json.loads(aggregation_pipeline_str)

log.info(f"Aggregation: {aggregation_pipeline}")

docs = col.aggregate(aggregation_pipeline)
data = list(docs)

log.info(f"Data length: {len(data)}")
log.info(f"Last doc: {data[-1]}")

# Extract the data
x = [datetime.strptime(doc['time']['datetime'], "%Y-%m-%dT%H:%M:%S") for doc in data]
y = np.array([doc['T1']["t"] for doc in data])
z = np.array([doc['S'] for doc in data])

# Perform 3D linear regression to fit a plane
x_numeric = np.array([dt.timestamp() for dt in x])
X = np.column_stack((x_numeric, y))
model = LinearRegression().fit(X, z)
z_pred = model.predict(X)

# Calculate the R-squared value
r_squared = r2_score(z, z_pred)
log.info(f"R-squared: {r_squared}")

# Create a meshgrid for the trendline plane
x_range = np.linspace(x_numeric.min(), x_numeric.max(), 50)
y_range = np.linspace(y.min(), y.max(), 50)
x_mesh, y_mesh = np.meshgrid(x_range, y_range)
z_mesh = model.predict(np.column_stack((x_mesh.ravel(), y_mesh.ravel()))).reshape(x_mesh.shape)

# Convert x_range back to datetime for plotting
x_mesh_datetime = [datetime.fromtimestamp(ts) for ts in x_range]

# Create 3D scatter plot using Plotly
scatter_trace = go.Scatter3d(
    x=x,
    y=y,
    z=z,
    mode='markers',
    marker=dict(
        size=5,
        color=z,
        colorscale='Viridis',
        opacity=0.8
    ),
    name='Data Points'
)

# Add the fitted plane as a surface
plane_trace = go.Surface(
    x=x_mesh_datetime,
    y=y_mesh,
    z=z_mesh,
    colorscale='Viridis',
    opacity=0.5,
    name='Trendline Plane'
)

# Create the figure and add both traces
fig = go.Figure(data=[scatter_trace, plane_trace])

# Set the layout to use orthogonal (orthographic) projection
fig.update_layout(
    scene=dict(
        xaxis_title='Time',
        yaxis_title='Temperature',
        zaxis_title='S14',
        xaxis=dict(type='date'),
        camera=dict(
            projection=dict(
                type='orthographic'
            )
        )
    ),
    margin=dict(l=0, r=0, b=0, t=0),
    annotations=[
        dict(
            xref="paper",
            yref="paper",
            x=0.1,
            y=1.05,
            showarrow=False,
            text=f'R-squared: {r_squared:.3f}',
            font=dict(
                size=14,
                color="black"
            ),
        )
    ]
)

fig.show()
