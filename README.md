
# AI Job Assistant

AI Job Assistant is an AI tool made to help users, **especially 4th year students**, find jobs, generate sample resumes, and create sample cover letters. It integrates modern generative AI with real-time job search data to make the job application process interesting and possibly more efficient.

## Link to Streamlit App
Go [here](https://ebrb2022-ai-job-assistant-app-r3mair.streamlit.app/) to access the the AI Job Assistant Streamlit app.

## Features
- **Task Planning:**  
  Break down the job search process into actionable tasks using the planner module.

- **Job Search Integration:**  
  Find matching job listings using the Google Jobs Scraper API (via RapidAPI).

- **Resume and Cover Letter Generation:**  
  Use ~~OpenAI's~~ Hugging Face API (I'm broke lol) to generate resumes and cover letters based on the job title and required skills.

- **Skill Extraction:**  
  Automatically extract key skills required for the desired job using generative AI.

- **Streamlit UI:**  
  A user-friendly interface that displays the agent's thought process and outputs in real-time.

- **Related Job Posts**
This AI bot also lists you job-related posts from the internet.

NOTE: THIS APP MIGHT NOT WORK WITHOUT THE API KEYS IF YOU DECIDE TO RUN THIS LOCALLY

## Installation

1. Create a virtual environment and install the required packages via requirements.txt:
```bash
pip install -r requirements.txt
```
2. Make .env file and add your API keys. To get the RAPID API KEY, get one from here: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch The Hugging Face API key and the SerpAPI key can be easily obtained after creating an account on their respective websites.


## Running the App

Start the Streamlit app using:

```bash
streamlit run app.py
```

Then view the app in your browser at the local URL provided by Streamlit.

## Overview

AI Job Assistant demonstrates the potential of integrated AI systems:
- **Planner Module:** Breaks the job search process into actionable tasks.
- **Tool Module:** Uses APIs to gather job data, generate resumes, and create cover letters.
- **ReAct Loop:** Displays each step (thought, action, and observation) in a transparent, interactive UI.

## License

Distributed under the MIT License. See `LICENSE` for more information.
