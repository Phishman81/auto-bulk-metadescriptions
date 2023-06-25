import openai
import pandas as pd
import streamlit as st

# Initialize OpenAI API key
openai.api_key = 'your-api-key'

# Define your predefined prompts for each page type
prompts = {
    "Product Page": "This is a product page for {}...",
    "Blog Article": "This is a blog article about {}...",
    # Add more page types as needed
}

def classify_page_type(url, title, meta_desc):
    """Use GPT-3 to classify the page type."""
    prompt = f"URL: {url}\nPage Title: {title}\nMeta Description: {meta_desc}\n\nPage Type:"
    response = openai.Completion.create(
      engine="text-davinci-003",
      prompt=prompt,
      max_tokens=60
    )
    return response.choices[0].text.strip()

def generate_description(prompt):
    """Use GPT-3 to generate a description based on the prompt."""
    response = openai.Completion.create(
      engine="text-davinci-003",
      prompt=prompt,
      max_tokens=200  # Adjust as needed
    )
    return response.choices[0].text.strip()

def main():
    st.title('SEO Content Generator')
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        st.write(data)
        if st.button('Generate Content'):
            # Iterate over each row in the data
            for idx, row in data.iterrows():
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
  
