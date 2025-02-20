import pickle
from tensorflow.keras.preprocessing.text import Tokenizer
from etc.etc import KST_now
import os

# 케라스 토크나이저 설정
def set_tokenizer(corpus, vocab_size, oov, save_path):
    '''
    :param corpus: 토크나이징할 문장 데이터
    :param vocab_size: 설정할 어휘집합의 수
    :param oov: 어휘집합에 포함되지 않은 단어를 어떻게 표시할지
    :param save_path: 토크나이저 저장 경로
    :return: 토크나이저 경로, 토크나이저 객체
    '''
    if oov:
        oov_token = "OOV"
        tokenizer = Tokenizer(num_words=vocab_size + 1, oov_token=oov_token)
    else:
        tokenizer = Tokenizer(num_words=vocab_size + 1)

    tokenizer.fit_on_texts(corpus)
    print(f"Total {len(tokenizer.word_index)} words in tokenizer.")  # 총 어휘 인덱스에 몇 개 있는지. 그 중에서 사용하는 집합은 제한되어 있음.
    print(f"Tokened Results: {tokenizer.word_index}")

    now = KST_now()
    tok_dir = f"{save_path}/tokenizer"
    tok_name = f"{tok_dir}/tok-{now}"

    if not os.path.exists(tok_dir):
        os.makedirs(tok_dir)

    with open(f"{tok_dir}/tokenizer_info.txt", "a+", encoding="utf-8") as f:
        if oov:
            data = f"\ndatetime : {now}, tokenizer : {tok_name}, num_words : {vocab_size + 1}, oov : {oov_token}\n"
        else:
            data = f"\ndatetime : {now}, tokenizer : {tok_name}, num_words : {vocab_size + 1}, oov : check dropped indices.\n"
        f.write(data)

    with open(f"{tok_name}.pickle", 'wb') as tok_f:
        pickle.dump(tokenizer, tok_f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"Done setting Keras tokenizer! Check {tok_name}.pickle!")
    print("\n")

    return f"{tok_name}.pickle", tokenizer

# 케라스 토크나이저를 이용해 문장 토크나이징
def tokenize(corpus, tok):
    '''
    :param corpus: 토크나이징할 문장
    :param tok: 케라스 토크나이저 객체
    :return: 토큰화된 문장, 토크나이징 후 빈 문장 인덱스
    '''
    tokens = tok.texts_to_sequences(corpus)
    print(f"Total {len(tokens)} amounts of tokens.")
    print(f"Sample tokens : {tokens[:3]}")
    drop_indices = [idx for idx, sent in enumerate(tokens) if len(sent) < 1]
    return tokens, drop_indices

# 최소 빈도 이하의 문장 체크
def check_freq(thre, corpus):
    '''
    :param thre: 해당 빈도 이하의 문장을 체크하기 위한 기준 수
    :param corpus: 문장 데이터
    :return: 전체 문장 수, 희귀 문장 수, thre로 설정했을 때 어휘집합의 수
    '''
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(corpus)

    total_cnt = len(tokenizer.word_index)
    rare_cnt = 0
    total_freq = 0
    rare_freq = 0
    for key, val in tokenizer.word_counts.items():
        total_freq += val
        if val < thre:
            rare_cnt += 1
            rare_freq += val

    vocab_size = total_cnt - rare_cnt + 1

    print(f"Minimum Threshold : {thre}")
    print(f"Total Vocabs : {total_cnt}")
    print(f"Rare Vocabs : {rare_cnt}")
    print(f"Rare Cnt Proportion : {(rare_cnt/total_cnt)*100}%")
    print(f"Rare Freq Proportion : {(rare_freq/total_freq)*100}%")

    return total_cnt, rare_cnt, vocab_size