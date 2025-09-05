import torch
import torch.nn as nn
import torch.optim as optim
import time
import os
import spacy
import jieba
from torch.utils.data import DataLoader, Dataset
from torch.nn.utils.rnn import pad_sequence

# 导入现代 torchtext 的词典构建工具
from torchtext.vocab import build_vocab_from_iterator

# --- 1. 模型定义 (保持不变) ---
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
                 pad_idx): # 增加 pad_idx
        super().__init__()
        self.device = device
        self.embedding_src = nn.Embedding(src_vocab_size, d_model)
        self.embedding_trg = nn.Embedding(trg_vocab_size, d_model)
        self.pos_encoder = nn.Parameter(torch.zeros(1, 512, d_model))
        self.transformer = nn.Transformer(d_model, nhead, num_encoder_layers, num_decoder_layers, dim_feedforward, dropout, batch_first=False) # batch_first=False
        self.fc = nn.Linear(d_model, trg_vocab_size)
        self.dropout = nn.Dropout(dropout)
        self.pad_idx = pad_idx

    def make_src_mask(self, src):
        # src shape: [src_len, N]
        src_mask = src.transpose(0, 1) == self.pad_idx
        # src_mask shape: [N, src_len]
        return src_mask.to(self.device)

    def forward(self, src, trg):
        # src: [src_len, N]
        # trg: [trg_len, N]
        src_seq_len, N = src.shape
        trg_seq_len, N = trg.shape
        src_pos = self.pos_encoder[:, :src_seq_len, :]
        trg_pos = self.pos_encoder[:, :trg_seq_len, :]
        
        embed_src = self.dropout((self.embedding_src(src) + src_pos.transpose(0,1)))
        embed_trg = self.dropout((self.embedding_trg(trg) + trg_pos.transpose(0,1)))

        src_padding_mask = self.make_src_mask(src)
        trg_mask = self.transformer.generate_square_subsequent_mask(trg_seq_len).to(self.device)

        out = self.transformer(embed_src, embed_trg, src_key_padding_mask=src_padding_mask, tgt_mask=trg_mask)
        out = self.fc(out)
        return out

# --- 2. 损失函数 (保持不变) ---
class LabelSmoothing(nn.Module):
    def __init__(self, size, padding_idx, smoothing=0.1):
        super(LabelSmoothing, self).__init__()
        self.criterion = nn.KLDivLoss(reduction='sum')
        self.padding_idx = padding_idx
        self.confidence = 1.0 - smoothing
        self.smoothing = smoothing
        self.size = size
        self.true_dist = None

    def forward(self, x, target):
        assert x.size(1) == self.size
        true_dist = x.data.clone()
        true_dist.fill_(self.smoothing / (self.size - 2))
        true_dist.scatter_(1, target.data.unsqueeze(1), self.confidence)
        true_dist[:, self.padding_idx] = 0
        mask = torch.nonzero(target.data == self.padding_idx, as_tuple=False) # 兼容新版PyTorch
        if mask.dim() > 0:
            true_dist.index_fill_(0, mask.squeeze(), 0.0)
        self.true_dist = true_dist
        return self.criterion(x, true_dist.clone().detach())

# --- 3. 现代化的数据加载 ---
def tokenize_cn(text):
    return list(jieba.cut(text))

def tokenize_en(text, spacy_en):
    return [tok.text for tok in spacy_en.tokenizer(text)]

def yield_tokens(file_path, tokenizer_func, tokenizer_args):
    with open(file_path, encoding='utf-8') as f:
        for line in f:
            yield tokenizer_func(line.strip(), **tokenizer_args)

class TranslationDataset(Dataset):
    def __init__(self, src_file, tgt_file, src_vocab, tgt_vocab, src_tokenizer, tgt_tokenizer, src_tok_args, tgt_tok_args):
        self.src_sents = self._read_data(src_file)
        self.tgt_sents = self._read_data(tgt_file)
        self.src_vocab = src_vocab
        self.tgt_vocab = tgt_vocab
        self.src_tokenizer = src_tokenizer
        self.tgt_tokenizer = tgt_tokenizer
        self.src_tok_args = src_tok_args
        self.tgt_tok_args = tgt_tok_args
    
    def _read_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.readlines()
            
    def __len__(self):
        return len(self.src_sents)
    
    def __getitem__(self, idx):
        src_text = self.src_sents[idx].strip()
        tgt_text = self.tgt_sents[idx].strip()
        src_tokens = ['<sos>'] + self.src_tokenizer(src_text, **self.src_tok_args) + ['<eos>']
        tgt_tokens = ['<sos>'] + self.tgt_tokenizer(tgt_text, **self.tgt_tok_args) + ['<eos>']
        src_indices = self.src_vocab(src_tokens)
        tgt_indices = self.tgt_vocab(tgt_tokens)
        return torch.tensor(src_indices), torch.tensor(tgt_indices)

class Collate:
    def __init__(self, pad_idx):
        self.pad_idx = pad_idx
    
    def __call__(self, batch):
        srcs = [item[0] for item in batch]
        tgts = [item[1] for item in batch]
        
        srcs_padded = pad_sequence(srcs, batch_first=False, padding_value=self.pad_idx)
        tgts_padded = pad_sequence(tgts, batch_first=False, padding_value=self.pad_idx)
        
        return srcs_padded, tgts_padded

# --- 4. 训练循环 (微调以适应DataLoader) ---
def run_epoch(data_loader, model, criterion, optimizer, device):
    model.train()
    total_loss = 0
    total_tokens = 0
    for src, trg in data_loader:
        src, trg = src.to(device), trg.to(device)
        trg_input = trg[:-1, :]
        optimizer.zero_grad()
        output = model(src, trg_input)
        output = output.reshape(-1, output.shape[2])
        trg_out = trg[1:].reshape(-1)
        loss = criterion(output, trg_out)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1)
        optimizer.step()
        total_loss += loss.item()
        total_tokens += (trg_out != criterion.padding_idx).sum().item()
    return total_loss / total_tokens

# --- 主函数 ---
def start_training_process(config, data_path):
    logs = []
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logs.append(f"Using device: {device}")

    try:
        src_file_path = os.path.join(data_path, 'train.cn')
        tgt_file_path = os.path.join(data_path, 'train.en')
        spacy_en = spacy.load('en_core_web_sm')
        
        specials = ['<unk>', '<pad>', '<sos>', '<eos>']
        
        # 构建词典
        cn_vocab = build_vocab_from_iterator(yield_tokens(src_file_path, tokenize_cn, {}), min_freq=2, specials=specials)
        en_vocab = build_vocab_from_iterator(yield_tokens(tgt_file_path, tokenize_en, {'spacy_en': spacy_en}), min_freq=2, specials=specials)
        cn_vocab.set_default_index(cn_vocab['<unk>'])
        en_vocab.set_default_index(en_vocab['<unk>'])
        
        pad_idx = cn_vocab['<pad>']
        
        # 创建数据集和DataLoader
        train_dataset = TranslationDataset(src_file_path, tgt_file_path, cn_vocab, en_vocab, tokenize_cn, tokenize_en, {}, {'spacy_en': spacy_en})
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, collate_fn=Collate(pad_idx=pad_idx))

        logs.append("中英数据集已通过现代 torchtext API 成功加载。")
        logs.append(f"源语言 (中) 词典大小: {len(cn_vocab)}")
        logs.append(f"目标语言 (英) 词典大小: {len(en_vocab)}")
    except Exception as e:
        logs.append(f"数据加载错误: {e}")
        logs.append("请确保您已安装 Spacy (en_core_web_sm) 和 Jieba。")
        logs.append(f"并确保在 '{data_path}' 目录下有 train.cn 和 train.en 文件。")
        return logs

    src_vocab_size = len(cn_vocab)
    trg_vocab_size = len(en_vocab)
    
    model = Transformer(
        src_vocab_size=src_vocab_size,
        trg_vocab_size=trg_vocab_size,
        d_model=config['embed_dim'],
        nhead=config['heads'],
        num_encoder_layers=config['num_encoder_layers'],
        num_decoder_layers=config['num_decoder_layers'],
        dim_feedforward=config['ff_dim'],
        dropout=config.get('dropout', 0.1),
        device=device,
        pad_idx=pad_idx
    ).to(device)

    logs.append("模型已根据动态配置初始化:")
    logs.append(str(config))

    optimizer = optim.Adam(model.parameters(), lr=0.0001)
    criterion = LabelSmoothing(size=trg_vocab_size, padding_idx=pad_idx, smoothing=0.1)

    num_epochs = config.get('epochs', 5)
    for epoch in range(num_epochs):
        start_time = time.time()
        train_loss = run_epoch(train_loader, model, criterion, optimizer, device)
        end_time = time.time()
        
        epoch_mins = int((end_time - start_time) / 60)
        epoch_secs = int((end_time - start_time) - (epoch_mins * 60))
        
        log_msg = f"Epoch: {epoch + 1:02} | Time: {epoch_mins}m {epoch_secs}s | Train Loss: {train_loss:.3f} | Train PPL: {torch.exp(torch.tensor(train_loss)):7.3f}"
        print(log_msg)
        logs.append(log_msg)
        
    logs.append("训练完成。")
    return logs