from urlextract import URLExtract
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from collections import Counter
import pandas as pd
import emoji
import numpy as np

extractor = URLExtract()
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def fetch_stats(selected_user, df):
    """Fetch comprehensive chat statistics"""
    if selected_user:
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]

    # Count words (excluding media placeholders)
    words = []
    for message in df['message']:
        if message != '<Media omitted>\n':
            words.extend(message.split())

    # Count media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # Extract links
    links = []
    for message in df['message']:
        links.extend(extractor.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)


def most_busy_user(df):
    """Identify most active participants"""
    # Filter out group notifications
    df_filtered = df[df['user'] != 'group_notification']

    # Get message counts
    message_counts = df_filtered['user'].value_counts()

    # Calculate percentages
    percentage_df = round((message_counts / df_filtered.shape[0]) * 100, 2).reset_index()
    percentage_df.columns = ['name', 'percent']

    return message_counts.head(10), percentage_df.head(10)


def create_wordcloud(selected_user, df):
    """Generate word cloud visualization"""
    if selected_user:
        df = df[df['user'] == selected_user]

    # Filter out media messages and group notifications
    temp_df = df[df['user'] != 'group_notification']
    temp_df = temp_df[temp_df['message'] != '<Media omitted>\n']

    if temp_df.empty:
        return None

    # Create word cloud
    wc = WordCloud(
        width=800,
        height=600,
        min_font_size=10,
        background_color='white',
        colormap='viridis',
        max_words=200,
        contour_width=1,
        contour_color='steelblue'
    )

    text = ' '.join(temp_df['message'].astype(str))
    df_wc = wc.generate(text)
    return df_wc


def most_commen_words(selected_user, df):
    """Extract and analyze most common words"""
    try:
        # Load stop words
        with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
            stop_words_hinglish = set(f.read().splitlines())
    except FileNotFoundError:
        stop_words_hinglish = set()

    # Download NLTK stopwords if not available
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('stopwords', quiet=True)

    stop_words_english = set(stopwords.words('english'))
    stop_words = stop_words_english.union(stop_words_hinglish)

    if selected_user:
        df = df[df['user'] == selected_user]

    # Filter data
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    temp = temp[temp['message'].notna()]

    if temp.empty:
        return pd.DataFrame(columns=['word', 'count'])

    # Process words
    all_words = []
    for message in temp['message']:
        # Remove special characters and lowercase
        words = message.lower().split()
        # Filter words
        filtered_words = [
            word for word in words
            if word.isalpha() and len(word) >= 4 and word not in stop_words
        ]
        all_words.extend(filtered_words)

    # Get most common words
    word_counts = Counter(all_words).most_common(20)
    most_common_df = pd.DataFrame(word_counts, columns=['word', 'count'])

    return most_common_df


def emoji_helper(selected_user, df):
    """Analyze emoji usage patterns"""
    if selected_user:
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        # Extract emojis from message
        emojis.extend([char for char in message if emoji.is_emoji(char)])

    if not emojis:
        return pd.DataFrame(columns=['Emoji', 'Count'])

    emoji_counts = Counter(emojis)
    emoji_df = pd.DataFrame(emoji_counts.most_common(), columns=['Emoji', 'Count'])

    return emoji_df


def monthly_timeline(selected_user, df):
    """Generate monthly timeline of messages"""
    if selected_user:
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month_name']).size().reset_index(name='message')

    if timeline.empty:
        return pd.DataFrame(columns=['time', 'message'])

    # Create formatted time string
    timeline['time'] = timeline['month_name'] + ' ' + timeline['year'].astype(str)

    return timeline[['time', 'message']]


def daily_timeline(selected_user, df):
    """Generate daily timeline of messages"""
    if selected_user:
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').size().reset_index(name='message')
    daily_timeline['only_date'] = pd.to_datetime(daily_timeline['only_date'])
    daily_timeline = daily_timeline.sort_values('only_date')

    return daily_timeline


def get_activity_heatmap(selected_user, df):
    """Generate activity heatmap data"""
    if selected_user:
        df = df[df['user'] == selected_user]

    # Create hour and day columns
    df['hour'] = pd.to_datetime(df['date']).dt.hour
    df['day_of_week'] = pd.to_datetime(df['date']).dt.day_name()

    # Create pivot table for heatmap
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = pd.crosstab(df['hour'], df['day_of_week'])
    heatmap_data = heatmap_data[days_order]

    return heatmap_data