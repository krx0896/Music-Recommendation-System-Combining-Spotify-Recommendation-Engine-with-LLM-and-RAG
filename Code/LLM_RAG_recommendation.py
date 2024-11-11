# 필요한 패키지 설치
# pip install openai
# pip install pinecone
# pip install langchain
# pip install spotipy
# pip install langchain_community
# pip install tiktoken

# 필요한 라이브러리 임포트
import pandas as pd
import numpy as np
import ast
import time
import os
import re
import json
import warnings
warnings.filterwarnings('ignore')

from openai import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import SystemMessage, HumanMessage
from langchain.chat_models import ChatOpenAI

from pinecone import Pinecone
from langchain.vectorstores import Pinecone as PineconeVectorStore

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# API KEY 설정
MY_PINECONE_API_KEY = "YOUR_PINECONE_API_KEY"
MY_OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
MY_SPOTIFY_CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID"
MY_SPOTIFY_CLIENT_SECRET = "YOUR_SPOTIFY_CLIENT_SECRET"


## 1. 데이터 로드 (Load Data)

# 데이터 경로 지정
file_path = "file_path"

# 데이터 로드
df = pd.read_csv(file_path, sep=',')

# 임베딩 벡터 문자열을 리스트로 변환
df['Embeddings'] = df['Embeddings'].apply(ast.literal_eval)

# 임베딩 벡터 리스트를 가져옵니다.
embeddings = df['Embeddings'].tolist()

# 첫 번째 임베딩 벡터의 차원 확인
embedding_dimension = len(embeddings[0])

## 2. LangChain과 OpenAI 모델 설정 (LangChain & OpenAI Model Setup)

# OpenAI 클라이언트 인스턴스 생성
client = OpenAI(
    api_key=MY_OPENAI_API_KEY
)

# LLM 인스턴스 생성
llm = ChatOpenAI(
    openai_api_key=MY_OPENAI_API_KEY,
    model_name="gpt-4o",  # 요청에 따라 변경하지 않음
    temperature=0.7
)

# Embeddings 인스턴스 생성
embed_model = OpenAIEmbeddings(
    openai_api_key=MY_OPENAI_API_KEY,
    model="text-embedding-3-large"
)

## 3. Pinecone 벡터 스토어 설정 (Pinecone Vector Store Setup)

# Pinecone 초기화
pc = Pinecone(
    api_key=MY_PINECONE_API_KEY
)

# 인덱스 이름 설정
index_name = 'music-recommendation'

# 인덱스에 연결
index = pc.Index(index_name)

# 벡터 스토어 객체 생성
vectorstore = PineconeVectorStore(
    index=index,
    embedding=embed_model.embed_query,
    text_key='Description'
)

## 4. 사용자 정보 데이터 생성 (User Data Generation)

# 사용자 정보 딕셔너리 생성 (실사용자 데이터로 변경 가능)
user_info = {
    'born': 1999,
    'preferred_genres': ['Pop', 'Acoustic'],
    'favorite_artists': ['Ed Sheeran', 'Taylor Swift'],
    'listened_tracks': ['Shape of You', 'Blank Space']
}

# 사용자 정보를 문자열로 변환
user_info_str = f"Born: {user_info['born']}\n" \
                f"Preferred Genres: {', '.join(user_info['preferred_genres'])}\n" \
                f"Favorite Artists: {', '.join(user_info['favorite_artists'])}\n" \
                f"Listened Tracks: {', '.join(user_info['listened_tracks'])}"

## 5. 추천 시스템 엔진 (Recommendation System Engine)

# Spotipy 클라이언트 설정
client_credentials_manager = SpotifyClientCredentials(
    client_id=MY_SPOTIFY_CLIENT_ID,
    client_secret=MY_SPOTIFY_CLIENT_SECRET
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_recommendations(seed_artists=None, seed_genres=None, seed_tracks=None, target_features=None, limit=10):
    recommendations = sp.recommendations(
        seed_artists=seed_artists,
        seed_genres=seed_genres,
        seed_tracks=seed_tracks,
        limit=limit,
        **(target_features or {})
    )

    # 데이터프레임에 저장할 데이터를 리스트로 준비
    data = []

    for i, track in enumerate(recommendations['tracks']):
        # 기본 트랙 정보 수집
        track_data = {
            "track_name": track['name'],
            "artists": ', '.join([artist['name'] for artist in track['artists']]),
            "preview_url": track['preview_url'],
            "external_urls": track['external_urls']['spotify'],
            "track_id": track['id']
        }

        # 주요 아티스트의 ID 가져오기
        main_artist_id = track['artists'][0]['id'] if track['artists'] else None
        genre_info = "N/A"  # 기본값으로 'N/A' 설정

        # 주요 아티스트의 장르 정보 가져오기
        if main_artist_id:
            artist_info = sp.artist(main_artist_id)
            genre_info = ', '.join(artist_info.get('genres', []))

        # 장르 정보를 트랙 데이터에 추가
        track_data['genre'] = genre_info

        # Audio Features 조회
        audio_features = sp.audio_features(track['id'])[0]

        # Audio Features와 기타 정보 추가
        if audio_features:
            features = {
                "danceability": audio_features.get('danceability'),
                "energy": audio_features.get('energy'),
                "key": audio_features.get('key'),
                "loudness": audio_features.get('loudness'),
                "mode": audio_features.get('mode'),
                "speechiness": audio_features.get('speechiness'),
                "acousticness": audio_features.get('acousticness'),
                "instrumentalness": audio_features.get('instrumentalness'),
                "liveness": audio_features.get('liveness'),
                "valence": audio_features.get('valence'),
                "tempo": audio_features.get('tempo'),
                "duration_ms": audio_features.get('duration_ms'),
                "time_signature": audio_features.get('time_signature')
            }
            track_data.update(features)

        # 수집된 데이터를 리스트에 추가
        data.append(track_data)

    # 데이터프레임 생성
    df = pd.DataFrame(data)
    return df

## 6. 메인 함수 및 사용자 입력 처리 (Main Function & User Input)

def augment_prompt(query: str, results, user_info_str):
    source_knowledge = "\n\n".join([
        f"Song {idx+1}:\n"
        f"Track Name: {res.metadata.get('Track Name') or res.metadata.get('track_name')}\n"
        f"Artists: {res.metadata.get('Artists') or res.metadata.get('artists')}\n"
        f"Genre: {res.metadata.get('Genre') or res.metadata.get('genre')}\n"
        f"Danceability: {res.metadata.get('Danceability') or res.metadata.get('danceability')}\n"
        f"Energy: {res.metadata.get('Energy') or res.metadata.get('energy')}\n"
        f"Key: {res.metadata.get('Key') or res.metadata.get('key')}\n"
        f"Loudness: {res.metadata.get('Loudness') or res.metadata.get('loudness')}\n"
        f"Mode: {res.metadata.get('Mode') or res.metadata.get('mode')}\n"
        f"Speechiness: {res.metadata.get('Speechiness') or res.metadata.get('speechiness')}\n"
        f"Acousticness: {res.metadata.get('Acousticness') or res.metadata.get('acousticness')}\n"
        f"Instrumentalness: {res.metadata.get('Instrumentalness') or res.metadata.get('instrumentalness')}\n"
        f"Liveness: {res.metadata.get('Liveness') or res.metadata.get('liveness')}\n"
        f"Valence: {res.metadata.get('Valence') or res.metadata.get('valence')}\n"
        f"Tempo: {res.metadata.get('Tempo') or res.metadata.get('tempo')}\n"
        f"Description: {res.page_content}"
        for idx, res in enumerate(results)
    ])

    # Spotify API parameter definitions
    hyperparameter_definitions = """
    Spotify API Hyperparameter Definitions:
    - `seed_genres`: A list of genres relevant to the user's query and preferences. Up to 5 seed values may be provided.
    - `min_acousticness`, `max_acousticness`, `target_acousticness`: Numeric values between 0.0 and 1.0 specifying the minimum, maximum, and target acousticness of the tracks.
    - `min_danceability`, `max_danceability`, `target_danceability`: Numeric values between 0.0 and 1.0 specifying the minimum, maximum, and target danceability.
    - `min_energy`, `max_energy`, `target_energy`: Numeric values between 0.0 and 1.0 specifying the minimum, maximum, and target energy.
    - `min_instrumentalness`, `max_instrumentalness`, `target_instrumentalness`: Numeric values between 0.0 and 1.0 specifying the minimum, maximum, and target instrumentalness.
    - `min_liveness`, `max_liveness`, `target_liveness`: Numeric values between 0.0 and 1.0 specifying the minimum, maximum, and target liveness.
    - `min_loudness`, `max_loudness`, `target_loudness`: Numeric values specifying the minimum, maximum, and target loudness in decibels (dB). Values typically range between -60 and 0 dB.
    - `min_mode`, `max_mode`, `target_mode`: Integer values 0 or 1 specifying the modality (minor or major) of the tracks.
    - `min_speechiness`, `max_speechiness`, `target_speechiness`: Numeric values between 0.0 and 1.0 specifying the minimum, maximum, and target speechiness.
    - `min_tempo`, `max_tempo`, `target_tempo`: Numeric values specifying the minimum, maximum, and target tempo in beats per minute (BPM).
    - `min_valence`, `max_valence`, `target_valence`: Numeric values between 0.0 and 1.0 specifying the minimum, maximum, and target valence.
    - Other Parameters: Similar patterns apply for other audio features like `key`.
    Note: Only include parameters that are relevant and based on significant trends in the provided song options. Use values within the specified ranges.
    """

    augmented_prompt = f"""You are an assistant that generates hyperparameters for a song recommendation engine.

---

Instructions for Generating Hyperparameters:

**Instructions for generating `target_features`:**
- Analyze Trends: Examine the provided song options to identify consistent trends or values in audio features.
- Set Appropriate Parameters: Based on these trends, set the corresponding Spotify API parameters (`min_*`, `max_*`, `target_*`).
  - For example, if most songs have a `danceability` above 0.7, you might set `min_danceability` to 0.7.
  - If the `energy` values cluster around 0.6, you might set `target_energy` to 0.6.

**Instructions for generating `seed_genres`:**
- Select Relevant Seed Genres:
  - Identify genres from the song options and the user's query that match the user's preferences or the mood described.
  - Include up to 5 genres that are most relevant.
  - For example, if the user's query mentions "calm and emotional rainy day," include genres like "acoustic" or "singer-songwriter".

- Formatting Guidelines:
  - Do not provide any explanations or additional text; output only the hyperparameters.

Based on the user's query, the provided song options, and the user's history data, generate the hyperparameters in the following format:
"seed_genres": [...], "target_features": {{"feature_name": value, ...}}


User Query:
{query}

User Info:
{user_info_str}

Here are some song options:
{source_knowledge}

Please generate the hyperparameters accordingly.
"""

    return augmented_prompt

def main():
    # 사용자로부터 쿼리 입력 받기
    query = input("Enter your music preference query: ")

    # 유사도 검색 수행
    results = vectorstore.similarity_search(query, k=10)

    # 프롬프트 생성
    prompt = augment_prompt(query, results, user_info_str)

    messages = [
        SystemMessage(content="You are an assistant that generates hyperparameters for a song recommendation engine."),
        HumanMessage(content=prompt)
    ]

    # LLM을 사용하여 응답 생성
    response = llm(messages)

    # LLM의 응답 내용
    content1 = response.content.strip()

    # Remove any code block markers like ```json or ```
    content1 = re.sub(r'^```[a-z]*\n', '', content1)
    content1 = re.sub(r'\n```$', '', content1)
    content1 = content1.strip()

    # Ensure the content is enclosed within curly braces {}
    if not content1.startswith('{'):
        content1 = '{' + content1
    if not content1.endswith('}'):
        content1 = content1 + '}'

    # Count the number of opening and closing braces
    open_braces = content1.count('{')
    close_braces = content1.count('}')

    # Add missing closing braces
    while close_braces < open_braces:
        content1 += '}'
        close_braces += 1

    # Parse the JSON content
    try:
        hyperparameters = json.loads(content1)
        seed_genres = hyperparameters.get('seed_genres', [])
        target_features = hyperparameters.get('target_features', {})
    except json.JSONDecodeError as e:
        print(f"Error parsing hyperparameters: {e}")
        return

    # 추천 함수 호출
    recommendation_df = get_recommendations(
        seed_genres=seed_genres,
        target_features=target_features,
        limit=30
    )

    # 추천 결과 출력
    for idx, row in recommendation_df.iterrows():
        print(f"{idx + 1}. {row['track_name']} - {row['artists']}")
        print(f"   Genre: {row['genre']}")
        print(f"   Preview URL: {row['preview_url']}")
        print(f"   Spotify URL: {row['external_urls']}\n")

if __name__ == "__main__":
    main()