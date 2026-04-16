"""
NemoGPT — Tiny character-level Transformer language model.
CPU-friendly, minimal footprint.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import os
import time

# ── Tiny Hyperparameters (CPU-friendly) ──────────────────────────
BATCH_SIZE = 16
BLOCK_SIZE = 64
MAX_ITERS = 2000
EVAL_INTERVAL = 500
LEARNING_RATE = 1e-3
DEVICE = 'cpu'
N_EMBED = 48
N_HEAD = 4
N_LAYER = 2
DROPOUT = 0.1
# ─────────────────────────────────────────────────────────────────


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
        k = self.key(x)
        q = self.query(x)
        v = self.value(x)
        wei = q @ k.transpose(-2, -1) * (1.0 / math.sqrt(k.shape[-1]))
        wei = wei.masked_fill(self.tril[:T, :T] == 0, float('-inf'))
        wei = F.softmax(wei, dim=-1)
        wei = self.dropout(wei)
        return wei @ v


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
            nn.Linear(n_embd, 4 * n_embd),
            nn.GELU(),
            nn.Linear(4 * n_embd, n_embd),
            nn.Dropout(DROPOUT),
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
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        tok_emb = self.token_emb(idx)
        pos_emb = self.pos_emb(torch.arange(T, device=DEVICE))
        x = tok_emb + pos_emb
        x = self.blocks(x)
        x = self.ln_f(x)
        logits = self.lm_head(x)
        if targets is None:
            loss = None
        else:
            B, T, C = logits.shape
            logits = logits.view(B * T, C)
            targets = targets.view(B * T)
            loss = F.cross_entropy(logits, targets)
        return logits, loss

    def generate(self, idx, max_new_tokens, temperature=1.0):
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -BLOCK_SIZE:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :] / temperature
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)
        return idx


def get_batch(data):
    ix = torch.randint(len(data) - BLOCK_SIZE, (BATCH_SIZE,))
    x = torch.stack([data[i:i + BLOCK_SIZE] for i in ix])
    y = torch.stack([data[i + 1:i + BLOCK_SIZE + 1] for i in ix])
    return x, y


@torch.no_grad()
def estimate_loss(model, train_data, val_data):
    model.eval()
    out = {}
    for split, data in [('train', train_data), ('val', val_data)]:
        losses = []
        for _ in range(20):
            x, y = get_batch(data)
            _, loss = model(x, y)
            losses.append(loss.item())
        out[split] = sum(losses) / len(losses)
    model.train()
    return out


def main():
    # Training corpus
    text = """
    In the beginning, there was nothing. Then came the code. Line by line,
    function by function, a world was built from pure logic and imagination.
    The developers worked through the night, their screens casting blue light
    across their faces. Each commit pushed them closer to something great.
    Hello, world! The first program anyone writes. A simple greeting to the
    machine, and the machine answers back. From that small beginning, entire
    systems grow. Operating systems, databases, neural networks, and more.
    The transformer architecture changed everything. Attention is all you need,
    they said. And they were right. Self-attention allows each token to look
    at every other token, building rich contextual representations. Layer by
    layer, the model learns patterns in language, from simple character
    sequences to complex grammatical structures.
    A neural network is a function approximator. Give it enough data and
    parameters, and it can learn almost any mapping from inputs to outputs.
    But small models have their charm too. They train fast, run on modest
    hardware, and teach us the fundamentals of deep learning.
    NemoClaw is a chill coder. It writes code with style and precision.
    Every function has a purpose, every variable a meaning. Clean code
    reads like prose and runs like clockwork. That is the way.
    The ocean is vast and deep. Beneath the waves, creatures glow in the
    darkness. Bioluminescence lights up the abyss. Nemo explores the depths,
    searching for treasures hidden in the code of the deep sea.
    In the world of machine learning, data is king. The more diverse and
    high-quality the data, the better the model learns. But even with
    limited data, a well-designed architecture can achieve remarkable results.
    """ * 50

    chars = sorted(list(set(text)))
    vocab_size = len(chars)
    stoi = {ch: i for i, ch in enumerate(chars)}
    itos = {i: ch for i, ch in enumerate(chars)}
    encode = lambda s: [stoi[c] for c in s]
    decode = lambda l: ''.join([itos[i] for i in l])

    data = torch.tensor(encode(text), dtype=torch.long)
    n = int(0.9 * len(data))
    train_data = data[:n]
    val_data = data[n:]

    print(f"Vocab: {vocab_size} chars | Dataset: {len(data):,} tokens")
    print(f"Model: {N_LAYER} layers, {N_HEAD} heads, {N_EMBED} dim | Device: {DEVICE}")

    model = NemoGPT(vocab_size)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Parameters: {n_params:,}")
    print()

    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)

    start = time.time()
    for i in range(MAX_ITERS):
        xb, yb = get_batch(train_data)
        logits, loss = model(xb, yb)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

        if i % EVAL_INTERVAL == 0 or i == MAX_ITERS - 1:
            losses = estimate_loss(model, train_data, val_data)
            elapsed = time.time() - start
            print(f"Step {i:5d} | train {losses['train']:.4f} | val {losses['val']:.4f} | {elapsed:.1f}s")

    # Save
    os.makedirs('checkpoints', exist_ok=True)
    torch.save({
        'model_state': model.state_dict(),
        'stoi': stoi, 'itos': itos,
        'vocab_size': vocab_size,
        'config': {'n_embed': N_EMBED, 'n_head': N_HEAD, 'n_layer': N_LAYER, 'block_size': BLOCK_SIZE}
    }, 'checkpoints/nemogpt.pt')
    print(f"\nSaved to checkpoints/nemogpt.pt")

    # Generate
    print("\n" + "=" * 50)
    print("SAMPLE GENERATIONS")
    print("=" * 50)
    model.eval()
    for label, temp in [("conservative", 0.5), ("creative", 0.8), ("wild", 1.2)]:
        ctx = torch.zeros((1, 1), dtype=torch.long)
        out = model.generate(ctx, max_new_tokens=300, temperature=temp)
        print(f"\n--- {label} (temp={temp}) ---")
        print(decode(out[0].tolist()))


if __name__ == '__main__':
    main()
