import sqlite3
import os
from rapidfuzz import process, fuzz
import re

def tokenize(text):
    if not text:
        return ""
    return " ".join(re.findall(r'\b\w+\b', text.lower()))

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "nutrition.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Create foods table
    c.execute('''
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,
            name_pt TEXT NOT NULL,
            name_en TEXT NOT NULL,
            category TEXT,
            cooking_method TEXT,
            density_g_cm3 REAL NOT NULL,
            kcal_100g REAL NOT NULL,
            protein_100g REAL NOT NULL,
            carbs_100g REAL NOT NULL,
            fat_100g REAL NOT NULL,
            fiber_100g REAL NOT NULL,
            typical_unit_weight_g REAL
        )
    ''')

    # Create barcodes table
    c.execute('''
        CREATE TABLE IF NOT EXISTS barcodes (
            ean13 TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            serving_size_g REAL,
            kcal_100g REAL,
            protein_100g REAL,
            carbs_100g REAL,
            fat_100g REAL
        )
    ''')

    # Create user_containers table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_containers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            diameter_cm REAL,
            depth_cm REAL,
            volume_ml REAL
        )
    ''')

    # Create FTS5 virtual table for faster/flexible searching
    c.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS foods_fts USING fts5(
            name_pt, name_en, category, slug
        )
    ''')

    conn.commit()
    conn.close()

def fuzzy_search_food(query: str, limit: int = 5):
    """
    Hybrid search: uses FTS first, then uses rapidfuzz on all foods if necessary.
    """
    conn = get_connection()
    c = conn.cursor()

    # Simple direct/FTS search
    c.execute('''
        SELECT f.id, f.slug, f.name_pt, f.name_en, f.category, f.cooking_method,
               f.density_g_cm3, f.kcal_100g, f.protein_100g, f.carbs_100g, f.fat_100g, f.fiber_100g, f.typical_unit_weight_g
        FROM foods f
        JOIN foods_fts fts ON f.name_pt = fts.name_pt
        WHERE foods_fts MATCH ?
        LIMIT ?
    ''', (query + '*', limit))

    results = [dict(row) for row in c.fetchall()]

    if len(results) < limit:
        # Fallback to fuzzy search if not enough FTS results
        c.execute('SELECT * FROM foods')
        all_foods = [dict(row) for row in c.fetchall()]

        # We search against a combined string
        choices = {food['id']: f"{tokenize(food['name_pt'])} {tokenize(food['name_en'])}" for food in all_foods}
        query_tokenized = tokenize(query)

        # Get top matches
        matches = process.extract(query_tokenized, choices, scorer=fuzz.token_set_ratio, limit=limit)

        # Merge results, avoiding duplicates
        existing_ids = {r['id'] for r in results}
        for match in matches:
            # match format: (score, id, choice) or similar depending on extract implementation
            # rapidfuzz extract with dict: returns (match_string, score, key)
            key = match[2]
            if key not in existing_ids:
                food_item = next(f for f in all_foods if f['id'] == key)
                results.append(food_item)
                existing_ids.add(key)
                if len(results) >= limit:
                    break

    conn.close()
    return results

def get_food_by_slug(slug: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM foods WHERE slug = ?', (slug,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None
