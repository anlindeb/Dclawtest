# NemoGPT 🔱

A small character-level Transformer language model built from scratch with PyTorch.

## Two Variants

| | **NemoGPT (Tiny)** | **NemoGPT Shakespeare** |
|---|---|---|
| Dataset | Custom prose (91K chars) | Shakespeare (1.1M chars) |
| Layers | 2 | 3 |
| Heads | 4 | 4 |
| Embed Dim | 48 | 64 |
| Context | 64 | 64 |
| Parameters | 63,595 | 161,985 |
| Training Steps | 2,000 | 3,000 |
| Final Val Loss | 0.16 | 2.07 |
| Training Time | ~80s (CPU) | ~3 min (CPU) |
| Checkpoint | `checkpoints/nemogpt.pt` | `checkpoints/nemogpt_shakespeare.pt` |

## Architecture

Pure GPT-style Transformer with no high-level abstractions:

- **Token + Positional Embeddings** — characters embedded with position info
- **Multi-Head Causal Self-Attention** — masked so tokens only attend to past
- **Feed-Forward Networks** — 4x expansion with GELU activation
- **LayerNorm + Residual Connections** — pre-norm with skip connections
- **Autoregressive Generation** — predicts next character given context

## Shakespeare Sample Output

**Conservative (temp=0.5):**
```
And be the macke ing of his that the are wear
The are he mathe have ast my proter of thear.

SICHARDWARDD IE:
Whith to the may be that come to houst my of his the'd the so the buther
on the the you the whe beare sliest a and so mangely to an his paitere and
Willl be the to the whose may for the sart this sour a so the foress.
```

**Creative (temp=0.8):**
```
Buth chimerly cut lie, peeces you to the bee have
And he den whe you to paue the the whore giithters?

MUNUCICjATENUS:
Wit sou
What broud hing but oinds sillle tage you me afthis old
Hos low me that hem iths or me your mourt
```

**Wild (temp=1.2):**
```
Man: misiguday.
MANRIIO:
He mallaw, geee. Recomidy, thoumbatht wore
Uproncome'r ew batrah, you ball broy;
Ance have say. I conesbeeregs.
```

The model has learned Shakespeare's structure — dialogue format, character names, iambic-ish rhythm — but with creative spelling at this scale. A 10x bigger model would produce near-convincing Shakespeare.

## Training Curves

**Shakespeare model:**
```
Step     0 | train 4.0894 | val 4.0903
Step   500 | train 2.4995 | val 2.5015
Step  1000 | train 2.3544 | val 2.3506
Step  1500 | train 2.2675 | val 2.2424
Step  2000 | train 2.1419 | val 2.1710
Step  2500 | train 2.0697 | val 2.1247
Step  2999 | train 1.9900 | val 2.0730
```

## Usage

```bash
# Train the tiny model
python3 nemogpt.py

# Train on Shakespeare (download data automatically)
python3 nemogpt_shakespeare.py
```

## Dependencies

- Python 3.11+
- PyTorch 2.x

## Why?

Small models are great for learning the fundamentals. No abstractions, no frameworks — just raw Transformer code you can read end-to-end in one sitting.

Built by NemoClaw 🔱
