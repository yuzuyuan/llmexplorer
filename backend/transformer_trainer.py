import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import time
import os
import spacy
import jieba
import math
import numpy as np
import traceback
import json
# --- 1. 模型定义 (保持不变) ---
# 这里的模型结构与您原有的保持一致
class Transformer(nn.Module):
    def __init__(self,
                 src_vocab_size,
                 trg_vocab_size,
                 d_model,
                 nhead,
                 num_encoder_layers,
                 num_decoder_layers,
                 dim_feedforward,
                 dropout,
                 device,
                 pad_idx):
        super().__init__()
        self.device = device
        self.pad_idx = pad_idx
        
        self.embedding_src = nn.Embedding(src_vocab_size, d_model)
        self.embedding_trg = nn.Embedding(trg_vocab_size, d_model)
        # 使用固定的sin/cos位置编码，更稳定
        self.pos_encoder = PositionalEncoding(d_model, dropout)
        self.transformer = nn.Transformer(d_model, nhead, num_encoder_layers, num_decoder_layers, dim_feedforward, dropout, batch_first=True)
        self.fc = nn.Linear(d_model, trg_vocab_size)
        self.dropout = nn.Dropout(dropout)

    def _generate_square_subsequent_mask(self, sz):
        mask = (torch.triu(torch.ones(sz, sz, device=self.device)) == 1).transpose(0, 1)
        mask = mask.float().masked_fill(mask == 0, float('-inf')).masked_fill(mask == 1, float(0.0))
        return mask

    def _create_padding_mask(self, seq):
        return (seq == self.pad_idx).to(self.device)

    def forward(self, src, trg):
        # src: [batch_size, src_len]
        # trg: [batch_size, trg_len]
        src_padding_mask = self._create_padding_mask(src)
        trg_padding_mask = self._create_padding_mask(trg)
        trg_mask = self._generate_square_subsequent_mask(trg.size(1))

        embed_src = self.pos_encoder(self.embedding_src(src))
        embed_trg = self.pos_encoder(self.embedding_trg(trg))
        
        out = self.transformer(embed_src, embed_trg,
                               src_mask=None, # Encoder self-attention mask
                               tgt_mask=trg_mask,
                               memory_mask=None, # Encoder-Decoder attention mask
                               src_key_padding_mask=src_padding_mask,
                               tgt_key_padding_mask=trg_padding_mask,
                               memory_key_padding_mask=src_padding_mask)
        return self.fc(out)

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)

# --- 2. 损失函数 (保持不变) ---
class LabelSmoothing(nn.Module):
    def __init__(self, size, padding_idx, smoothing=0.1):
        super(LabelSmoothing, self).__init__()
        self.criterion = nn.KLDivLoss(reduction='sum')
        self.padding_idx = padding_idx
        self.confidence = 1.0 - smoothing
        self.smoothing = smoothing
        self.size = size

    def forward(self, x, target):
        assert x.size(1) == self.size
        true_dist = x.data.clone()
        true_dist.fill_(self.smoothing / (self.size - 2))
        true_dist.scatter_(1, target.data.unsqueeze(1), self.confidence)
        true_dist[:, self.padding_idx] = 0
        mask = torch.nonzero(target.data == self.padding_idx, as_tuple=False)
        if mask.dim() > 0:
            true_dist.index_fill_(0, mask.squeeze(), 0.0)
        return self.criterion(x, true_dist.clone().detach())

# --- 3. 数据加载 (全新，来自参考文件) ---
def tokenize_cn(text):
    return list(jieba.cut(text))

def tokenize_en(text, spacy_en):
    return [tok.text for tok in spacy_en.tokenizer(text)]
    
def load_data(src_path, tgt_path, spacy_en):
    logs = []
    src_sents, tgt_sents = [], []
    with open(src_path, 'r', encoding='utf-8') as f_src, \
         open(tgt_path, 'r', encoding='utf-8') as f_tgt:
        for src_line, tgt_line in zip(f_src, f_tgt):
            src_sents.append(['<sos>'] + tokenize_cn(src_line.strip()) + ['<eos>'])
            tgt_sents.append(['<sos>'] + tokenize_en(tgt_line.strip(), spacy_en) + ['<eos>'])
    logs.append(f"日志: 从 {src_path} 和 {tgt_path} 加载了 {len(src_sents)} 个句子对。")
    return src_sents, tgt_sents, logs

def build_vocab(sentences, min_freq=2):
    word_counts = {}
    for sent in sentences:
        for word in sent:
            word_counts[word] = word_counts.get(word, 0) + 1
            
    specials = ['<unk>', '<pad>', '<sos>', '<eos>']
    vocab = {word: i for i, word in enumerate(specials)}
    idx = len(specials)
    
    for word, count in word_counts.items():
        if count >= min_freq and word not in vocab:
            vocab[word] = idx
            idx += 1
            
    vocab.setdefault('<unk>', 0)
    return vocab

def numericalize(sentences, vocab):
    unk_idx = vocab['<unk>']
    return [[vocab.get(token, unk_idx) for token in sent] for sent in sentences]

def get_batch_indices(n, batch_size, shuffle=True):
    indices = np.arange(n)
    if shuffle:
        np.random.shuffle(indices)
    for start in range(0, n, batch_size):
        end = min(start + batch_size, n)
        yield indices[start:end]

def pad_batch(batch_data, pad_idx):
    max_len = max(len(seq) for seq in batch_data)
    padded = np.full((len(batch_data), max_len), pad_idx, dtype=np.int64)
    for i, seq in enumerate(batch_data):
        padded[i, :len(seq)] = seq
    return torch.from_numpy(padded)


# --- 4. 训练循环 (微调以适应新数据格式) ---
def run_epoch(X_data, Y_data, model, criterion, optimizer, batch_size, device):
    model.train()
    total_loss = 0
    total_tokens = 0

    batch_indices_generator = get_batch_indices(len(X_data), batch_size)

    for indices in batch_indices_generator:
        src_batch_raw = [X_data[i] for i in indices]
        trg_batch_raw = [Y_data[i] for i in indices]

        src_batch = pad_batch(src_batch_raw, model.pad_idx).to(device)
        trg_batch = pad_batch(trg_batch_raw, model.pad_idx).to(device)
        
        trg_input = trg_batch[:, :-1]
        trg_target = trg_batch[:, 1:]
        
        optimizer.zero_grad()
        
        # batch_first=True, so output shape is [batch_size, seq_len, vocab_size]
        output = model(src_batch, trg_input)
        
        output_flat = output.reshape(-1, output.shape[-1])
        trg_target_flat = trg_target.reshape(-1)
        
        loss = criterion(F.log_softmax(output_flat, dim=-1), trg_target_flat)
        loss.backward()
        
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        
        # criterion返回的是sum loss，所以要除以token数
        total_loss += loss.item()
        total_tokens += (trg_target_flat != model.pad_idx).sum().item()

    return total_loss / total_tokens if total_tokens > 0 else 0


# --- 主函数 (重构) ---
def start_training_process(config, data_path,learning_rate=0.0001,epoches =5):
    # Helper to yield structured JSON data
    def yield_data(data_type, content):
        return json.dumps({"type": data_type, "payload": content}) + "\n"

    try:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        yield yield_data("log", f"日志: 使用设备: {device}")

        src_file_path = os.path.join(data_path, 'train.cn')
        tgt_file_path = os.path.join(data_path, 'train.en')
        
        yield yield_data("log", "日志: 正在加载 Spacy 英文模型...")
        spacy_en = spacy.load('en_core_web_sm')
        
        # 1. 加载和分词
        src_sents, tgt_sents, data_logs = load_data(src_file_path, tgt_file_path, spacy_en)
        for log in data_logs:
            yield yield_data("log", log)
        
        # 2. 构建词典
        cn_vocab = build_vocab(src_sents, min_freq=2)
        en_vocab = build_vocab(tgt_sents, min_freq=2)
        pad_idx = cn_vocab['<pad>']
        
        yield yield_data("log", "日志: 中英数据集已成功加载。")
        yield yield_data("log", f"日志: 源语言 (中) 词典大小: {len(cn_vocab)}")
        yield yield_data("log", f"日志: 目标语言 (英) 词典大小: {len(en_vocab)}")
        
        # 3. 文本数值化
        X_data = numericalize(src_sents, cn_vocab)
        Y_data = numericalize(tgt_sents, en_vocab)

        # 4. 初始化模型
        src_vocab_size = len(cn_vocab)
        trg_vocab_size = len(en_vocab)
        
        model = Transformer(
            src_vocab_size=src_vocab_size,
            trg_vocab_size=trg_vocab_size,
            d_model=config.get('embed_dim', 512),
            nhead=config.get('heads', 8),
            num_encoder_layers=config.get('num_encoder_layers', 6),
            num_decoder_layers=config.get('num_decoder_layers', 6),
            dim_feedforward=config.get('ff_dim', 2048),
            dropout=config.get('dropout', 0.1),
            device=device,
            pad_idx=pad_idx
        ).to(device)

        yield yield_data("log", "日志: 模型已根据动态配置初始化:")
        yield yield_data("log", str(config))

        optimizer = optim.Adam(model.parameters(), lr=learning_rate, betas=(0.9, 0.98), eps=1e-9)
        criterion = LabelSmoothing(size=trg_vocab_size, padding_idx=pad_idx, smoothing=0.1)

        num_epochs = epoches
        batch_size = config.get('batch_size', 32)
        yield yield_data("log", f"日志: 开始训练，共 {num_epochs} 个 Epoch，批次大小为 {batch_size}。")

        for epoch in range(num_epochs):
            start_time = time.time()
            
            train_loss = run_epoch(X_data, Y_data, model, criterion, optimizer, batch_size, device)
            
            end_time = time.time()
            epoch_mins = int((end_time - start_time) / 60)
            epoch_secs = int((end_time - start_time) - (epoch_mins * 60))
            
            train_ppl = math.exp(train_loss)
            
            log_msg = f"Epoch: {epoch + 1:02} | 耗时: {epoch_mins}m {epoch_secs}s | 训练损失: {train_loss:.3f} | 训练困惑度: {train_ppl:7.3f}"
            
            # Yield both a log message and structured metric data
            yield yield_data("log", log_msg)
            yield yield_data("metric", {
                "epoch": epoch + 1,
                "loss": round(train_loss, 3),
                "ppl": round(train_ppl, 3)
            })
            
        yield yield_data("log", "日志: 训练完成。")

    except FileNotFoundError as e:
        yield yield_data("log", f"错误: 依赖文件未找到 - {e}")
        yield yield_data("log", "提示: 请确保 Spacy 英文模型 'en_core_web_sm' 已下载 (python -m spacy download en_core_web_sm)。")
        yield yield_data("log", f"提示: 并确保在 '{data_path}' 目录下有 train.cn 和 train.en 文件。")
    except Exception as e:
        yield yield_data("log", f"严重错误: 训练过程中断 - {e}")
        yield yield_data("log", traceback.format_exc())