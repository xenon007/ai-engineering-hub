import streamlit as st
import ollama
from PIL import Image
import io

# Page configuration
st.set_page_config(
    page_title="Llama OCR",
    page_icon="🦙",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add custom CSS for scrollable container
st.markdown("""
    <style>
    .uploadSection {
        max-height: 80vh;
        overflow-y: auto;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🦙 Llama OCR")

# Add clear button in the top right
col_desc, col_clear = st.columns([4, 1])
with col_desc:
    st.markdown("""
    Extract structured text from images using Llama 3.2 Vision!. 
    """)
with col_clear:
    if st.button("Clear 🗑️"):
        st.session_state['ocr_result'] = None
        st.rerun()

# Create container for scrollable content
container = st.container()

# Create two columns with the same ratio
with container:
    col1, spacer, col2 = st.columns([1, 0.05, 2])

    # Left panel (col1) for image upload
    with col1:
        # Wrap the expander content in a div with the scrollable class
        st.markdown('<div class="uploadSection">', unsafe_allow_html=True)
        with st.expander("Upload Image", expanded=True):
            uploaded_file = st.file_uploader("Choose an image...", type=['png', 'jpg', 'jpeg'])
            
            if uploaded_file is not None:
                # Display the uploaded image
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                
                if st.button("Extract Text 🔍", type="primary"):
                    with st.spinner("Processing image..."):
                        try:
                            response = ollama.chat(
                                model='llama3.2-vision',
                                messages=[{
                                    'role': 'user',
                                    'content': """Analyze the text in the provided image. Extract all readable content
                                                and present it in a structured Markdown format that is clear, concise, 
                                                and well-organized. Ensure proper formatting (e.g., headings, lists, or
                                                code blocks) as necessary to represent the content effectively.""",
                                    'images': [uploaded_file.getvalue()]
                                }]
                            )
                            st.session_state['ocr_result'] = response.message.content
                        except Exception as e:
                            st.error(f"Error processing image: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Right panel (col2) for results
    with col2:
        st.subheader("Extracted Text")
        if 'ocr_result' in st.session_state:
            st.markdown(st.session_state['ocr_result'])
        else:
            st.info("Upload an image and click 'Extract Text' to see the results here.")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Llama Vision Model2 | [Report an Issue](https://github.com/yourusername/llama-ocr/issues)")