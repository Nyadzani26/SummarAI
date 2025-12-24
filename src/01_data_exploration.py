"""
Step 1: Data Exploration
Download and explore the CNN/DailyMail dataset

Run this script to:
- Download the dataset (first time: ~10-15 min, 3GB)
- Analyze text lengths
- Visualize distributions
- Save sample data for quick experiments
"""

import pandas as pd
import numpy as np
from datasets import load_dataset
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import warnings
import os

warnings.filterwarnings('ignore')
sns.set_style('whitegrid')

print("="*70)
print("📊 STEP 1: DATA EXPLORATION")
print("="*70)

# ============================================================================
# 1. Load Dataset
# ============================================================================

print("\n📥 Downloading CNN/DailyMail dataset...")
print("⏱️  First run: 10-15 minutes (3GB download)")
print("⏱️  Subsequent runs: ~30 seconds (cached)\n")

try:
    dataset = load_dataset("cnn_dailymail", "3.0.0")
    
    print("✓ Dataset loaded successfully!\n")
    print(f"📦 Dataset sizes:")
    print(f"   Train:      {len(dataset['train']):,} examples")
    print(f"   Validation: {len(dataset['validation']):,} examples")
    print(f"   Test:       {len(dataset['test']):,} examples")
    print(f"   Total:      {len(dataset['train']) + len(dataset['validation']) + len(dataset['test']):,} examples")
    
except Exception as e:
    print(f"❌ Error loading dataset: {e}")
    print("\nTroubleshooting:")
    print("1. Check internet connection")
    print("2. Try again (download may have been interrupted)")
    print("3. Ensure you have ~5GB free disk space")
    exit(1)

# ============================================================================
# 2. Explore Structure
# ============================================================================

print("\n" + "="*70)
print("📋 DATASET STRUCTURE")
print("="*70)

example = dataset['train'][0]
print(f"\n📄 Example Article (ID: {example.get('id', 'N/A')}):")
print("-" * 70)
print(example['article'][:500] + "...\n")
print("-" * 70)
print(f"\n📝 Example Summary:")
print("-" * 70)
print(example['highlights'])
print("-" * 70)

# ============================================================================
# 3. Analyze Text Lengths
# ============================================================================

print("\n" + "="*70)
print("📏 ANALYZING TEXT LENGTHS")
print("="*70)
print("\nProcessing 10,000 samples for statistics...")

def get_text_lengths(dataset_split, num_samples=10000):
    """Calculate article and summary lengths"""
    article_lengths = []
    summary_lengths = []
    
    max_samples = min(num_samples, len(dataset_split))
    
    for i in range(max_samples):
        if i % 1000 == 0:
            print(f"  Processed {i:,}/{max_samples:,} samples...")
        
        article_lengths.append(len(dataset_split[i]['article'].split()))
        summary_lengths.append(len(dataset_split[i]['highlights'].split()))
    
    return article_lengths, summary_lengths

article_lens, summary_lens = get_text_lengths(dataset['train'])

# Create statistics dataframe
stats_df = pd.DataFrame({
    'Metric': ['Min', 'Max', 'Mean', 'Median', '25th %ile', '75th %ile'],
    'Article Length': [
        min(article_lens),
        max(article_lens),
        int(np.mean(article_lens)),
        int(np.median(article_lens)),
        int(np.percentile(article_lens, 25)),
        int(np.percentile(article_lens, 75))
    ],
    'Summary Length': [
        min(summary_lens),
        max(summary_lens),
        int(np.mean(summary_lens)),
        int(np.median(summary_lens)),
        int(np.percentile(summary_lens, 25)),
        int(np.percentile(summary_lens, 75))
    ]
})

print("\n📊 Length Statistics (in words):")
print(stats_df.to_string(index=False))

# ============================================================================
# 4. Visualize Distributions
# ============================================================================

print("\n" + "="*70)
print("📊 CREATING VISUALIZATIONS")
print("="*70)

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Article lengths histogram
axes[0, 0].hist(article_lens, bins=50, edgecolor='black', alpha=0.7, color='steelblue')
axes[0, 0].axvline(np.mean(article_lens), color='r', linestyle='--', linewidth=2,
                    label=f'Mean: {np.mean(article_lens):.0f}')
axes[0, 0].axvline(np.median(article_lens), color='g', linestyle='--', linewidth=2,
                    label=f'Median: {np.median(article_lens):.0f}')
axes[0, 0].set_xlabel('Article Length (words)', fontsize=12)
axes[0, 0].set_ylabel('Frequency', fontsize=12)
axes[0, 0].set_title('Distribution of Article Lengths', fontsize=14, fontweight='bold')
axes[0, 0].legend(fontsize=10)
axes[0, 0].grid(alpha=0.3)

# Summary lengths histogram
axes[0, 1].hist(summary_lens, bins=50, edgecolor='black', alpha=0.7, color='seagreen')
axes[0, 1].axvline(np.mean(summary_lens), color='r', linestyle='--', linewidth=2,
                    label=f'Mean: {np.mean(summary_lens):.0f}')
axes[0, 1].axvline(np.median(summary_lens), color='orange', linestyle='--', linewidth=2,
                    label=f'Median: {np.median(summary_lens):.0f}')
axes[0, 1].set_xlabel('Summary Length (words)', fontsize=12)
axes[0, 1].set_ylabel('Frequency', fontsize=12)
axes[0, 1].set_title('Distribution of Summary Lengths', fontsize=14, fontweight='bold')
axes[0, 1].legend(fontsize=10)
axes[0, 1].grid(alpha=0.3)

# Box plots
data_for_box = pd.DataFrame({
    'Article': article_lens,
    'Summary': summary_lens
})
axes[1, 0].boxplot([article_lens, summary_lens], labels=['Article', 'Summary'])
axes[1, 0].set_ylabel('Length (words)', fontsize=12)
axes[1, 0].set_title('Length Distribution Comparison', fontsize=14, fontweight='bold')
axes[1, 0].grid(alpha=0.3)

# Compression ratio
compression_ratios = [s/a if a > 0 else 0 for s, a in zip(summary_lens, article_lens)]
axes[1, 1].hist(compression_ratios, bins=50, edgecolor='black', alpha=0.7, color='coral')
axes[1, 1].axvline(np.mean(compression_ratios), color='r', linestyle='--', linewidth=2,
                    label=f'Mean: {np.mean(compression_ratios):.3f}')
axes[1, 1].set_xlabel('Compression Ratio (summary/article)', fontsize=12)
axes[1, 1].set_ylabel('Frequency', fontsize=12)
axes[1, 1].set_title('Summary Compression Ratios', fontsize=14, fontweight='bold')
axes[1, 1].legend(fontsize=10)
axes[1, 1].grid(alpha=0.3)

plt.tight_layout()

# Save plot
os.makedirs('data', exist_ok=True)
plot_path = 'data/length_distributions.png'
plt.savefig(plot_path, dpi=300, bbox_inches='tight')
print(f"✓ Saved visualization to: {plot_path}")

# Display plot
plt.show()

# ============================================================================
# 5. Analyze Summary Characteristics
# ============================================================================

print("\n" + "="*70)
print("🔍 ANALYZING SUMMARY CHARACTERISTICS")
print("="*70)

def analyze_summaries(dataset_split, num_samples=5000):
    """Analyze summary characteristics"""
    summary_sentences = []
    compression_ratios = []
    
    max_samples = min(num_samples, len(dataset_split))
    print(f"\nProcessing {max_samples:,} samples...")
    
    for i in range(max_samples):
        if i % 1000 == 0:
            print(f"  Processed {i:,}/{max_samples:,} samples...")
        
        article = dataset_split[i]['article']
        summary = dataset_split[i]['highlights']
        
        # Count sentences (CNN/DailyMail uses newlines)
        num_sentences = len([s for s in summary.split('\n') if s.strip()])
        summary_sentences.append(num_sentences)
        
        # Compression ratio
        article_words = len(article.split())
        summary_words = len(summary.split())
        if article_words > 0:
            ratio = summary_words / article_words
            compression_ratios.append(ratio)
    
    return summary_sentences, compression_ratios

sent_counts, comp_ratios = analyze_summaries(dataset['train'])

print(f"\n📊 Summary Characteristics:")
print(f"   Average sentences per summary: {np.mean(sent_counts):.1f}")
print(f"   Most common sentence counts: {Counter(sent_counts).most_common(5)}")
print(f"\n   Compression ratio statistics:")
print(f"      Mean:   {np.mean(comp_ratios):.3f} ({np.mean(comp_ratios)*100:.1f}%)")
print(f"      Median: {np.median(comp_ratios):.3f} ({np.median(comp_ratios)*100:.1f}%)")
print(f"      Min:    {min(comp_ratios):.3f}")
print(f"      Max:    {max(comp_ratios):.3f}")

# ============================================================================
# 6. Save Sample Datasets
# ============================================================================

print("\n" + "="*70)
print("💾 SAVING SAMPLE DATASETS")
print("="*70)
print("\nCreating smaller samples for quick experiments...")

# Create samples
sample_train = dataset['train'].select(range(1000))
sample_val = dataset['validation'].select(range(200))
sample_test = dataset['test'].select(range(200))

# Save samples
os.makedirs('data/processed', exist_ok=True)

sample_train.save_to_disk('data/processed/sample_train')
sample_val.save_to_disk('data/processed/sample_val')
sample_test.save_to_disk('data/processed/sample_test')

print("✓ Saved sample datasets:")
print(f"   data/processed/sample_train (1,000 examples)")
print(f"   data/processed/sample_val (200 examples)")
print(f"   data/processed/sample_test (200 examples)")

# ============================================================================
# 7. Summary Report
# ============================================================================

print("\n" + "="*70)
print("📊 KEY INSIGHTS")
print("="*70)

print(f"""
Dataset: CNN/DailyMail
├─ Total Examples: {len(dataset['train']) + len(dataset['validation']) + len(dataset['test']):,}
├─ Train/Val/Test: {len(dataset['train']):,} / {len(dataset['validation']):,} / {len(dataset['test']):,}
│
Article Statistics:
├─ Average length: {np.mean(article_lens):.0f} words
├─ Typical range: {int(np.percentile(article_lens, 25))}-{int(np.percentile(article_lens, 75))} words
└─ BART can handle: up to 1024 tokens (~800 words)
│
Summary Statistics:
├─ Average length: {np.mean(summary_lens):.0f} words
├─ Average sentences: {np.mean(sent_counts):.1f}
└─ Compression ratio: {np.mean(comp_ratios)*100:.1f}% of original
│
Quality Assessment:
├─ ✅ Large dataset (300K+ pairs)
├─ ✅ Human-written summaries
├─ ✅ Professional content (news)
├─ ✅ Consistent formatting
└─ ✅ Perfect for fine-tuning

Next Steps:
1. Clean and filter data (remove outliers, fix formatting)
2. Test pre-trained BART model (establish baseline)
3. Fine-tune on cleaned data
4. Evaluate performance
""")

print("\n" + "="*70)
print("✅ DATA EXPLORATION COMPLETE")
print("="*70)
print("\nNext: Run 'python src/02_data_cleaning.py'")
print("="*70)
