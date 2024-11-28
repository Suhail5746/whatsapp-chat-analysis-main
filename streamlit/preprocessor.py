import re
import pandas as pd

def preprocess(data):
    # Pattern to detect date and time in WhatsApp chat
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APap][mM]\s-\s'

    # Splitting the data based on the pattern, which will give us the messages
    messages = re.split(pattern, data)[1:]  # First item is empty, skip it

    # Extract the dates from the data using the same pattern
    dates = re.findall(pattern, data)

    # Debug: Print the number of messages and dates
    print(f"Total messages: {len(messages)}")
    print(f"Total dates: {len(dates)}")

    # Create a DataFrame with the messages and dates
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    
    # Convert message_date to datetime format
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %I:%M %p - ', errors='coerce')

    # Debug: Check the DataFrame right after creation
    print(df.head())

    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Initialize lists to store users and messages
    users = []
    final_messages = []

    for message in df['user_message']:
        # Splitting each message to separate user from the message content
        entry = re.split(r'([\w\W]+?):\s', message)
        if len(entry) > 1:  # Check if the split was successful
            users.append(entry[1])  # The user's name
            final_messages.append(" ".join(entry[2:]))  # The actual message
        else:
            users.append('group_notification')  # For system messages
            final_messages.append(entry[0])  # The message itself

    # Adding the 'user' and 'message' columns to the DataFrame
    df['user'] = users
    df['message'] = final_messages

    # Drop the 'user_message' column since it's been split into 'user' and 'message'
    df.drop(columns=['user_message'], inplace=True)

    # Extract more features from the 'date' column
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Creating a 'period' column to indicate hour ranges
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(f"{hour}-00")
        elif hour == 0:
            period.append(f"00-{hour+1}")
        else:
            period.append(f"{hour}-{hour+1}")

    df['period'] = period

    # Debug: Check the final DataFrame
    print(df.head())

    return df
