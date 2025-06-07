import streamlit as st # Corrected: 'import' was missing 'i'
from docx import Document
import pypdf
from io import BytesIO
import os

# --- Custom Streamlit Component for Mermaid.js ---
# This allows us to render Mermaid diagrams directly in Streamlit.
# In a real project, you would typically develop this as a separate Python package
# (e.g., using `streamlit-component-template`). For this example, we'll
# simulate it with direct HTML embedding for simplicity, or use a pre-built one
# if available and simple to integrate for direct text-to-diagram.
# For truly robust custom components, you'd follow Streamlit's official guide
# and create a separate frontend React/JS build.
# For this example, we will use `st.components.v1.html` to embed the Mermaid.js
# library and render the diagram.

# HTML template for embedding Mermaid.js
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
    reader = PyPDF2.PdfReader(file_bytes)
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


# --- Main Streamlit Application ---
st.set_page_config(
    page_title="Protocol Comparator",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔬 Protocompare")
st.markdown("""
Welcome to the *in silico* Protocol Comparator! Upload your research protocols to compare their content, steps, and key parameters.
This tool is designed to help you streamline protocol analysis and identify differences or commonalities efficiently.
""")

st.sidebar.header("Upload Protocols")
uploaded_files = st.sidebar.file_uploader(
    "Upload multiple protocol documents (TXT, PDF, DOCX)",
    type=["txt", "pdf", "docx"],
    accept_multiple_files=True
)

protocols_data = {}

if uploaded_files:
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

    if protocols_data:
        st.header("Uploaded Protocols & Extracted Text")
        cols = st.columns(len(protocols_data))
        file_names = list(protocols_data.keys())

        for idx, file_name in enumerate(file_names):
            with cols[idx]:
                st.subheader(f"� {file_name}")
                st.text_area(f"Text from {file_name}", protocols_data[file_name], height=300)
                st.metric("Word Count", len(protocols_data[file_name].split()))

        st.markdown("---")

        # --- Placeholder for Comparison Logic ---
        st.header("🔍 Protocol Comparison (Conceptual)")
        st.info("""
        **Note:** In a full implementation, advanced Natural Language Processing (NLP) models
        would analyze the extracted text from each protocol to:
        - Identify common steps and unique procedures.
        - Extract specific parameters (e.g., temperatures, concentrations, durations).
        - Determine semantic similarities and differences between protocols.
        """)

        if len(protocols_data) >= 2:
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
        mermaid_chart(example_mermaid_code, height=400) # Use the custom component

        st.markdown("---")
        st.write("Developed by Anthony, Guglielmo, Filip, Piotr, Leonardo, Gururaj, Elliot and Miranda with ❤️ Streamlit")

else:
    st.info("Upload protocol documents in the sidebar to begin comparison.")
