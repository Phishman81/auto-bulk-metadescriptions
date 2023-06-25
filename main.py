import streamlit as st
import pandas as pd
from openai import OpenAI

# Set up your GPT-3 API key
openai = OpenAI("your_api_key_here")

# Define your prompts
prompts = {
    'PDP': 'Product description for {}',
    'Category Page': 'Description for category page {}',
    'Blog Article': 'Summary for blog article {}',
    'About Page': 'About us content for {}',
    # Add more page types and prompts as needed
}

def classify_page_type(url, title, meta_description):
    # Implement your page type classification logic here
    # For the purpose of this example, this function just returns 'PDP'
    return 'PDP'

def generate_description(prompt):
    # Use the OpenAI API to generate a description based on the prompt
    response = openai.complete(prompt=prompt)
    return response.choices[0].text.strip()

def main():
    st.title('SEO Content Generator')
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        data['Generated Description'] = ''
        st.write(data)
        fill_empty_meta = st.checkbox('Only generate descriptions for rows with empty meta descriptions')
        if st.button('Generate Content'):
            # Iterate over each row in the data
            for idx, row in data.iterrows():
                # Only consider URLs with status code 200 and that are "indexable"
                if row['Status Code'] != 200 or row['Indexability'] != 'indexable':
                    continue
                # If user selected to fill empty meta descriptions, skip rows that already have a meta description
                if fill_empty_meta and pd.notnull(row['Meta Description']):
                    continue
                # Use GPT-3 to classify page type
                page_type = classify_page_type(row['URL'], row['Title'], row['Meta Description'])
                # Select the appropriate prompt for the page type
                if page_type in prompts:
                    prompt = prompts[page_type].format(row['URL'])
                    # Generate the description
                    description = generate_description(prompt)
                    # Store the generated description in the dataframe
                    data.at[idx, 'Generated Description'] = description
            st.write(data)

if __name__ == "__main__":
    main()
    
