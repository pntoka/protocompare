import streamlit as st 
from docx import Document
from pypdf import PdfReader
from io import BytesIO, StringIO
import pandas as pd
import os
from PIL import Image
import base64
import requests
import json
import plotly.graph_objects as go # Import Plotly for the radar chart
import plotly.express as px

def unpack_json_protocol_list(json_file_content):
    protocol_titles = []
    protocol_step_list = []
    
    try:
        if isinstance(json_file_content, list):
            for protocol in json_file_content:
                protocol_df = pd.DataFrame(columns=["Step Number", "Type",
                                        "Input", "Output",
                                        "Action", "Parameters"])
                protocol_titles.append(protocol['doi'])
                protocol_steps = protocol['protocol']
                # print("Processing a list of protocol steps:") # Suppress console prints in Streamlit
                for i, protocol_step_data in enumerate(protocol_steps):
                    # print(f"\n--- Step {i+1} ---") # Suppress console prints in Streamlit
                    protocol_df.loc[len(protocol_df)] = [protocol_step_data["step_number"],
                                    protocol_step_data["step_type"],
                                    protocol_step_data["input"],
                                    protocol_step_data["output"],
                                    protocol_step_data["action"],
                                    protocol_step_data["parameter"]]
                protocol_step_list.append(protocol_df)

        else:
            # print("Processing a single protocol step:") # Suppress console prints in Streamlit
            protocol_step_data = json_file_content
            # This path for single protocol JSON needs to be handled differently if it should return a DataFrame
            # For now, it will return empty lists if a single object is passed and not a list of protocols.
            st.warning("JSON file contains a single object, not a list of protocols. Processing might be incomplete.")
            # Example of how you might handle a single dict, return a df in a list
            single_protocol_df = pd.DataFrame(columns=["Step Number", "Type", "Input", "Output", "Action", "Parameters"])
            single_protocol_df.loc[0] = [protocol_step_data["step_number"],
                                            protocol_step_data["step_type"],
                                            protocol_step_data["input"],
                                            protocol_step_data["output"],
                                            protocol_step_data["action"],
                                            protocol_step_data["parameter"]]
            protocol_step_list.append(single_protocol_df)
            protocol_titles.append(protocol_step_data.get('doi', 'Single Protocol')) # Get DOI or default title
    except json.JSONDecodeError:
        st.error(f"Error: Could not decode JSON. Check if the file is valid JSON.")
    except KeyError as e:
        st.error(f"Error: Missing required key in JSON data: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
    finally:
        # print(protocol_df.head()) # This print can cause issues if protocol_df is not always defined
        return protocol_step_list, protocol_titles

# --- Main Streamlit Application ---
# st.set_page_config() MUST be the first Streamlit command called
st.set_page_config(
    page_title="Protocompare - Protocol Comparator", # Changed title slightly for clarity
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Styling ---
st.markdown(
    """
    <style>
    /* Ensure the entire page background is consistent and pure white */
    html, body, .stApp, 
    [data-testid="stAppViewContainer"], 
    [data-testid="stBlock"], 
    .reportview-container, 
    .main,
    .st-emotion-cache-1ldf3gq { /* Targeting sidebar too */
        background-color: #FFFFFF !important; /* Pure white, forced */
        background: #FFFFFF !important; /* Ensuring all background properties are overridden */
        color: #333333; /* Darker text for readability */
    }

    /* Light blue box for the file uploader area (in sidebar) */
    [data-testid="stFileUploader"] {
        background-color: #E3F2FD; /* Soft sky blue */
        border-radius: 12px; /* Slightly more rounded corners */
        padding: 25px; /* More padding */
        border: 1px solid #BBDEFB; /* Slightly darker subtle blue border */
        box-shadow: 3px 3px 10px rgba(0,0,0,0.15); /* Slightly more prominent soft shadow */
    }
    
    /* Adjust title alignment and color */
    .st-emotion-cache-dv62a9 { /* Common class for main title */
        text-align: center;
        color: #2C3E50; /* A dark, professional blue-grey for main titles */
    }
    h1, h2, h3, h4, h5, h6 { /* General heading styles */
        color: #2C3E50;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Custom Streamlit Component for Mermaid.js ---
MERMAID_HTML_TEMPLATE = """
<div class="mermaid">
    {diagram_code}
</div>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
<script>
    mermaid.initialize({{ startOnLoad: true }});
</script>
"""

def mermaid_chart(chart_code: str, height: int = 300):
    """
    Renders a Mermaid.js chart in Streamlit.
    Note: This is a simplified embedding. For robust component development,
    consider `streamlit-component-template`.
    """
    html_code = MERMAID_HTML_TEMPLATE.format(diagram_code=chart_code)
    st.components.v1.html(html_code, height=height + 50) # Add some buffer height


# --- Text Extraction Functions ---
def extract_text_from_pdf(file_bytes: BytesIO) -> str:
    """Extracts text from a PDF file."""
    reader = PdfReader(file_bytes)
    text = ""
    for page_num in range(len(reader.pages)):
        text += reader.pages[page_num].extract_text() or ""
    return text

def extract_text_from_docx(file_bytes: BytesIO) -> str:
    """Extracts text from a DOCX file."""
    document = Document(file_bytes)
    full_text = []
    for paragraph in document.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

def extract_text_from_txt(file_bytes: BytesIO) -> str:
    """Extracts text from a TXT file."""
    return file_bytes.read().decode("utf-8")

def convert_mermaid_to_image(mermaid_code: str, format: str = "png") -> bytes:
    """
    Converts Mermaid diagram code to an image using the Mermaid Live Editor API.
    Returns the image data as bytes.
    """
    # Mermaid Live Editor API endpoint
    url = "https://mermaid.ink/img/"
    
    # Encode the Mermaid code
    encoded_code = base64.b64encode(mermaid_code.encode()).decode()
    
    # Make the request
    response = requests.get(f"{url}{encoded_code}?type={format}")
    
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to convert Mermaid diagram: {response.text}")

def convert_mermaid_to_pdf(mermaid_code: str) -> bytes:
    """
    Converts Mermaid diagram code to PDF using the Mermaid Live Editor API.
    Returns the PDF data as bytes.
    """
    return convert_mermaid_to_image(mermaid_code, format="pdf")


# --- Function to generate a dynamic spider chart (using Plotly) ---
def create_spider_chart(protocol_scores: dict, chart_title: str = "Protocol Characteristics"):
    """
    Generates an interactive spider/radar chart using Plotly.
    protocol_scores: A dictionary where keys are categories/parameters (e.g., "Efficiency")
                     and values are their scores (e.g., 1-10).
    """
    if not protocol_scores:
        st.warning("No data provided for the spider chart.")
        return

    categories = list(protocol_scores.keys())
    values = list(protocol_scores.values())

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Protocol Score'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values) + 1] # Adjust range based on max value for better scaling
            )),
        showlegend=False,
        title_text=chart_title,
        title_x=0.5, # Center the title
        title_font_size=20
    )
    
    st.plotly_chart(fig, use_container_width=True)


# --- Main Streamlit Application UI ---
st.title("🔬 Protocompare")
st.markdown("""
Welcome to the *in silico* Protocol Comparator! Upload your research protocols to compare their content, steps, and key parameters.
This tool is designed to help you streamline protocol analysis and identify differences or commonalities efficiently.
""")

# Load and convert image to base64
# IMPORTANT: Ensure 'logo.png' exists in the same directory as this script!
logo_path = "logo.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_data = f.read()
    encoded_logo = base64.b64encode(logo_data).decode()

    # Display centered, responsive, half-size image using HTML
    st.sidebar.markdown(
        f"""
        <div style="text-align: left; padding-bottom: 20px;">
            <img src="data:image/png;base64,{encoded_logo}" style="width:20%; height:auto;">
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.sidebar.warning(f"Logo image not found at '{logo_path}'. Please place 'logo.png' in the script directory.")


st.sidebar.header("Upload Protocols")
uploaded_files = st.sidebar.file_uploader(
    "Upload multiple protocol documents (TXT, PDF, DOCX)",
    type=["txt", "pdf", "docx"],
    accept_multiple_files=True
)

# Add action buttons - moved outside the uploaded_files condition
col1, col2 = st.columns(2)
with col1:
    # Count PDF files
    pdf_count = sum(1 for file in uploaded_files if file.name.lower().endswith('.pdf')) if uploaded_files else 0
    compare_button = st.button(
        "🔍 Compare Multiple Protocols", 
        use_container_width=True,
        disabled=pdf_count < 2,
        help="Upload at least 2 PDF files to enable comparison" if pdf_count < 2 else None
    )
with col2:
    search_button = st.button(
        "🔎 Search Database", 
        use_container_width=True,
        disabled=pdf_count != 1,
        help="Upload exactly 1 PDF file to enable search" if pdf_count != 1 else None
    )

#upload json file
uploaded_json_file = st.sidebar.file_uploader("Choose a file (JSON)", type=["json"])
if uploaded_json_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_json_file.getvalue()
    try:
        # Decode bytes to string, then load JSON
        string_data = bytes_data.decode("utf-8")
        json_data = json.loads(string_data)
        protocol_step_list, protocol_titles = unpack_json_protocol_list(json_data)
        
        # Display the parsed protocols
        if protocol_step_list:
            st.subheader("Parsed JSON Protocols:")
            for i, protocol_df in enumerate(protocol_step_list):
                st.markdown(f"**Protocol: {protocol_titles[i]}**")
                st.dataframe(protocol_df, hide_index=True)
        else:
            st.warning("No protocols found in the uploaded JSON file.")

    except json.JSONDecodeError:
        st.error(f"Error: Could not decode JSON from the uploaded file. Please ensure it's valid JSON.")
    except KeyError as e:
        st.error(f"Error: Missing required key in JSON data: {e}. Ensure keys like 'doi' and 'protocol' are present.")
    except Exception as e:
        st.error(f"An unexpected error occurred while processing JSON: {e}")


protocols_data = {}

if uploaded_files: # This block handles PDF/DOCX/TXT uploads
    for i, uploaded_file in enumerate(uploaded_files):
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        extracted_text = ""

        with st.spinner(f"Extracting text from {uploaded_file.name}..."):
            try:
                if file_extension == ".pdf":
                    extracted_text = extract_text_from_pdf(uploaded_file)
                elif file_extension == ".docx":
                    extracted_text = extract_text_from_docx(uploaded_file)
                elif file_extension == ".txt":
                    extracted_text = extract_text_from_txt(uploaded_file)
                else:
                    st.warning(f"Unsupported file type for {uploaded_file.name}: {file_extension}. Skipping.")
                    continue

                protocols_data[uploaded_file.name] = extracted_text
                st.sidebar.success(f"Successfully extracted text from {uploaded_file.name}")
            except Exception as e:
                st.sidebar.error(f"Error processing {uploaded_file.name}: {e}")

    # Display results only if compare or search button is pressed AND relevant files are uploaded
    if (compare_button and protocols_data and pdf_count >= 2) or \
       (search_button and protocols_data and pdf_count == 1):
        st.header("Uploaded Protocols & Extracted Text")
        cols = st.columns(len(protocols_data))
        file_names = list(protocols_data.keys())

        for idx, file_name in enumerate(file_names):
            with cols[idx]:
                st.subheader(f"📄 {file_name}") # Changed from 'Protocol {idx + 1}' to actual filename
                st.text_area(f"Text from {file_name}", protocols_data[file_name], height=300)
                st.metric("Word Count", len(protocols_data[file_name].split()))

        st.markdown("---")

        # --- Placeholder for Comparison Logic ---
        st.header("🔍 Protocol Analysis")
        st.info("""
        **Note:** In a full implementation, advanced Natural Language Processing (NLP) models
        would analyze the extracted text from each protocol to:
        - Identify common steps and unique procedures.
        - Extract specific parameters (e.g., temperatures, concentrations, durations).
        - Determine semantic similarities and differences between protocols.
        """)

        if compare_button and len(protocols_data) >= 2:
            st.subheader("Simple Similarity Indicator (Placeholder)")
            # Very basic placeholder for text similarity (e.g., Jaccard similarity on words)
            # This is NOT robust NLP but demonstrates the concept.
            text1 = protocols_data[file_names[0]]
            text2 = protocols_data[file_names[1]]

            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())

            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            jaccard_similarity = intersection / union if union else 0

            st.write(f"**Jaccard Word Similarity between '{file_names[0]}' and '{file_names[1]}':** {jaccard_similarity:.2f}")
            st.progress(jaccard_similarity, text=f"Similarity: {jaccard_similarity:.0%}")

        st.markdown("---")

        # --- Dynamic Spider Chart Section ---
        st.header("🎯 Protocol Characteristics Radar Chart")
        st.info("""
        This radar chart conceptually visualizes key characteristics of the uploaded protocol(s).
        In a full implementation, the scores for parameters like 'Efficiency', 'Complexity',
        and 'Safety' would be derived from deep NLP analysis of your protocol content.
        """)
        
        # --- Mock Data for Spider Chart ---
        # This data would come from your NLP backend after processing protocols.
        # Example 1: Single Protocol Characteristics
        if len(protocols_data) == 1:
            mock_protocol_1_scores = {
                "Efficiency": 8,
                "Reproducibility": 7,
                "Cost-effectiveness": 6,
                "Complexity": 5,
                "Safety": 9
            }
            create_spider_chart(mock_protocol_1_scores, f"Characteristics of {file_names[0]}")
            st.caption("Above: Hypothetical characteristics for the single uploaded protocol.")

        # Example 2: Comparing Two Protocols
        elif len(protocols_data) >= 2:
            mock_protocol_1_scores = {
                "Efficiency": 8,
                "Reproducibility": 7,
                "Cost-effectiveness": 6,
                "Complexity": 5,
                "Safety": 9
            }
            mock_protocol_2_scores = {
                "Efficiency": 6,
                "Reproducibility": 9,
                "Cost-effectiveness": 7,
                "Complexity": 8,
                "Safety": 7
            }
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=list(mock_protocol_1_scores.values()),
                theta=list(mock_protocol_1_scores.keys()),
                fill='toself',
                name=f"{file_names[0]} Scores"
            ))
            fig.add_trace(go.Scatterpolar(
                r=list(mock_protocol_2_scores.values()),
                theta=list(mock_protocol_2_scores.keys()),
                fill='toself',
                name=f"{file_names[1]} Scores"
            ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10] # Assuming scores are 0-10
                    )),
                showlegend=True,
                title_text="Comparative Protocol Characteristics",
                title_x=0.5,
                title_font_size=20
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"Above: Hypothetical comparative characteristics for {file_names[0]} vs {file_names[1]}.")

        else:
            st.write("Upload protocols to see characteristic visualization here.")


        st.markdown("---")
  
######### LEO Data visualization
        st.subheader("Data graph visualization")
        IMGDATA = [("networkgraph.png", "Keyword graph"), 
                  ("webchart.png", "Webchart"), 
                  ("decision_tree.png", "Decision tree")]

        # IMPORTANT: Ensure these image files exist in your script directory!
        # Added checks for image existence to prevent FileNotFoundError
        imgs = []
        for img_file, caption in IMGDATA:
            img_path = os.path.join(os.getcwd(), img_file) # Get full path
            if os.path.exists(img_path):
                try:
                    imgs.append(Image.open(img_path))
                except Exception as e:
                    st.error(f"Error loading image '{img_file}': {e}")
                    imgs.append(None) # Append None to maintain list length
            else:
                st.warning(f"Image '{img_file}' not found at '{img_path}'. Skipping.")
                imgs.append(None)

        # Only display columns if there's at least one image loaded
        if any(img is not None for img in imgs):
            cols = st.columns(3)
            for i, img_data in enumerate(IMGDATA):
                if imgs[i] is not None:
                    with cols[i]:
                        st.image(imgs[i], caption=img_data[1], use_container_width=True)
                else:
                    with cols[i]:
                        st.markdown(f"<div style='text-align:center;'>Image '{img_data[1]}' missing.</div>", unsafe_allow_html=True)


        # --- Placeholder for Visualization ---
        st.header("📊 Visualizing Protocol Flow (Mermaid.js Example)")
        st.info("""
        This section demonstrates how a flowchart could be generated. In a real system,
        the Mermaid diagram code would be dynamically created by parsing your protocols
        with sophisticated NLP to extract sequential steps and conditional logic.
        """)

        # Example Mermaid Flowchart
        example_mermaid_code = """
        graph TD
            A[Start Protocol] --> B{Check Sample Type?};
            B -- Type A --> C(Process Sample A);
            B -- Type B --> D(Process Sample B);
            C --> E[Incubate at 37°C];
            D --> E;
            E --> F{Analyze Results?};
            F -- Yes --> G[Generate Report];
            F -- No --> H[Store Sample];
            G --> I[End Protocol];
            H --> I;
        """
        st.subheader("Example Protocol Flowchart (Hardcoded Mermaid)")
        mermaid_chart(example_mermaid_code, height=400)


        # Download section
        st.subheader("Download Flowchart") # Changed title for clarity
        col1_dl, col2_dl = st.columns(2) # Use different variable names to avoid conflict
        
        try:
            with col1_dl: # Use the new column variable
                png_data = convert_mermaid_to_image(example_mermaid_code)
                st.download_button(
                    label="Download as PNG",
                    data=png_data,
                    file_name="protocol_flowchart.png",
                    mime="image/png",
                    help="Download the flowchart as a PNG image"
                )
                
            with col2_dl: # Use the new column variable
                pdf_data = convert_mermaid_to_pdf(example_mermaid_code)
                st.download_button(
                    label="Download as PDF",
                    data=pdf_data,
                    file_name="protocol_flowchart.pdf",
                    mime="application/pdf",
                    help="Download the flowchart as a PDF document"
                )
        except Exception as e:
            st.error(f"Error generating downloads: {str(e)}")

        st.markdown("---")
        st.write("Developed by Anthony, Guglielmo, Filip, Piotr, Leonardo, Gururaj, Elliot and Miranda with ❤️ Streamlit")

else:
    st.info("Upload protocol documents in the sidebar to begin comparison or upload JSON to view structured data.")

