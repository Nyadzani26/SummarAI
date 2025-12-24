"""
Step 2: Data Cleaning & Preprocessing
Clean text, filter quality, and prepare training datasets

Run this script to:
- Clean text (fix encoding, remove artifacts)
- Filter poor quality examples
- Remove extractive summaries (we want abstractive)
- Create train/validation/test splits
- Save cleaned datasets
"""

import pandas as pd
import numpy as np
from datasets import load_dataset, Dataset
import re
from tqdm import tqdm
import warnings
import os

warnings.filterwarnings('ignore')

print("="*70)
print("🧹 STEP 2: DATA CLEANING & PREPROCESSING")
print("="*70)

# ============================================================================
# 1. Load Dataset
# ============================================================================

print("\n📥 Loading CNN/DailyMail dataset...")
print("(This should be fast since it's cached from Step 1)\n")

try:
    dataset = load_dataset("cnn_dailymail", "3.0.0")
    print("✓ Dataset loaded from cache")
    print(f"\n📦 Dataset sizes:")
    print(f"   Train:      {len(dataset['train']):,} examples")
    print(f"   Validation: {len(dataset['validation']):,} examples")
    print(f"   Test:       {len(dataset['test']):,} examples")
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
    """
    Clean and normalize text
    
    What it does:
    - Removes extra whitespace
    - Fixes encoding issues (smart quotes, dashes)
    - Removes URLs
    - Normalizes line breaks
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove multiple spaces/tabs/newlines
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Fix common encoding issues (Windows-1252 -> UTF-8)
    replacements = {
        '\x92': "'",      # Smart single quote
        '\x93': '"',      # Smart double quote (open)
        '\x94': '"',      # Smart double quote (close)
        '\x97': '--',     # Em dash
        '\x96': '-',      # En dash
        '\x85': '...',    # Ellipsis
        '\x91': "'",      # Left single quote
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove URLs (optional - news articles may have links)
    text = re.sub(r'http\S+|www\.\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove extra spaces created by previous operations
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def clean_summary(summary):
    """
    Clean summary text specifically
    
    CNN/DailyMail summaries use newlines as sentence separators.
    We convert them to proper sentences with spaces.
    """
    # Split by newlines (each line is a sentence)
    sentences = [s.strip() for s in summary.split('\n') if s.strip()]
    
    # Join with spaces
    summary = ' '.join(sentences)
    
    # Apply general cleaning
    summary = clean_text(summary)
    
    return summary

# Test cleaning functions
print("\n🧪 Testing cleaning functions...")
test_text = "This   is  a\ntest\x92s text with  extra   spaces and\x93smart quotes\x94."
cleaned = clean_text(test_text)
print(f"Original: {repr(test_text)}")
print(f"Cleaned:  {repr(cleaned)}")
print("✓ Cleaning functions work correctly")

# ============================================================================
# 3. Define Quality Filtering Functions
# ============================================================================

print("\n" + "="*70)
print("🔍 DEFINING QUALITY FILTERS")
print("="*70)

def is_valid_pair(article, summary, 
                  min_article_words=50, max_article_words=1500,
                  min_summary_words=10, max_summary_words=150):
    """
    Check if article-summary pair meets quality criteria
    
    Quality checks:
    1. Length constraints (avoid too short/long)
    2. Compression ratio (summary should be much shorter)
    3. Extractive vs abstractive (avoid copy-paste summaries)
    
    Returns:
        (is_valid: bool, reason: str)
    """
    
    article_words = len(article.split())
    summary_words = len(summary.split())
    
    # Check 1: Article length
    if article_words < min_article_words:
        return False, "article_too_short"
    if article_words > max_article_words:
        return False, "article_too_long"
    
    # Check 2: Summary length
    if summary_words < min_summary_words:
        return False, "summary_too_short"
    if summary_words > max_summary_words:
        return False, "summary_too_long"
    
    # Check 3: Compression ratio
    # Summary should be at least 3x shorter than article
    if article_words / summary_words < 3:
        return False, "poor_compression"
    
    # Check 4: Avoid too extractive summaries
    # If summary has >90% word overlap with article start, it's likely extractive
    article_start = ' '.join(article.split()[:summary_words])
    
    # Calculate word overlap
    article_words_set = set(article_start.lower().split())
    summary_words_set = set(summary.lower().split())
    overlap = len(article_words_set & summary_words_set)
    
    if summary_words > 0:
        similarity = overlap / summary_words
        if similarity > 0.9:
            return False, "too_extractive"
    
    # Check 5: Avoid empty or meaningless content
    if not article.strip() or not summary.strip():
        return False, "empty_content"
    
    return True, "valid"

# Test filtering
print("\n🧪 Testing quality filters...")
test_article = "This is a sample news article. " * 100  # ~500 words
test_summary = "This is a good abstractive summary of the main points."
is_valid, reason = is_valid_pair(test_article, test_summary)
print(f"Test pair valid: {is_valid} (reason: {reason})")
print("✓ Quality filters work correctly")

# ============================================================================
# 4. Clean and Filter Training Data
# ============================================================================

def clean_and_filter_dataset(dataset_split, split_name="train", max_samples=None):
    """
    Clean and filter dataset split
    
    Args:
        dataset_split: HuggingFace dataset split
        split_name: Name for logging (train/val/test)
        max_samples: Limit processing (None = process all)
    
    Returns:
        List of cleaned examples
    """
    
    print(f"\n{'='*70}")
    print(f"🧹 CLEANING {split_name.upper()} SPLIT")
    print(f"{'='*70}")
    print(f"Original size: {len(dataset_split):,} examples")
    
    if max_samples:
        print(f"Processing first {max_samples:,} examples only")
        dataset_split = dataset_split.select(range(min(max_samples, len(dataset_split))))
    
    cleaned_data = []
    filter_stats = {
        "valid": 0,
        "article_too_short": 0,
        "article_too_long": 0,
        "summary_too_short": 0,
        "summary_too_long": 0,
        "poor_compression": 0,
        "too_extractive": 0,
        "empty_content": 0
    }
    
    print("\nProcessing examples...")
    for example in tqdm(dataset_split, desc=f"Cleaning {split_name}"):
        # Clean texts
        article = clean_text(example['article'])
        summary = clean_summary(example['highlights'])
        
        # Filter
        is_valid, reason = is_valid_pair(article, summary)
        filter_stats[reason] += 1
        
        if is_valid:
            cleaned_data.append({
                'article': article,
                'summary': summary,
                'id': example.get('id', '')
            })
    
    # Print statistics
    print(f"\n📊 Filtering Statistics for {split_name}:")
    print(f"   ✓ Valid:                 {filter_stats['valid']:,} ({filter_stats['valid']/len(dataset_split)*100:.1f}%)")
    print(f"   ✗ Article too short:     {filter_stats['article_too_short']:,}")
    print(f"   ✗ Article too long:      {filter_stats['article_too_long']:,}")
    print(f"   ✗ Summary too short:     {filter_stats['summary_too_short']:,}")
    print(f"   ✗ Summary too long:      {filter_stats['summary_too_long']:,}")
    print(f"   ✗ Poor compression:      {filter_stats['poor_compression']:,}")
    print(f"   ✗ Too extractive:        {filter_stats['too_extractive']:,}")
    print(f"   ✗ Empty content:         {filter_stats['empty_content']:,}")
    
    removed = len(dataset_split) - len(cleaned_data)
    print(f"\n✓ Cleaned size: {len(cleaned_data):,}")
    print(f"  Removed: {removed:,} examples ({removed/len(dataset_split)*100:.1f}%)")
    
    return cleaned_data

# Clean each split
print("\n" + "="*70)
print("🚀 STARTING DATA CLEANING PROCESS")
print("="*70)
print("\nThis will take 20-30 minutes for full dataset...")
print("Processing train, validation, and test splits...\n")

# Clean train split
train_cleaned = clean_and_filter_dataset(dataset['train'], "train")

# Clean validation split
val_cleaned = clean_and_filter_dataset(dataset['validation'], "validation")

# Clean test split
test_cleaned = clean_and_filter_dataset(dataset['test'], "test")

# ============================================================================
# 5. Convert to HuggingFace Dataset Format
# ============================================================================

print("\n" + "="*70)
print("💾 CONVERTING TO DATASET FORMAT")
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

print("\n✓ Converted to HuggingFace Dataset format")
print(f"\nFinal dataset sizes:")
print(f"   Train:      {len(train_dataset):,} examples")
print(f"   Validation: {len(val_dataset):,} examples")
print(f"   Test:       {len(test_dataset):,} examples")

# ============================================================================
# 6. Save Cleaned Datasets
# ============================================================================

print("\n" + "="*70)
print("💾 SAVING CLEANED DATASETS")
print("="*70)

os.makedirs('data/processed', exist_ok=True)

print("\nSaving full cleaned datasets...")
train_dataset.save_to_disk('data/processed/train_cleaned')
val_dataset.save_to_disk('data/processed/val_cleaned')
test_dataset.save_to_disk('data/processed/test_cleaned')

print("✓ Saved full datasets:")
print("   data/processed/train_cleaned/")
print("   data/processed/val_cleaned/")
print("   data/processed/test_cleaned/")

# ============================================================================
# 7. Create Quick Samples for Fast Experiments
# ============================================================================

print("\n" + "="*70)
print("⚡ CREATING QUICK SAMPLES")
print("="*70)
print("\nCreating smaller samples for fast experimentation...")

# Create quick samples (5K train, 500 val, 500 test)
quick_train = train_dataset.select(range(min(5000, len(train_dataset))))
quick_val = val_dataset.select(range(min(500, len(val_dataset))))
quick_test = test_dataset.select(range(min(500, len(test_dataset))))

quick_train.save_to_disk('data/processed/quick_train')
quick_val.save_to_disk('data/processed/quick_val')
quick_test.save_to_disk('data/processed/quick_test')

print("✓ Saved quick samples:")
print(f"   data/processed/quick_train/ ({len(quick_train):,} examples)")
print(f"   data/processed/quick_val/ ({len(quick_val):,} examples)")
print(f"   data/processed/quick_test/ ({len(quick_test):,} examples)")

# ============================================================================
# 8. Quality Check - Show Examples
# ============================================================================

print("\n" + "="*70)
print("🔍 QUALITY CHECK - SAMPLE EXAMPLES")
print("="*70)

print("\n📄 Example 1 (Cleaned):")
print("-" * 70)
ex = train_dataset[0]
print(f"Article ({len(ex['article'].split())} words):")
print(ex['article'][:300] + "...\n")
print(f"Summary ({len(ex['summary'].split())} words):")
print(ex['summary'])
print("-" * 70)

print("\n📄 Example 2 (Cleaned):")
print("-" * 70)
ex = train_dataset[100]
print(f"Article ({len(ex['article'].split())} words):")
print(ex['article'][:300] + "...\n")
print(f"Summary ({len(ex['summary'].split())} words):")
print(ex['summary'])
print("-" * 70)

# ============================================================================
# 9. Save Cleaning Report
# ============================================================================

print("\n" + "="*70)
print("📊 GENERATING CLEANING REPORT")
print("="*70)

report = {
    "original_sizes": {
        "train": len(dataset['train']),
        "validation": len(dataset['validation']),
        "test": len(dataset['test'])
    },
    "cleaned_sizes": {
        "train": len(train_dataset),
        "validation": len(val_dataset),
        "test": len(test_dataset)
    },
    "removal_rates": {
        "train": f"{(1 - len(train_dataset)/len(dataset['train']))*100:.1f}%",
        "validation": f"{(1 - len(val_dataset)/len(dataset['validation']))*100:.1f}%",
        "test": f"{(1 - len(test_dataset)/len(dataset['test']))*100:.1f}%"
    },
    "quality_criteria": {
        "min_article_words": 50,
        "max_article_words": 1500,
        "min_summary_words": 10,
        "max_summary_words": 150,
        "min_compression_ratio": 3.0,
        "max_extractive_similarity": 0.9
    }
}

import json
with open('data/processed/cleaning_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("✓ Saved cleaning report to: data/processed/cleaning_report.json")

# ============================================================================
# 10. Summary
# ============================================================================

print("\n" + "="*70)
print("✅ DATA CLEANING COMPLETE")
print("="*70)

print(f"""
📦 Cleaned Datasets Summary:
   
   Full datasets (for final training):
   ├─ Train:      {len(train_dataset):,} examples
   ├─ Validation: {len(val_dataset):,} examples
   └─ Test:       {len(test_dataset):,} examples
   
   Quick samples (for fast experiments):
   ├─ Train:      {len(quick_train):,} examples
   ├─ Validation: {len(quick_val):,} examples
   └─ Test:       {len(quick_test):,} examples

🎯 Quality Improvements:
   ✓ Removed encoding artifacts
   ✓ Normalized whitespace
   ✓ Filtered poor quality examples
   ✓ Removed extractive summaries
   ✓ Ensured proper length constraints

📂 Saved Files:
   data/processed/
   ├─ train_cleaned/
   ├─ val_cleaned/
   ├─ test_cleaned/
   ├─ quick_train/
   ├─ quick_val/
   ├─ quick_test/
   └─ cleaning_report.json

Next Steps:
1. Test pre-trained BART model (establish baseline)
2. Run: python src/03_test_pretrained.py
""")

print("\n" + "="*70)
print("🎯 Ready for next step!")
print("="*70)
print("\nRun: python src\\03_test_pretrained.py")
print("="*70)
