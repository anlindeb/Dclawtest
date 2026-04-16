"""
NemoGPT Shakespeare — Fits in a tight sandbox. 🔱
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math, os, time

BATCH_SIZE = 16
BLOCK_SIZE = 64
MAX_ITERS = 3000
EVAL_INTERVAL = 500
LEARNING_RATE = 3e-4
DEVICE = 'cpu'
N_EMBED = 64
N_HEAD = 4
N_LAYER = 3
DROPOUT = 0.1


class Head(nn.Module):
    def __init__(self, head_size):
        super().__init__()
        self.key = nn.Linear(N_EMBED, head_size, bias=False)
        self.query = nn.Linear(N_EMBED, head_size, bias=False)
        self.value = nn.Linear(N_EMBED, head_size, bias=False)
        self.register_buffer('tril', torch.tril(torch.ones(BLOCK_SIZE, BLOCK_SIZE)))
        self.dropout = nn.Dropout(DROPOUT)

    def forward(self, x):
        B, T, C = x.shape
        wei = self.query(x) @ self.key(x).transpose(-2, -1) * (1.0 / math.sqrt(C // 1))
        wei = wei.masked_fill(self.tril[:T, :T] == 0, float('-inf'))
        wei = F.softmax(wei, dim=-1)
        wei = self.dropout(wei)
        return wei @ self.value(x)


class MultiHeadAttention(nn.Module):
    def __init__(self, num_heads, head_size):
        super().__init__()
        self.heads = nn.ModuleList([Head(head_size) for _ in range(num_heads)])
        self.proj = nn.Linear(num_heads * head_size, N_EMBED)
        self.dropout = nn.Dropout(DROPOUT)

    def forward(self, x):
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        return self.dropout(self.proj(out))


class FeedForward(nn.Module):
    def __init__(self, n_embd):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd), nn.GELU(),
            nn.Linear(4 * n_embd, n_embd), nn.Dropout(DROPOUT),
        )

    def forward(self, x):
        return self.net(x)


class Block(nn.Module):
    def __init__(self, n_embd, n_head):
        super().__init__()
        head_size = n_embd // n_head
        self.sa = MultiHeadAttention(n_head, head_size)
        self.ffwd = FeedForward(n_embd)
        self.ln1 = nn.LayerNorm(n_embd)
        self.ln2 = nn.LayerNorm(n_embd)

    def forward(self, x):
        x = x + self.sa(self.ln1(x))
        x = x + self.ffwd(self.ln2(x))
        return x


class NemoGPT(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        self.token_emb = nn.Embedding(vocab_size, N_EMBED)
        self.pos_emb = nn.Embedding(BLOCK_SIZE, N_EMBED)
        self.blocks = nn.Sequential(*[Block(N_EMBED, N_HEAD) for _ in range(N_LAYER)])
        self.ln_f = nn.LayerNorm(N_EMBED)
        self.lm_head = nn.Linear(N_EMBED, vocab_size)
        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None: nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        x = self.token_emb(idx) + self.pos_emb(torch.arange(T, device=DEVICE))
        x = self.blocks(x)
        x = self.ln_f(x)
        logits = self.lm_head(x)
        if targets is None:
            return logits, None
        B, T, C = logits.shape
        return logits.view(B*T, C), F.cross_entropy(logits.view(B*T, C), targets.view(B*T))

    def generate(self, idx, max_new_tokens, temperature=1.0):
        for _ in range(max_new_tokens):
            logits, _ = self(idx[:, -BLOCK_SIZE:])
            probs = F.softmax(logits[:, -1, :] / temperature, dim=-1)
            idx = torch.cat((idx, torch.multinomial(probs, num_samples=1)), dim=1)
        return idx


def get_batch(data):
    ix = torch.randint(len(data) - BLOCK_SIZE, (BATCH_SIZE,))
    return torch.stack([data[i:i+BLOCK_SIZE] for i in ix]), torch.stack([data[i+1:i+BLOCK_SIZE+1] for i in ix])


@torch.no_grad()
def estimate_loss(model, train_data, val_data):
    model.eval()
    out = {}
    for split, data in [('train', train_data), ('val', val_data)]:
        losses = [model(*get_batch(data))[1].item() for _ in range(10)]
        out[split] = sum(losses) / len(losses)
    model.train()
    return out


def main():
    with open('/tmp/shakespeare.txt', 'r') as f:
        text = f.read()

    chars = sorted(list(set(text)))
    vocab_size = len(chars)
    stoi = {ch: i for i, ch in enumerate(chars)}
    itos = {i: ch for i, ch in enumerate(chars)}
    encode = lambda s: [stoi[c] for c in s]
    decode = lambda l: ''.join([itos[i] for i in l])

    data = torch.tensor(encode(text), dtype=torch.long)
    n = int(0.9 * len(data))

    model = NemoGPT(vocab_size)
    print(f"Vocab: {vocab_size} | Tokens: {len(data):,} | Params: {sum(p.numel() for p in model.parameters()):,}", flush=True)
    print(f"Model: {N_LAYER}L {N_HEAD}H {N_EMBED}D ctx={BLOCK_SIZE} bs={BATCH_SIZE}", flush=True)

    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)
    start = time.time()

    for i in range(MAX_ITERS):
        xb, yb = get_batch(data[:n])
        _, loss = model(xb, yb)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        if i % EVAL_INTERVAL == 0 or i == MAX_ITERS - 1:
            losses = estimate_loss(model, data[:n], data[n:])
            print(f"Step {i:5d} | train {losses['train']:.4f} | val {losses['val']:.4f} | {time.time()-start:.0f}s", flush=True)

    os.makedirs('checkpoints', exist_ok=True)
    torch.save({'model_state': model.state_dict(), 'stoi': stoi, 'itos': itos,
                'vocab_size': vocab_size, 'config': {'n_embed': N_EMBED, 'n_head': N_HEAD, 'n_layer': N_LAYER, 'block_size': BLOCK_SIZE}},
               'checkpoints/nemogpt_shakespeare.pt')
    print(f"\nSaved.", flush=True)

    print("\n" + "=" * 60, flush=True)
    print("SHAKESPEARE GENERATIONS 🔱", flush=True)
    print("=" * 60, flush=True)
    model.eval()
    for label, temp in [("conservative", 0.5), ("creative", 0.8), ("wild", 1.2)]:
        ctx = torch.zeros((1, 1), dtype=torch.long)
        out = model.generate(ctx, max_new_tokens=500, temperature=temp)
        print(f"\n--- {label} (temp={temp}) ---", flush=True)
        print(decode(out[0].tolist()), flush=True)


if __name__ == '__main__':
    main()
