import torch
import torch.nn as nn
import torch.optim as optim
import time
import os
import spacy
import jieba
from torch.utils.data import DataLoader, Dataset
from torch.nn.utils.rnn import pad_sequence
from torchtext.vocab import build_vocab_from_iterator
import math

# --- 1. 模型定义 (微调) ---
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
        # 增加位置编码的最大长度
        self.pos_encoder = nn.Parameter(torch.zeros(1, 1024, d_model))
        self.transformer = nn.Transformer(d_model, nhead, num_encoder_layers, num_decoder_layers, dim_feedforward, dropout, batch_first=False)
        self.fc = nn.Linear(d_model, trg_vocab_size)
        self.dropout = nn.Dropout(dropout)

    def _generate_square_subsequent_mask(self, sz):
        mask = (torch.triu(torch.ones(sz, sz)) == 1).transpose(0, 1)
        mask = mask.float().masked_fill(mask == 0, float('-inf')).masked_fill(mask == 1, float(0.0))
        return mask.to(self.device)

    def _create_padding_mask(self, seq):
        # seq shape: [seq_len, batch_size]
        return (seq.transpose(0, 1) == self.pad_idx).to(self.device)

    def forward(self, src, trg):
        # src: [src_len, batch_size]
        # trg: [trg_len, batch_size]
        src_seq_len, _ = src.shape
        trg_seq_len, _ = trg.shape

        src_pos = self.pos_encoder[:, :src_seq_len, :]
        trg_pos = self.pos_encoder[:, :trg_seq_len, :]

        embed_src = self.dropout((self.embedding_src(src) + src_pos.transpose(0, 1)))
        embed_trg = self.dropout((self.embedding_trg(trg) + trg_pos.transpose(0, 1)))

        src_padding_mask = self._create_padding_mask(src)
        trg_padding_mask = self._create_padding_mask(trg)
        trg_mask = self._generate_square_subsequent_mask(trg_seq_len)

        out = self.transformer(embed_src, embed_trg,
                               src_mask=None,
                               tgt_mask=trg_mask,
                               memory_mask=None,
                               src_key_padding_mask=src_padding_mask,
                               tgt_key_padding_mask=trg_padding_mask,
                               memory_key_padding_mask=src_padding_mask)
        return self.fc(out)

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

# --- 3. 数据加载 (保持不变) ---
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
        with open(src_file, 'r', encoding='utf-8') as f:
            self.src_sents = f.readlines()
        with open(tgt_file, 'r', encoding='utf-8') as f:
            self.tgt_sents = f.readlines()
            
        self.src_vocab = src_vocab
        self.tgt_vocab = tgt_vocab
        self.src_tokenizer = src_tokenizer
        self.tgt_tokenizer = tgt_tokenizer
        self.src_tok_args = src_tok_args
        self.tgt_tok_args = tgt_tok_args
    
    def __len__(self):
        return len(self.src_sents)
    
    def __getitem__(self, idx):
        src_text = self.src_sents[idx].strip()
        tgt_text = self.tgt_sents[idx].strip()
        src_tokens = ['<sos>'] + self.src_tokenizer(src_text, **self.src_tok_args) + ['<eos>']
        tgt_tokens = ['<sos>'] + self.tgt_tokenizer(tgt_text, **self.tgt_tok_args) + ['<eos>']
        return torch.tensor(self.src_vocab(src_tokens)), torch.tensor(self.tgt_vocab(tgt_tokens))

class Collate:
    def __init__(self, pad_idx):
        self.pad_idx = pad_idx
    
    def __call__(self, batch):
        srcs = [item[0] for item in batch]
        tgts = [item[1] for item in batch]
        srcs_padded = pad_sequence(srcs, batch_first=False, padding_value=self.pad_idx)
        tgts_padded = pad_sequence(tgts, batch_first=False, padding_value=self.pad_idx)
        return srcs_padded, tgts_padded

# --- 4. 训练循环 (优化) ---
def run_epoch(data_loader, model, criterion, optimizer, device):
    model.train()
    total_loss = 0
    total_tokens = 0

    for src, trg in data_loader:
        src, trg = src.to(device), trg.to(device)
        
        # Decoder的输入是trg的[<sos>, ..., token_n], 输出目标是[..., token_n, <eos>]
        trg_input = trg[:-1, :]
        
        optimizer.zero_grad()
        
        output = model(src, trg_input)
        
        # output: [trg_len-1, batch_size, trg_vocab_size]
        # target: [trg_len-1, batch_size]
        output_flat = output.reshape(-1, output.shape[-1])
        trg_target = trg[1:, :].reshape(-1)
        
        loss = criterion(F.log_softmax(output_flat, dim=-1), trg_target)
        loss.backward()
        
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        
        # 计算总损失和用于计算困惑度的token数
        # criterion返回的是sum loss，所以要除以token数
        total_loss += loss.item()
        total_tokens += (trg_target != criterion.padding_idx).sum().item()

    return total_loss / total_tokens if total_tokens > 0 else 0

# --- 主函数 (优化) ---
def start_training_process(config, data_path):
    logs = []
    try:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logs.append(f"日志: 使用设备: {device}")

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

        logs.append("日志: 中英数据集已成功加载。")
        logs.append(f"日志: 源语言 (中) 词典大小: {len(cn_vocab)}")
        logs.append(f"日志: 目标语言 (英) 词典大小: {len(en_vocab)}")
        
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

        logs.append("日志: 模型已根据动态配置初始化:")
        logs.append(str(config))

        optimizer = optim.Adam(model.parameters(), lr=0.0001, betas=(0.9, 0.98), eps=1e-9)
        criterion = LabelSmoothing(size=trg_vocab_size, padding_idx=pad_idx, smoothing=0.1)

        num_epochs = config.get('epochs', 5)
        logs.append(f"日志: 开始训练，共 {num_epochs} 个 Epoch。")

        for epoch in range(num_epochs):
            start_time = time.time()
            train_loss = run_epoch(train_loader, model, criterion, optimizer, device)
            end_time = time.time()
            
            epoch_mins = int((end_time - start_time) / 60)
            epoch_secs = int((end_time - start_time) - (epoch_mins * 60))
            
            # 使用 math.exp 替代 torch.exp，避免不必要的张量操作
            train_ppl = math.exp(train_loss)
            
            log_msg = f"Epoch: {epoch + 1:02} | 耗时: {epoch_mins}m {epoch_secs}s | 训练损失: {train_loss:.3f} | 训练困惑度: {train_ppl:7.3f}"
            print(log_msg)
            logs.append(log_msg)
            
        logs.append("日志: 训练完成。")

    except FileNotFoundError as e:
        logs.append(f"错误: 依赖文件未找到 - {e}")
        logs.append("提示: 请确保 Spacy 英文模型 'en_core_web_sm' 已下载 (python -m spacy download en_core_web_sm)。")
        logs.append(f"提示: 并确保在 '{data_path}' 目录下有 train.cn 和 train.en 文件。")
    except Exception as e:
        logs.append(f"严重错误: 训练过程中断 - {e}")
        import traceback
        logs.append(traceback.format_exc())

    return logs