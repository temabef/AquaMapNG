import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium, folium_static
import os
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(
    page_title="AquaMapNG - Nigerian Aquaculture Map",
    page_icon="🐟",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    data_path = os.path.join("data", "aquaculture_clusters.csv")
    data = pd.read_csv(data_path)
    return data

# Main function
def main():
    # Header
    st.title("AquaMapNG")
    st.subheader("Interactive Map of Nigerian Aquaculture Clusters")
    
    # Load data
    df = load_data()
    
    # Sidebar filters
    st.sidebar.title("Filter Options")
    
    # State filter
    states = ["All"] + sorted(df["State"].unique().tolist())
    selected_state = st.sidebar.selectbox("Select State", states)
    
    # Species filter
    species = ["All"] + sorted(df["Species"].unique().tolist())
    selected_species = st.sidebar.selectbox("Select Species", species)
    
    # Disease risk filter
    risk_levels = ["All"] + sorted(df["Disease_Risk"].unique().tolist())
    selected_risk = st.sidebar.selectbox("Select Disease Risk Level", risk_levels)
    
    # Map view options
    map_view = st.sidebar.radio(
        "Map View",
        ["Markers", "Heatmap", "Both"],
        index=0
    )
    
    # Filter data based on selections
    filtered_df = df.copy()
    
    if selected_state != "All":
        filtered_df = filtered_df[filtered_df["State"] == selected_state]
        
    if selected_species != "All":
        filtered_df = filtered_df[filtered_df["Species"] == selected_species]
        
    if selected_risk != "All":
        filtered_df = filtered_df[filtered_df["Disease_Risk"] == selected_risk]
    
    # Display stats
    st.sidebar.markdown("---")
    st.sidebar.subheader("Farm Statistics")
    st.sidebar.write(f"Total Farms Displayed: {len(filtered_df)}")
    
    # Count farms by state
    if len(filtered_df) > 0:
        # State stats
        state_counts = filtered_df["State"].value_counts().head(10)
        st.sidebar.write("Top 10 States:")
        for state, count in state_counts.items():
            st.sidebar.write(f"- {state}: {count}")
        
        # Species stats
        species_counts = filtered_df["Species"].value_counts()
        st.sidebar.markdown("---")
        st.sidebar.write("Species Distribution:")
        species_colors = {"Tilapia": "#3498db", "Catfish": "#2ecc71", "Mixed": "#e74c3c"}
        
        # Create species pie chart
        fig1, ax1 = plt.subplots(figsize=(4, 3))
        ax1.pie(species_counts, labels=species_counts.index, autopct='%1.1f%%',
                startangle=90, colors=[species_colors.get(s, "#95a5a6") for s in species_counts.index])
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        st.sidebar.pyplot(fig1)
        
        # Disease risk stats
        risk_counts = filtered_df["Disease_Risk"].value_counts()
        st.sidebar.markdown("---")
        st.sidebar.write("Disease Risk Levels:")
        risk_colors = {"Low": "#2ecc71", "Medium": "#f39c12", "High": "#e74c3c"}
        
        # Create risk pie chart
        fig2, ax2 = plt.subplots(figsize=(4, 3))
        ax2.pie(risk_counts, labels=risk_counts.index, autopct='%1.1f%%',
                startangle=90, colors=[risk_colors.get(r, "#95a5a6") for r in risk_counts.index])
        ax2.axis('equal')
        st.sidebar.pyplot(fig2)
    
    # Create maps based on view selection
    st.write("### Interactive Aquaculture Map")
    
    # Define risk color mapping
    risk_colors = {
        "Low": "green",
        "Medium": "orange",
        "High": "red"
    }
    
    # Create maps for different views
    if map_view == "Markers" or map_view == "Both":
        col1, col2 = st.columns([3, 1])
        with col1:
            # Create map with markers
            m_markers = folium.Map(location=[9.0765, 7.3986], zoom_start=6, tiles="OpenStreetMap")
            marker_cluster = MarkerCluster().add_to(m_markers)
            
            # Add markers to the map
            for idx, row in filtered_df.iterrows():
                # Create popup content
                popup_content = f"""
                <b>Farm:</b> {row['Farm_Name']}<br>
                <b>State:</b> {row['State']}<br>
                <b>LGA:</b> {row['LGA']}<br>
                <b>Species:</b> {row['Species']}<br>
                <b>Disease Risk:</b> {row['Disease_Risk']}<br>
                <b>Notes:</b> {row['Notes']}
                """
                
                # Add marker
                folium.Marker(
                    location=[row['Latitude'], row['Longitude']],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=folium.Icon(color=risk_colors.get(row['Disease_Risk'], 'blue')),
                ).add_to(marker_cluster)
                
            st.write("#### Farm Markers")
            folium_static(m_markers, width=800)
            
    if map_view == "Heatmap" or map_view == "Both":
        # Create heatmap
        m_heat = folium.Map(location=[9.0765, 7.3986], zoom_start=6, tiles="OpenStreetMap")
        
        # Prepare heatmap data
        heat_data = [[row['Latitude'], row['Longitude']] for _, row in filtered_df.iterrows()]
        
        # Add heatmap layer
        HeatMap(
            heat_data,
            radius=15,
            blur=10,
            gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}
        ).add_to(m_heat)
        
        st.write("#### Farm Density Heatmap")
        folium_static(m_heat, width=800)
    
    # Display data table
    st.write("### Aquaculture Farm Data")
    st.dataframe(filtered_df)
    
    # About section
    st.markdown("---")
    st.write("### About AquaMapNG")
    st.write("""
    AquaMapNG is an interactive web application that visualizes aquaculture clusters across Nigeria. 
    It aims to showcase the spatial distribution of fish farming activity by mapping fish farms, 
    aquaculture zones, species farmed, and disease risk levels.
    
    This project uses simulated data to demonstrate how GIS and data visualization can support smarter
    policy, disease monitoring, and resource allocation in Nigeria's aquaculture sector.
             
    By Kolawole Saheed
    """)

if __name__ == "__main__":
    main() 