# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 11:13:00 2025
Modified: hard-coded CV + button controlled dashboard
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
import requests
import colorsys


# -----------------------------------------------------------------------------
# Hard-coded CV data
# -----------------------------------------------------------------------------
CV_DATA = {
    "name": "Csongor Báthory",
    "summary": "Calibration- and Testing Process development engineer",
    "job_list": [
        {
            "title": "Air Quality Expert",
            "company": "National Inspectorate for Environment and Nature",
            "location": "Hungary",
            "city": "Budapest",
            "start": "2013-12",
            "end": "2015-03",
            "skills": [
                "Interpretation of laws and regulations",
                "Government environment",
                "Team working",
            ],
        },
        {
            "title": "Environmental Engineering",
            "company": "Vibrocomp Kft",
            "location": "Hungary",
            "city": "Budapest",
            "start": "2015-03",
            "end": "2016-09",
            "skills": [
                "Air pollution modelling",
                "Impact study compilation",
            ],
        },
        {
            "title": "Air Quality Expert",
            "company": "Vibrocomp FZO Middle East",
            "location": "United Arab Emirates",
            "city": "Dubai",
            "start": "2016-09",
            "end": "2017-09",
            "skills": [
                "Impact study compilation",
                "Air quality measurement",
                "Project management",
                "Team working",
            ],
        },
        {
            "title": "Research associate",
            "company": "University of Miskolc",
            "location": "Hungary",
            "city": "Miskolc",
            "start": "2018-06",
            "end": "2021-12",
            "skills": [
                "Raspberry Pi",
                "Matlab",
                "Project management",
                "Python",
                "Data analyzing",
                "Neural network",
                "Data visualization",
                "Air pollution modelling",
                "Air quality measurement",
            ],
        },
        {
            "title": "Test Engineer",
            "company": "Robert Bosch Body and Energy Systems Ltd",
            "location": "Hungary",
            "city": "Miskolc",
            "start": "2022-01",
            "end": "Present",
            "skills": [
                "Noise and Vibration measurement",
                "Artemis",
                "Data analyzing",
                "Data visualization",
                "Python",
                "LabView basics",
                "Github",
                "Team working",
            ],
        },
    ],
}


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------
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


def wrap_text(text, width=15):
    return "\n".join(textwrap.wrap(text, width))


def generate_colors(n):
    """Generate n visually distinct colors using HSL color space."""
    colors = []
    for i in range(n):
        hue = i / n
        lightness = (50 + 10 * (i % 2)) / 100
        saturation = 0.9
        rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
        hex_color = "#{:02x}{:02x}{:02x}".format(
            int(rgb[0] * 255),
            int(rgb[1] * 255),
            int(rgb[2] * 255),
        )
        colors.append(hex_color)
    return colors


def get_coordinates(city):
    url = f"https://nominatim.openstreetmap.org/search?city={city}&format=json"
    response = requests.get(url, headers={"User-Agent": "streamlit-app"})
    if response.status_code == 200 and response.json():
        result = response.json()[0]
        return float(result["lat"]), float(result["lon"])
    return None


# -----------------------------------------------------------------------------
# Streamlit app
# -----------------------------------------------------------------------------
st.title("Career Dashboard")

if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False

if st.button(
    "CV of Csongor Báthory",
    type="primary",
    use_container_width=True,
):
    st.session_state.show_dashboard = True

if st.session_state.show_dashboard:
    # Copy the hard-coded data so the original CV_DATA is not modified by the app
    data = {
        "name": CV_DATA["name"],
        "summary": CV_DATA["summary"],
        "job_list": [job.copy() for job in CV_DATA["job_list"]],
    }

    st.header(f"{data['name']} - {data['summary']}")

    # -------------------------------------------------------------------------
    # Timeline of Positions
    # -------------------------------------------------------------------------
    st.subheader("Timeline of Positions")

    timeline_df = pd.DataFrame(data["job_list"])
    timeline_df["start"] = pd.to_datetime(timeline_df["start"])
    timeline_df["end"] = timeline_df["end"].replace(
        "Present",
        datetime.datetime.today().strftime("%Y-%m"),
    )
    timeline_df["end"] = pd.to_datetime(timeline_df["end"])

    fig = px.timeline(
        timeline_df,
        x_start="start",
        x_end="end",
        y="title",
        color="company",
    )
    fig.update_layout(xaxis_title="Date", yaxis_title="Position")
    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------------------------------
    # Timeline of Skills
    # -------------------------------------------------------------------------
    st.subheader("Timeline of Skills")

    current_date = datetime.datetime.now().strftime("%Y-%m")
    for job in data["job_list"]:
        if job["end"] == "Present":
            job["end"] = current_date

    timeline_data = []
    for job in data["job_list"]:
        for skill in job["skills"]:
            timeline_data.append(
                {
                    "Skill": skill,
                    "Company": job["company"],
                    "Start": pd.to_datetime(job["start"]),
                    "End": pd.to_datetime(job["end"]),
                }
            )

    df_timeline = pd.DataFrame(timeline_data)
    df_timeline = df_timeline.sort_values("Skill", ascending=True)
    df_timeline = df_timeline.rename(
        columns={"Skill": "Task", "Start": "Start", "End": "Finish"}
    )

    unique_skills = df_timeline["Task"].unique()
    unique_colors = generate_colors(max(len(unique_skills), 1))
    skill_color_map = {skill: unique_colors[i] for i, skill in enumerate(unique_skills)}

    fig = ff.create_gantt(
        df_timeline,
        index_col="Task",
        show_colorbar=False,
        group_tasks=True,
        colors=skill_color_map,
        task_names=df_timeline["Company"],
        show_hover_fill=True,
    )
    fig.update_layout(title="", xaxis_title="Time", yaxis_title="Skills")
    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------------------------------
    # Positions and Skills Network
    # -------------------------------------------------------------------------
    G1 = nx.Graph()

    for job in data["job_list"]:
        job_title = wrap_text(f"{job['title']}")
        G1.add_node(job_title, color="rgba(135, 206, 235,1)")
        for skill in job["skills"]:
            wrapped_skill = wrap_text(skill)
            G1.add_node(wrapped_skill, color="lightgreen")
            G1.add_edge(job_title, wrapped_skill)

    net1 = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")

    for node, data_ in G1.nodes(data=True):
        net1.add_node(
            node,
            color={
                "background": data_["color"],
                "border": "#464646",
            },
            borderWidth=1,
            borderWidthSelected=1,
        )

    for edge in G1.edges():
        net1.add_edge(edge[0], edge[1])

    html_content = net1.generate_html()

    st.subheader("Positions and Skills Network")
    components.html(html_content, height=600)

    # -------------------------------------------------------------------------
    # Skills Co-occurrence Network
    # -------------------------------------------------------------------------
    G2 = nx.Graph()

    skill_pairs = {}
    for job in data["job_list"]:
        for i, skill1 in enumerate(job["skills"]):
            wrapped_skill1 = wrap_text(skill1)
            for skill2 in job["skills"][i + 1:]:
                wrapped_skill2 = wrap_text(skill2)
                if (wrapped_skill1, wrapped_skill2) in skill_pairs:
                    skill_pairs[(wrapped_skill1, wrapped_skill2)] += 1
                else:
                    skill_pairs[(wrapped_skill1, wrapped_skill2)] = 1

    for (skill1, skill2), weight in skill_pairs.items():
        G2.add_node(skill1, color="lightgreen")
        G2.add_node(skill2, color="lightgreen")
        G2.add_edge(skill1, skill2, weight=weight)

    net2 = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")

    for node, data_1 in G2.nodes(data=True):
        net2.add_node(
            node,
            color={
                "background": data_1["color"],
                "border": "#464646",
            },
            borderWidth=1,
            borderWidthSelected=1,
            size=17,
            font={"size": 10},
        )

    for edge in G2.edges(data=True):
        net2.add_edge(edge[0], edge[1], value=edge[2]["weight"], color="#898989")

    net2.set_options(
        """
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
        """
    )

    html_content2 = net2.generate_html()

    st.subheader("Skills Co-occurrence Network")
    components.html(html_content2, height=600)

    # -------------------------------------------------------------------------
    # Time spent on location
    # -------------------------------------------------------------------------
    city_time = {}
    for job in data["job_list"]:
        city = job["city"]
        total_months, delta_years, delta_months = calculate_months(
            job["start"],
            job["end"],
        )
        if city in city_time:
            city_time[city]["total_months"] += total_months
            city_time[city]["delta_years"] += delta_years
            city_time[city]["delta_months"] += delta_months
        else:
            city_time[city] = {
                "total_months": total_months,
                "delta_years": delta_years,
                "delta_months": delta_months,
            }

    city_time_df = pd.DataFrame(
        [
            {
                "City": city,
                "Months": city_data["total_months"],
                "Delta Years": city_data["delta_years"],
                "Delta Months": city_data["delta_months"],
            }
            for city, city_data in city_time.items()
        ]
    )

    cities = set(job["city"] for job in data["job_list"])

    city_coordinates = {}
    for city in cities:
        coords = get_coordinates(city)
        if coords:
            city_coordinates[city] = coords

    city_time_df["Latitude"] = city_time_df["City"].apply(lambda x: city_coordinates[x][0])
    city_time_df["Longitude"] = city_time_df["City"].apply(lambda x: city_coordinates[x][1])

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

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{City}\n{Delta Years} year {Delta Months} month"},
    )
    html_content_3 = r.to_html(as_string=True, notebook_display=False)

    st.subheader("Time spent on location")
    components.html(html_content_3, height=600)

    # -------------------------------------------------------------------------
    # Raw data
    # -------------------------------------------------------------------------
    st.subheader("Raw data")
    st.json(data, expanded=2)

else:
    st.info('Click the "CV of Csongor Báthory" button to open the dashboard.')
