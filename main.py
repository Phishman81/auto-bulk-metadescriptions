import streamlit as st
import pandas as pd
import openai
import csv
import base64

# Load the secrets.toml file
st.secrets = st.secrets["streamlit"]["secrets"]

# Main page title
st.title("Auto Metadescriptions Generator")

# Password for access
password = st.secrets["password"]
password_input = st.text_input("Enter Password", type="password")

if password_input == password:

    # Upload the CSV
    file = st.file_uploader("Upload a CSV file", type=['csv'])

    # Options for the user
    option = st.radio("Choose your option:", 
                      ('Generate Metadescriptions for all URLs', 'Generate Metadescriptions for only SEO Relevant URLs'))

    if file is not None:
        try:
            # Load the CSV
            df = pd.read_csv(file)
            st.success("File uploaded successfully!")

            # If SEO relevant URLs is selected
            if option == 'Generate Metadescriptions for only SEO Relevant URLs':
                if 'Status Code' in df.columns and 'Indexability' in df.columns:
                    # Filter the dataframe
                    df = df[(df['Status Code'] == 200) & (df['Indexability'] == 'indexable')]
                else:
                    st.error("The columns 'Status Code' and 'Indexability' are missing. Please select the other option.")
                    return

            # Add the pagetype column
            df['pagetype'] = ''

            # Define the page types
            page_types = ['Home Page', 'Product Detail Page', 'Category Page', 
                          'About Us Page', 'Contact Us Page', 'Blog Article Page',
                          'Services Page', 'Landing Page', 'Privacy Policy Page', 
                          'Terms and Conditions Page', 'FAQ Page', 'Testimonials Page',
                          'Portfolio Page', 'Case Study Page', 'Press Release Page', 
                          'Events Page', 'Resources/Downloads Page', 'Team Members Page',
                          'Careers/Jobs Page', 'Login/Register Page', 'E-commerce shopping cart page',
                          'Forum/community page', 'News Page']

            # Use GPT-3 to assign a page type
            openai.api_key = st.secrets["openai_key"]

            st.write("Generating Page types... Please wait.")
            for i in range(len(df)):
                prompt = f"{df.iloc[i, df.columns.get_loc('url')]} {df.iloc[i, df.columns.get_loc('pagetitle')]} {df.iloc[i, df.columns.get_loc('metadescription')]}"

                response = openai.Completion.create(engine="gpt-3.5-turbo", prompt=prompt, temperature=0.5, max_tokens=3)

                df.iloc[i, df.columns.get_loc('pagetype')] = response.choices[0].text.strip()
            st.success("Page types generated successfully!")

            # Add new metadescription column
            df['new metadescription'] = ''

            # Use GPT-3 to generate metadescriptions
            st.write("Generating Metadescriptions... Please wait.")
            for i in range(len(df)):
                prompt = f"{df.iloc[i, df.columns.get_loc('url')]} {df.iloc[i, df.columns.get_loc('pagetitle')]} {df.iloc[i, df.columns.get_loc('H1')]} {df.iloc[i, df.columns.get_loc('metadescription')]} {df.iloc[i, df.columns.get_loc('pagetype')]}"
                response = openai.Completion.create(engine="gpt-3.5-turbo", prompt=prompt, temperature=0.5, max_tokens=60)

                df.iloc[i, df.columns.get_loc('new metadescription')] = response.choices[0].text.strip()

            st.success("Metadescriptions generated successfully!")

            # Download the new CSV
            st.write(df)
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()  
            href = f'<a href="data:file/csv;base64,{b64}" download="metadescriptions.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred: {e}")

else:
    st.write("Invalid Password. Please try again.")
                
