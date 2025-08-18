import streamlit as st
import plotly.graph_objects as go
import os
import pylas

st.set_page_config(page_title="3D LiDAR Viewer", layout="wide")
st.title("🌍 LiDAR 3D Viewer with Layer & Classification Toggle")

# Load LAS files from data folder
data_folder = "data"
las_files = [f for f in os.listdir(data_folder) if f.endswith(".las")]

# Sidebar for LAS file selection
st.sidebar.header("Select LAS Files")
file_options = {}
for las_file in las_files:
    file_options[las_file] = st.sidebar.checkbox(las_file, True)

# Plotly figure
fig = go.Figure()

# Predefined classification names (LAS standard ones – you can adjust)
classification_names = {
    0: "Created, never classified",
    1: "Unclassified",
    2: "Ground",
    3: "Low Vegetation",
    4: "Medium Vegetation",
    5: "High Vegetation",
    6: "Building",
    7: "Low Point (Noise)",
    9: "Water",
    17: "Bridge Deck",
}

# Loop over files
for las_file in las_files:
    if file_options[las_file]:
        las_path = os.path.join(data_folder, las_file)
        las = pylas.read(las_path)

        st.sidebar.subheader(f"Classifications in {las_file}")

        # Get unique classifications in this file
        unique_classes = set(las.classification)

        for c in unique_classes:
            class_name = classification_names.get(c, f"Class {c}")

            # Checkbox to toggle classification
            show_class = st.sidebar.checkbox(f"{las_file} → {class_name}", True)

            # Color picker for this class
            color = st.sidebar.color_picker(f"Color for {class_name}", "#ff0000", key=f"{las_file}_{c}")

            if show_class:
                mask = (las.classification == c)
                fig.add_trace(go.Scatter3d(
                    x=las.x[mask],
                    y=las.y[mask],
                    z=las.z[mask],
                    mode='markers',
                    marker=dict(size=2, color=color),
                    name=f"{las_file} - {class_name}"
                ))

# Layout
fig.update_layout(
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z'
    ),
    height=800
)

st.plotly_chart(fig, use_container_width=True)
