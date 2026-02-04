"""
Turns a job title → task list for the agent.
"""
def generate_tasks(goal: str):
    return [
        {"thought": "Research skills required", "tool": "skills"},
        {"thought": "Draft tailored resume",     "tool": "resume"},
        {"thought": "Draft tailored cover letter","tool": "cover"},
        {"thought": "Find matching job listings", "tool": "jobs"},
        {"thought": "Find related posts for this job", "tool": "posts"}
    ]
