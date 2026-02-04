import streamlit as st
from dotenv import load_dotenv
from agent import run_agent
from agent import parse_resume
from agent import parse_cover_letter
import re

load_dotenv()


st.set_page_config(page_title="Job Assistant", layout="wide")
st.title("AI Job Assistant")

def clean_text(text):
    if not isinstance(text, str):
        return text
    text = text.replace('\n', ' ').replace('\r', ' ') # replaces \n and \r with space
    text = re.sub(r'\s+', ' ', text) # replaces multiple spaces with a single space
    return text.strip()

job = st.text_input("🔎︎ Desired Job Title", placeholder="e.g., Data Analyst, Software Engineer")

if st.button("Generate") and job.strip():
    trace = st.empty()
    buf = []

    def logger(line):
        buf.append(line)
        trace.text_area("Agent Trace", "\n".join(buf), height=300)

    memory = run_agent(job, log=logger)

    st.success("Job search completed! Here are the results:")
    
    # JOB LISTINGS
    if "jobs" in memory and memory["jobs"]:
        st.markdown("## 🔎︎ Job Listings")
        for i, job_item in enumerate(memory["jobs"]):
            title = clean_text(job_item['title'])
            company = clean_text(job_item['company'])
            location = clean_text(job_item['location'])
            salary = clean_text(job_item.get('salary', ''))
            description = clean_text(job_item['description'][:300] + "...")
            
            with st.expander(f"{i+1}. {title} at {company}"):
                st.markdown(f"### {title}", unsafe_allow_html=True) 
                st.write(f"**Company:** {company}")
                st.write(f"**Location:** {location}")
                if job_item.get('date_posted'):
                    st.write(f"**Posted:** {job_item['date_posted']}")
                if salary:
                    st.write(f"**Salary:** {salary}")
                st.write(description)
                if job_item.get('url'):
                    st.markdown(f"[🔗 Apply Here]({job_item['url']})")
    
    # NEWS AND ARTICLES
    if "posts" in memory and memory["posts"]:
        st.markdown("---")
        st.markdown("## 📰 Industry News & Career Resources")
        st.caption(f"Recent articles and resources related to {job}")
        
        for i, post in enumerate(memory["posts"], 1):
            with st.container():
                col1, col2 = st.columns([1, 20])
                
                with col1:
                    st.markdown(f"**{i}.**")
                
                with col2:
                    # Title as clickable link
                    st.markdown(f"### [{post['title']}]({post['link']})")
                    
                    # Snippet/description
                    if post.get('snippet'):
                        st.write(post['snippet'])
                    
                    # Link btn
                    st.markdown(f"🔗 [Read More]({post['link']})")
                
                st.markdown("---")
    
    else:
        st.info("💡 No news articles found. Try enabling Google Custom Search API.")

    # RESUME
    st.markdown("\n\n")
    if "resume" in memory and memory["resume"]:
        st.markdown("## 📄 Sample Resume")
        resume_sections = parse_resume(memory["resume"])
        
        # Extract contact info
        contact_lines = []
        for line in memory["resume"].splitlines():
            if line.strip().startswith("##"):
                break
            if line.strip().lower() in {"summary", "key skills", "experience", "education", "---"}:
                continue
            if line.strip():
                contact_lines.append(line.strip().replace("#", "").strip())
        
        # Remove code block markers
        if contact_lines and contact_lines[0].startswith("```"):
            contact_lines[0] = contact_lines[0].replace("```markdown", "").replace("```", "").strip()
        if contact_lines and contact_lines[-1].endswith("```"):
            contact_lines[-1] = contact_lines[-1].replace("```", "").strip()
        
        # Display contact info
        if contact_lines:
            for line in contact_lines:
                st.markdown(f"**{line}**")
        
        # Display sections
        if "Professional Summary" in resume_sections:
            st.markdown("### Professional Summary")
            st.write(resume_sections["Professional Summary"])
        
        if "Key Skills" in resume_sections:
            st.markdown("### Key Skills")
            st.write(resume_sections["Key Skills"])
        
        if "Work Experience" in resume_sections:
            st.markdown("### Work Experience")
            st.write(resume_sections["Work Experience"])
        
        if "Education" in resume_sections:
            st.markdown("### Education")
            education_lines = [
                line for line in resume_sections["Education"].splitlines()
                if "references available upon request" not in line.lower()
            ]
            while education_lines and education_lines[-1].strip() in {"```"}:
                education_lines = education_lines[:-1]
            st.write("\n".join(education_lines))

    # COVER LETTER
    if "cover" in memory:
        if memory["cover"]:
            st.markdown("---")
            st.markdown("## ✉️ Sample Cover Letter")
            cover_sections = parse_cover_letter(memory["cover"])
            
            if cover_sections:
                for section, content in cover_sections.items():
                    st.markdown(f"**{section}**")
                    st.write(content)
                    st.write("")  # add spacing
            else:
                # display as plain text if parsing fails
                st.write(memory["cover"])
        else:
            st.warning("No cover letter was generated.")

else:
    st.info("💡 Type a job title and press **Generate** to get started.")
    
    # examples of job titles
    st.markdown("### Example Job Titles:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("- Software Engineer in New York")
        st.markdown("- Web Design Intern in Denver, Colorado")
    with col2:
        st.markdown("- Goodwill Cashier")
        st.markdown("- Registered Nurse at AdventHealth")
    with col3:
        st.markdown("- Entry Level Marketing Assistant")
        st.markdown("- Dog Sitter")