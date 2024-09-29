# import json
# import pandas as pd
# import re
# import streamlit as st
# from io import BytesIO  # Updated to use BytesIO for binary data
# from langchain_community.document_loaders import WebBaseLoader
# from groq import Groq

# # Function to load webpage content using WebBaseLoader
# def load_webpage_content(url):
#     try:
#         loader = WebBaseLoader(url)
#         documents = loader.load()  # Load content from the URL
#         return documents
#     except Exception as e:
#         st.error(f"Error loading webpage: {e}")
#         return []

# # Function to use the Groq model (Llama) for extracting institutions and meaningful data
# def extract_institutions_with_llm(client, content):
#     prompt = f"""
#     You are a helpful assistant. Here is the content from a webpage. Extract all public universities, colleges, and schools, 
#     along with any other meaningful data that is directly available on the webpage, such as status (public/private), addresses, 
#     degree level (Master's, PhD, Postdoc), and enrollment numbers if available and for each university provide its official website URL.
#     Provide the result in the following JSON format:

#     [
#         {{
#             "name": "Institution Name",
#             "status": "Public/Private",
#             "address": "Institution Address",
#             "degree_level": "Master's/PhD/Postdoc",
#             "enrollment": "Total Enrollment (if available)",
#             "website_url": "Official Website URL"
#         }},
#         ...
#     ]

#     Only extract the details that are present directly in the webpage content. Do not infer or predict any missing details. 
#     Webpage Content: {content}
#     """

#     try:
#         completion = client.chat.completions.create(
#             model="llama-3.1-70b-versatile",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=1,
#             top_p=1,
#             stream=False  # Set to False to get the full response at once
#         )

#         return completion.choices[0].message.content

#     except Exception as e:
#         st.error(f"Error generating insights with LLM: {e}")
#         return "Unable to generate insights."

# # Function to clean the raw text and extract valid JSON
# def extract_json_from_response(response):
#     try:
#         # Use regex to find the JSON array in the response
#         json_str = re.search(r'\[\s*{.*}\s*\]', response, re.DOTALL)
#         if json_str:
#             return json_str.group(0)  # Return the matched JSON string
#         else:
#             st.warning("Valid JSON not found in the response.")
#             return None
#     except Exception as e:
#         st.error(f"Error extracting JSON from the response: {e}")
#         return None

# # Function to convert DataFrame to CSV and return as BytesIO (binary data)
# def convert_df_to_csv(df):
#     csv_buffer = BytesIO()  # Use BytesIO for binary format
#     df.to_csv(csv_buffer, index=False)
#     csv_buffer.seek(0)
#     return csv_buffer

# # Streamlit App Layout
# def main():
#     st.title("University Data Extractor")
#     st.write("Enter a URL to extract public institutions and their details using the Groq LLM.")

#     url = st.text_input("Enter the webpage URL:")
#     api_key = st.text_input("Enter your Groq API Key:", type="password")

#     # Button to start the extraction process
#     if st.button("Extract Data"):
#         if not url or not api_key:
#             st.error("Please provide both a URL and an API key.")
#         else:
#             with st.spinner("Loading webpage content and extracting data..."):
#                 # Load webpage content
#                 documents = load_webpage_content(url)

#                 # Check if documents are available
#                 if documents:
#                     page_content = " ".join([doc.page_content for doc in documents])

#                     # Initialize Groq client
#                     client = Groq(api_key=api_key)

#                     # Extract institutions and related data using the LLM
#                     extracted_data = extract_institutions_with_llm(client, page_content)

#                     if extracted_data == "Unable to generate insights.":
#                         st.error("Failed to generate insights.")
#                         return

#                     # Extract JSON content from the raw response
#                     json_data = extract_json_from_response(extracted_data)

#                     if json_data:
#                         try:
#                             # Convert the extracted JSON string to a Python object (list of dictionaries)
#                             institutions_data = json.loads(json_data)

#                             # Convert the data to a DataFrame
#                             df = pd.DataFrame(institutions_data)

#                             # Display the table
#                             st.write("### Extracted Institutions Data:")
#                             st.dataframe(df)

#                             # Provide an option to download the data as a CSV file
#                             csv_buffer = convert_df_to_csv(df)
#                             st.download_button(
#                                 label="Download CSV",
#                                 data=csv_buffer,
#                                 file_name='institutions_data.csv',
#                                 mime='text/csv'
#                             )

#                         except json.JSONDecodeError as e:
#                             st.error(f"Error parsing the extracted data into JSON: {e}")
#                             st.text(extracted_data)  # Show raw data for debugging
#                     else:
#                         st.warning("No valid JSON data found.")
#                 else:
#                     st.warning("No content found at the provided URL.")

# if __name__ == "__main__":
#     main()


import streamlit as st
import page1  # Import first page (institution extraction by URL)
import page2  # Import second page (graduate program extraction by university name)

# Define a function to navigate between pages
def main():
    st.sidebar.title("Navigation")
    page_selection = st.sidebar.radio("Go to", ["University Data Extractor", "Graduate Program Extractor"])

    # Page navigation logic
    if page_selection == "University Data Extractor":
        page1.show_page()  # Call the function from page1
    elif page_selection == "Graduate Program Extractor":
        page2.show_page()  # Call the function from page2

if __name__ == "__main__":
    main()
