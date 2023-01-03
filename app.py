import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import urllib.request
from helper import senti
import pickle
import requests
# import SessionState

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=cab208a1af730b020afeec1de21f8538&language=en-US".format(movie_id)
    # url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path


def recommend(movie,similarity,movies):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        # fetch the movie poster
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters
# movies = 0
movies1 = pickle.load(open('movie_list1.pkl', 'rb'))
similarity1 = pickle.load(open('similarity1.pkl', 'rb'))
movies2 = pickle.load(open('movie_list2.pkl', 'rb'))
similarity2 = pickle.load(open('similarity2.pkl', 'rb'))
movies3 = pickle.load(open('movie_list3.pkl', 'rb'))
similarity3 = pickle.load(open('similarity3.pkl', 'rb'))

# movie_list = movies['title'].values
# selected_movie = st.selectbox(
#             "Type or select a movie from the dropdown",
#             movie_list
#             )

button1 = st.empty()
text1 = st.empty()
button2 = st.empty()
text2 = st.empty()

st.sidebar.title("Whatsapp Chat Analyzer")

urllib.request.urlretrieve(
    'https://i.pinimg.com/originals/04/38/35/043835a704a0ed63e1369231ac4f568e.jpg',
    "ronaldo.jpg")
# urllib.request.urlretrieve(
#   'https://i.ytimg.com/vi/Oqkm10bBtoU/mqdefault.jpg',
#    "nags.jpg")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is None:
    st.header("Calm Down and select a whatsapp file!!!")
    image = Image.open("ronaldo.jpg")
    st.image(image, caption='Calm down')
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    # st.sidebar.button(bytes_data)
    df = preprocessor.preprocess(data)
    # st.sidebar.button(df)
    # print(df.info())
    # fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    menu = ["Show Analysis","Recommend Movies"]

    choice = st.sidebar.selectbox("Menu", menu)

    if choice == 'Recommend Movies':
        selected_user2 = st.selectbox("Show analysis wrt", user_list)
        # print("new emotion")

        emo = senti(selected_user2,df)
        print("new emotion",emo)
        movies = movies1
        similarity = similarity1
        if emo == 'Positive':
            movies = movies2
            similarity = similarity2
        elif emo == 'Negative':
            movies = movies3
            similarity = similarity3

        movie_list = movies['title'].values
        selected_movie = st.selectbox(
        "Type or select a movie from the dropdown",
        movie_list
        )

        if st.button('Show Recommendation'):
            recommended_movie_names,recommended_movie_posters = recommend(selected_movie,similarity,movies)
    # col1, col2, col3, col4, col5 = st.beta_columns(5)
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.text(recommended_movie_names[0])
                st.image(recommended_movie_posters[0])
            with col2:
                st.text(recommended_movie_names[1])
                st.image(recommended_movie_posters[1])

            with col3:
                st.text(recommended_movie_names[2])
                st.image(recommended_movie_posters[2])
            with col4:
                st.text(recommended_movie_names[3])
                st.image(recommended_movie_posters[3])
            with col5:
                st.text(recommended_movie_names[4])
                st.image(recommended_movie_posters[4])


    if choice == "Show Analysis":
        selected_user1 = st.selectbox("Show analysis wrt", user_list)
    

    # selected_user1 = st.sidebar.selectbox(data,user_list)
    
        if st.button("Show Analysis"):

        # Stats Area
            num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user1, df)
            st.title("Top Statistics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.header("Total Messages")
                st.title(num_messages)
            with col2:
                st.header("Total Words")
                st.title(words)
            with col3:
                st.header("Media Shared")
                st.title(num_media_messages)
            with col4:
                st.header("Links Shared")
                st.title(num_links)

        # monthly timeline
            st.title("Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user1, df)
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'], color='green')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # daily timeline
            st.title("Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_user1, df)
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # activity map
            st.title('Activity Map')
            col1, col2 = st.columns(2)

            with col1:
                st.header("Most busy day")
                busy_day = helper.week_activity_map(selected_user1, df)
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values, color='purple')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.header("Most busy month")
                busy_month = helper.month_activity_map(selected_user1, df)
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values, color='orange')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            st.title("Weekly Activity Map")
            user_heatmap = helper.activity_heatmap(selected_user1, df)
            fig, ax = plt.subplots()
            ax = sns.heatmap(user_heatmap)
            st.pyplot(fig)

        # finding the busiest users in the group(Group level)
            if selected_user1 == 'Overall':
                st.title('Most Busy Users')
                x, new_df = helper.most_busy_users(df)
                fig, ax = plt.subplots()

                col1, col2 = st.columns(2)

                with col1:
                    ax.bar(x.index, x.values, color='red')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                with col2:
                    st.dataframe(new_df)

        # WordCloud
            df_wc = helper.create_wordcloud(selected_user1, df)

            st.title("Wordcloud")
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)

        # most common words

            most_common_df = helper.most_common_words(selected_user1, df)
            if most_common_df.empty:
                st.title("")
            else:
                fig, ax = plt.subplots()
                ax.barh(most_common_df[0], most_common_df[1])
                plt.xticks(rotation='vertical')
                st.title('Most commmon words')
                st.pyplot(fig)

        # emoji analysis
            emoji_df = helper.emoji_helper(selected_user1, df)
            if not emoji_df.empty:
                st.title("Emoji Analysis")

                col1, col2 = st.columns(2)

                with col1:
                    st.dataframe(emoji_df)
                with col2:
                    fig, ax = plt.subplots()
                    ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
                    st.pyplot(fig)
    # movies = pickle.load(open('movie_list.pkl', 'rb'))
    #     if selected_user1 != 'Overall':
    #         # movies = 0
    #         # if emo == "Neutral":
    #         #     movies = movies1

            

    #         movie_list = movies['title'].values
    #         st.header('Options to choose recommended movie depending on current mood')
    #         selected_movie = st.selectbox("Type or select a movie from the dropdown",movie_list)
    #         print("hello1")
    #         if st.button('Show Recommendation'):
    #             print("hello2")
    #             recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    #             print(recommended_movie_names)
    # # col1, col2, col3, col4, col5 = st.beta_columns(5)
    #             col1, col2, col3, col4, col5 = st.columns(5)

    #             with col1:
    #                 st.text(recommended_movie_names[0])
    #                 st.image(recommended_movie_posters[0])
    #             with col2:
    #                 st.text(recommended_movie_names[1])
    #                 st.image(recommended_movie_posters[1])

    #             with col3:
    #                 st.text(recommended_movie_names[2])
    #                 st.image(recommended_movie_posters[2])
    #             with col4:
    #                 st.text(recommended_movie_names[3])
    #                 st.image(recommended_movie_posters[3])
    #             with col5:
    #                 st.text(recommended_movie_names[4])
    #                 st.image(recommended_movie_posters[4])


    # selected_user2 = st.sidebar.selectbox("Do personalised Movie Recommendation",user_list)
    # emo = senti(selected_user2,df) #store the current mood of the user
    # ss = SessionState.get(button1=False)
    # # b1 = 
    # # if st.sidebar.button1("Recommend"):
    #     # ss.button1 = True
    
    # if st.sidebar.button1("Recommend"):
    #     movie_list = movies['title'].values
    #     selected_movie = st.selectbox(
    #         "Type or select a movie from the dropdown",
    #         movie_list
    #         )
    #     recommended_movie_names,recommended_movie_posters = recommend(selected_movie)
    # # col1, col2, col3, col4, col5 = st.beta_columns(5)
    #     print("hello1")
    #     if st.button2("Show Recommendations"):
    #         print("hello2")
    #         col1, col2, col3, col4, col5 = st.columns(5)

    #         with col1:
    #             st.text(recommended_movie_names[0])
    #             st.image(recommended_movie_posters[0])
    #         with col2:
    #             st.text(recommended_movie_names[1])
    #             st.image(recommended_movie_posters[1])

    #         with col3:
    #             st.text(recommended_movie_names[2])
    #             st.image(recommended_movie_posters[2])
    #         with col4:
    #             st.text(recommended_movie_names[3])
    #             st.image(recommended_movie_posters[3])
    #         with col5:
    #             st.text(recommended_movie_names[4])
    #             st.image(recommended_movie_posters[4])







     


            