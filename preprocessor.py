import re
import pandas as pd
from datetime import datetime


def preprocess(data):
    """
    Preprocess WhatsApp chat export data
    """
    # Pattern for WhatsApp date format
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\u202f[AP]M\s-\s'

    # Extract messages and dates
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    if not messages or not dates:
        raise ValueError("Invalid chat format. Please ensure you exported the chat without media.")

    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'user-message': messages
    })

    # Convert to datetime
    try:
        df['datetime'] = pd.to_datetime(df['date'], format='%m/%d/%y, %I:%M\u202f%p - ')
    except:
        # Alternative format
        df['datetime'] = pd.to_datetime(df['date'], format='%d/%m/%y, %I:%M\u202f%p - ')

    # Extract user and message
    users = []
    messages = []

    for message in df['user-message']:
        # Split on first colon to separate user and message
        entry = re.split(r'([^:]+):\s', message, 1)
        if len(entry) > 2:  # Valid user message
            users.append(entry[1].strip())
            messages.append(entry[2].strip())
        else:
            users.append('group_notification')
            messages.append(entry[0].strip())

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user-message'], inplace=True)

    # Extract temporal features
    df['year'] = df['datetime'].dt.year
    df['month_name'] = df['datetime'].dt.strftime('%B')
    df['month_num'] = df['datetime'].dt.month
    df['day'] = df['datetime'].dt.day
    df['only_date'] = df['datetime'].dt.date
    df['hour'] = df['datetime'].dt.hour
    df['minute'] = df['datetime'].dt.minute
    df['day_name'] = df['datetime'].dt.day_name()
    df['week_num'] = df['datetime'].dt.isocalendar().week

    # Clean message column
    df['message'] = df['message'].fillna('')

    # Drop original date column
    df.drop(columns=['date'], inplace=True)

    # Rename datetime to date for clarity
    df.rename(columns={'datetime': 'date'}, inplace=True)

    return df


def validate_chat_format(df):
    """
    Validate that the chat data has the required columns
    """
    required_columns = ['user', 'message', 'date']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    return True


def get_chat_summary(df):
    """
    Generate a summary of the chat data
    """
    summary = {
        'total_messages': len(df),
        'unique_users': df['user'].nunique(),
        'date_range': {
            'start': df['date'].min(),
            'end': df['date'].max()
        },
        'total_days': (df['date'].max() - df['date'].min()).days,
        'media_messages': len(df[df['message'] == '<Media omitted>']),
        'system_messages': len(df[df['user'] == 'group_notification'])
    }

    return summary