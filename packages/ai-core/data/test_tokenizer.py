import sys
import sentencepiece as spm

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

tokenizer_path = "experimental/phase9_2/tokenizers/bpe_8k/sp_bpe_8k.model"
sp = spm.SentencePieceProcessor()
sp.load(tokenizer_path)

print(f"Tokenizer vocabulary size: {sp.get_piece_size()}")
print(f"Vocabulary type: BPE")

# Test Bengali text
bengali_text = "আমার নাম কি"
bengali_tokens = sp.encode(bengali_text, out_type=str)
bengali_ids = sp.encode(bengali_text, out_type=int)
print(f"\nBengali text: {bengali_text}")
print(f"Tokens: {bengali_tokens}")
print(f"Token IDs: {bengali_ids}")
print(f"Decoded: {sp.decode(bengali_ids)}")

# Test English text
english_text = "What is your name?"
english_tokens = sp.encode(english_text, out_type=str)
english_ids = sp.encode(english_text, out_type=int)
print(f"\nEnglish text: {english_text}")
print(f"Tokens: {english_tokens}")
print(f"Token IDs: {english_ids}")
print(f"Decoded: {sp.decode(english_ids)}")

# Test mixed text
mixed_text = "My name is NexusAI এবং আমি বাংলায় কথা বলতে পারি"
mixed_tokens = sp.encode(mixed_text, out_type=str)
mixed_ids = sp.encode(mixed_text, out_type=int)
print(f"\nMixed text: {mixed_text}")
print(f"Tokens: {mixed_tokens}")
print(f"Token IDs: {mixed_ids}")
print(f"Decoded: {sp.decode(mixed_ids)}")

# Test math text
math_text = "2 + 2 = 4"
math_tokens = sp.encode(math_text, out_type=str)
math_ids = sp.encode(math_text, out_type=int)
print(f"\nMath text: {math_text}")
print(f"Tokens: {math_tokens}")
print(f"Token IDs: {math_ids}")
print(f"Decoded: {sp.decode(math_ids)}")

# Check special tokens
print(f"\nSpecial tokens:")
print(f"<pad>: {sp.piece_to_id('<pad>')}")
print(f"<unk>: {sp.piece_to_id('<unk>')}")
print(f"<s>: {sp.piece_to_id('<s>')}")
print(f"</s>: {sp.piece_to_id('</s>')}")

# Test unknown token rate
test_texts = [
    "আমার নাম কি",
    "What is your name?",
    "আমি ভালো আছি",
    "The capital of Bangladesh is Dhaka",
    "2 * 8 = 16"
]

print(f"\nUnknown token rate test:")
for text in test_texts:
    tokens = sp.encode(text, out_type=int)
    unk_id = sp.piece_to_id('<unk>')
    unk_count = tokens.count(unk_id)
    print(f"{text}: {unk_count}/{len(tokens)} unknown tokens ({unk_count/len(tokens)*100:.1f}%)")
