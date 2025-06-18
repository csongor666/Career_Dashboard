# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 11:13:00 2025

@author: BAC5MC
"""

import streamlit as st
import pandas as pd
import datetime
import textwrap
import networkx as nx
from pyvis.network import Network
import plotly.express as px
import plotly.figure_factory as ff
import pydeck as pdk
import streamlit.components.v1 as components
import json

# Function to calculate the number of months between two dates
def calculate_months(start, end):
    start_date = datetime.datetime.strptime(start, "%Y-%m")
    if end == "Present":
        end_date = datetime.datetime.now()
    else:
        end_date = datetime.datetime.strptime(end, "%Y-%m")
    total_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
    delta_years = total_months // 12
    delta_months = total_months % 12
    return total_months, delta_years, delta_months

st.title("Upload your CV")

# Fájl feltöltése
uploaded_file = st.file_uploader("Use JSON format", type="json")

if uploaded_file is not None:
    # JSON beolvasása
    data = json.load(uploaded_file)
    
# # Sample data
# data = {
#     "name": "Csongor Báthory",
#     "summary": "Data Scientist position",
#     "timeline": [
#         {
#             "title": "Air Quality Expert",
#             "company": "National Inspectorate for Environment and Nature",
#             "location": "Hungary",
#             "city": "Budapest",
#             "start": "2013-12",
#             "end": "2015-03",
#             "skills": ["Interpretation of laws and regulations", "Government environment", "Team working"]
#         },
#         {
#             "title": "Environmental Engineering",
#             "company": "Vibrocomp Kft",
#             "location": "Hungary",
#             "city": "Budapest",
#             "start": "2015-03",
#             "end": "2016-09",
#             "skills": ["Air pollution modelling", "Impact study compilation"]
#         },
#         {
#             "title": "Air Quality Expert",
#             "company": "Vibrocomp FZO Middle East",
#             "location": "United Arab Emirates",
#             "city": "Dubai",
#             "start": "2016-09",
#             "end": "2017-09",
#             "skills": ["Impact study compilation", "Air quality measurement", "Project management", "Team working"]
#         },
#         {
#             "title": "Research associate",
#             "company": "University of Miskolc",
#             "location": "Hungary",
#             "city": "Miskolc",
#             "start": "2018-06",
#             "end": "2021-12",
#             "skills": ["Raspberry Pi", "Matlab", "Project management", "Python", "Data analyzing", "Neural network", "Data visualization", "Air pollution modelling", "Air quality measurement"]
#         },
#         {
#             "title": "Test Engineer",
#             "company": "Robert Bosch Body and Energy Systems Ltd",
#             "location": "Hungary",
#             "city": "Miskolc",
#             "start": "2022-01",
#             "end": "Present",
#             "skills": ["Noise and Vibration measurement", "Artemis", "Data analyzing", "Data visualization", "Python", "LabView basics", "Github", "Team working"]
#         },
#     ]
# }

    # Helper function to wrap text
    def wrap_text(text, width=15):
        return '\n'.join(textwrap.wrap(text, width))
    
    # Streamlit app
    st.title("Career Dashboard")
    st.header(f"{data['name']} - {data['summary']}")
    
    st.subheader("Timeline of Positions")
    
    # Create the fourth visualization: Timeline of Positions
    timeline_df = pd.DataFrame(data['job_list'])
    timeline_df['start'] = pd.to_datetime(timeline_df['start'])
    
    # Replace 'Present' with today's date
    timeline_df['end'] = timeline_df['end'].replace('Present', datetime.datetime.today().strftime('%Y-%m'))
    timeline_df['end'] = pd.to_datetime(timeline_df['end'])
    
    # Plot the timeline using Plotly
    # fig = px.timeline(timeline_df, x_start="start", x_end="end", y="title", color="company", text="company")
    fig = px.timeline(timeline_df, x_start="start", x_end="end", y="title", color="company")
    # fig.update_layout(title='Timeline of Positions', xaxis_title='Date', yaxis_title='Position')
    fig.update_layout(xaxis_title='Date', yaxis_title='Position')
    
    st.plotly_chart(fig)
    
    st.subheader("Timeline of Skills")
    # Create the third visualization: Timeline of Skills
    # Convert "Present" to current date
    current_date = datetime.datetime.now().strftime("%Y-%m")
    for job in data['job_list']:
        if job['end'] == "Present":
            job['end'] = current_date
    
    # Create a DataFrame for the timeline
    timeline_data = []
    for job in data['job_list']:
        for skill in job['skills']:
            timeline_data.append({
                'Skill': skill,
                'Company' : job['company'],
                'Start': pd.to_datetime(job['start']),
                'End': pd.to_datetime(job['end'])
            })
    
    df_timeline = pd.DataFrame(timeline_data)
    df_timeline = df_timeline.sort_values('Skill', ascending=True)
    df_timeline = df_timeline.rename(columns={"Skill": "Task", "Start": "Start", "End": "Finish"})
    
    import colorsys
    
    def generate_colors(n):
        """Generate n visually distinct colors using HSL color space."""
        colors = []
        for i in range(n):
            hue = i / n
            lightness = (50 + 10 * (i % 2)) / 100  # Alternate lightness for better distinction
            saturation = 0.9  # High saturation for vivid colors
            rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
            hex_color = "#{:02x}{:02x}{:02x}".format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
            colors.append(hex_color)
        return colors
    
    # Generate 20 unique colors
    unique_colors = generate_colors(20)
    
    # Generate unique colors for each skill
    unique_skills = df_timeline['Task'].unique()
    # colors = px.colors.qualitative.Plotly[:len(unique_skills)]
    
    # Create a dictionary to map skills to colors
    skill_color_map = {skill: unique_colors[i] for i, skill in enumerate(unique_skills)}
    
    # Plot the timeline using Plotly
    fig = ff.create_gantt(df_timeline, index_col='Task', show_colorbar=False,
                          group_tasks=True,
                          colors=skill_color_map,
                          task_names=df_timeline['Company'],
                          show_hover_fill=True)
    # fig.update_layout(title='Timeline of Skills', xaxis_title='Time', yaxis_title='Skills')
    fig.update_layout(title='', xaxis_title='Time', yaxis_title='Skills')
    st.plotly_chart(fig)
    
    
    # Create the first network: Positions and Skills
    G1 = nx.Graph()
    
    for job in data['job_list']:
        job_title = wrap_text(f"{job['title']}")
        G1.add_node(job_title, color="rgba(135, 206, 235,1)")
        for skill in job['skills']:
            wrapped_skill = wrap_text(skill)
            G1.add_node(wrapped_skill, color='lightgreen')
            G1.add_edge(job_title, wrapped_skill)
    
    # Create PyVis network for Positions and Skills
    net1 = Network(height='600px', width='100%', bgcolor='#ffffff', font_color='black')
    # Step 4: Use the Json Dictionary that sets the options to specify that I want the color of the node to change to red when clicked on
    
    
    
    for node, data_ in G1.nodes(data=True):
        net1.add_node(
            node,
            color={
                'background': data_['color'],
                'border': '#464646'
            },
            borderWidth=1,
            borderWidthSelected=1
        )
    for edge in G1.edges():
        net1.add_edge(edge[0], edge[1])
    
    # net1.show("positions_skills.html")
    
    # Generate the network and get the HTML content
    html_content = net1.generate_html()

    st.subheader("Positions and Skills Network")
    # components.html(open("positions_skills.html").read(), height=600)
    components.html(html_content, height=600)
    
    # Create the second network: Skills Co-occurrence
    G2 = nx.Graph()
    
    skill_pairs = {}
    for job in data['job_list']:
        for i, skill1 in enumerate(job['skills']):
            wrapped_skill1 = wrap_text(skill1)
            for skill2 in job['skills'][i + 1:]:
                wrapped_skill2 = wrap_text(skill2)
                if (wrapped_skill1, wrapped_skill2) in skill_pairs:
                    skill_pairs[(wrapped_skill1, wrapped_skill2)] += 1
                else:
                    skill_pairs[(wrapped_skill1, wrapped_skill2)] = 1
    
    for (skill1, skill2), weight in skill_pairs.items():
        G2.add_node(skill1, color='lightgreen')
        G2.add_node(skill2, color='lightgreen')
        G2.add_edge(skill1, skill2, weight=weight)
    
    # Create PyVis network for Skills Co-occurrence
    net2 = Network(height='600px', width='100%', bgcolor='#ffffff', font_color='black')
    for node, data_1 in G2.nodes(data=True):
        net2.add_node(
            node,
            color={
                'background': data_1['color'],
                'border': '#464646'
            },
            borderWidth=1,
            borderWidthSelected=1,
            size=17,
            font={'size': 10}
        )
    for edge in G2.edges(data=True):
        net2.add_edge(edge[0], edge[1], value=edge[2]['weight'], color="#898989")
    net2.set_options("""
{
  "physics": {
    "forceAtlas2Based": {
      "gravitationalConstant": -50,
      "centralGravity": 0.01,
      "springLength": 100,
      "springConstant": 0.08
    },
    "maxVelocity": 50,
    "solver": "forceAtlas2Based",
    "timestep": 0.35,
    "stabilization": { "iterations": 150 }
  }
}
""")


    # net2.show_buttons()
    # net2.show("skills_cooccurrence.html")
    html_content2 = net1.generate_html()
    st.subheader("Skills Co-occurrence Network")
    # components.html(open("skills_cooccurrence.html").read(), height=600)
    components.html(html_content2, height=600)
    

    
    # Calculate the total time spent in each city
    city_time = {}
    for job in data["job_list"]:
        city = job["city"]
        total_months, delta_years, delta_months = calculate_months(job["start"], job["end"])
        if city in city_time:
            city_time[city]["total_months"] += total_months
            city_time[city]["delta_years"] += delta_years
            city_time[city]["delta_months"] += delta_months
        else:
            city_time[city] = {
                "total_months": total_months,
                "delta_years": delta_years,
                "delta_months": delta_months
            }
    
    # Convert the city_time dictionary to a DataFrame
    city_time_df = pd.DataFrame([
        {"City": city, "Months": data["total_months"], "Delta Years": data["delta_years"], "Delta Months": data["delta_months"]}
        for city, data in city_time.items()
    ])
    
    
    # Define the coordinates for the cities
    city_coordinates = {
        "Budapest": [47.4979, 19.0402],
        "Dubai": [25.276987, 55.296249],
        "Miskolc": [48.1031, 20.7784]
    }
    
    # Add coordinates to the DataFrame
    city_time_df["Latitude"] = city_time_df["City"].apply(lambda x: city_coordinates[x][0])
    city_time_df["Longitude"] = city_time_df["City"].apply(lambda x: city_coordinates[x][1])
    
    # Create a PyDeck chart 37.86/35.60
    view_state = pdk.ViewState(latitude=37.86, longitude=35.60, zoom=3, pitch=50)
    
    layer = pdk.Layer(
        "ColumnLayer",
        data=city_time_df,
        get_position=["Longitude", "Latitude"],
        get_elevation="Months",
        elevation_scale=7000,
        radius=55000,
        get_color="[200, 30, 0, 160]",
        pickable=True,
        auto_highlight=True,
    )
    
    r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{City}\n{Delta Years} year {Delta Months} month"})
    # r.to_html("city_time_chart.html")
    html_content_3 = r.to_html(as_string=True, notebook_display=False)

    print("PyDeck chart has been created and saved as city_time_chart.html.")
    
    # net2.show("skills_cooccurrence.html")
    st.subheader("Time spent on location")
    components.html(html_content_3, height=600)
    
    
    st.subheader("Raw data")
    
    st.json(
            data,
            expanded=2,
            )
