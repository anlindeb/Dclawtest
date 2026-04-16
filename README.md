# NemoGPT 🔱

A small character-level Transformer language model built from scratch with PyTorch.

## Architecture

| Component | Value |
|-----------|-------|
| Layers | 2 |
| Attention Heads | 4 |
| Embedding Dim | 48 |
| Context Window | 64 tokens |
| Parameters | 63,595 |
| Dropout | 0.1 |

## How It Works

NemoGPT is a minimal GPT-style language model that learns to generate text one character at a time. It uses:

- **Token + Positional Embeddings** — characters get embedded with position info
- **Multi-Head Self-Attention** — each head learns different relationships between characters
- **Feed-Forward Networks** — per-position MLPs with GELU activation
- **LayerNorm + Residual Connections** — stable training with skip connections
- **Autoregressive Generation** — predicts next character given previous context

## Training

Trained on a small corpus of ~91K characters (English prose about coding, ML, and the deep sea). CPU-only, ~80 seconds for 2,000 steps.

```
Step     0 | train 3.6308 | val 3.6336
Step   500 | train 1.3192 | val 1.3208
Step  1000 | train 0.3405 | val 0.3311
Step  1500 | train 0.2034 | val 0.1960
Step  1999 | train 0.1551 | val 0.1589
```

## Sample Output

**Conservative (temp=0.5):**
```
sequences to complex grammatical structures.
A neural network is a function approximator. Give it enough data and
parameters, and it can learn almost any mapping from inputs to outputs.
But small models have their charm too. They train fast, run on modest
hardware, and teach us t
```

**Creative (temp=0.8):**
```
Helo, world! The first program anyone writes. A simple greeting to the
darkness. Bioluminescence lights up the abyss. Nemo explores the depths,
searching for treasures hidden in the code of the dep sea.
```

**Wild (temp=1.2):**
```
A neural network is a function approgram anivatioas a a cor. Thever.
It worites and like clockwork. That is the way.
```

## Usage

```bash
# Train from scratch
python3 nemogpt.py

# Model checkpoint saved to checkpoints/nemogpt.pt
```

## Dependencies

- Python 3.11+
- PyTorch 2.x

## Why?

Small models are great for learning the fundamentals. No abstractions, no frameworks — just raw Transformer code you can read end-to-end in one sitting.

Built by NemoClaw 🔱
