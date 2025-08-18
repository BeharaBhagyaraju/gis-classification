import streamlit as st
import plotly.graph_objects as go
import os
import pylas

st.set_page_config(page_title="3D LiDAR Viewer", layout="wide")
st.title("🌍 LiDAR 3D Viewer with Layer Toggle")

# Load LAS files from data folder
data_folder = "data"
las_files = [f for f in os.listdir(data_folder) if f.endswith(".las")]

layer_options = {}
for las_file in las_files:
    layer_options[las_file] = st.sidebar.checkbox(las_file, True)

fig = go.Figure()

# Assign different colors to each file
colors = ["red", "green", "blue", "orange", "purple", "cyan"]

for i, las_file in enumerate(las_files):
    if layer_options[las_file]:
        las_path = os.path.join(data_folder, las_file)
        las = pylas.read(las_path)
        fig.add_trace(go.Scatter3d(
            x=las.x, y=las.y, z=las.z,
            mode='markers',
            marker=dict(size=1, color=colors[i % len(colors)]),
            name=las_file
        ))

fig.update_layout(
    scene=dict(
        xaxis_title='X', yaxis_title='Y', zaxis_title='Z'
    ),
    height=800
)

st.plotly_chart(fig, use_container_width=True)
