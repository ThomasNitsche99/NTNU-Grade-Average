import streamlit as st
from grade_average import GradeCalculator

st.set_page_config(
    page_title="NTNU Grade Point Average Calculator",
    page_icon="🎓",
)

def main():
    st.title("NTNU Grade Point Average Calculator")

    # File uploader allows users to upload a PDF file
    uploaded_file = st.file_uploader("Upload a PDF file ", type="pdf", help="Upload a Transcript of Records from NTNU")

    if uploaded_file is not None:
        st.write("File uploaded successfully!")

        # Process the PDF file
        with st.spinner('Processing...'):
            # Replace this function with your actual processing logic
            try:
                calculator = GradeCalculator(uploaded_file, False)
                results = calculator.calculate()
            except Exception as err:
                st.error(f"{err}", icon="🚨")
                return
            
        st.success('Processing complete!', icon="🥳")
    
        st.write("**Results:**")

        col1, col2 = st.columns(2)

        with col1:
                st.metric("Language", results.get('language', 'N/A').upper())
                st.metric("Study Points", results.get('study_points', 'N/A'))

        with col2:
                st.metric("Grade Avg (Raw)", results.get('grade_average_raw', 'N/A'))
                st.metric("Grade Avg (Rounded)", results.get('grade_average_ceil', 'N/A'))
                st.metric("Grade Avg Letter", results.get('grade_average_ceil_letter', 'N/A'))
                

    def add_footer():
        footer = """
        <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            # background-color: black;
            color: white;
            text-align: center;
            padding: 10px 0;
        }
        </style>
        <div class="footer">
            Developed by Thomas with love ❤️
        </div>
        """
        st.markdown(footer, unsafe_allow_html=True)
    
    add_footer()
    
    
if __name__ == '__main__':
    main()
