from urlextract import URLExtract
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from collections import Counter
import pandas as pd
import emoji
import numpy as np

# Download once
nltk.download('stopwords', quiet=True)

extractor = URLExtract()


def fetch_stats(selected_user, df):
    if selected_user:
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]
    words = []
    for message in df['message']:
        if message != '<Media omitted>\n':
            words.extend(message.split())

    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]
    links = []
    for message in df['message']:
        links.extend(extractor.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)


def most_busy_user(df):
    df_filtered = df[df['user'] != 'group_notification']
    message_counts = df_filtered['user'].value_counts()
    percentage_df = round((message_counts / df_filtered.shape[0]) * 100, 2).reset_index()
    percentage_df.columns = ['name', 'percent']
    return message_counts.head(10), percentage_df.head(10)


def create_wordcloud(selected_user, df):
    if selected_user:
        df = df[df['user'] == selected_user]

    temp_df = df[df['user'] != 'group_notification']
    temp_df = temp_df[temp_df['message'] != '<Media omitted>\n']

    if temp_df.empty:
        return None

    wc = WordCloud(width=800, height=600, min_font_size=10, background_color='white', colormap='viridis', max_words=200)
    text = ' '.join(temp_df['message'].astype(str))
    return wc.generate(text)


def most_commen_words(selected_user, df):
    stop_words_hinglish = set()
    try:
        with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
            stop_words_hinglish = set(f.read().splitlines())
    except FileNotFoundError:
        pass

    stop_words_english = set(stopwords.words('english'))
    stop_words = stop_words_english.union(stop_words_hinglish)

    if selected_user:
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    temp = temp[temp['message'].notna()]

    if temp.empty:
        return pd.DataFrame(columns=['word', 'count'])

    all_words = []
    for message in temp['message']:
        words = message.lower().split()
        filtered_words = [word for word in words if word.isalpha() and len(word) >= 4 and word not in stop_words]
        all_words.extend(filtered_words)

    word_counts = Counter(all_words).most_common(20)
    return pd.DataFrame(word_counts, columns=['word', 'count'])


def emoji_helper(selected_user, df):
    if selected_user:
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([char for char in message if emoji.is_emoji(char)])

    if not emojis:
        return pd.DataFrame(columns=['Emoji', 'Count'])

    emoji_counts = Counter(emojis)
    return pd.DataFrame(emoji_counts.most_common(), columns=['Emoji', 'Count'])


def monthly_timeline(selected_user, df):
    if selected_user:
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month_name']).size().reset_index(name='message')
    if timeline.empty:
        return pd.DataFrame(columns=['time', 'message'])

    timeline['time'] = timeline['month_name'] + ' ' + timeline['year'].astype(str)
    return timeline[['time', 'message']]


def daily_timeline(selected_user, df):
    if selected_user:
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').size().reset_index(name='message')
    daily_timeline['only_date'] = pd.to_datetime(daily_timeline['only_date'])
    return daily_timeline.sort_values('only_date')