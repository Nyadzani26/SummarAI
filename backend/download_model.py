"""
Download BART Model for Summarization
This script downloads the facebook/bart-large-cnn model (~1.6GB)
Run this once before using summarization features
"""

import os
from transformers import BartForConditionalGeneration, BartTokenizer

print("="*70)
print("[*] Downloading BART Model for Document Summarization")
print("="*70)
print("\n[!] This will download ~1.6GB of data")
print("[*] Expected time: 10-15 minutes (depending on internet speed)\n")

# Model details
model_name = "facebook/bart-large-cnn"
save_path = "../models/pretrained/facebook/bart-large-cnn"

# Create directory if it doesn't exist
os.makedirs(save_path, exist_ok=True)

try:
    print(f"[1/2] Downloading tokenizer from HuggingFace...")
    tokenizer = BartTokenizer.from_pretrained(model_name)
    tokenizer.save_pretrained(save_path)
    print("[+] Tokenizer downloaded successfully\n")
    
    print(f"[2/2] Downloading model (this is the large file ~1.5GB)...")
    model = BartForConditionalGeneration.from_pretrained(model_name)
    model.save_pretrained(save_path)
    print("[+] Model downloaded successfully\n")
    
    print("="*70)
    print("[+] SUCCESS! Model downloaded and ready to use")
    print("="*70)
    print(f"\n[*] Saved to: {save_path}")
    print("\n[+] You can now use the summarization feature!")
    print("    The model will load automatically when you generate summaries.\n")
    
except Exception as e:
    print(f"\n[!] ERROR: Failed to download model")
    print(f"    {str(e)}")
    print("\n[*] Troubleshooting:")
    print("    1. Check your internet connection")
    print("    2. Make sure you have ~2GB free disk space")
    print("    3. Try running the script again")
    print("    4. If it keeps failing, the model will auto-download on first use\n")
