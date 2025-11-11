#!/usr/bin/env python3
"""
Extract semantic data from Polish WordNet for game words.
Creates an enhanced JSON file with word metadata including hypernyms, collocations, fuzzy synonyms, and hints.
"""

import json
from collections import defaultdict
from typing import Any

import plwordnet

# Load plWordNet
print("Loading plWordNet database...")
wn = plwordnet.load("plwordnet_data/plwordnet_4_2/plwordnet_4_2.xml")
print(f"✅ Loaded {len(wn.lexical_units)} lexical units\n")


def get_fuzzy_synonyms(lexical_unit, wn, max_count: int = 3) -> list[str]:
    """
    Get fuzzy synonyms - similar but not exact matches.
    These provide helpful hints without being too revealing.
    """
    fuzzy_synonyms = []

    for subj, pred, obj in wn.lexical_relations_where(subject=lexical_unit):
        pred_name = pred.name.lower()
        base_lemma = obj.name.split(".")[0]

        # Fuzzy synonyms - similar but not exact
        if "fuzzynimia" in pred_name:
            if base_lemma not in fuzzy_synonyms:
                fuzzy_synonyms.append(base_lemma)

    return fuzzy_synonyms[:max_count]


def get_hypernym_words(
    synset, wn, max_count: int = 3, preferred_level: int = 3
) -> list[str]:
    """
    Get hypernyms from preferred_level and fill the rest going DOWN the path.
    This creates a natural progression from abstract to specific.

    Example: preferred_level=3, max_count=3
      → Try level 3 (most abstract)
      → Then level 2
      → Then level 1 (most specific)

    Parameters
    ----------
    preferred_level : int
        Starting level to get hypernyms from (3 = most abstract)
    """
    hypernym_words = []

    # Build hypernym hierarchy levels (0=synset, 1=direct hypernym, 2=2 up, etc.)
    levels = [[synset]]
    for _ in range(preferred_level + 1):
        current_level = levels[-1]
        next_level = []
        for syn in current_level:
            next_level.extend(wn.hypernyms(syn))
        if not next_level:
            break
        levels.append(next_level)

    # Get hypernyms starting from preferred_level and going DOWN
    # This gives: most abstract → less abstract → most specific
    for level in range(preferred_level, 0, -1):
        if len(hypernym_words) >= max_count:
            break

        if len(levels) > level:
            for h in levels[level]:
                if len(hypernym_words) >= max_count:
                    break

                if h.lexical_units:
                    lu = next(iter(h.lexical_units))
                    base_lemma = lu.name.split(".")[0]
                    if base_lemma not in hypernym_words:
                        hypernym_words.append(base_lemma)

    return hypernym_words[:max_count]


def get_collocations(lexical_unit, wn, max_count: int = 5) -> list[str]:
    """
    Get only collocations (words that commonly appear together) and modifiers.
    These provide contextual hints without being too revealing.
    """
    collocations = []

    for subj, pred, obj in wn.lexical_relations_where(subject=lexical_unit):
        pred_name = pred.name.lower()
        base_lemma = obj.name.split(".")[0]

        # Only include collocations and modifiers
        if "kolokacyjność" in pred_name or "określnik" in pred_name:
            if base_lemma not in collocations and len(collocations) < max_count:
                collocations.append(base_lemma)

    return collocations


def generate_hints(
    fuzzy: list[str],
    hypernyms: list[str],
    collocations: list[str],
) -> list[str]:
    """
    Generate helpful hints for the impostor.
    Uses hypernyms (for broader categories), collocations, and fuzzy synonyms.
    Category is kept in JSON metadata but not shown in hints to avoid redundancy.
    """
    hints = []

    # Add hypernym hints (these provide the category progression)
    if hypernyms:
        for hypernym in hypernyms:
            hints.append(f"Rodzaj: {hypernym}")

    # Add collocation hints (contextual words that appear together)
    if collocations:
        hints.append(f"Często z: {', '.join(collocations[:3])}")

    # Add fuzzy synonym hint (similar but not exact)
    if fuzzy:
        hints.append(f"Podobne do: {fuzzy[0]}")

    return hints  # Max 5 hints


def assess_difficulty(word: str, collocations: list[str], hypernyms: list[str]) -> str:
    """Assess word difficulty for the game based on word length and available hints."""
    # Base difficulty on word length
    if len(word) <= 4:
        base_difficulty = "easy"
    elif len(word) <= 7:
        base_difficulty = "medium"
    else:
        base_difficulty = "hard"

    # Having good hints makes it easier
    if (len(hypernyms) >= 2 or len(collocations) >= 2) and base_difficulty == "hard":
        return "medium"

    return base_difficulty


def extract_word_data(word: str, wn) -> dict[str, Any] | None:
    """Extract all semantic data for a word from WordNet."""
    lexical_units = wn.find(word)

    if not lexical_units:
        return None

    # Use the first (most common) lexical unit
    lu = lexical_units[0]
    synset = lu.synset

    # Extract data
    fuzzy_synonyms = get_fuzzy_synonyms(lu, wn)
    hypernyms = get_hypernym_words(synset, wn)
    collocations = get_collocations(lu, wn)

    # Generate hints (using fuzzy synonyms, hypernyms, and collocations)
    hints = generate_hints(fuzzy_synonyms, hypernyms, collocations)

    # Skip words with no hints
    if not hints:
        return None

    # Assess difficulty
    difficulty = assess_difficulty(word, collocations, hypernyms)

    return {
        "word": word,
        "fuzzy_synonyms": fuzzy_synonyms,
        "hypernyms": hypernyms,
        "collocations": collocations,
        "hints": hints,
        "difficulty": difficulty,
        "variants": len(lexical_units),  # How many meanings this word has
    }


def process_word_list(words: list[str], output_file: str = "enhanced_words.json"):
    """Process a list of words and create enhanced JSON file."""
    enhanced_words = []
    not_found = []

    print(f"Processing {len(words)} words...")

    for i, word in enumerate(words, 1):
        if i % 10 == 0:
            print(f"  Processed {i}/{len(words)} words...")

        word_data = extract_word_data(word, wn)

        if word_data:
            enhanced_words.append(word_data)
        else:
            not_found.append(word)

    # Create output structure
    output = {
        "metadata": {
            "total_words": len(enhanced_words),
            "source": "plWordNet 4.2",
            "not_found_count": len(not_found),
        },
        "words": enhanced_words,
    }

    # Save to JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Successfully processed {len(enhanced_words)} words")
    print(f"❌ Could not find {len(not_found)} words in WordNet")
    if not_found:
        print(
            f"   Not found: {', '.join(not_found[:10])}{'...' if len(not_found) > 10 else ''}"
        )
    print(f"📄 Saved to: {output_file}")

    # Print difficulty distribution
    difficulty_counts = defaultdict(int)
    for w in enhanced_words:
        difficulty_counts[w["difficulty"]] += 1

    print(f"\n📊 Difficulty distribution:")
    for diff, count in sorted(difficulty_counts.items()):
        print(f"   {diff}: {count}")


if __name__ == "__main__":
    # Load existing word list
    print("Loading existing word list...")
    with open("functions/words.txt", "r", encoding="utf-8") as f:
        all_words = [line.strip() for line in f if line.strip()]

    # Process all words
    print(f"Processing all {len(all_words)} words\n")

    process_word_list(all_words, "functions/enhanced_words.json")
