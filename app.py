import streamlit as st
import laspy
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.colors as mcolors

# Title
st.title("3D LiDAR Point Cloud Viewer")

# File uploader
uploaded_file = st.file_uploader("Upload LAS/LAZ file", type=["las", "laz"])

if uploaded_file:
    # Read LAS file safely
    las = laspy.read(uploaded_file)
    st.write(f"✅ Loaded {len(las.points)} points from file")

    # Create DataFrame from LAS data (force arrays to avoid scalar issues)
    df = pd.DataFrame({
        "X": np.array(las.x),
        "Y": np.array(las.y),
        "Z": np.array(las.z),
        "Class": np.array(las.classification)
    })

    # Map class codes to names
    class_mapping = {
        0: "Created, Never Classified",
        1: "Unclassified",
        2: "Ground",
        3: "Low Vegetation",
        4: "Medium Vegetation",
        5: "High Vegetation",
        6: "Building",
        7: "Low Point (Noise)",
        9: "Water",
        10: "Rail",
        17: "Bridge Deck",
        18: "High Noise"
    }

    # Add class name column
    df["ClassName"] = df["Class"].map(class_mapping).fillna("Other")

    # Get unique classes
    unique_classes = df["Class"].unique()

    # Initialize session state for class settings
    if "classes" not in st.session_state:
        st.session_state.classes = {
            c: {
                "visible": True,
                "color": np.random.choice(list(mcolors.CSS4_COLORS.values()))
            }
            for c in unique_classes
        }

    # Sidebar for controls
    st.sidebar.header("Class Controls")

    # Checkbox to show all points in one color
    show_all = st.sidebar.checkbox("Show all points as one color", value=False)

    # Controls for each class
    for c in unique_classes:
        class_name = class_mapping.get(c, "Other")
        col1, col2 = st.sidebar.columns([2, 1])
        with col1:
            st.session_state.classes[c]["visible"] = st.checkbox(
                f"{c}: {class_name}", value=st.session_state.classes[c]["visible"]
            )
        with col2:
            st.session_state.classes[c]["color"] = st.color_picker(
                f"Color {c}",
                value=st.session_state.classes[c]["color"],
                label_visibility="collapsed"
            )

    # Apply filters
    if show_all:
        plot_df = df.copy()
        plot_df["Color"] = "#888888"  # uniform gray
    else:
        visible_classes = [c for c, v in st.session_state.classes.items() if v["visible"]]
        plot_df = df[df["Class"].isin(visible_classes)].copy()
        plot_df["Color"] = plot_df["Class"].map(lambda c: st.session_state.classes[c]["color"])

    # Plot 3D scatter
    if not plot_df.empty:
        fig = px.scatter_3d(
            plot_df, x="X", y="Y", z="Z",
            color="Color",
            title="LiDAR Point Cloud",
            color_discrete_map="identity"  # Ensures hex colors are used directly
        )
        fig.update_traces(marker=dict(size=2))  # smaller points for clarity
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No points selected for display.")

    # Summary stats
    st.subheader("Summary Statistics")
    stats = df.groupby("ClassName").agg(
        Point_Count=("Z", "size"),
        Min_Z=("Z", "min"),
        Max_Z=("Z", "max")
    ).reset_index()
    st.dataframe(stats)

else:
    st.info("👆 Please upload a LAS/LAZ file to get started.")
