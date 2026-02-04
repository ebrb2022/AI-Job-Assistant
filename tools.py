import os, re, requests
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

client = InferenceClient(token=os.getenv("HF_TOKEN")) # the Hugging Face Inference API client
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY") 
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def generate_content(prompt, task_type="general", max_tokens=None):
    """Generate content with task-specific parameters using Hugging Face Inference API"""
    
    configs = {
        'resume': {
            'max_tokens': 2000, # to get detailed resumes
            'temperature': 0.3, # lower temperature for more focused output (less randomness)
            'top_p': 0.85, # more deterministic output
        },
        'cover_letter': {
            'max_tokens': 1500, # still sufficient for a detailed cover letter
            'temperature': 0.4, # slightly higher temperature for more creative output
            'top_p': 0.9, # slightly more creative output
        },
        'skills': {
            'max_tokens': 200, # just enough for a concise list of skills
            'temperature': 0.2, # more focused on the terms
            'top_p': 0.8, # more deterministic output
        },
        'general': {
            'max_tokens': 1000, # the default maximum number of tokens for general tasks, not too long
            'temperature': 0.5, # default temperature for general tasks, which is a balance between creativity and focus
            'top_p': 0.9, # for the most diverse output
        }
    }
    

    config = configs.get(task_type, configs['general'])
    if max_tokens:
        config['max_tokens'] = max_tokens

    # format as chat message
    messages = [
        {"role": "system", "content": "You are a professional career advisor and resume writer."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        # Call Hugging Face Inference API, using this llama model because it's good at following instructions
        response = client.chat_completion(
            model="meta-llama/Llama-3.2-3B-Instruct",
            messages=messages,
            max_tokens=config['max_tokens'],
            temperature=config['temperature'],
            top_p=config['top_p'],
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Error generating content: {e}")
        return f"Error: Unable to generate content. Please try again."


# TOOL FUNCTS

def required_skills(job: str) -> list[str]:
    """extract required skills for a job role"""
    prompt = (
        f"List 8-12 core skills or technologies commonly required for a {job} position. "
        "Return ONLY a comma-separated list with no other text. "
        "Example format: Python, SQL, Data Analysis, Excel, Tableau, Machine Learning"
    )
    raw = generate_content(prompt, task_type='skills')
    
    # parse comma-separated or newline-separated skills
    skills = [s.strip() for s in re.split(r",|\n|•|-", raw) if s.strip()]
    # clean up any numbering or bullets
    skills = [re.sub(r'^\d+[\.)]\s*', '', s) for s in skills]
    return skills[:12]  # Limit to 12 skills


def sample_resume(job: str, skills: list[str]) -> str:
    """generate a professional resume"""
    skills_list = ', '.join(skills[:8])
    
    prompt = f"""Create a professional one-page resume in clean Markdown format for a {job} position.

Focus on these key skills: {skills_list}

Structure (use ## for headers):

## Contact Information
John Doe | john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe

## Professional Summary
Write 2-3 sentences highlighting expertise as a {job} with experience in {skills[0]}, {skills[1] if len(skills) > 1 else 'related technologies'}, and other key skills.

## Key Skills
List 6-8 relevant skills as bullet points, including:
- {skills[0]}
- {skills[1] if len(skills) > 1 else 'Additional skill'}
- {skills[2] if len(skills) > 2 else 'Additional skill'}
- And 3-5 more relevant skills

## Work Experience

**Senior {job}** | ABC Corporation | 2021 - Present
- Achievement demonstrating {skills[0]} expertise with quantifiable results
- Technical accomplishment showcasing problem-solving abilities
- Leadership or collaboration example

**{job}** | XYZ Company | 2018 - 2021
- Key accomplishment using {skills[1] if len(skills) > 1 else 'technical skills'}
- Process improvement with measurable impact
- Cross-functional collaboration example

## Education
Bachelor of Science in Computer Science
State University | Graduated 2018

Keep it professional and concise. Use proper Markdown formatting with ## for section headers."""

    return generate_content(prompt, task_type='resume')


def sample_cover(job: str, skills: list[str]) -> str:
    """Generate a professional cover letter"""
    skills_list = ', '.join(skills[:5])
    
    prompt = f"""Write a professional cover letter for a {job} position (250-300 words).

Highlight these skills: {skills_list}

Structure:

**Paragraph 1 (Opening):**
Express genuine enthusiasm for the {job} position. Mention 1-2 key qualifications that make you an ideal candidate.

**Paragraph 2 (Body):**
Highlight 2-3 relevant skills and experiences:
- Specific example demonstrating {skills[0]} expertise
- Accomplishment showing {skills[1] if len(skills) > 1 else 'technical proficiency'}
- Brief mention of {skills[2] if len(skills) > 2 else 'additional relevant skills'}

**Paragraph 3 (Closing):**
Express enthusiasm for contributing to the team, mention you look forward to discussing your qualifications further, and thank them for their consideration.

Sincerely,
John Doe

Be professional, concise, and personable. Use plain text paragraphs, no special formatting or markdown."""

    return generate_content(prompt, task_type='cover_letter')


def search_jobs(query: str, location: str = "") -> list[dict]:
    """Search for job listings using RapidAPI"""
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "jsearch.p.rapidapi.com",
    }
    search_query = f"{query}{' in ' + location if location else ''}"
    
    querystring = {
        "query": search_query,
        "page": "1",
        "num_pages": "1",
        "country": "us",
        "date_posted": "all"
    }

    try:
        resp = requests.get(url, headers=headers, params=querystring, timeout=10)
        
        if resp.status_code == 404:
            print(f"Error: Invalid endpoint - {resp.json().get('message', 'Not found')}")
            return _no_jobs(query, location)
        elif resp.status_code == 401:
            print("Error: Invalid API key or unauthorized access")
            return _no_jobs(query, location)
        elif resp.status_code == 403:
            print("Error: API access forbidden")
            return _no_jobs(query, location)
        
        if resp.status_code != 200 or not resp.text.strip():
            print(f"→ Non-200 ({resp.status_code}) or empty response")
            return _no_jobs(query, location)
            
        data = resp.json()
        lst = data.get("data", [])
        
        if not isinstance(lst, list):
            print("→ Response format invalid, expected list")
            return _no_jobs(query, location)
        
        jobs = []
        for item in lst[:10]:
            jobs.append({
                "title": item.get("job_title", "Unknown Position"),
                "company": item.get("employer_name", "Unknown Company"),
                "location": item.get("job_location", "Location not specified"),
                "description": item.get("job_description", "No description available"),
                "url": item.get("job_apply_link", ""),
                "date_posted": item.get("job_posted_at_datetime_utc", "")[:10] if item.get("job_posted_at_datetime_utc") else "",
                "salary": item.get("job_salary", "")
            })
        
        return jobs if jobs else _no_jobs(query, location)
        
    except requests.exceptions.Timeout:
        print("Error: Request timed out")
        return _no_jobs(query, location)
    except Exception as e:
        print(f"Error searching for jobs: {e}")
        return _no_jobs(query, location)


def _no_jobs(query: str, location: str = "") -> list[dict]:
    """Return empty job result"""
    return [{
        "title": f"No jobs found for '{query}'{' in ' + location if location else ''}",
        "company": "",
        "location": location if location else "Try different search terms",
        "description": "No job listings matched your search criteria. Try:\n- Broadening your search terms\n- Different locations\n- Related job titles",
        "url": "",
        "date_posted": "",
        "salary": ""
    }]


def search_posts(job_title, company="", location=""):
    """Search for industry posts and discussions using SerpAPI (still uses Google Search API) instead of Google CSE since it's denying me permission to use it :(."""
    attempts = []
    if job_title and company and location:
        attempts.append([job_title, company, location])
    if job_title and company:
        attempts.append([job_title, company])
    if job_title and location:
        attempts.append([job_title, location])
    if job_title:
        attempts.append([job_title])

    synonyms = "(career OR trends OR tips OR advice OR news OR discussion)"

    for terms in attempts:
        query = " ".join(terms + [synonyms])

        url = "https://serpapi.com/search"
        params = {
            "engine": "google",
            "q": query,
            "num": 5,
            "api_key": SERPAPI_KEY
        }

        #  try to fetch search results from SerpAPI
        try:
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()

            if "error" in data:
                print("SerpAPI Error:", data["error"])
                continue
            posts = []
            for item in data.get("organic_results", []):
                posts.append({
                    "title": item.get("title", "No title"),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "No description available")
                })

            if posts:
                return posts

        except Exception as e:
            print(f"Error searching SerpAPI: {e}")
            continue

    return []


# THE HANDYMAN
def use_tool(name, *, memory, goal):
    """ Use specified tool to perform task based on the category and update memory  """
    
    if name == "skills":
        memory["skills"] = required_skills(goal)
        return memory["skills"]

    if name == "resume":
        skills = memory.get("skills") or required_skills(goal)
        memory["resume"] = sample_resume(goal, skills)
        return memory["resume"]

    if name == "cover":
        skills = memory.get("skills") or required_skills(goal)
        memory["cover"] = sample_cover(goal, skills)
        return memory["cover"]
        
    if name == "jobs":
        location = memory.get("location", "")
        memory["jobs"] = search_jobs(goal, location)
        return memory["jobs"]
    
    if name == "posts":
        job = goal
        company = memory.get("company", "")
        location = memory.get("location", "")
        memory["posts"] = search_posts(job, company, location)
        return memory["posts"]

    raise ValueError(f"Unknown tool: {name}")