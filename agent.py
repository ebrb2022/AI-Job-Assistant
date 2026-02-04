"""
ReAct loop for the Job Assistant.
"""
from typing import Callable, Dict, Any
from planner import generate_tasks
import tools
from typing import Callable, Dict, Any
from planner import generate_tasks
import tools


def parse_resume(resume_md):
    """Parse the Markdown resume into sections."""
    sections = {}
    current = None
    lines = resume_md.splitlines()
    
    for line in lines:
        line = line.strip()
        
        # skip those empty lines and code blocks
        if not line or line.startswith('```'):
            continue
            
        # checking for section headers to start a new section
        if line.startswith("## "):
            current = line.replace("##", "").strip()
            sections[current] = []

        # finds top-level header and treats it as contact info
        elif line.startswith("# "):
            current = "Contact"
            sections[current] = [line.replace("#", "").strip()]

        # add content to current section
        elif current:
            sections[current].append(line)
    
    for k in sections:
        sections[k] = "\n".join(sections[k]).strip()
    
    return sections


def parse_cover_letter(cover_md):
    """Turn the Markdown cover letter into sections."""
    sections = {}
    current = None
    lines = cover_md.splitlines()
    
    for line in lines:
        line = line.strip()
        
        if not line or line.startswith('```'):
            continue
        
        if line.startswith("## "):
            current = line.replace("##", "").strip()
            sections[current] = []

        elif current:
            sections[current].append(line)

        # Adds opening section if no header found
        elif not current:
            if "Opening" not in sections:
                sections["Opening"] = []
            sections["Opening"].append(line)
    
    # Join lines for each section
    for k in sections:
        sections[k] = "\n".join(sections[k]).strip()
    
    return sections


def run_agent(job_title: str, log: Callable[[str], None] = print):
    """
    Run the agent to generate job search materials
    
    Returns:
        Dict with keys: 'jobs', 'posts', 'resume', 'cover'
    """
    log(f"PLAN: Generating tasks for → {job_title}")
    tasks = generate_tasks(job_title)
    memory: Dict[str, Any] = {}

    for task in tasks:
        log(f"\nTHOUGHT: {task['thought']}")
        output = tools.use_tool(task["tool"], memory=memory, goal=job_title)
        
        # store output with consistent keys for app.py
        tool_name = task["tool"]
        memory[tool_name] = output
        
        log(f"OBSERVE: {str(output)[:600]}")

    # map tool outputs to expected keys for app.py
    result = {
        "jobs": memory.get("jobs", []),
        "posts": memory.get("posts", []),
        "resume": memory.get("resume", ""),
        "cover": memory.get("cover", ""),
    }

    log("\nFINISH.")
    return result