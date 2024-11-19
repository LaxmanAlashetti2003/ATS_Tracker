from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Gemini API (update with the supported model)
genai.configure(api_key=os.getenv("AIzaSyDzRTWFWeGb6dr0oye--aEzW4hvz1ety0U"))

# Function to handle Google Gemini API response
def get_gemini_response(input_text, file_content, prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')  # Updated to supported model
        response = model.generate_content([input_text, file_content[0], prompt])
        return response.text
    except Exception as e:
        st.error(f"Error communicating with Gemini API: {e}")
        return None

# Function to process uploaded files (PDFs or images)
def input_file_setup(uploaded_file):
    if uploaded_file is not None:
        # Handle image files
        if uploaded_file.type.startswith("image/"):
            try:
                image = Image.open(uploaded_file)
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()

                file_parts = [
                    {
                        "mime_type": "image/jpeg",
                        "data": base64.b64encode(img_byte_arr).decode()
                    }
                ]
                return file_parts
            except Exception as e:
                st.error(f"Error processing image: {e}")
                return None

        # Handle PDF files
        elif uploaded_file.type == "application/pdf":
            try:
                # Specify Poppler path here
                poppler_path = r"C:\Program Files\poppler\Library\bin"  # Replace with your actual Poppler path
                images = pdf2image.convert_from_bytes(
                    uploaded_file.read(),
                    poppler_path=poppler_path  # Ensure Poppler path is passed
                )

                first_page = images[0]
                img_byte_arr = io.BytesIO()
                first_page.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()

                file_parts = [
                    {
                        "mime_type": "image/jpeg",
                        "data": base64.b64encode(img_byte_arr).decode()
                    }
                ]
                return file_parts
            except Exception as e:
                st.error(f"Error processing PDF: {e}")
                return None

        else:
            st.error("Unsupported file type. Please upload a PDF or an image.")
            return None
    else:
        st.error("No file uploaded")
        return None

# Streamlit App Configuration
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

# Add a user guide
st.markdown("### How to Use")
st.write("""
1. Enter the job description in the text area below.
2. Upload your resume as a PDF or an image file.
3. Click **'Tell Me About the Resume'** to get a detailed evaluation.
4. Click **'Percentage Match'** to see how well your resume aligns with the job description.
""")

# User input
input_text = st.text_area("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF or Image)...", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.write("✅ Resume uploaded successfully!")

# Buttons for actions
submit1 = st.button("Tell Me About the Resume")
submit3 = st.button("Percentage Match")

# Prompts for Gemini
input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description.
Please share your professional evaluation on whether the candidate's profile aligns with the role. Highlight strengths and weaknesses
of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality.
Your task is to evaluate the resume against the provided job description. Give a percentage match for the resume against
the job description, list missing keywords, and provide final thoughts.
"""

# Actions for buttons
if submit1:
    if uploaded_file is not None:
        file_content = input_file_setup(uploaded_file)
        if file_content:
            response = get_gemini_response(input_text, file_content, input_prompt1)
            if response:
                st.subheader("Evaluation Response")
                st.write(response)
        else:
            st.warning("Please upload a valid resume.")
    else:
        st.warning("Please upload a resume.")

elif submit3:
    if uploaded_file is not None:
        file_content = input_file_setup(uploaded_file)
        if file_content:
            response = get_gemini_response(input_text, file_content, input_prompt3)
            if response:
                st.subheader("Percentage Match Response")
                st.write(response)
        else:
            st.warning("Please upload a valid resume.")
    else:
        st.warning("Please upload a resume.")
