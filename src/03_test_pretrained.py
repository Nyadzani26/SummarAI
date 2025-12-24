"""
Step 3: Test Pre-trained BART Model
Load BART and test on cleaned data to establish baseline performance

Run this script to:
- Download pre-trained BART model (~1.6GB, first time only)
- Test summarization on sample articles
- Calculate ROUGE scores (quality metrics)
- Save baseline results
- See AI summarization in action!
"""

from transformers import BartForConditionalGeneration, BartTokenizer
from datasets import load_from_disk
import torch
from tqdm import tqdm
import warnings
import json
import time
import os

warnings.filterwarnings('ignore')

print("="*70)
print("🤖 STEP 3: TEST PRE-TRAINED BART MODEL")
print("="*70)

# ============================================================================
# 1. Load Pre-trained BART Model
# ============================================================================

print("\n📥 Loading BART model (facebook/bart-large-cnn)...")
print("⏱️  First time: Downloads ~1.6GB (5-10 minutes)")
print("⏱️  Subsequent runs: Instant (cached)\n")

model_name = "facebook/bart-large-cnn"

try:
    print("Loading tokenizer...")
    tokenizer = BartTokenizer.from_pretrained(model_name)
    print("✓ Tokenizer loaded")
    
    print("\nLoading model (this is the big download)...")
    model = BartForConditionalGeneration.from_pretrained(model_name)
    print("✓ Model loaded")
    
    # Move to GPU if available, otherwise CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    
    print(f"\n✓ Model ready on {device.upper()}")
    if device == "cpu":
        print("  💡 Using CPU (slower but works fine)")
        print("  💡 GPU would be 10x faster, but not needed for testing")
    
except Exception as e:
    print(f"\n❌ Error loading model: {e}")
    print("\nTroubleshooting:")
    print("1. Check internet connection")
    print("2. Ensure ~5GB free disk space")
    print("3. Try again (download may have been interrupted)")
    exit(1)

# ============================================================================
# 2. Load Test Data
# ============================================================================

print("\n" + "="*70)
print("📂 LOADING TEST DATA")
print("="*70)

try:
    test_dataset = load_from_disk('data/processed/test_cleaned')
    print(f"\n✓ Loaded {len(test_dataset):,} test examples")
except Exception as e:
    print(f"\n❌ Error loading test data: {e}")
    print("Make sure you ran Step 2 (data cleaning) first!")
    exit(1)

# ============================================================================
# 3. Define Summarization Function
# ============================================================================

print("\n" + "="*70)
print("⚙️ DEFINING SUMMARIZATION FUNCTION")
print("="*70)

def summarize_text(text, max_length=150, min_length=30, 
                   length_penalty=2.0, num_beams=4):
    """
    Generate summary for given text
    
    Parameters explained:
    - max_length: Maximum words in summary (150 is ~2-3 sentences)
    - min_length: Minimum words (30 ensures decent detail)
    - length_penalty: >1 favors longer summaries, <1 favors shorter
    - num_beams: Beam search width (4 is good balance of quality/speed)
    
    Returns:
        summary (str)
    """
    
    # Tokenize input (convert text to numbers model understands)
    inputs = tokenizer(
        text, 
        max_length=1024,      # BART max input length
        truncation=True,       # Cut off if longer
        return_tensors="pt"    # Return PyTorch tensors
    ).to(device)
    
    # Generate summary
    with torch.no_grad():  # Don't compute gradients (faster, less memory)
        summary_ids = model.generate(
            inputs["input_ids"],
            max_length=max_length,
            min_length=min_length,
            length_penalty=length_penalty,
            num_beams=num_beams,
            early_stopping=True
        )
    
    # Decode (convert numbers back to text)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    return summary

print("\n✓ Summarization function ready")
print("\n💡 How it works:")
print("   1. Tokenize: Text → Numbers")
print("   2. Generate: Model creates summary tokens")
print("   3. Decode: Numbers → Text")

# ============================================================================
# 4. Test on Single Example
# ============================================================================

print("\n" + "="*70)
print("🧪 TESTING ON SINGLE EXAMPLE")
print("="*70)

example = test_dataset[0]

print(f"\n📄 Original Article ({len(example['article'].split())} words):")
print("-" * 70)
print(example['article'][:500] + "...")
print("-" * 70)

print(f"\n📝 Reference Summary ({len(example['summary'].split())} words):")
print("-" * 70)
print(example['summary'])
print("-" * 70)

print("\n🤖 Generating AI summary...")
start_time = time.time()
generated = summarize_text(example['article'])
elapsed = time.time() - start_time

print(f"\n✨ Generated Summary ({len(generated.split())} words):")
print("-" * 70)
print(generated)
print("-" * 70)
print(f"\n⏱️  Generation time: {elapsed:.2f} seconds")

# ============================================================================
# 5. Test on Multiple Examples
# ============================================================================

print("\n" + "="*70)
print("📊 TESTING ON MULTIPLE EXAMPLES")
print("="*70)

num_examples = min(5, len(test_dataset))
print(f"\nGenerating summaries for {num_examples} examples...\n")

for i in range(num_examples):
    example = test_dataset[i]
    generated = summarize_text(example['article'])
    
    print(f"\n{'='*70}")
    print(f"Example {i+1}/{num_examples}")
    print(f"{'='*70}")
    
    print(f"\n📄 Article preview ({len(example['article'].split())} words):")
    print(example['article'][:200] + "...")
    
    print(f"\n📝 Reference summary:")
    print(example['summary'][:150] + ("..." if len(example['summary']) > 150 else ""))
    
    print(f"\n🤖 AI Generated:")
    print(generated)

# ============================================================================
# 6. Evaluate with ROUGE Scores
# ============================================================================

print("\n" + "="*70)
print("📈 CALCULATING ROUGE SCORES")
print("="*70)

try:
    from evaluate import load
    rouge = load('rouge')
    print("\n✓ ROUGE evaluator loaded")
except Exception as e:
    print(f"\n❌ Error loading ROUGE: {e}")
    print("Install with: pip install rouge-score")
    exit(1)

# Evaluate on 100 examples (good balance of accuracy and speed)
num_eval = min(100, len(test_dataset))
print(f"\n🧪 Evaluating on {num_eval} examples...")
print("⏱️  This will take 5-15 minutes depending on your machine\n")

references = []
predictions = []

for i in tqdm(range(num_eval), desc="Generating summaries"):
    example = test_dataset[i]
    
    # Generate summary
    generated = summarize_text(example['article'])
    
    references.append(example['summary'])
    predictions.append(generated)

# Calculate ROUGE scores
print("\n📊 Calculating ROUGE scores...")
results = rouge.compute(predictions=predictions, references=references)

print("\n" + "="*70)
print("🎯 BASELINE PERFORMANCE (Pre-trained BART)")
print("="*70)

print(f"""
ROUGE Scores (0.0 to 1.0, higher is better):
   
   ROUGE-1: {results['rouge1']:.4f}
      ↳ Unigram overlap (individual words match)
      ↳ Measures content coverage
   
   ROUGE-2: {results['rouge2']:.4f}
      ↳ Bigram overlap (2-word phrases match)
      ↳ Measures fluency and coherence
   
   ROUGE-L: {results['rougeL']:.4f}
      ↳ Longest common subsequence
      ↳ Measures sentence structure similarity

💡 What do these scores mean?
   
   0.35-0.40: Good baseline
   0.40-0.45: Very good (typical for BART)
   0.45+:     Excellent (near human-level)
   
Your baseline: ROUGE-1 = {results['rouge1']:.4f}
   
🎯 Goal: Beat this with fine-tuning!
   Target improvement: +0.03 to +0.05 points
""")

# ============================================================================
# 7. Parameter Experiments
# ============================================================================

print("\n" + "="*70)
print("🔬 EXPERIMENTING WITH PARAMETERS")
print("="*70)

example = test_dataset[0]

print("\n💡 Testing different generation settings on one example:\n")

configs = [
    {"name": "Short & Fast", "max_length": 100, "min_length": 20, "num_beams": 2},
    {"name": "Balanced (Default)", "max_length": 150, "min_length": 30, "num_beams": 4},
    {"name": "Detailed & Careful", "max_length": 200, "min_length": 50, "num_beams": 8},
]

for i, config in enumerate(configs, 1):
    name = config.pop("name")
    summary = summarize_text(example['article'], **config)
    
    print(f"\n{i}. {name}:")
    print(f"   Settings: {config}")
    print(f"   Result ({len(summary.split())} words):")
    print(f"   {summary}")

print("\n💡 Observations:")
print("   - More beams = better quality, slower")
print("   - Longer max_length = more detail")
print("   - Default settings usually work best")

# ============================================================================
# 8. Save Baseline Results
# ============================================================================

print("\n" + "="*70)
print("💾 SAVING BASELINE RESULTS")
print("="*70)

os.makedirs('models/pretrained', exist_ok=True)

baseline_results = {
    "model": model_name,
    "device": device,
    "num_eval_samples": num_eval,
    "generation_params": {
        "max_length": 150,
        "min_length": 30,
        "length_penalty": 2.0,
        "num_beams": 4
    },
    "rouge_scores": {
        "rouge1": float(results['rouge1']),
        "rouge2": float(results['rouge2']),
        "rougeL": float(results['rougeL'])
    },
    "example_predictions": [
        {
            "article": test_dataset[i]['article'][:300] + "...",
            "reference": test_dataset[i]['summary'],
            "generated": predictions[i]
        }
        for i in range(min(5, len(predictions)))
    ]
}

results_path = 'models/pretrained/baseline_results.json'
with open(results_path, 'w') as f:
    json.dump(baseline_results, f, indent=2)

print(f"\n✓ Saved baseline results to: {results_path}")

# ============================================================================
# 9. Summary
# ============================================================================

print("\n" + "="*70)
print("✅ BASELINE TESTING COMPLETE")
print("="*70)

print(f"""
🎯 Your Baseline Performance:
   
   ROUGE-1: {results['rouge1']:.4f}
   ROUGE-2: {results['rouge2']:.4f}
   ROUGE-L: {results['rougeL']:.4f}
   
   This is your benchmark to beat!

📊 What We Learned:
   
   ✓ Pre-trained BART works well out-of-the-box
   ✓ Generates abstractive summaries (not copy-paste)
   ✓ Takes ~{elapsed:.1f}s per summary on {device.upper()}
   ✓ Quality is already quite good
   
🎓 Key ML Concepts Covered:
   
   ✓ Tokenization (text → numbers)
   ✓ Model inference (forward pass)
   ✓ Beam search (generation strategy)
   ✓ Evaluation metrics (ROUGE)
   ✓ Baseline establishment

🔜 Next Steps:
   
   Option A: Fine-tune on your data (recommended)
      - Further improve these scores
      - Adapt to your domain
      - Run: Check QUICKSTART.md for fine-tuning guide
   
   Option B: Start building the application
      - Use this pre-trained model
      - Already good enough for many use cases
      - Move to Phase 2: Backend API

💡 Recommendation:
   
   The current model already works well! You can:
   1. Proceed to fine-tuning (Step 4) for better scores
   2. OR start building the web app with this baseline
   
   Either way, you've learned the core ML concepts! 🎉
""")

print("\n" + "="*70)
print("🎯 Phase 1: ML Model Development")
print("="*70)
print("""
Progress:
   ✓ Step 1: Data Exploration
   ✓ Step 2: Data Cleaning
   ✓ Step 3: Baseline Testing  ← YOU ARE HERE
   
   Next Options:
   □ Step 4: Fine-tuning (Google Colab)
   □ Phase 2: Build Backend API
   □ Phase 3: Build Frontend
""")

print("\n" + "="*70)
print("🎉 CONGRATULATIONS!")
print("="*70)
print("\nYou've successfully:")
print("   ✓ Set up ML environment")
print("   ✓ Explored and cleaned data")
print("   ✓ Tested a state-of-the-art AI model")
print("   ✓ Evaluated model performance")
print("   ✓ Learned core NLP/ML concepts")
print("\nYou now understand how document summarization works! 🚀")
print("="*70)
