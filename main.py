import streamlit as st
import pandas as pd
import openai
import base64
import sys

# Main page title
st.title("Auto Metadescriptions Generator")

#Description
st.markdown("""
#### This application is specifically designed to streamline the process of auto-generating meta descriptions for your website in bulk. Offering you a choice to either:
- Generate meta descriptions for all valid pages,
- Focus solely on SEO relevant pages (i.e., the indexable ones),
- Even better: target URLs missing descriptions.

###### How to Use:
- Upload a CSV file from Screaming Frog SEO Spider containing your site's URLs.
- Select the necessary parameters for processing.

###### Automatic Exclusion and Page Type Definition:
Automatically excluding irrelevant URLs like scripts and images.
By analyzing the url, current title - and if available, H1 and meta description - the application defines the page type for each URL to enhance the understanding of potential user intent.

###### Final Output:
Upon completion, auto-generates an improved CSV file populated with improved meta descriptions.
""")

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
        st.write("Uploaded file is being processed...")
        st.write("Filtering for 'text/html' URLs and excluding image URLs...")
        df = pd.read_csv(file)

        try:
            required_columns = ['Address', 'Title 1', 'Meta Description 1', 'Content Type']
            valid_csv = all(col in df.columns for col in required_columns)

            if not valid_csv:
                missing_columns = [col for col in required_columns if col not in df.columns]
                missing_columns_str = ', '.join(missing_columns)
                st.error(f"Invalid CSV file. It is missing the following columns: {missing_columns_str}.")
                sys.exit()

            if 'Content Type' in df.columns:
                if df['Content Type'].str.contains('text/html').any():                
                    df = df[~df['Address'].str.contains('image/svg\+xml|\.jpeg|\.jpg|\.gif|\.png|\.svg|\.bmp|\.tiff|\.webp|\.heic|\.ico|\.psd|\.ai|\.eps$', regex=True)]

                    option_1 = st.selectbox('Choose URLs category:', ('All URLs', 'SEO Relevant URLs'))
                    option_2 = st.selectbox('Choose optimization category:', ('All Descriptions', 'Only Missing Descriptions'))

                    if option_1 == 'All URLs' and option_2 == 'All Descriptions':
                        pass

                    elif option_1 == 'All URLs' and option_2 == 'Only Missing Descriptions':
                        df = df[df['Meta Description 1'].isna() | df['Meta Description 1'] == ""]

                    elif option_1 == 'SEO Relevant URLs' and option_2 == 'All Descriptions':
                        if 'Status Code' in df.columns and 'Indexability' in df.columns:
                            df['Indexability'] = df['Indexability'].str.strip().str.lower()
                            df = df[(df['Status Code'] == 200) & (df['Indexability'] == 'indexable')]
                        else:
                            proceed = st.radio('The CSV does not contain the necessary columns for SEO relevance checking (Status Code and Indexability). Proceed by optimizing all URLs?', ('Yes', 'No'))
                            if proceed == 'No':
                                st.warning("Terminating the execution.")
                                sys.exit()

                    elif option_1 == 'SEO Relevant URLs' and option_2 == 'Only Missing Descriptions':
                        if 'Status Code' in df.columns and 'Indexability' in df.columns:
                            df['Indexability'] = df['Indexability'].str.strip().str.lower()
                            df = df[(df['Status Code'] == 200) & (df['Indexability'] == 'indexable') & (df['Meta Description 1'].isna() | df['Meta Description 1'] == "")]
                        else:
                            proceed = st.radio('The CSV does not contain the necessary columns for SEO relevance checking (Status Code and Indexability). Proceed by optimizing all URLs?', ('Yes', 'No'))
                            if proceed == 'No':
                                st.warning("Terminating the execution.")
                                sys.exit()

                    if df.empty:
                        if option_2 == 'Optimize Only Missing Meta Descriptions':
                            st.warning("There are no missing Meta Descriptions in your selection.")
                        else:
                            st.warning("No URLs matching the conditions were found.")
                        sys.exit()

                else:
                    st.warning("No URLs with 'text/html' content type found in the CSV.")
                    sys.exit()

                st.write(f"Total URLs to be processed: {len(df)}")

                start_button = st.button(f"Start Processing {len(df)} URLs")

                if start_button:
                    df['pagetype'] = ''

                    openai.api_key = st.secrets["openai_key"]

                    page_types = ['Home Page', 'Product Detail Page', 'Category Page',
                                'About Us Page', 'Contact Us Page', 'Blog Article Page',
                                'Services Page', 'Landing Page', 'Privacy Policy Page',
                                'Terms and Conditions Page', 'FAQ Page', 'Testimonials Page',
                                'Portfolio Page', 'Case Study Page', 'Press Release Page',
                                'Events Page', 'Resources/Downloads Page', 'Team Members Page',
                                'Careers/Jobs Page', 'Login/Register Page', 'E-commerce shopping cart page',
                                'Forum/community page', 'News Page']

                    st.write("Defining the pagetype for every URL... Please wait.")
                    for i in range(len(df)):
                        address = df.iloc[i]['Address']
                        title = df.iloc[i]['Title 1']
                        h1 = df.iloc[i]['H1-1']
                        meta_description = df.iloc[i]['Meta Description 1']

                        prompt = f"You are an SEO expert. From the best of your knowledge, please assign the most suitable pagetype from the following list:\n{page_types}\n\nFor a page with the URL: {address}\nPage a heading: {h1}\n Title: {title}\nMeta Description: {meta_description}\n\nUsing the given information, define the most suitable pagetype from the options provided. Do not write anything else than that."

                        response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, temperature=0.5, max_tokens=50)

                        pagetype = response.choices[0].text.strip()

                        df.iloc[i, df.columns.get_loc('pagetype')] = pagetype

                    st.write("Intermediate Result - Processed URLs with their Pagetypes:")
                    processed_urls_df = df[['Content Type', 'Address', 'Title 1', 'Meta Description 1', 'H1-1', 'pagetype','Status Code', 'Indexability']]
                    st.dataframe(processed_urls_df)

                    st.write("Generating new metadescriptions for every URL... Please wait.")
                    df['new_metadescription'] = ''

                    for i in range(len(df)):
                        address = df.iloc[i]['Address']
                        title = df.iloc[i]['Title 1']
                        h1 = df.iloc[i]['H1-1']
                        meta_description = df.iloc[i]['Meta Description 1']
                        pagetype = df.iloc[i]['pagetype']

                        prompt = f""" You are an SEO Expert who crafts excellent meta descriptions. Generate a concise and engaging meta description of maximum 150 characters for a webpage of type '{pagetype}', with the URL '{address}', page title '{title}', the main heading '{h1}' and a current meta description that looks like the following but needs improvement '{meta_description}'. """

                        response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, temperature=0.5, max_tokens=80)

                        new_metadescription = response.choices[0].text.strip()

                        df.iloc[i, df.columns.get_loc('new_metadescription')] = new_metadescription

                    st.write("Result - Processed URLs with their Pagetypes and New Metadescriptions:")
                    processed_urls_df = df[['Content Type', 'Address', 'Title 1', 'Meta Description 1', 'pagetype', 'new_metadescription']]
                    st.dataframe(processed_urls_df)

                    st.success("Metadescriptions have been created successfully! You can download the updated CSV below.")
                    csv = df.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="new_metadescriptions.csv">Download CSV File</a>'
                    st.markdown(href, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

elif password_entered:
    st.error("Incorrect password. Please try again.")
