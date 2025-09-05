import os
import pickle
import numpy as np

# 假设数据文件和此脚本位于同一目录下或指定路径下
# 请确保 data_path 指向您存放 cn.txt, en.txt 等文件的目录
DATA_DIR = "./backend/dldemos/Transformer/data"
CACHE_DIR = "./backend/dldemos/Transformer/data/cache"

# 创建缓存目录
os.makedirs(CACHE_DIR, exist_ok=True)

def load_vocab(lang, data_dir=DATA_DIR):
    """加载词汇表"""
    vocab_path = os.path.join(data_dir, f'{lang}.txt.vocab.tsv')
    word2idx = {'<pad>': 0, '<unk>': 1, '<s>': 2, '</s>': 3}
    idx = len(word2idx)
    with open(vocab_path, 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip().split('\t')[0]
            if word not in word2idx:
                word2idx[word] = idx
                idx += 1
    idx2word = {i: w for w, i in word2idx.items()}
    return word2idx, idx2word

def load_train_data(data_dir=DATA_DIR, cache_dir=CACHE_DIR):
    """加载并缓存处理好的训练数据"""
    cn_cache_path = os.path.join(cache_dir, 'cn_data.pkl')
    en_cache_path = os.path.join(cache_dir, 'en_data.pkl')

    if os.path.exists(cn_cache_path) and os.path.exists(en_cache_path):
        print("Loading data from cache...")
        with open(cn_cache_path, 'rb') as f:
            cn_data = pickle.load(f)
        with open(en_cache_path, 'rb') as f:
            en_data = pickle.load(f)
        return cn_data, en_data

    print("Loading data from source files...")
    cn2idx, _ = load_vocab('cn', data_dir)
    en2idx, _ = load_vocab('en', data_dir)

    cn_path = os.path.join(data_dir, 'cn.txt')
    en_path = os.path.join(data_dir, 'en.txt')

    cn_data, en_data = [], []
    with open(cn_path, 'r', encoding='utf-8') as f_cn, \
         open(en_path, 'r', encoding='utf-8') as f_en:
        for cn_line, en_line in zip(f_cn, f_en):
            cn_tokens = ['<s>'] + cn_line.strip().split() + ['</s>']
            en_tokens = ['<s>'] + en_line.strip().split() + ['</s>']
            cn_ids = [cn2idx.get(t, cn2idx['<unk>']) for t in cn_tokens]
            en_ids = [en2idx.get(t, en2idx['<unk>']) for t in en_tokens]
            cn_data.append(cn_ids)
            en_data.append(en_ids)
    
    # 缓存结果
    with open(cn_cache_path, 'wb') as f:
        pickle.dump(cn_data, f)
    with open(en_cache_path, 'wb') as f:
        pickle.dump(en_data, f)
        
    return cn_data, en_data

def get_batch_indices(n, batch_size, shuffle=True):
    """生成批次索引"""
    indices = np.arange(n)
    if shuffle:
        np.random.shuffle(indices)
    for start in range(0, n, batch_size):
        end = min(start + batch_size, n)
        yield indices[start:end]

def pad_batch(batch_data):
    """对批次数据进行填充"""
    max_len = max(len(seq) for seq in batch_data)
    padded = np.zeros((len(batch_data), max_len), dtype=np.int64)
    for i, seq in enumerate(batch_data):
        padded[i, :len(seq)] = seq
    return padded