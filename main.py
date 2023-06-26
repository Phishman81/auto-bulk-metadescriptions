import streamlit as st
import pandas as pd
import openai
import base64

def check_password():
    """Returns `True` if the user entered the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store the password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.title('Social Media Post Generator with GPT-4')
        st.write("")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.title('Social Media Post Generator with GPT-4')
        st.write("Welcome to the Social Media Post Generator with GPT-4! This app helps you effortlessly create engaging and compelling social media posts for platforms like LinkedIn, Instagram, Facebook, YouTube, TikTok, Snapchat, and Google Profile Page. Simply enter the topic of your post, the goal you want to achieve, the target group you're aiming for, and other preferences like content length, hashtags, emojis, list type, hook style, and communication style.")
        st.write("Using the power of GPT-4, the app generates high-quality posts tailored to your specifications. This saves you time and effort, as you no longer need to write each post from scratch. The generated posts capture the desired tone, writing style, and even replicate the author's voice when provided with an example text.")
        st.write("")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

# Streamlit application
def main():
    if not check_password():
        return


   
    # Function to classify page type
    def classify_page_type(url: str, title: str, meta_description: str) -> str:
        # Set your OpenAI API key
        openai.api_key = api_key

        # List of possible page types
        page_types = ['Home Page', 'Product Detail Page', 'Category Page', 
                      'About Us Page', 'Contact Us Page', 'Blog Article Page',
                      'Services Page', 'Landing Page', 'Privacy Policy Page', 
                      'Terms and Conditions Page', 'FAQ Page', 'Testimonials Page',
                      'Portfolio Page', 'Case Study Page', 'Press Release Page', 
                      'Events Page', 'Resources/Downloads Page', 'Team Members Page',
                      'Careers/Jobs Page', 'Login/Register Page', 'E-commerce shopping cart page',
                      'Forum/community page', 'News Page']

        # Generate the prompt string
        page_types_prompt = ', '.join(page_types)

        # Generate the text completion
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"The URL is: {url}\nThe title is: {title}\nThe meta description is: {meta_description}\nGiven the following page types: {page_types_prompt}, the page type is",
            temperature=0.3,
            max_tokens=60
        )

        # Return the generated text
        return response.choices[0].text.strip()

    # Function to generate description
    def generate_description(prompt: str) -> str:
        # Set your OpenAI API key
        openai.api_key = api_key
        
        # Generate the text completion
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0.3,
            max_tokens=60
        )
        
        # Return the generated text
        return response.choices[0].text.strip()

    # Function to process data
    def process_data(df: pd.DataFrame) -> pd.DataFrame:
        # Filter based on 'Status Code' and 'Indexability'
        df = df[(df['Status Code'] == 200) & (df['Indexability'] == 'Indexable')]

        # Classify page types
        df['PageType'] = df.apply(lambda row: classify_page_type(row['Address'], row['Title 1'], row['Meta Description 1']), axis=1)
        
        # Define prompts for each page type.
        prompts = {
            "Home Page": "Write a compelling meta description for a Home Page with title '{title}' and url '{url}'",
            "Product Detail Page": "Write a compelling meta description for a Product Detail Page with title '{title}' and url '{url}'",
            # Add other page types here
        }
        
    
    # Generate descriptions for each page type
        for page_type, prompt_template in prompts.items():
            df.loc[df['PageType'] == page_type, 'Generated Meta Description'] = df[df['PageType'] == page_type].apply(
                lambda row: generate_description(prompt_template.format(title=row['Title 1'], url=row['Address'])), axis=1)
        return df

    # Create a file uploader
    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx'])

    # If a file is uploaded
    if uploaded_file is not None:
        # Load the data
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)

        # Process the data
        df = process_data(df)

        # Download the processed data
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}" download="processed_data.csv">Download CSV File</a>'
        st.markdown(href, unsafe_allow_html=True)

else:
    # If the password is incorrect, show an error message
    st.error('The password you entered is incorrect.')
    
