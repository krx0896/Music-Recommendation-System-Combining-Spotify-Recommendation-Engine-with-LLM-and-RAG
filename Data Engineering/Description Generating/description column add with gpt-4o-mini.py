# 100개당 0.04토큰($3.35/7683개)

import pandas as pd
from openai import OpenAI
import time
import os

df = pd.read_csv("D:\윤성쓰\대학원관련\개인 프로젝트\데이터\description변수추가\spotify_data_description_only_7683개.csv", sep=",")

OPENAI_API_KEY = 'OPENAI_API_KEY'


client = OpenAI(
  api_key=OPENAI_API_KEY,  # this is also the default, it can be omitted
)

# 데이터셋 로드
# df = pd.read_csv('your_dataset.csv')
# 이미 df가 로드되어 있다고 가정합니다.

# description 컬럼이 없으면 생성
if 'description' not in df.columns:
    df['description'] = ''

# Few-shot 예시 정의
examples = [
    {
        "track_genre": "Pop",
        "artists": "Maroon 5",
        "track_name": "Sugar",
        "lyrics": "I'm hurting baby I'm broken down I need your loving loving I need it now When I'm without you I'm something weak You got me begging begging I'm on my knees I don't wanna be needing your love I just wanna be deep in your love And it's killing me when you're away Ooh baby cause a bullet don't care where you are I just wanna be there where you are And I gotta get one little taste Sugar Yes please Won't you come and put it down on me Oh right here cause I need Little love and little sympathy Yeah you show me good loving Make it alright Need a little a sweetness in my life Sugar Yes please Won't you come and put it down on me My broken pieces You put them up Don't leave me hanging hanging Come get me some When I'm without ya So insecure You are the one thing one thing I'm living for I don't wanna be needing your love I just wanna be deep in your love And it's killing me when you're away Ooh baby cause a bullet don't care where you are I just wanna be there where you are And I gotta get one little taste Sugar Yes please Won't you come and put it down on me Oh right here cause I need Little love and little sympathy Yeah you show me good loving Make it alright Need a little a sweetness in my life Sugar Yes please Won't you come and put it down on me Yeah I want that red velvet I want that sugar sweet Don't let nobody touch it Unless that somebody is me I gotta be a man There ain't no other way Cause girl you're hotter than southern california day I don't wanna play no games I don't gotta be afraid Don't give all that shy sht No make up on That's my Sugar Yes please Won't you come and put it down on me Oh right here cause I need Little love and little sympathy Yeah you show me good loving Make it alright Need a little a sweetness in my life Sugar Yes please Won't you come and put it down on me Sugar Yes please Won't you come and put it down on me Oh right here cause I need Little love and little sympathy Yeah you show me good loving Make it alright Need a little a sweetness in my life Sugar Yes please Won't you come and put it down on me",
        "description": "The theme of Maroon 5's Sugar is a lighthearted celebration of love and desire, with a focus on the sweet and irresistible nature of romantic attraction. The lyrics depict a person 's intense desire to be loved and accepted by their significant other. They want to be close to their partner and feel insecure when they are apart. The song is upbeat and energetic, with a focus on the need for love and affection."
    },
    {
        "track_genre": "Hip-Hop",
        "artists": "Eminem",
        "track_name": "Stan (feat. Dido)",
        "lyrics": "My tea's gone cold, I'm wondering why I Got out of bed at all The morning rain clouds up my window (Window) And I can't see at all And even if I could, it'd all be grey But your picture on my wall It reminds me that it's not so bad, it's not so bad (Bad) My tea's gone cold, I'm wondering why I Got out of bed at all The morning rain clouds up my window (Window) And I can't see at all And even if I could, it'd all be grey But your picture on my wall It reminds me that it's not so bad, it's not so bad (Bad) Dear Slim, I wrote you, but you still ain't callin' I left my cell, my pager and my home phone at the bottom I sent two letters back in autumn, you must not've got 'em There prob'ly was a problem at the post office or somethin' Sometimes I scribble addresses too sloppy when I jot 'em But anyways, fuck it, what's been up, man? How's your daughter? My girlfriend's pregnant too, I'm 'bout to be a father If I have a daughter, guess what I'ma call her? I'ma name her Bonnie I read about your Uncle Ronnie too, I'm sorry I had a friend kill himself over some bitch who didn't want him I know you prob'ly hear this every day, but I'm your biggest fan I even got the underground shit that you did with Skam I got a room full of your posters and your pictures, man I like the shit you did with Rawkus too, that shit was phat Anyways, I hope you get this, man, hit me back Just to chat, truly yours, your biggest fan, this is Stan My tea's gone cold, I'm wondering why I Got out of bed at all The morning rain clouds up my window (Window) And I can't see at all And even if I could, it'd all be grey But your picture on my wall It reminds me that it's not so bad, it's not so bad (Bad) Dear Slim, you still ain't called or wrote, I hope you have a chance I ain't mad, I just think it's fucked up you don't answer fans If you didn't want to talk to me outside your concert, you didn't have to But you coulda signed an autograph for Matthew That's my little brother, man, he's only six years old We waited in the blisterin' cold for you, for four hours, and you just said, no That's pretty shitty, man, you're like his fuckin' idol He wants to be just like you, man, he likes you more than I do I ain't that mad, though I just don't like bein' lied to Remember when we met in Denver? You said if I'd write you, you would write back See, I'm just like you in a way: I never knew my father neither He used to always cheat on my mom and beat her I can relate to what you're sayin' in your songs So when I have a shitty day, I drift away and put 'em on 'Cause I don't really got shit else, so that shit helps when I'm depressed I even got a tattoo with your name across the chest Sometimes I even cut myself to see how much it bleeds It's like adrenaline, the pain is such a sudden rush for me See, everything you say is real, and I respect you 'cause you tell it My girlfriend's jealous 'cause I talk about you 24/7 But she don't know you like I know you, Slim, no one does She don't know what it was like for people like us growin' up You gotta call me, man, I'll be the biggest fan you'll ever lose Sincerely yours, Stan, PS: We should be together too My tea's gone cold, I'm wondering why I Got out of bed at all The morning rain clouds up my window (Window) And I can't see at all And even if I could, it'd all be grey But your picture on my wall It reminds me that it's not so bad, it's not so bad (Bad) Dear Mr. I'm-Too-Good-to-Call-or-Write-My-Fans This'll be the last package I ever send your ass It's been six months, and still no word, I don't deserve it? I know you got my last two letters, I wrote the addresses on 'em perfect So this is my cassette I'm sendin' you, I hope you hear it I'm in the car right now, I'm doin' ninety on the freeway Hey, Slim, I drank a fifth of vodka, you dare me to drive? You know the song by Phil Collins, In the Air of the Night About that guy who coulda saved that other guy from drownin' But didn't, then Phil saw it all, then at a show he found him? That's kinda how this is: You coulda rescued me from drownin' Now it's too late, I'm on a thousand downers now, I'm drowsy And all I wanted was a lousy letter or a call I hope you know I ripped all of your pictures off the wall I loved you, Slim, we coulda been together, think about it You ruined it now, I hope you can't sleep and you dream about it And when you dream, I hope you can't sleep and you scream about it I hope your conscience eats at you, and you can't breathe without me See, Slim, shut up, bitch! I'm tryna talk Hey, Slim, that's my girlfriend screamin' in the trunk But I didn't slit her throat, I just tied her up, see? I ain't like you 'Cause if she suffocates she'll suffer more and then she'll die too Well, gotta go, I'm almost at the bridge now Oh, shit, I forgot, how am I supposed to send this shit out?! My tea's gone cold, I'm wondering why I Got out of bed at all The morning rain clouds up my window (Window) And I can't see at all And even if I could, it'd all be grey But your picture on my wall It reminds me that it's not so bad, it's not so bad (Bad) Dear Stan, I meant to write you sooner, but I just been busy You said your girlfriend's pregnant now, how far along is she? Look, I'm really flattered you would call your daughter that And here's an autograph for your brother, I wrote it on a Starter cap I'm sorry I didn't see you at the show, I must've missed you Don't think I did that shit intentionally just to diss you But what's this shit you said about you like to cut your wrists too? I say that shit just clownin', dawg, come on, how fucked up is you? You got some issues, Stan, I think you need some counselin' To help your ass from bouncin' off the walls when you get down some And what's this shit about us meant to be together? That type of shit'll make me not want us to meet each other I really think you and your girlfriend need each other Or maybe you just need to treat her better I hope you get to read this letter, I just hope it reaches you in time Before you hurt yourself, I think that you'll be doin' just fine If you relax a little, I'm glad I inspire you, but, Stan Why are you so mad? Try to understand that I do want you as a fan I just don't want you to do some crazy shit I seen this one shit on the news a couple weeks ago that made me sick Some dude was drunk and drove his car over a bridge And had his girlfriend in the trunk, and she was pregnant with his kid And in the car, they found a tape, but they didn't say who it was to Come to think about it, his name was, it was you Damn",
        "description": "The theme of Eminem's Stan (feat. Dido) is a poignant exploration of despair, admiration, and the emotional struggles that accompany isolation and the longing for connection. The lyrics depict a sense of despair and longing, as the narrator struggles with feelings of isolation and uncertainty. The imagery of rain and a foggy window symbolizes emotional barriers and a lack of clarity in life. The narrator expresses a deep admiration for a figure in the music industry, sharing personal struggles and aspirations, including impending fatherhood. This connection highlights themes of fandom and the desire for recognition. Ultimately, the song conveys a mix of melancholy and hope, suggesting that despite hardships, there are moments of solace and reminders that life can improve."
    },
    {
        "track_genre": "Rock",
        "artists": "Queen",
        "track_name": "We Will Rock You",
        "lyrics": "Buddy you're a boy make a big noise Playin' in the street gonna be a big man some day You got mud on yo' face You big disgrace Kickin' your can all over the place Singin' 'We will we will rock you We will we will rock you' Buddy you're a young man hard man Shoutin' in the street gonna take on the world some day You got blood on yo' face You big disgrace Wavin' your banner all over the place 'We will we will rock you' Singin' 'We will we will rock you' Buddy you're an old man poor man Pleadin' with your eyes gonna make you some peace some day You got mud on your face You big disgrace Somebody better put you back into your place 'We will we will rock you' Singin' 'We will we will rock you' Everybody 'We will we will rock you' 'We will we will rock you' Alright.",
        "description": "The theme of Queen's We Will Rock You is a powerful anthem of resilience and strength, emphasizing defiance, unity, and the determination to overcome challenges. The lyrics depict a journey through life, highlighting the struggles and aspirations of individuals at different stages. It begins with a young man full of ambition, facing challenges and societal expectations, symbolized by the mud and blood on his face. As he grows older, he becomes a figure of resilience, still fighting against adversity. The repeated chant serves as a rallying cry, emphasizing unity and determination. The emotions conveyed range from defiance to hope, capturing the essence of perseverance in the face of life′s obstacles. Ultimately, it celebrates the spirit of overcoming challenges."
    },
    {
        "track_genre": "K-Pop",
        "artists": "ITZY",
        "track_name": "ICY",
        "lyrics": "Hey hey hey yass whoo Beep beep Hey hey hey hey hey hey I see that I'm icy Go rising up up I see that I'm icy 차갑게 보여도 어떡해 Cool한 나니까 눈치 볼 마음 없어 Oh Come on 당당하게 Let it go Here we go 길거리를 누비고 On a roll Background music이 깔려 Bomb bomb bomb bomb Icy but I'm on fire 내 안에 있는 Dream 난 자신 있어 날 봐 I'm not a liar 너의 틀에 날 맞출 맘은 없어 (Dance) 다들 Blah blah 참 말 많아 난 괜찮아 계속 Blah blah They keep talkin' I keep walkin' 다들 Blah blah 참 말 많아 난 괜찮아 계속 Blah blah They keep talkin' I keep walkin' Ring ring ring 울려 All day long 모두 날 찾느라 바빠 이 노래가 Your favorite song 그렇게 될 걸 잘 알아 Hey 이 맛은 마치 딱 살얼음같이 Bling bling bling 반짝이는 걸 별빛같이 Icy Uhh shout out to 내 엄마 Thank you to 우리 Papa 좋은 것만 쏙 빼닮아 짠짠짜짠짠짠 당당하게 Let it go Here we go 길거리를 누비고 On a roll Background music이 깔려 Bomb bomb bomb bomb Icy but I'm on fire 내 안에 있는 Dream 난 자신 있어 날 봐 I'm not a liar 너의 틀에 날 맞출 맘은 없어 다들 Blah blah 참 말 많아 난 괜찮아 계속 Blah blah They keep talkin' I keep walkin' 다들 Blah blah 참 말 많아 난 괜찮아 계속 Blah blah They keep talkin' I keep walkin' Get it Hey Shake it Hey Yeah come on girls 더더 빨리 달려 Don't care what they say 내 답은 내가 아니까 It's ok (Dance) Up up up up up we go 끝없이 위로 위로 절대 멈추지 않고 No one can stop us now Blah blah 참 말 많아 난 괜찮아 계속 Blah blah They keep talkin' I keep walkin' 다들 Blah blah 참 말 많아 난 괜찮아 계속 Blah blah They keep talkin' I keep walkin' I see that I'm icy I see that I'm icy I see that I'm icy I see that I'm icy",
        "description": "The theme of ITZY's ICY is a bold expression of self-confidence and resilience, celebrating individuality and a carefree attitude toward others' opinions. The song emphasizes empowerment and staying true to oneself despite external judgment. The song ′Icy′ expresses confidence and self-assurance in the face of criticism and judgment. The lyrics convey a message of staying true to oneself and not being swayed by others′ opinions. The song′s upbeat and energetic tone reflects a sense of empowerment and determination to keep moving forward despite the negativity. The use of ′icy′ and ′fire′ imagery represents the duality of being cool and confident while also being passionate and driven. Overall, the song conveys a message of self-empowerment and resilience."
    }
]

# 프롬프트 생성 함수 정의
def create_prompt(row):
    prompt = "The following are examples of song descriptions based on their lyrics:\n\n"
    for ex in examples:
        prompt += f"Song Information:\nGenre: {ex['track_genre']}\nArtist: {ex['artists']}\nTitle: {ex['track_name']}\nLyrics: {ex['lyrics']}\nDescription: {ex['description']}\n\n"
    prompt += f"Now, based on the lyrics of the following song, please provide a summary describing the theme and mood of the song in English.\n\n"
    prompt += f"Song Information:\nGenre: {row['track_genre']}\nArtist: {row['artists']}\nTitle: {row['track_name']}\nLyrics: {row['lyrics']}\nDescription:"
    return prompt

# API 호출을 위한 함수 정의
def get_description(row):
    prompt = create_prompt(row)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes song themes and moods based on lyrics."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=180,
            temperature=0.7,
            top_p=0.9,
            frequency_penalty=0,
            presence_penalty=0
        )
        description = response.choices[0].message.content.strip()
        return description
    except Exception as e:
        print(f"Error processing row {row.name}: {e}")
        return None

# 배치 처리 및 진행 상황 표시 설정
batch_size = 100
total_rows = len(df)
start_time = time.time()

for start_idx in range(0, total_rows, batch_size):
    end_idx = min(start_idx + batch_size, total_rows)
    batch = df.iloc[start_idx:end_idx]

    print(f"Processing batch {start_idx+1} to {end_idx} of {total_rows}")

    # 배치 내에서 각 행 처리
    for idx_in_batch, (index, row) in enumerate(batch.iterrows(), start=1):
        # 이미 description이 존재하면 건너뜁니다.
        if pd.notnull(row['description']) and row['description'] != '':
            continue

        row_start_time = time.time()  # 각 행 처리 시작 시간 기록

        description = get_description(row)
        df.at[index, 'description'] = description

        row_elapsed_time = time.time() - row_start_time  # 각 행 처리 시간 계산
        total_elapsed_time = time.time() - start_time  # 전체 누적 시간 계산

        # 현재 진행 상황 및 소요 시간 출력
        print(f"Processed {index+1}/{total_rows} rows | Time taken: {row_elapsed_time:.2f} sec | Total elapsed time: {total_elapsed_time:.2f} sec")

        # 결과 저장 주기
        if (index + 1) % 100 == 0:
            df.to_csv('dataset_with_descriptions_backup.csv', index=False)
            print(f"Backup saved at index {index+1}")

# 최종 결과 저장
df.to_csv('D:\윤성쓰\대학원관련\개인 프로젝트\데이터\description변수추가\dataset_with_descriptions.csv', index=False)
print("Processing complete. Final dataset saved.")