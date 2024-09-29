import json
import pandas as pd
import re
import streamlit as st
from io import BytesIO
from googlesearch import search  # To search for Wikipedia pages
from langchain_community.document_loaders import WebBaseLoader
from groq import Groq

# Function to load webpage content using WebBaseLoader
def load_webpage_content(url):
    try:
        loader = WebBaseLoader(url)
        documents = loader.load()  # Load content from the URL
        return documents
    except Exception as e:
        st.error(f"Error loading webpage: {e}")
        return []

# Function to use the Groq model (Llama) for extracting institutions and meaningful data
def extract_institutions_with_llm(client, content):
    prompt = f"""
    You are a helpful assistant. Here is the content from a webpage. Extract all public universities, colleges, and schools, 
    along with any other meaningful data that is directly available on the webpage, such as status (public/private), addresses, 
    degree level (Master's, PhD, Postdoc), and enrollment numbers if available, and for each university provide its official website URL.
    
    Provide the result in the following JSON format, with no additional explanations or text:
    [
        {{
            "name": "Institution Name",
            "status": "Public/Private",
            "address": "Institution Address",
            "degree_level": "Master's/PhD/Postdoc",
            "enrollment": "Total Enrollment (if available)",
            "website_url": "Official Website URL"
        }},
        ...
    ]

    Only extract the details that are present directly in the webpage content. Do not infer or predict any missing details. 
    Webpage Content: {content}
    """
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            top_p=1,
            stream=False
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating insights with LLM: {e}")
        return "Unable to generate insights."

# Function to clean the raw text and extract valid JSON
def extract_json_from_response(response):
    try:
        json_str = re.search(r'\[\s*{.*}\s*\]', response, re.DOTALL)
        if json_str:
            return json_str.group(0)
        else:
            st.warning("Valid JSON not found in the response.")
            return None
    except Exception as e:
        st.error(f"Error extracting JSON from the response: {e}")
        return None

# Function to convert DataFrame to CSV and return as BytesIO (binary data)
def convert_df_to_csv(df):
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    return csv_buffer

# Function to search for Wikipedia page listing universities in the state
def search_wikipedia_page_for_state(state_name):
    query = f"list of universities and colleges in {state_name} site:wikipedia.org"
    urls = []

    try:
        # Use Google search to find URLs
        for result in search(query, num_results=10):
            if 'wikipedia.org' in result:  # Filter results to get only Wikipedia links
                urls.append(result)
        return urls
    except Exception as e:
        st.error(f"Error during Google search: {e}")
        return []

# Streamlit App Layout
def show_page():
    st.title("State University Data Extractor")
    st.write("Enter a State Name to extract universities/colleges details using the Groq LLM.")

    state = st.text_input("Enter the State Name:")
    api_key = st.text_input("Enter your Groq API Key:", type="password")

    if st.button("Search and Extract Data"):
        if not state or not api_key:
            st.error("Please provide both a State name and an API key.")
        else:
            with st.spinner(f"Searching for Wikipedia page of universities in {state}..."):
                # Search Google for the Wikipedia page listing universities in the given state
                wikipedia_urls = search_wikipedia_page_for_state(state)

                if wikipedia_urls:
                    st.success(f"Found Wikipedia page(s) for universities in {state}. Using the top result.")
                    top_wikipedia_url = wikipedia_urls[0]  # Pick the top Wikipedia result
                    st.write(f"Processing Wikipedia URL: {top_wikipedia_url}")

                    with st.spinner(f"Loading and processing {top_wikipedia_url}..."):
                        # Load webpage content from Wikipedia
                        documents = load_webpage_content(top_wikipedia_url)

                        if documents:
                            page_content = " ".join([doc.page_content for doc in documents])

                            client = Groq(api_key=api_key)

                            # Extract institutions and related data using the LLM
                            extracted_data = extract_institutions_with_llm(client, page_content)

                            if extracted_data == "Unable to generate insights.":
                                st.error("Failed to generate insights from the Wikipedia page.")
                                return

                            # Extract JSON content from the raw response
                            json_data = extract_json_from_response(extracted_data)

                            if json_data:
                                try:
                                    institutions_data = json.loads(json_data)
                                    df = pd.DataFrame(institutions_data)
                                    st.write("### Extracted Institutions Data:")
                                    st.dataframe(df)

                                    csv_buffer = convert_df_to_csv(df)
                                    st.download_button(
                                        label="Download CSV",
                                        data=csv_buffer,
                                        file_name=f'{state}_universities_data.csv',
                                        mime='text/csv'
                                    )
                                except json.JSONDecodeError as e:
                                    st.error(f"Error parsing the extracted data into JSON: {e}")
                                    st.text(extracted_data)
                            else:
                                st.warning("No valid JSON data found.")
                        else:
                            st.warning("No content found at the Wikipedia URL.")
                else:
                    st.error(f"No Wikipedia page found for universities in {state}.")

# Run the app
if __name__ == "__main__":
    show_page()
