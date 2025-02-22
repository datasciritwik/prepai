import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from markdownlit import mdlit


from modules.document_processing import load_resume
from modules.result_generator import skill_gap_findings
from modules.result_generator import ATS_calculation
import plotly.graph_objects as go
from modules.page_utils import refresh

st.set_page_config(
    page_title="dashboard",
    initial_sidebar_state="collapsed",
    layout="wide"
)

st.markdown("""
            <style>
            #MainMenu {visibility:hidden;}
            footer {visibility:hidden;}
            </style>
            """, unsafe_allow_html=True)
hide_img_fs = '''
<style>
button[title="View fullscreen"]{
    visibility: hidden;}
</style>
'''
st.html("<style>[data-testid='stHeaderActionElements'] {display: none;}</style>")

st.markdown(hide_img_fs, unsafe_allow_html=True)
    

    
# Function to plot ATS score as a donut chart using Plotly
def plot_ats_donut(ats_score):
    fig = go.Figure(data=[go.Pie(
        values=[ats_score, 100 - ats_score],
        labels=[f"ATS Score: {ats_score}%", "Remaining"],
        hole=0.6,  # Creates the donut effect
        marker=dict(colors=["#ff4d00", "#D3D3D3"]),  # Colors
        textinfo="percent"
    )])

    fig.update_layout(
        showlegend=False,
        annotations=[dict(text=f"{ats_score}%", x=0.5, y=0.5, font_size=20, showarrow=False)]
    )

    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)

try:
    user_id = st.session_state.get("user_id", "user id not found")
    user_datas = st.session_state.get("data_dict", "user id not found")
    llm = st.session_state.get("llm", "Instance Not Found")
except:
    st.switch_page("/")
    
try:
    # st.write(user_id['user_idd'])
    job_description = user_datas[user_id['user_idd']]['job_description']
    resume_path = user_datas[user_id['user_idd']]['file_name']

    resume_text = load_resume(resume_path)
except:
    st.switch_page("pages/user.py")


set1, set2, set3 = st.columns([4,10,4])
# set3.image("pages/image.png", width=60)
with set3:
    refresh(resume_path)
        
with set2:
    col1, col2 = st.columns(2, gap="medium")
    with col1.container(border=True):
        if st.button("Chat", use_container_width=True, type="tertiary", help="Chat with AI and more improve your resume."):
            st.switch_page("pages/qna.py")
    with col2.container(border=True):
        if st.button("Improve Resume", use_container_width=True, type="tertiary", help="Enhanced your Resume and Cover letter."):
            st.switch_page("pages/resumecover.py")
            

add_vertical_space(3)

st.markdown("<h1 style='text-align: left; font-size: 30px; color: orange; font-family: monospace; font-weight: bold;'>Skill Gap Analysis</h1>", unsafe_allow_html=True)

# Ensure session state has the required key before checking
if "skills_gaps" not in st.session_state:
    st.session_state.skills_gaps = None  # Initialize if not already present

# Check if skill gaps are already stored
if st.session_state.skills_gaps:
    mdlit(st.session_state.skills_gaps)  # Print stored result
else:
    with st.spinner(text="Generating..."):
        if job_description and resume_text:  # Ensure inputs are provided
            _skills_gaps = skill_gap_findings(job_description=job_description, resume_text=resume_text, llm=llm)
            
            if _skills_gaps:  # Check if results are valid
                st.session_state.skills_gaps = _skills_gaps  # Store in session state
                mdlit(_skills_gaps)  # Print result
            else:
                st.warning("No skill gaps found. Please check the provided resume and job description.")
        else:
            st.error("Missing job description or resume. Please provide both to analyze skill gaps.")

add_vertical_space(3)

st.markdown("<h1 style='text-align: left; font-size: 30px; color: orange; font-family: monospace; font-weight: bold;'>Check ATS score</h1>", unsafe_allow_html=True)

if "ATS_score" not in st.session_state:
    st.session_state.ATS_score = 0
    
if "ATS_score_content" not in st.session_state:
    st.session_state.ATS_score_content = None
    
if st.session_state.ATS_score_content:
    mdlit(st.session_state.ATS_score_content)
else:
    with st.spinner("Calculating ATS Score..."):
        if job_description and resume_text:
            try:
                _ats_score = ATS_calculation(job_description=job_description, resume_text=resume_text, llm=llm)
                
                if isinstance(_ats_score, dict):
                    # Extract score from content if value is not present
                    if 'content' in _ats_score:
                        st.session_state.ATS_score_content = _ats_score['content']
                        # Try to extract numeric score from content
                        try:
                            # Assuming score is mentioned in the content
                            score_text = _ats_score['content']
                            # Extract numeric value (assuming it's mentioned as a percentage)
                            import re
                            score_match = re.search(r'(\d+)%', score_text)
                            if score_match:
                                st.session_state.ATS_score = int(score_match.group(1))
                            else:
                                st.session_state.ATS_score = 0  # Default score if not found
                        except:
                            st.session_state.ATS_score = 0  # Default score if extraction fails
                        
                        mdlit(_ats_score['content'])
                    else:
                        st.warning("Unexpected response format from ATS calculation")
                else:
                    st.warning("Invalid response from ATS calculation")
            except Exception as e:
                st.error(f"Error calculating ATS score: {str(e)}")
        else:
            st.error("Missing job description or resume. Please provide both for generating scores")
    
if st.session_state.ATS_score != 0:
    plot_ats_donut(st.session_state.ATS_score)