import openai
import pandas as pd
import concurrent.futures

# Set OpenAI key
openai.api_key = '"ENTER YOUR API KEY HERE"' 

# Read the CSV file into a pandas DataFrame
df = pd.read_csv('b2b.csv')

# Strip leading and trailing spaces from column names
df.columns = df.columns.str.strip()

# Define a function to make API call
def ask_chat_gpt(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Based on this company description = '{message}', generate a compliment I can use in my outreach. Praise them for something based of the description I provided. We will targeting someone from the executive team. Start with Love how you guys..., If you can't, simply respond with UNABLE"}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"API call error: {str(e)}"

# Initialize a list to store responses
responses = []

# Define executor
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    # Loop through each row in the DataFrame
    futures = {executor.submit(ask_chat_gpt, row['Description']): index for index, row in df.iterrows()}
    
    for future in concurrent.futures.as_completed(futures):
        index = futures[future]
        try:
            response = future.result(timeout=30)
        except concurrent.futures.TimeoutError:
            response = "API call timed out"
        responses.append((index, response))
        print(f"Completed row: {index}")

# Sort responses by index and extract only response text
responses.sort(key=lambda x: x[0])
responses = [response for index, response in responses]

# Add responses to column 'F' with header 'Relevance Check' in the DataFrame
df['result'] = responses

# Save DataFrame back to CSV
df.to_csv('b2bcompliments', index=False)
