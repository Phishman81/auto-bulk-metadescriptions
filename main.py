import streamlit as st
import pandas as pd
import openai
import base64
import sys

# Main page title
st.title("Auto Metadescriptions Generator")

# Password for access
password = st.secrets["password"]
password_input = st.text_input("Enter Password", type="password")
password_entered = False  # Track if the password has been entered

if password_input:  # Check if a password has been entered
    password_entered = True  # Set the flag to True

if password_entered and password_input == password:
    # File upload
    file = st.file_uploader("Upload a CSV File", type=['csv'])

    if file is not None:
        df = pd.read_csv(file)

        try:
            # Check if the CSV file is valid
            required_columns = ['Address', 'Title 1', 'Meta Description 1', 'Content Type']
            valid_csv = all(col in df.columns for col in required_columns)

            if not valid_csv:
                missing_columns = [col for col in required_columns if col not in df.columns]
                missing_columns_str = ', '.join(missing_columns)
                st.error(f"Invalid CSV file. Please ensure it contains the following columns: {missing_columns_str}.")
                sys.exit()

            # Check if 'Content Type' column contains 'text/html'
            if 'Content Type' in df.columns:
                if df['Content Type'].str.contains('text/html').any():
                    # Ask if metadescriptions should be generated for all URLs or only SEO relevant ones
                    option = st.radio('Choose an option:', ('All URLs', 'SEO Relevant URLs'))

                    if option == 'SEO Relevant URLs':
                        if 'Status Code' in df.columns and 'Indexability' in df.columns:
                            df = df[(df['Status Code'] == 200) & (df['Indexability'] == 'Indexable') & (df['Content Type'].str.contains('text/html'))]
                        else:
                            proceed = st.radio(
                                'The CSV does not contain the necessary columns for SEO relevance checking (Status Code and Indexability). Proceed by optimizing all URLs?',
                                ('Yes', 'No'))
                            if proceed == 'No':
                                st.warning("Terminating the execution.")
                                sys.exit()
                    else:
                        df = df[df['Content Type'].str.contains('text/html')]
                else:
                    st.warning("No URLs with 'text/html' content type found in the CSV.")
                    sys.exit()
            else:
                st.warning("The CSV does not contain the 'Content Type' column.")
                sys.exit()

            # Display count of URLs
            st.write(f"Total URLs to be processed: {len(df)}")

            # Button to initiate processing
            start_button = st.button("Start Processing")

            if start_button:
                df['pagetype'] = ''

                # Use GPT-3 to assign a page type
                openai.api_key = st.secrets["openai_key"]

                page_types = ['Home Page', 'Product Detail Page', 'Category Page',
                              'About Us Page', 'Contact Us Page', 'Blog Article Page',
                              'Services Page', 'Landing Page', 'Privacy Policy Page',
                              'Terms and Conditions Page', 'FAQ Page', 'Testimonials Page',
                              'Portfolio Page', 'Case Study Page', 'Press Release Page',
                              'Events Page', 'Resources/Downloads Page', 'Team Members Page',
                              'Careers/Jobs Page', 'Login/Register Page', 'E-commerce shopping cart page',
                              'Forum/community page', 'News Page']

                # Assigning page type
                st.write("Defining the pagetype for every URL... Please wait.")
                for i in range(len(df)):
                    address = df.iloc[i]['Address']
                    title = df.iloc[i]['Title 1']
                    meta_description = df.iloc[i]['Meta Description 1']

                    prompt = f"You are an SEO expert. From the best of your knowledge, please assign the most suitable pagetype from the following list:\n{page_types}\n\nFor a page with the URL: {address}\nPage Title: {title}\nMeta Description: {meta_description}\n\nUsing the given information, define the most suitable pagetype from the options provided. Do not write anything else than that."

                    response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, temperature=0.5, max_tokens=50)

                    pagetype = response.choices[0].text.strip()

                    df.iloc[i, df.columns.get_loc('pagetype')] = pagetype

                # Intermediate result table
                st.write("Intermediate Result - URLs per Pagetype:")
                pagetype_counts = df['pagetype'].value_counts()
                st.table(pagetype_counts)

                # Allow the user to download the new CSV
                st.success("Metadescriptions have been created successfully! You can download the updated CSV below.")
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="new_metadescriptions.csv">Download CSV File</a>'
                st.markdown(href, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

elif password_entered:  # Check if the password has been entered
    st.error("Incorrect password. Please try again.")
