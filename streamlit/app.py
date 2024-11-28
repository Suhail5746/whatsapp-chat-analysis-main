import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Sidebar configuration
st.sidebar.title("📊 WhatsApp Chat Analyzer")
st.sidebar.markdown("This application analyzes your WhatsApp chat data to provide insights.")
st.sidebar.markdown("---")  # Divider

# File Upload Section
uploaded_file = st.sidebar.file_uploader("📂 Choose a WhatsApp chat file (txt)", type="txt")
st.sidebar.markdown("---")  # Divider

# Date Range Selection (only visible when a file is uploaded)
if uploaded_file is not None:
    start_date = st.sidebar.date_input("📅 Start Date", value=pd.to_datetime("2022-01-01"))
    end_date = st.sidebar.date_input("📅 End Date", value=pd.to_datetime("2024-12-31"))

    with st.spinner("Processing file..."):
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
        df = preprocessor.preprocess(data)

    # Filter data by date range
    df['date'] = pd.to_datetime(df['date'])  # Ensure 'date' column is in datetime format
    filtered_df = df[(df['date'] >= pd.Timestamp(start_date)) & (df['date'] <= pd.Timestamp(end_date))]

    # Check if the filtered DataFrame is empty
    if filtered_df.empty:
        st.error("No data available for the selected date range.")
    else:
        # Fetch unique users and handle group notifications
        user_list = filtered_df['user'].unique().tolist()
        if 'group_notification' in user_list:
            user_list.remove('group_notification')
        user_list.sort()
        user_list.insert(0, "Overall")

        selected_user = st.sidebar.selectbox("🔍 Show analysis for", user_list)

        if st.sidebar.button("🚀 Show Analysis"):
            st.markdown("---")

            # Display Top Statistics
            st.header("📊 Top Statistics")
            num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, filtered_df)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📨 Total Messages", num_messages if num_messages > 0 else 0)
            with col2:
                st.metric("✍️ Total Words", words if words > 0 else 0)
            with col3:
                st.metric("🖼️ Media Shared", num_media_messages if num_media_messages > 0 else 0)
            with col4:
                st.metric("🔗 Links Shared", num_links if num_links > 0 else 0)

            st.markdown("---")  # Divider

            # Monthly Timeline
            st.header("📅 Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user, filtered_df)
            if not timeline.empty:
                fig, ax = plt.subplots()
                ax.plot(timeline['time'], timeline['message'], color='green')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            else:
                st.warning("No data available to display Monthly Timeline.")

            st.markdown("---")  # Divider

            # Daily Timeline
            st.header("📆 Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_user, filtered_df)
            if not daily_timeline.empty:
                fig, ax = plt.subplots()
                ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            else:
                st.warning("No data available to display Daily Timeline.")

            st.markdown("---")  # Divider

            # Activity Map
            st.header('📊 Activity Map')
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🗓️ Most Busy Day")
                busy_day = helper.week_activity_map(selected_user, filtered_df)
                if not busy_day.empty:
                    fig, ax = plt.subplots()
                    ax.bar(busy_day.index, busy_day.values, color='purple')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                else:
                    st.warning("No data available for Most Busy Day.")

            with col2:
                st.subheader("📅 Most Busy Month")
                busy_month = helper.month_activity_map(selected_user, filtered_df)
                if not busy_month.empty:
                    fig, ax = plt.subplots()
                    ax.bar(busy_month.index, busy_month.values, color='orange')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                else:
                    st.warning("No data available for Most Busy Month.")

            st.markdown("---")  # Divider

            # Weekly Activity Heatmap
            st.header("🔥 Weekly Activity Heatmap")
            user_heatmap = helper.activity_heatmap(selected_user, filtered_df)
            if not user_heatmap.empty:
                fig, ax = plt.subplots()
                sns.heatmap(user_heatmap, cmap="YlGnBu", ax=ax)
                st.pyplot(fig)
            else:
                st.warning("No data available to generate Weekly Activity Heatmap.")

            st.markdown("---")  # Divider

            # Busiest Users (if group chat)
            if selected_user == 'Overall':
                st.header('👥 Most Busy Users')
                x, new_df = helper.most_busy_users(filtered_df)
                if not x.empty:
                    fig, ax = plt.subplots()
                    col1, col2 = st.columns(2)

                    with col1:
                        ax.bar(x.index, x.values, color='red')
                        plt.xticks(rotation='vertical')
                        st.pyplot(fig)
                    with col2:
                        st.dataframe(new_df)
                else:
                    st.warning("No data available to display Most Busy Users.")

            st.markdown("---")  # Divider

            # Wordcloud
            st.header("☁️ Word Cloud")
            df_wc = helper.create_wordcloud(selected_user, filtered_df)
            if df_wc:
                fig, ax = plt.subplots()
                ax.imshow(df_wc)
                st.pyplot(fig)
            else:
                st.warning("No data available to create Word Cloud.")

            st.markdown("---")  # Divider

            # Most Common Words
            st.header('🔠 Most Common Words')
            most_common_df = helper.most_common_words(selected_user, filtered_df)
            if not most_common_df.empty:
                fig, ax = plt.subplots()
                ax.barh(most_common_df[0], most_common_df[1], color='green')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            else:
                st.warning("No data available for Most Common Words.")

            st.markdown("---")  # Divider

            # Emoji Analysis
            st.header('😀 Emoji Distribution')
            emoji_df = helper.emoji_helper(selected_user, filtered_df)

            if not emoji_df.empty:
                fig, ax = plt.subplots(figsize=(12, 8))
                ax.bar(emoji_df['Emoji'].head(10), emoji_df['Count'].head(10), color='teal')
                ax.set_xlabel('Emoji')
                ax.set_ylabel('Count')
                ax.set_title('Top 10 Emojis Distribution')
                plt.xticks(rotation=45)
                st.pyplot(fig)
            else:
                st.warning("No data available for Emoji Distribution.")
