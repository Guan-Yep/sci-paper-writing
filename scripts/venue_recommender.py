#!/usr/bin/env python3
"""
Venue Recommender: Suggest the best conferences/journals for your paper.

Analyzes paper topic and experimental results to recommend top-5 venues
with acceptance rate estimates and deadline information.

Usage:
    python venue_recommender.py --topic "deep reinforcement learning"
    python venue_recommender.py --topic "computer vision" --results "89.4% accuracy"
    python venue_recommender.py --file abstract.txt

Dependencies:
    None (pure Python, uses built-in matching)
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


# =============================================================================
# Conference/Journal Database
# =============================================================================

VENUES = [
    # CV + ML
    {
        'name': 'CVPR',
        'full_name': 'IEEE/CVF Conference on Computer Vision and Pattern Recognition',
        'category': 'Computer Vision',
        'tier': 'A*',
        'acceptance_rate': '25%',
        'h5_index': 440,
        'cycles': ['June'],
        'typical_deadline': 'November',
        'format': '8 pages + references, double column',
        'strengths': ['visual recognition', 'object detection', 'segmentation', 'generative models'],
        'keywords': ['computer vision', 'image', 'video', 'detection', 'segmentation', 'generative', 'diffusion', 'GAN'],
    },
    {
        'name': 'ICCV',
        'full_name': 'International Conference on Computer Vision',
        'category': 'Computer Vision',
        'tier': 'A*',
        'acceptance_rate': '26%',
        'h5_index': 440,
        'cycles': ['October'],
        'typical_deadline': 'March',
        'format': '8 pages + references, double column',
        'strengths': ['3D vision', 'visual understanding', 'scene understanding'],
        'keywords': ['computer vision', '3D', 'reconstruction', 'visual', 'image'],
    },
    {
        'name': 'NeurIPS',
        'full_name': 'Neural Information Processing Systems',
        'category': 'Machine Learning',
        'tier': 'A*',
        'acceptance_rate': '26%',
        'h5_index': 192,
        'cycles': ['December'],
        'typical_deadline': 'May',
        'format': '9 pages + references, single column',
        'strengths': ['deep learning theory', 'optimization', 'probabilistic methods', 'reinforcement learning'],
        'keywords': ['machine learning', 'deep learning', 'neural network', 'optimization', 'reinforcement', 'RL', 'probabilistic', 'Bayesian'],
    },
    {
        'name': 'ICML',
        'full_name': 'International Conference on Machine Learning',
        'category': 'Machine Learning',
        'tier': 'A*',
        'acceptance_rate': '28%',
        'h5_index': 192,
        'cycles': ['July'],
        'typical_deadline': 'January',
        'format': '9 pages + references, single column',
        'strengths': ['learning theory', 'algorithms', 'unsupervised learning', 'representation learning'],
        'keywords': ['machine learning', 'deep learning', 'unsupervised', 'self-supervised', 'representation', 'algorithm'],
    },
    {
        'name': 'ICLR',
        'full_name': 'International Conference on Learning Representations',
        'category': 'Machine Learning',
        'tier': 'A*',
        'acceptance_rate': '32%',
        'h5_index': 192,
        'cycles': ['May'],
        'typical_deadline': 'September',
        'format': '8 pages + references, double column',
        'strengths': ['representation learning', 'self-supervised learning', 'transfer learning', 'generative models'],
        'keywords': ['representation', 'self-supervised', 'transfer', 'meta-learning', 'few-shot', 'contrastive'],
    },
    {
        'name': 'ACL',
        'full_name': 'Annual Meeting of the Association for Computational Linguistics',
        'category': 'NLP',
        'tier': 'A*',
        'acceptance_rate': '25%',
        'h5_index': 157,
        'cycles': ['July'],
        'typical_deadline': 'December',
        'format': '8 pages + references, double column',
        'strengths': ['natural language processing', 'machine translation', 'language understanding', 'dialogue'],
        'keywords': ['NLP', 'natural language', 'text', 'translation', 'dialogue', 'LLM', 'transformer', 'BERT', 'GPT'],
    },
    {
        'name': 'EMNLP',
        'full_name': 'Conference on Empirical Methods in Natural Language Processing',
        'category': 'NLP',
        'tier': 'A*',
        'acceptance_rate': '26%',
        'h5_index': 157,
        'cycles': ['November'],
        'typical_deadline': 'June',
        'format': '8 pages + references, double column',
        'strengths': ['empirical NLP', 'language models', 'information extraction'],
        'keywords': ['NLP', 'language model', 'extraction', 'sentiment', 'parsing'],
    },
    {
        'name': 'AAAI',
        'full_name': 'AAAI Conference on Artificial Intelligence',
        'category': 'AI General',
        'tier': 'A*',
        'acceptance_rate': '23%',
        'h5_index': 178,
        'cycles': ['February'],
        'typical_deadline': 'August',
        'format': '7 pages + references, single column',
        'strengths': ['broad AI', 'planning', 'knowledge representation', 'multi-agent'],
        'keywords': ['AI', 'artificial intelligence', 'planning', 'reasoning', 'knowledge', 'agent'],
    },
    {
        'name': 'IJCAI',
        'full_name': 'International Joint Conference on Artificial Intelligence',
        'category': 'AI General',
        'tier': 'A*',
        'acceptance_rate': '20%',
        'h5_index': 134,
        'cycles': ['August'],
        'typical_deadline': 'January',
        'format': '7 pages + references, single column',
        'strengths': ['multi-agent systems', 'automated reasoning', 'AI applications'],
        'keywords': ['AI', 'multi-agent', 'automated', 'reasoning', 'game theory'],
    },
    {
        'name': 'RSS',
        'full_name': 'Robotics: Science and Systems',
        'category': 'Robotics',
        'tier': 'A',
        'acceptance_rate': '30%',
        'h5_index': 85,
        'cycles': ['July'],
        'typical_deadline': 'January',
        'format': '8 pages + references, single column',
        'strengths': ['robotics', 'manipulation', 'locomotion', 'sim-to-real'],
        'keywords': ['robotics', 'robot', 'manipulation', 'locomotion', 'control', 'sim-to-real', 'humanoid', 'bipedal'],
    },
    {
        'name': 'CoRL',
        'full_name': 'Conference on Robot Learning',
        'category': 'Robotics',
        'tier': 'A',
        'acceptance_rate': '35%',
        'h5_index': 75,
        'cycles': ['November'],
        'typical_deadline': 'June',
        'format': '8 pages + references, single column',
        'strengths': ['robot learning', 'RL for robotics', 'imitation learning'],
        'keywords': ['robotics', 'robot learning', 'reinforcement', 'imitation', 'locomotion'],
    },
    {
        'name': 'ICRA',
        'full_name': 'IEEE International Conference on Robotics and Automation',
        'category': 'Robotics',
        'tier': 'A*',
        'acceptance_rate': '40%',
        'h5_index': 120,
        'cycles': ['May'],
        'typical_deadline': 'September',
        'format': '6 pages + references, double column',
        'strengths': ['robotics hardware', 'automation', 'motion planning', 'SLAM'],
        'keywords': ['robotics', 'automation', 'SLAM', 'planning', 'navigation', 'control'],
    },
    {
        'name': 'TMLR',
        'full_name': 'Transactions on Machine Learning Research',
        'category': 'Machine Learning',
        'tier': 'A',
        'acceptance_rate': '35%',
        'h5_index': 120,
        'cycles': ['Rolling'],
        'typical_deadline': 'Rolling',
        'format': 'No page limit, single column',
        'strengths': ['rigorous ML research', 'no deadline pressure', 'open access'],
        'keywords': ['machine learning', 'deep learning', 'theory', 'algorithm'],
    },
    {
        'name': 'Nature Machine Intelligence',
        'full_name': 'Nature Machine Intelligence',
        'category': 'ML Journal',
        'tier': 'A*',
        'acceptance_rate': '8%',
        'h5_index': 120,
        'cycles': ['Monthly'],
        'typical_deadline': 'Rolling',
        'format': 'Article, no fixed length',
        'strengths': ['high-impact interdisciplinary', 'broad audience', 'prestige'],
        'keywords': ['machine learning', 'AI', 'interdisciplinary', 'biology', 'chemistry', 'physics'],
    },
    {
        'name': 'IEEE T-PAMI',
        'full_name': 'IEEE Transactions on Pattern Analysis and Machine Intelligence',
        'category': 'CV/ML Journal',
        'tier': 'A*',
        'acceptance_rate': '15%',
        'h5_index': 300,
        'cycles': ['Monthly'],
        'typical_deadline': 'Rolling',
        'format': 'Journal article, typically 12+ pages',
        'strengths': ['computer vision', 'pattern recognition', 'long-form deep analysis'],
        'keywords': ['computer vision', 'pattern recognition', 'image', 'video', 'segmentation', 'detection'],
    },
]


# =============================================================================
# Matching Engine
# =============================================================================

def score_venue(topic, results_text, venue):
    """Score how well a venue matches the paper."""
    topic_lower = topic.lower()
    results_lower = results_text.lower() if results_text else ''
    combined = topic_lower + ' ' + results_lower

    score = 0.0
    matched_keywords = []

    # Keyword matching
    for kw in venue['keywords']:
        if kw.lower() in combined:
            score += 3.0
            matched_keywords.append(kw)

    # Strength matching
    for strength in venue['strengths']:
        words = strength.lower().split()
        match_count = sum(1 for w in words if w in combined)
        if match_count > 0:
            score += match_count * 2.0

    # Category bonus
    category_keywords = {
        'computer vision': ['computer vision', 'image', 'video', 'visual'],
        'machine learning': ['machine learning', 'deep learning', 'neural', 'optimization'],
        'NLP': ['NLP', 'natural language', 'text', 'LLM', 'transformer'],
        'robotics': ['robotics', 'robot', 'locomotion', 'manipulation', 'control'],
        'AI General': ['AI', 'artificial intelligence', 'planning', 'reasoning'],
    }

    for cat, kws in category_keywords.items():
        if venue['category'] == cat:
            for kw in kws:
                if kw.lower() in combined:
                    score += 1.0

    # Tier bonus (higher tier = more competitive, but also more prestigious)
    tier_bonus = {'A*': 2.0, 'A': 1.0}
    score += tier_bonus.get(venue['tier'], 0)

    # Novelty / results strength bonus
    if results_lower:
        # Check for strong quantitative results
        strong_indicators = ['sota', 'state-of-the-art', 'outperform', 'best', 'first', 'novel']
        for ind in strong_indicators:
            if ind in results_lower:
                score += 2.0

    return score, matched_keywords


def estimate_next_deadline(venue, current_date=None):
    """Estimate the next submission deadline."""
    if current_date is None:
        current_date = datetime.now()

    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12,
    }

    if venue['typical_deadline'] == 'Rolling':
        return 'Rolling (no fixed deadline)'

    deadline_month = month_map.get(venue['typical_deadline'], 6)
    current_month = current_date.month

    # Estimate next occurrence
    if deadline_month > current_month:
        year = current_date.year
    else:
        year = current_date.year + 1

    return f"~{venue['typical_deadline']} {year} (estimated)"


def days_until_deadline(venue, current_date=None):
    """Calculate approximate days until next deadline."""
    if venue['typical_deadline'] == 'Rolling':
        return float('inf')

    if current_date is None:
        current_date = datetime.now()

    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12,
    }

    deadline_month = month_map.get(venue['typical_deadline'], 6)
    current_month = current_date.month

    if deadline_month > current_month:
        year = current_date.year
    else:
        year = current_date.year + 1

    deadline = datetime(year, deadline_month, 15)  # Approximate mid-month
    delta = deadline - current_date
    return delta.days


def recommend(topic, results_text=None, top_k=5, include_journals=True):
    """Recommend top-K venues for a paper."""
    scored = []
    for venue in VENUES:
        if not include_journals and 'Journal' in venue['category']:
            continue

        score, matched = score_venue(topic, results_text, venue)
        scored.append({
            'venue': venue,
            'score': score,
            'matched_keywords': matched,
        })

    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[:top_k]


def print_recommendations(recommendations):
    """Pretty-print recommendations."""
    print("\n" + "=" * 70)
    print("  TOP VENUE RECOMMENDATIONS")
    print("=" * 70)

    for i, rec in enumerate(recommendations, 1):
        v = rec['venue']
        score = rec['score']
        matched = rec['matched_keywords'][:5]
        deadline = estimate_next_deadline(v)
        days_left = days_until_deadline(v)

        urgency = ""
        if days_left < 60:
            urgency = " [URGENT]"
        elif days_left < 120:
            urgency = " [Soon]"
        elif days_left == float('inf'):
            urgency = " [Rolling]"

        print(f"\n  #{i} {v['name']} {urgency}")
        print(f"     Full: {v['full_name']}")
        print(f"     Category: {v['category']} | Tier: {v['tier']} | H5: {v['h5_index']}")
        print(f"     Acceptance: {v['acceptance_rate']} | Format: {v['format']}")
        print(f"     Next Deadline: {deadline}")
        if days_left != float('inf'):
            print(f"     Days Left: ~{days_left} days")
        print(f"     Match Score: {score:.1f}")
        if matched:
            print(f"     Matched Keywords: {', '.join(matched)}")
        print(f"     Strengths: {', '.join(v['strengths'][:3])}")

    print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(description='Recommend conferences/journals for your paper')
    parser.add_argument('--topic', '-t', required=True,
                        help='Paper topic or abstract text')
    parser.add_argument('--results', '-r',
                        help='Experimental results summary (e.g., "89.4% accuracy, SOTA")')
    parser.add_argument('--file', '-f',
                        help='File containing topic/abstract text')
    parser.add_argument('--top-k', '-k', type=int, default=5,
                        help='Number of recommendations')
    parser.add_argument('--no-journals', action='store_true',
                        help='Exclude journals, recommend only conferences')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')
    args = parser.parse_args()

    topic = args.topic
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            topic = f.read()

    print(f"Topic: {topic[:80]}...")
    if args.results:
        print(f"Results: {args.results[:80]}...")

    recommendations = recommend(
        topic=topic,
        results_text=args.results,
        top_k=args.top_k,
        include_journals=not args.no_journals
    )

    if args.json:
        output = []
        for rec in recommendations:
            v = rec['venue']
            output.append({
                'rank': len(output) + 1,
                'name': v['name'],
                'full_name': v['full_name'],
                'category': v['category'],
                'tier': v['tier'],
                'acceptance_rate': v['acceptance_rate'],
                'deadline': estimate_next_deadline(v),
                'days_left': days_until_deadline(v) if days_until_deadline(v) != float('inf') else None,
                'format': v['format'],
                'match_score': rec['score'],
                'matched_keywords': rec['matched_keywords'],
            })
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print_recommendations(recommendations)


if __name__ == '__main__':
    main()
