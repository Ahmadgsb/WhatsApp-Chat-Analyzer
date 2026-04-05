import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
# import seaborn as sns
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="WhatsApp Chat Analyzer Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        padding: 0rem 1rem;
    }

    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }

    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }

    .main-header p {
        color: rgba(255,255,255,0.9);
        margin-top: 0.5rem;
    }

    /* Stat card styling */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .stat-card h3 {
        margin: 0;
        font-size: 1rem;
        opacity: 0.9;
    }

    .stat-card h1 {
        margin: 0.5rem 0;
        font-size: 2.5rem;
        font-weight: bold;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: transform 0.2s;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Section headers */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0.5rem 1rem;
        border-radius: 5px;
        color: white;
        margin: 2rem 0 1rem 0;
    }

    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Info box */
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

# Sidebar
with st.sidebar:
    st.markdown("### 📱 WhatsApp Chat Analyzer")
    st.markdown("---")

    uploaded_file = st.file_uploader(
        "Upload WhatsApp Chat Export",
        type=['txt'],
        help="Export your WhatsApp chat without media and upload the .txt file"
    )

    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
        df = preprocessor.preprocess(data)

        # User selection
        user_list = df['user'].unique().tolist()
        if 'group_notification' in user_list:
            user_list.remove('group_notification')
        user_list.sort()
        user_list.insert(0, "All Participants")

        selected_user = st.selectbox("Select Participant", user_list)

        st.markdown("---")
        analyze_button = st.button("Generate Analysis", use_container_width=True)

        if analyze_button:
            st.session_state.analysis_done = True
            st.session_state.df = df
            st.session_state.selected_user = selected_user

# Main content
if uploaded_file is None:
    # Welcome screen
    st.markdown("""
        <div class="main-header">
            <h1>WhatsApp Chat Analyzer Pro</h1>
            <p>Transform your conversations into actionable insights</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="stat-card">
                <h3>📊 Message Statistics</h3>
                <h1>Analyze</h1>
                <p>Message patterns and trends</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="stat-card">
                <h3>👥 User Insights</h3>
                <h1>Understand</h1>
                <p>Participation patterns</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="stat-card">
                <h3>💬 Content Analysis</h3>
                <h1>Discover</h1>
                <p>Key topics and trends</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div class="info-box">
            <strong>📌 How to use:</strong><br>
            1. Export your WhatsApp chat (without media)<br>
            2. Upload the .txt file using the sidebar<br>
            3. Select a participant or analyze the whole group<br>
            4. Click 'Generate Analysis' to see insights
        </div>
    """, unsafe_allow_html=True)

elif st.session_state.analysis_done:
    df = st.session_state.df
    selected_user = st.session_state.selected_user

    # Convert selected_user for helper functions
    helper_selected_user = None if selected_user == "All Participants" else selected_user

    # Get statistics
    num_messages, words, num_media_messages, num_links = helper.fetch_stats(helper_selected_user, df)

    # Header
    st.markdown(f"""
        <div class="main-header">
            <h1>Chat Analysis Dashboard</h1>
            <p>Analyzing: {selected_user}</p>
        </div>
    """, unsafe_allow_html=True)

    # Key Metrics Row
    st.markdown("### Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <h3>💬 Total Messages</h3>
                <h1>{num_messages:,}</h1>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <h3>📝 Words Written</h3>
                <h1>{words:,}</h1>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="stat-card">
                <h3>🖼️ Media Shared</h3>
                <h1>{num_media_messages:,}</h1>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="stat-card">
                <h3>🔗 Links Shared</h3>
                <h1>{num_links:,}</h1>
            </div>
        """, unsafe_allow_html=True)

    # Timeline Analysis Section
    st.markdown('<div class="section-header">📈 Temporal Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Monthly Message Trends")
        timeline = helper.monthly_timeline(helper_selected_user, df)
        if not timeline.empty:
            fig = px.line(
                timeline,
                x='time',
                y='message',
                title="Message Volume Over Time",
                labels={'message': 'Number of Messages', 'time': 'Month'},
                color_discrete_sequence=['#667eea']
            )
            fig.update_layout(
                plot_bgcolor='white',
                height=400,
                hovermode='x unified'
            )
            fig.update_traces(line=dict(width=3))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Daily Activity Patterns")
        daily_timeline = helper.daily_timeline(helper_selected_user, df)
        if not daily_timeline.empty:
            fig = px.line(
                daily_timeline,
                x='only_date',
                y='message',
                title="Daily Message Distribution",
                labels={'message': 'Number of Messages', 'only_date': 'Date'},
                color_discrete_sequence=['#764ba2']
            )
            fig.update_layout(
                plot_bgcolor='white',
                height=400,
                hovermode='x unified'
            )
            fig.update_traces(line=dict(width=2))
            st.plotly_chart(fig, use_container_width=True)

    # User Participation Section
    if selected_user == "All Participants":
        st.markdown('<div class="section-header">👥 Participant Analysis</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Most Active Participants")
            x, new_df = helper.most_busy_user(df)
            fig = px.bar(
                x=x.index,
                y=x.values,
                title="Message Count by Participant",
                labels={'x': 'Participant', 'y': 'Number of Messages'},
                color=x.values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                plot_bgcolor='white',
                height=500,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### Contribution Distribution")
            fig = px.pie(
                values=new_df['percent'].head(10),
                names=new_df['name'].head(10),
                title="Message Share Percentage",
                hole=0.3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

    # Content Analysis Section
    st.markdown('<div class="section-header">🔍 Content Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Word Cloud Visualization")
        df_wc = helper.create_wordcloud(helper_selected_user, df)
        if df_wc:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.imshow(df_wc, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)

    with col2:
        st.markdown("#### Most Frequent Words")
        most_common_df = helper.most_commen_words(helper_selected_user, df)
        if not most_common_df.empty:
            fig = px.bar(
                most_common_df.head(15),
                x='count',
                y='word',
                orientation='h',
                title="Top 15 Most Used Words",
                labels={'count': 'Frequency', 'word': 'Word'},
                color='count',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                plot_bgcolor='white',
                height=500,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)

    # Emoji Analysis Section
    emoji_df = helper.emoji_helper(helper_selected_user, df)
    if not emoji_df.empty:
        st.markdown('<div class="section-header">😊 Emoji Analysis</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Emoji Usage Statistics")
            # FIXED: Use iloc instead of direct indexing
            display_df = emoji_df.head(15).copy()
            display_df.columns = ['Emoji', 'Frequency']
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

        with col2:
            st.markdown("#### Emoji Distribution")
            # FIXED: Use iloc for column access
            fig = px.pie(
                values=emoji_df.iloc[:, 1].head(10),
                names=emoji_df.iloc[:, 0].head(10),
                title="Top 10 Emojis Used",
                hole=0.3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: gray;'>© 2024 WhatsApp Chat Analyzer Pro | Powered by Streamlit</p>",
        unsafe_allow_html=True
    )

else:
    st.info("👈 Please upload a chat file and click 'Generate Analysis' to begin")