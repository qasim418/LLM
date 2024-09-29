import streamlit as st
import pandas as pd
from groq import Groq
from googlesearch import search

def search_relevant_pages(university_name, keyword, uni_domain):
    query = f"{university_name} {keyword} site:{uni_domain}"
    result_links = []

    for result in search(query, num_results=10):
        result_links.append(result)

    return result_links

def extract_links(university_name, uni_domain):
    grad_program_links = search_relevant_pages(university_name, "graduate programs", uni_domain)
    funding_links = search_relevant_pages(university_name, "funding opportunities assistantships", uni_domain)
    faculty_links = search_relevant_pages(university_name, "faculty graduate programs", uni_domain)

    return grad_program_links, funding_links, faculty_links

def save_links_to_csv(data):
    df = pd.DataFrame(data)
    return df

def show_page():
    st.title("Graduate Program Extractor")

    university_name = st.text_input("Enter University Name:")
    uni_domain = st.text_input("Enter University Domain:")
    api_key = st.text_input("Enter your Groq API Key:", type="password")

    if st.button("Extract Links"):
        if not university_name or not uni_domain or not api_key:
            st.error("Please provide all the required fields.")
        else:
            with st.spinner("Extracting links..."):
                grad_program_links, funding_links, faculty_links = extract_links(university_name, uni_domain)

                # Display Graduate Programs Links
                if grad_program_links:
                    st.write("### Graduate Programs Links:")
                    df_grad_programs = pd.DataFrame(grad_program_links, columns=["Graduate Program Links"])
                    st.dataframe(df_grad_programs)

                    # Convert Graduate Programs Links to CSV
                    csv_buffer_grad = df_grad_programs.to_csv(index=False)
                    st.download_button(
                        label="Download Graduate Programs Links CSV",
                        data=csv_buffer_grad,
                        file_name='graduate_program_links.csv',
                        mime='text/csv'
                    )
                else:
                    st.warning("No Graduate Programs links found.")

                # Display Funding Opportunities Links
                if funding_links:
                    st.write("### Funding Opportunities Links:")
                    df_funding = pd.DataFrame(funding_links, columns=["Funding Opportunities Links"])
                    st.dataframe(df_funding)

                    # Convert Funding Opportunities Links to CSV
                    csv_buffer_funding = df_funding.to_csv(index=False)
                    st.download_button(
                        label="Download Funding Opportunities Links CSV",
                        data=csv_buffer_funding,
                        file_name='funding_opportunities_links.csv',
                        mime='text/csv'
                    )
                else:
                    st.warning("No Funding Opportunities links found.")

                # Display Faculty Information Links
                if faculty_links:
                    st.write("### Faculty Information Links:")
                    df_faculty = pd.DataFrame(faculty_links, columns=["Faculty Information Links"])
                    st.dataframe(df_faculty)

                    # Convert Faculty Information Links to CSV
                    csv_buffer_faculty = df_faculty.to_csv(index=False)
                    st.download_button(
                        label="Download Faculty Information Links CSV",
                        data=csv_buffer_faculty,
                        file_name='faculty_information_links.csv',
                        mime='text/csv'
                    )
                else:
                    st.warning("No Faculty Information links found.")
