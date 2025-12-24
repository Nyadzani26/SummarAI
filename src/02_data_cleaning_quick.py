"""
Step 2: Data Cleaning (Quick Version for Learning)
Process smaller samples to avoid memory issues

This version:
- Uses 10K train, 1K val, 1K test (instead of 300K)
- Runs fast on any laptop
- Teaches same concepts
- Good enough for learning and fine-tuning
"""

import pandas as pd
import numpy as np
from datasets import load_dataset, Dataset
import re
from tqdm import tqdm
import warnings
import os
import json

warnings.filterwarnings('ignore')

print("="*70)
print("🧹 STEP 2: DATA CLEANING (Quick Version)")
print("="*70)
print("\n💡 Using smaller samples to avoid memory issues")
print("   Perfect for learning - same quality, just less data!\n")

# ============================================================================
# 1. Load Dataset with Sampling
# ============================================================================

print("📥 Loading CNN/DailyMail dataset (sampled)...\n")

try:
    dataset = load_dataset("cnn_dailymail", "3.0.0")
    
    # Sample smaller portions to avoid memory issues
    print("📊 Creating memory-friendly samples:")
    train_sample = dataset['train'].shuffle(seed=42).select(range(10000))
    val_sample = dataset['validation'].shuffle(seed=42).select(range(1000))
    test_sample = dataset['test'].shuffle(seed=42).select(range(1000))
    
    print(f"   ✓ Train:      {len(train_sample):,} examples")
    print(f"   ✓ Validation: {len(val_sample):,} examples")
    print(f"   ✓ Test:       {len(test_sample):,} examples")
    print(f"\n💡 This is plenty for learning and fine-tuning!")
    
except Exception as e:
    print(f"❌ Error loading dataset: {e}")
    exit(1)

# ============================================================================
# 2. Define Cleaning Functions
# ============================================================================

print("\n" + "="*70)
print("🔧 DEFINING CLEANING FUNCTIONS")
print("="*70)

def clean_text(text):
    """Clean and normalize text"""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Fix encoding issues
    replacements = {
        '\x92': "'", '\x93': '"', '\x94': '"',
        '\x97': '--', '\x96': '-', '\x85': '...',
        '\x91': "'",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove URLs and emails
    text = re.sub(r'http\S+|www\.\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    
    # Final cleanup
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def clean_summary(summary):
    """Clean summary (CNN/DM uses newlines as separators)"""
    sentences = [s.strip() for s in summary.split('\n') if s.strip()]
    summary = ' '.join(sentences)
    return clean_text(summary)

def is_valid_pair(article, summary, 
                  min_article_words=50, max_article_words=1500,
                  min_summary_words=10, max_summary_words=150):
    """Check quality criteria"""
    
    article_words = len(article.split())
    summary_words = len(summary.split())
    
    # Length checks
    if article_words < min_article_words or article_words > max_article_words:
        return False, "article_length"
    if summary_words < min_summary_words or summary_words > max_summary_words:
        return False, "summary_length"
    
    # Compression ratio (summary should be much shorter)
    if article_words / summary_words < 3:
        return False, "poor_compression"
    
    # Avoid extractive summaries (>90% word overlap)
    article_start = ' '.join(article.split()[:summary_words])
    article_words_set = set(article_start.lower().split())
    summary_words_set = set(summary.lower().split())
    overlap = len(article_words_set & summary_words_set)
    
    if summary_words > 0:
        similarity = overlap / summary_words
        if similarity > 0.9:
            return False, "too_extractive"
    
    # Avoid empty content
    if not article.strip() or not summary.strip():
        return False, "empty_content"
    
    return True, "valid"

print("\n✓ Cleaning functions defined")

# ============================================================================
# 3. Clean and Filter Datasets
# ============================================================================

def clean_and_filter_dataset(dataset_split, split_name="train"):
    """Clean and filter dataset split"""
    
    print(f"\n{'='*70}")
    print(f"🧹 CLEANING {split_name.upper()} SPLIT")
    print(f"{'='*70}")
    
    cleaned_data = []
    filter_stats = {
        "valid": 0, "article_length": 0, "summary_length": 0,
        "poor_compression": 0, "too_extractive": 0, "empty_content": 0
    }
    
    print(f"Processing {len(dataset_split):,} examples...")
    for example in tqdm(dataset_split, desc=f"Cleaning {split_name}"):
        # Clean
        article = clean_text(example['article'])
        summary = clean_summary(example['highlights'])
        
        # Filter
        is_valid, reason = is_valid_pair(article, summary)
        filter_stats[reason] += 1
        
        if is_valid:
            cleaned_data.append({
                'article': article,
                'summary': summary
            })
    
    # Statistics
    total = len(dataset_split)
    print(f"\n📊 Results:")
    print(f"   ✓ Kept:    {filter_stats['valid']:,} ({filter_stats['valid']/total*100:.1f}%)")
    print(f"   ✗ Removed: {total - filter_stats['valid']:,} ({(total-filter_stats['valid'])/total*100:.1f}%)")
    
    if filter_stats['article_length'] > 0:
        print(f"      - Article length: {filter_stats['article_length']}")
    if filter_stats['summary_length'] > 0:
        print(f"      - Summary length: {filter_stats['summary_length']}")
    if filter_stats['poor_compression'] > 0:
        print(f"      - Poor compression: {filter_stats['poor_compression']}")
    if filter_stats['too_extractive'] > 0:
        print(f"      - Too extractive: {filter_stats['too_extractive']}")
    
    return cleaned_data, filter_stats

print("\n" + "="*70)
print("🚀 STARTING CLEANING PROCESS")
print("="*70)

# Clean each split
train_cleaned, train_stats = clean_and_filter_dataset(train_sample, "train")
val_cleaned, val_stats = clean_and_filter_dataset(val_sample, "validation")
test_cleaned, test_stats = clean_and_filter_dataset(test_sample, "test")

# ============================================================================
# 4. Convert to Dataset Format
# ============================================================================

print("\n" + "="*70)
print("💾 CREATING DATASETS")
print("="*70)

train_dataset = Dataset.from_dict({
    'article': [x['article'] for x in train_cleaned],
    'summary': [x['summary'] for x in train_cleaned]
})

val_dataset = Dataset.from_dict({
    'article': [x['article'] for x in val_cleaned],
    'summary': [x['summary'] for x in val_cleaned]
})

test_dataset = Dataset.from_dict({
    'article': [x['article'] for x in test_cleaned],
    'summary': [x['summary'] for x in test_cleaned]
})

print(f"\n✓ Final cleaned datasets:")
print(f"   Train:      {len(train_dataset):,} examples")
print(f"   Validation: {len(val_dataset):,} examples")
print(f"   Test:       {len(test_dataset):,} examples")

# ============================================================================
# 5. Save Datasets
# ============================================================================

print("\n" + "="*70)
print("💾 SAVING DATASETS")
print("="*70)

os.makedirs('data/processed', exist_ok=True)

print("\nSaving cleaned datasets...")
train_dataset.save_to_disk('data/processed/train_cleaned')
val_dataset.save_to_disk('data/processed/val_cleaned')
test_dataset.save_to_disk('data/processed/test_cleaned')

print("✓ Saved to data/processed/")

# ============================================================================
# 6. Show Example
# ============================================================================

print("\n" + "="*70)
print("🔍 QUALITY CHECK - SAMPLE")
print("="*70)

ex = train_dataset[0]
print(f"\n📄 Cleaned Example:")
print(f"Article ({len(ex['article'].split())} words):")
print(ex['article'][:400] + "...\n")
print(f"Summary ({len(ex['summary'].split())} words):")
print(ex['summary'])

# ============================================================================
# 7. Save Report
# ============================================================================

report = {
    "sample_sizes": {
        "train": len(train_sample),
        "validation": len(val_sample),
        "test": len(test_sample)
    },
    "cleaned_sizes": {
        "train": len(train_dataset),
        "validation": len(val_dataset),
        "test": len(test_dataset)
    },
    "filter_stats": {
        "train": train_stats,
        "validation": val_stats,
        "test": test_stats
    },
    "note": "Quick version for learning - memory-friendly"
}

with open('data/processed/cleaning_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("\n✓ Saved report to data/processed/cleaning_report.json")

# ============================================================================
# 8. Summary
# ============================================================================

print("\n" + "="*70)
print("✅ DATA CLEANING COMPLETE")
print("="*70)

print(f"""
📦 Cleaned Datasets (Memory-Friendly):
   ├─ Train:      {len(train_dataset):,} examples
   ├─ Validation: {len(val_dataset):,} examples
   └─ Test:       {len(test_dataset):,} examples

💡 Why Smaller Samples?
   ✓ Avoids memory errors on your laptop
   ✓ Still plenty of data for learning
   ✓ Fine-tuning will work great with this
   ✓ Faster experimentation

🎯 Quality Improvements:
   ✓ Cleaned text encoding
   ✓ Removed poor quality examples
   ✓ Filtered extractive summaries
   ✓ Proper length constraints

📂 Saved Files:
   data/processed/
   ├─ train_cleaned/
   ├─ val_cleaned/
   ├─ test_cleaned/
   └─ cleaning_report.json

Next Step:
   Test pre-trained BART model (see AI in action!)
   Run: python src\\03_test_pretrained.py
""")

print("\n" + "="*70)
print("🎯 Ready for Step 3!")
print("="*70)
