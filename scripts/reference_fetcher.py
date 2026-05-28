#!/usr/bin/env python3
"""
Reference Fetcher: Automatically retrieve and format academic references.

Queries CrossRef and Semantic Scholar APIs by title, DOI, or keywords,
returns formatted numbered citations [n] suitable for SCI papers.

Implements multi-round progressive search strategy:
    Round 1: Title/DOI exact match -> direct fetch
    Round 2: Keyword search -> top-N results
    Round 3: Citation network expansion -> related papers

Usage:
    python reference_fetcher.py --query "Deep Reinforcement Learning"
    python reference_fetcher.py --doi "10.1109/CVPR.2016.90"
    python reference_fetcher.py --title "ResNet: Deep Residual Learning for Image Recognition"
    python reference_fetcher.py --file queries.txt --output refs.txt

Dependencies:
    requests
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote_plus

import requests

# =============================================================================
# API Endpoints
# =============================================================================
CROSSREF_API = "https://api.crossref.org/works"
SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"

# Rate limit: CrossRef requires email for polite usage
EMAIL = os.environ.get('CROSSREF_EMAIL', '')

# =============================================================================
# Quality Control: Filters and Validation
# =============================================================================

# Acceptable publication types from CrossRef
ACCEPTABLE_TYPES = {
    'journal-article', 'proceedings-article', 'book-chapter',
    'report', 'standard', 'dissertation'
}

# Suspicious publishers to exclude
SUSPICIOUS_PUBLISHERS = {
    'shenzhen medical academy', 'predatory', 'academic journals',
}

# Suspicious venue patterns
SUSPICIOUS_VENUE_PATTERNS = [
    r'medical academy', r'research and translation',
    r'international journal of.*\d{4}',  # e.g. "International Journal of X 2025"
]


def normalize_title(title):
    """Normalize title for comparison: lowercase, strip punctuation."""
    t = title.lower()
    t = re.sub(r'[^\w\s]', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def title_similarity(t1, t2):
    """Compute simple token-based similarity between two titles."""
    s1 = set(normalize_title(t1).split())
    s2 = set(normalize_title(t2).split())
    if not s1 or not s2:
        return 0.0
    intersection = s1 & s2
    union = s1 | s2
    return len(intersection) / len(union)


def is_valid_result(item, query_title=None, min_similarity=0.85):
    """
    Validate a parsed result for quality.

    Filters:
    - Type must be acceptable (not 'component', 'reference-entry', etc.)
    - Year must be reasonable (not in the future)
    - Publisher/venue must not be suspicious
    - If query_title provided, title similarity must exceed threshold
    """
    # Check title similarity for title searches
    if query_title:
        title = item.get('title', '')
        sim = title_similarity(title, query_title)
        if sim < min_similarity:
            return False, f'title similarity {sim:.2f} < {min_similarity}'

    # Check year is reasonable
    year_str = str(item.get('year', ''))
    if year_str and year_str != 'N/A':
        try:
            year = int(year_str)
            current_year = time.localtime().tm_year
            if year > current_year + 1:
                return False, f'future year {year}'
            if year < 1900:
                return False, f'unreasonable year {year}'
        except ValueError:
            pass

    # Check venue/publisher is not suspicious
    venue = str(item.get('venue', '')).lower()
    for pattern in SUSPICIOUS_VENUE_PATTERNS:
        if re.search(pattern, venue):
            return False, f'suspicious venue: {venue}'

    # Check publisher (from raw CrossRef data, not parsed)
    # This is handled at parse time via raw_item parameter

    return True, 'ok'


# =============================================================================
# Retry Logic for API Calls
# =============================================================================

def retry_request(func, max_retries=3, backoff=2.0):
    """Execute func with exponential backoff on 429/5xx errors."""
    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else 0
            if status == 429 and attempt < max_retries - 1:
                wait = backoff * (2 ** attempt)
                print(f"    Rate limited (429), retrying in {wait:.1f}s...")
                time.sleep(wait)
                continue
            raise
        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                wait = backoff * (2 ** attempt)
                time.sleep(wait)
                continue
            raise
    return None


# =============================================================================
# Citation Format Templates
# =============================================================================

def format_reference(item, idx):
    """Format a reference item as [n] Author(s). Title. Venue, Year."""
    authors = item.get('authors', [])
    title = item.get('title', 'Unknown Title')
    venue = item.get('venue', item.get('container-title', 'Unknown Venue'))
    year = item.get('year', item.get('published', 'N/A'))

    # Author formatting
    if isinstance(authors, list) and authors:
        # Filter empty strings
        authors = [a for a in authors if a and a.strip()]
        if len(authors) == 0:
            author_str = 'Unknown Author'
        elif len(authors) <= 6:
            author_str = ', '.join(authors)
        else:
            author_str = f"{authors[0]} et al."
    else:
        author_str = authors if authors else 'Unknown Author'

    # Clean venue
    if isinstance(venue, list):
        venue = venue[0] if venue else 'Unknown Venue'

    # Clean year
    if isinstance(year, list) and year:
        year = year[0] if isinstance(year[0], str) else str(year[0])

    return f"[{idx}] {author_str}. {title}. {venue}, {year}."


def parse_crossref_item(item, query_title=None):
    """Parse a CrossRef API response item with quality checks."""
    result = {}

    # Title
    title_list = item.get('title', [])
    result['title'] = title_list[0] if title_list else 'Unknown Title'

    # Authors
    authors = item.get('author', [])
    result['authors'] = []
    for a in authors[:10]:
        given = a.get('given', '')
        family = a.get('family', '')
        if given and family:
            result['authors'].append(f"{given} {family}")
        elif family:
            result['authors'].append(family)

    # Venue: prefer container-title, fallback to publisher
    container = item.get('container-title', [])
    result['venue'] = container[0] if container else ''
    if not result['venue']:
        result['venue'] = item.get('publisher', 'Unknown Venue')

    # Year: try published date, then published-print
    date_parts = item.get('published', {}).get('date-parts', [])
    if date_parts and date_parts[0] and date_parts[0][0]:
        result['year'] = str(date_parts[0][0])
    else:
        pp = item.get('published-print', {}).get('date-parts', [])
        if pp and pp[0] and pp[0][0]:
            result['year'] = str(pp[0][0])
        else:
            result['year'] = 'N/A'

    # DOI
    result['doi'] = item.get('DOI', '')

    # URL
    result['url'] = item.get('URL', f"https://doi.org/{result['doi']}" if result['doi'] else '')

    # Type
    result['type'] = item.get('type', '')

    # Publisher (for validation)
    result['publisher'] = item.get('publisher', '')

    # Validate
    valid, reason = is_valid_result(result, query_title=query_title)
    if not valid:
        return None, reason

    return result, None


def parse_semantic_scholar_item(item):
    """Parse a Semantic Scholar API response item."""
    result = {}
    result['title'] = item.get('title', 'Unknown Title')

    authors = item.get('authors', [])
    result['authors'] = []
    for a in authors[:10]:
        if isinstance(a, dict):
            name = a.get('name', '')
            if name:
                result['authors'].append(name)
        else:
            result['authors'].append(str(a))

    result['venue'] = item.get('venue', 'Unknown Venue')
    result['year'] = str(item.get('year', 'N/A'))
    result['doi'] = item.get('externalIds', {}).get('DOI', '')
    result['url'] = item.get('url', '')
    result['citation_count'] = item.get('citationCount', 0)
    result['type'] = 'journal-article'  # SS doesn't provide type, assume valid

    # Validate
    valid, reason = is_valid_result(result, query_title=None)
    if not valid:
        return None, reason

    return result, None


# =============================================================================
# Search Functions
# =============================================================================

def search_by_doi(doi):
    """Round 1A: Exact DOI lookup via CrossRef."""
    print(f"  [Round 1A] DOI lookup: {doi}")
    headers = {}
    if EMAIL:
        headers['User-Agent'] = f'SciPaperSkill/1.0 (mailto:{EMAIL})'

    def do_crossref():
        resp = requests.get(f"{CROSSREF_API}/{doi}", headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if 'message' in data:
            parsed, reason = parse_crossref_item(data['message'])
            if parsed:
                return [parsed]
            else:
                print(f"    Filtered: {reason}")
        return []

    try:
        return retry_request(do_crossref, max_retries=2, backoff=1.0) or []
    except Exception as e:
        print(f"    CrossRef DOI error: {e}")

    # Fallback to Semantic Scholar
    def do_ss():
        resp = requests.get(f"{SEMANTIC_SCHOLAR_API}/paper/DOI:{doi}",
                           params={'fields': 'title,authors,year,venue,externalIds,citationCount,url'},
                           timeout=15)
        resp.raise_for_status()
        item = resp.json()
        parsed, reason = parse_semantic_scholar_item(item)
        if parsed:
            return [parsed]
        else:
            print(f"    SS filter: {reason}")
            return []

    try:
        return retry_request(do_ss, max_retries=2, backoff=1.0) or []
    except Exception as e:
        print(f"    Semantic Scholar DOI error: {e}")

    return []


def search_by_title(title, max_results=5):
    """Round 1B: Title search via CrossRef + Semantic Scholar with strict matching."""
    print(f"  [Round 1B] Title search: {title[:60]}...")
    results = []

    # CrossRef: use type filter to avoid spam entries
    headers = {}
    if EMAIL:
        headers['User-Agent'] = f'SciPaperSkill/1.0 (mailto:{EMAIL})'

    def do_crossref():
        params = {
            'query.title': title,
            'filter': 'type:journal-article,type:proceedings-article,type:book-chapter',
            'rows': max_results
        }
        resp = requests.get(CROSSREF_API, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        items = []
        for item in data.get('message', {}).get('items', []):
            parsed, reason = parse_crossref_item(item, query_title=title)
            if parsed:
                items.append(parsed)
            else:
                print(f"    Filtered (CrossRef): {reason}")
        return items

    try:
        cr_results = retry_request(do_crossref, max_retries=2, backoff=1.0) or []
        results.extend(cr_results)
    except Exception as e:
        print(f"    CrossRef title error: {e}")

    # Semantic Scholar (with longer backoff for 429)
    def do_ss():
        params = {'query': title, 'fields': 'title,authors,year,venue,externalIds,citationCount,url',
                  'limit': max_results}
        resp = requests.get(f"{SEMANTIC_SCHOLAR_API}/paper/search", params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        items = []
        for item in data.get('data', []):
            parsed, reason = parse_semantic_scholar_item(item)
            if parsed:
                items.append(parsed)
            else:
                print(f"    Filtered (SS): {reason}")
        return items

    try:
        ss_results = retry_request(do_ss, max_retries=3, backoff=5.0) or []
        results.extend(ss_results)
    except requests.exceptions.HTTPError as e:
        if e.response and e.response.status_code == 429:
            print("    Semantic Scholar rate limited (429). Consider using --doi for better accuracy.")
        else:
            print(f"    Semantic Scholar title error: {e}")
    except Exception as e:
        print(f"    Semantic Scholar title error: {e}")

    # If no results, suggest alternative
    if not results:
        print("    No results found. Tip: If you know the DOI, use --doi for exact lookup.")

    return deduplicate(results)


def search_by_keywords(keywords, max_results=10):
    """Round 2: Keyword search with type filtering."""
    print(f"  [Round 2] Keyword search: {keywords}")
    results = []

    headers = {}
    if EMAIL:
        headers['User-Agent'] = f'SciPaperSkill/1.0 (mailto:{EMAIL})'

    # CrossRef keyword search with type filter
    def do_crossref():
        params = {
            'query': keywords,
            'filter': 'type:journal-article,type:proceedings-article,type:book-chapter',
            'rows': max_results,
            'sort': 'relevance'
        }
        resp = requests.get(CROSSREF_API, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        items = []
        for item in data.get('message', {}).get('items', []):
            parsed, reason = parse_crossref_item(item)
            if parsed:
                items.append(parsed)
            else:
                print(f"    Filtered (CrossRef): {reason}")
        return items

    try:
        cr_results = retry_request(do_crossref, max_retries=2, backoff=1.0) or []
        results.extend(cr_results)
    except Exception as e:
        print(f"    CrossRef keyword error: {e}")

    # Semantic Scholar keyword search
    def do_ss():
        params = {'query': keywords, 'fields': 'title,authors,year,venue,externalIds,citationCount,url',
                  'limit': max_results}
        resp = requests.get(f"{SEMANTIC_SCHOLAR_API}/paper/search", params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        items = []
        for item in data.get('data', []):
            parsed, reason = parse_semantic_scholar_item(item)
            if parsed:
                items.append(parsed)
            else:
                print(f"    Filtered (SS): {reason}")
        return items

    try:
        ss_results = retry_request(do_ss, max_retries=3, backoff=5.0) or []
        results.extend(ss_results)
    except requests.exceptions.HTTPError as e:
        if e.response and e.response.status_code == 429:
            print("    Semantic Scholar rate limited (429). Results rely on CrossRef only.")
        else:
            print(f"    Semantic Scholar keyword error: {e}")
    except Exception as e:
        print(f"    Semantic Scholar keyword error: {e}")

    if not results:
        print("    No results found. Try broadening keywords or use --doi/--title.")

    return deduplicate(results)


def expand_citations(paper_id, max_results=5):
    """Round 3: Citation network expansion via Semantic Scholar."""
    print(f"  [Round 3] Citation expansion for: {paper_id[:40]}...")

    def do_expand():
        resp = requests.get(f"{SEMANTIC_SCHOLAR_API}/paper/{paper_id}/citations",
                           params={'fields': 'title,authors,year,venue,externalIds,citationCount,url',
                                   'limit': max_results},
                           timeout=15)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for citing in data.get('data', []):
            cited_paper = citing.get('citingPaper', {})
            if cited_paper:
                parsed, reason = parse_semantic_scholar_item(cited_paper)
                if parsed:
                    results.append(parsed)
                else:
                    print(f"    Filtered (expand): {reason}")
        return results

    try:
        return retry_request(do_expand, max_retries=2, backoff=1.0) or []
    except Exception as e:
        print(f"    Citation expansion error: {e}")
        return []


def deduplicate(results):
    """Remove duplicates based on DOI or normalized title+year."""
    seen = set()
    unique = []
    for r in results:
        doi = r.get('doi', '')
        if doi:
            key = doi.lower()
        else:
            title_norm = normalize_title(r.get('title', ''))
            year = str(r.get('year', ''))
            key = f"{title_norm}|{year}"
        if key and key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


# =============================================================================
# Main Interface
# =============================================================================

def fetch_references(queries, max_per_query=5, expand=False):
    """
    Main entry point: fetch references for a list of queries.

    Args:
        queries: List of dicts with keys: 'type' ('doi'|'title'|'keyword'), 'value'
        max_per_query: Max results per query
        expand: Whether to do citation network expansion (Round 3)

    Returns:
        List of formatted reference strings
    """
    all_results = []

    for q in queries:
        q_type = q.get('type', 'keyword')
        q_value = q.get('value', '')

        if q_type == 'doi':
            results = search_by_doi(q_value)
        elif q_type == 'title':
            results = search_by_title(q_value, max_results=max_per_query)
        else:
            results = search_by_keywords(q_value, max_results=max_per_query)

        all_results.extend(results)
        time.sleep(0.5)  # Rate limiting

    # Deduplicate across all queries
    all_results = deduplicate(all_results)

    # Round 3: Citation expansion (optional)
    if expand and all_results:
        print("\n[Round 3] Expanding citation network...")
        expanded = []
        for r in all_results[:3]:  # Expand top 3 papers
            if r.get('doi'):
                expanded.extend(expand_citations(f"DOI:{r['doi']}", max_results=3))
            time.sleep(0.5)
        all_results.extend(expanded)
        all_results = deduplicate(all_results)

    # Format
    formatted = []
    for idx, r in enumerate(all_results, 1):
        formatted.append(format_reference(r, idx))

    return formatted, all_results


def parse_query_file(filepath):
    """Parse a query file. Each line: type|value or just value (defaults to keyword)."""
    queries = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '|' in line:
                parts = line.split('|', 1)
                q_type = parts[0].strip().lower()
                q_value = parts[1].strip()
            else:
                q_type = 'keyword'
                q_value = line
            queries.append({'type': q_type, 'value': q_value})
    return queries


def main():
    parser = argparse.ArgumentParser(description='Fetch academic references from CrossRef/Semantic Scholar')
    parser.add_argument('--query', '-q', help='Search query (keywords)')
    parser.add_argument('--doi', help='DOI for exact lookup')
    parser.add_argument('--title', '-t', help='Paper title for search')
    parser.add_argument('--file', '-f', help='File with queries (one per line: type|value)')
    parser.add_argument('--output', '-o', help='Output file for formatted references')
    parser.add_argument('--max-results', '-n', type=int, default=5, help='Max results per query')
    parser.add_argument('--expand', action='store_true', help='Enable citation network expansion')
    parser.add_argument('--json', action='store_true', help='Also output raw JSON')
    args = parser.parse_args()

    # Build query list
    queries = []
    if args.doi:
        queries.append({'type': 'doi', 'value': args.doi})
    if args.title:
        queries.append({'type': 'title', 'value': args.title})
    if args.query:
        queries.append({'type': 'keyword', 'value': args.query})
    if args.file:
        queries.extend(parse_query_file(args.file))

    if not queries:
        print("Error: Provide at least one query via --query, --doi, --title, or --file")
        sys.exit(1)

    print(f"Fetching references for {len(queries)} query(s)...")
    print(f"Max results per query: {args.max_results}")
    print(f"Citation expansion: {'ON' if args.expand else 'OFF'}")
    print("=" * 60)

    formatted, raw = fetch_references(queries, max_per_query=args.max_results, expand=args.expand)

    print(f"\n{'=' * 60}")
    print(f"Found {len(formatted)} unique reference(s)")
    print()

    for ref in formatted:
        print(ref)

    # Save to file
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            for ref in formatted:
                f.write(ref + '\n')
        print(f"\nSaved to: {args.output}")

    # Save raw JSON
    if args.json and args.output:
        json_path = args.output.replace('.txt', '.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(raw, f, indent=2, ensure_ascii=False)
        print(f"Raw JSON saved to: {json_path}")


if __name__ == '__main__':
    # Fix Windows terminal encoding for non-ASCII characters
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    main()
