import sys
import datetime
import streamlit as st
from crewai import Crew, Process, Task, Agent
from browserbase import browserbase
from kayak import kayak_search  # Changed from 'kayak' to 'kayak_search'
from dotenv import load_dotenv
import time

load_dotenv()  # take environment variables from .env.

# Set page configuration
st.set_page_config(
    page_title="FlightFinder Pro",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 2rem;
    }
    .search-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    .result-container {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-top: 2rem;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
        padding: 0.5rem 2rem;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #1565C0;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown('<div class="main-header">✈️ FlightFinder Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Find the best flight deals with AI-powered search</div>', unsafe_allow_html=True)

# Search container
st.markdown('<div class="search-container">', unsafe_allow_html=True)
search_query = st.text_input("", placeholder="Enter your flight search (e.g., flights from SF to New York on November 5th)", key="search_input")
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    search_button = st.button("Find Flights ✈️", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Function to perform flight search
def search_flights(query):
    flights_agent = Agent(
        role="Flights",
        goal="Search flights",
        backstory="I am an agent that can search for flights.",
        tools=[kayak_search, browserbase],  # Changed from 'kayak' to 'kayak_search'
        allow_delegation=False,
    )

    summarize_agent = Agent(
        role="Summarize",
        goal="Summarize content",
        backstory="I am an agent that can summarize text.",
        allow_delegation=False,
    )

    output_search_example = """
    Here are our top 5 flights from San Francisco to New York on 21st September 2024:
    1. Delta Airlines: Departure: 21:35, Arrival: 03:50, Duration: 6 hours 15 minutes, Price: $125, Details: https://www.kayak.com/flights/sfo/jfk/2024-09-21/12:45/13:55/2:10/delta/airlines/economy/1
    """

    search_task = Task(
        description=(
            "Search flights according to criteria {request}. Current year: {current_year}"
        ),
        expected_output=output_search_example,
        agent=flights_agent,
    )

    output_providers_example = """
    Here are our top 5 picks from San Francisco to New York on 21st September 2024:
    1. Delta Airlines:
        - Departure: 21:35
        - Arrival: 03:50
        - Duration: 6 hours 15 minutes
        - Price: $125
        - Booking: [Delta Airlines](https://www.kayak.com/flights/sfo/jfk/2024-09-21/12:45/13:55/2:10/delta/airlines/economy/1)
        ...
    """

    search_booking_providers_task = Task(
        description="Load every flight individually and find available booking providers",
        expected_output=output_providers_example,
        agent=flights_agent,
    )

    crew = Crew(
        agents=[flights_agent, summarize_agent],
        tasks=[search_task, search_booking_providers_task],
        max_rpm=100,
        verbose=False,  # Changed to False for production UI
        planning=True,
    )

    result = crew.kickoff(
        inputs={
            "request": query,
            "current_year": datetime.date.today().year,
        }
    )

    return result

# Handle search button click
if search_button and search_query:
    st.markdown('<div class="result-container">', unsafe_allow_html=True)
    with st.spinner("🔍 Searching for the best flights... This may take a minute..."):
        try:
            # Add a small delay to show the spinner (optional)
            time.sleep(1)
            results = search_flights(search_query)
            
            # Display results
            st.markdown("### 🎉 Flight Search Results")
            st.markdown(results)
            
            # Add additional helpful information
            st.markdown("---")
            st.markdown("### 💡 Booking Tips")
            st.info("""
            - Prices may change based on availability
            - Consider booking directly with airlines for better customer service
            - Check baggage policies before booking
            """)
            
        except Exception as e:
            st.error(f"An error occurred during the search: {str(e)}")
            st.info("Please try again with a more specific search query.")
    st.markdown('</div>', unsafe_allow_html=True)
elif search_button:
    st.warning("Please enter a search query first.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>© 2024 FlightFinder Pro | Powered by AI | All rights reserved</p>
</div>
""", unsafe_allow_html=True)