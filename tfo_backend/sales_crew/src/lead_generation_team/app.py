#!/usr/bin/env python
import streamlit as st
import warnings
from crew import LeadGenerationTeam

# Suppress warnings
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Streamlit App
def main():
    st.title("Lead Generation Team")

    # Input from the user
    topic = st.text_input("Enter Lead Requirement", placeholder="Type your lead requirement here...")
    
    if st.button("Generate Leads"):
        if topic.strip():
            st.write(f"Running Lead Generation for {topic}")
            with st.spinner("Processing..."):
                run_crew(topic)
        else:
            st.error("Please enter a valid topic to proceed.")

def run_crew(topic):
    """
    Run the LeadGenerationTeam crew with the given topic and display results.
    """
    inputs = {'topic': topic}
    team = LeadGenerationTeam()
    
    # Run the process
    output = team.crew().kickoff(inputs=inputs)

    # Load and display the generated markdown files
    st.write("Generated Reports:")

    with open("report.md", "r") as file:
        st.subheader("Report")
        st.markdown(file.read())

    with open("qualified_leads_report.md", "r") as file:
        st.subheader("Qualified Leads")
        st.markdown(file.read())


if __name__ == "__main__":
    main()
