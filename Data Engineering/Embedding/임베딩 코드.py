# 7683/7683 [1:48:53<00:00,  1.18it/s], token: $0.16

import pandas as pd
from openai import OpenAI
import time
import os
from tqdm import tqdm  # 진행 상황 표시를 위해 사용합니다.

OPENAI_API_KEY = 'OPENAI_API_KEY'


client = OpenAI(
  api_key=OPENAI_API_KEY,  # this is also the default, it can be omitted
)

# 데이터셋 로드
df = pd.read_csv('D:\윤성쓰\대학원관련\개인 프로젝트\데이터\description변수추가\dataset_with_descriptions.csv')


# 임베딩을 저장할 리스트
embeddings = []

# 각 행에 대해 'description' 컬럼의 텍스트로 임베딩 생성
for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
    text = row['description']

    # 임베딩 생성
    try:
        embedding_response = client.embeddings.create(
            model="text-embedding-3-large",  # 최신 임베딩 모델 사용
            input=text
        )
        embedding = embedding_response.data[0].embedding
        embeddings.append(embedding)
    except Exception as e:
        print(f"Error at index {idx}: {e}")
        embeddings.append(None)  # 에러 발생 시 None 추가

    # API 호출량 제한을 준수하기 위해 딜레이 추가 (필요에 따라 조절)
    time.sleep(0.2)

# 임베딩을 데이터프레임에 추가
df['Embeddings'] = embeddings

# 결과를 CSV 파일로 저장 (임베딩은 리스트이므로 문자열로 변환)
df.to_csv('D:\윤성쓰\대학원관련\개인 프로젝트\데이터\임베딩데이터\music_data_with_embeddings.csv', index=False)

print("임베딩 생성 및 저장이 완료되었습니다.")