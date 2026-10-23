import sqlite3
import os
from .db import get_connection, init_db

# Typical food densities (g/cm^3)
# Water is 1.0.
# Breads ~0.2 - 0.3
# Meat ~1.05
# Rice (cooked) ~0.7 - 0.8
# Veggies ~0.4 - 0.7

SEED_DATA = [
    # Grains & Starches
    ("arroz_branco_cozido", "Arroz branco cozido", "White rice, cooked", "Grains", "boiled", 0.75, 130, 2.7, 28, 0.3, 0.4),
    ("batata_frita", "Batata frita", "French fries", "Starches", "fried", 0.40, 312, 3.4, 41, 15, 3.8),
    ("batata_cozida", "Batata cozida", "Boiled potato", "Starches", "boiled", 0.65, 87, 1.9, 20, 0.1, 1.8),
    ("esparguete_cozido", "Esparguete cozido", "Spaghetti, cooked", "Grains", "boiled", 0.60, 158, 5.8, 31, 0.9, 1.8),
    ("pao_trigo", "Pão de trigo/carcaça", "Wheat bread", "Baked", "baked", 0.25, 265, 9, 49, 3.2, 2.7),

    # Meats
    ("bife_vazia_grelhado", "Bife da vazia grelhado", "Grilled sirloin steak", "Meat", "grilled", 1.05, 250, 26, 0, 15, 0),
    ("peito_frango_grelhado", "Peito de frango", "Chicken breast, grilled", "Meat", "grilled", 1.05, 165, 31, 0, 3.6, 0),
    ("alheira", "Alheira", "Alheira sausage", "Meat", "fried", 0.95, 300, 12, 18, 20, 0),
    ("lombo_porco_assado", "Lombo de porco assado", "Roasted pork loin", "Meat", "roasted", 1.03, 242, 27, 0, 14, 0),

    # Fish & Seafood
    ("bacalhau_bras", "Bacalhau à Brás", "Bacalhau à Brás", "Fish", "mixed", 0.85, 200, 12, 15, 11, 1.5),
    ("bacalhau_cozido", "Bacalhau cozido", "Boiled cod", "Fish", "boiled", 0.90, 105, 23, 0, 0.5, 0),
    ("salmao_grelhado", "Salmão grelhado", "Grilled salmon", "Fish", "grilled", 1.02, 206, 22, 0, 13, 0),
    ("atum_lata_agua", "Atum em lata (água)", "Canned tuna in water", "Fish", "canned", 0.95, 116, 26, 0, 0.8, 0),

    # Legumes
    ("feijao_preto_cozido", "Feijão preto cozido", "Black beans, cooked", "Legumes", "boiled", 0.85, 132, 8.9, 23.7, 0.5, 8.7),
    ("grao_bico_cozido", "Grão-de-bico cozido", "Chickpeas, cooked", "Legumes", "boiled", 0.75, 164, 8.9, 27.4, 2.6, 7.6),

    # Eggs
    ("ovo_estrelado", "Ovo estrelado", "Fried egg", "Eggs", "fried", 1.00, 196, 13.6, 0.8, 14.8, 0),
    ("ovo_cozido", "Ovo cozido", "Boiled egg", "Eggs", "boiled", 1.03, 155, 12.6, 1.1, 10.6, 0),

    # Vegetables
    ("brocolos_cozidos", "Brócolos cozidos", "Broccoli, cooked", "Vegetables", "boiled", 0.45, 35, 2.4, 7.2, 0.4, 3.3),
    ("alface", "Alface", "Lettuce", "Vegetables", "raw", 0.15, 15, 1.4, 2.9, 0.2, 1.3),
    ("tomate", "Tomate", "Tomato", "Vegetables", "raw", 0.60, 18, 0.9, 3.9, 0.2, 1.2),
    ("cenoura_cozida", "Cenoura cozida", "Carrot, cooked", "Vegetables", "boiled", 0.65, 35, 0.8, 8.2, 0.2, 3),

    # Fats & Oils
    ("azeite", "Azeite", "Olive oil", "Fats", "raw", 0.92, 884, 0, 0, 100, 0),
    ("manteiga", "Manteiga", "Butter", "Fats", "raw", 0.91, 717, 0.8, 0.1, 81, 0),

    # Sweets/Snacks
    ("pastel_nata", "Pastel de nata", "Portuguese custard tart", "Sweets", "baked", 0.70, 298, 4.5, 38, 14, 0.5),
]

# Generate more placeholders to reach 60 items as requested for a robust initial DB
EXTRAS = [
    ("maca", "Maçã", "Apple", "Fruit", "raw", 0.8, 52, 0.3, 14, 0.2, 2.4),
    ("banana", "Banana", "Banana", "Fruit", "raw", 0.95, 89, 1.1, 23, 0.3, 2.6),
    ("laranja", "Laranja", "Orange", "Fruit", "raw", 0.9, 47, 0.9, 12, 0.1, 2.4),
    ("pera", "Pera", "Pear", "Fruit", "raw", 0.85, 57, 0.4, 15, 0.1, 3.1),
    ("morango", "Morango", "Strawberry", "Fruit", "raw", 0.5, 32, 0.7, 7.7, 0.3, 2.0),
    ("uva", "Uva", "Grape", "Fruit", "raw", 0.7, 69, 0.7, 18, 0.2, 0.9),
    ("pessego", "Pêssego", "Peach", "Fruit", "raw", 0.6, 39, 0.9, 9.5, 0.3, 1.5),
    ("melancia", "Melancia", "Watermelon", "Fruit", "raw", 0.9, 30, 0.6, 7.6, 0.2, 0.4),
    ("abacaxi", "Abacaxi", "Pineapple", "Fruit", "raw", 0.8, 50, 0.5, 13, 0.1, 1.4),
    ("manga", "Manga", "Mango", "Fruit", "raw", 0.8, 60, 0.8, 15, 0.4, 1.6),

    ("cebola", "Cebola", "Onion", "Vegetables", "raw", 0.6, 40, 1.1, 9.3, 0.1, 1.7),
    ("alho", "Alho", "Garlic", "Vegetables", "raw", 0.7, 149, 6.4, 33, 0.5, 2.1),
    ("pimento", "Pimento", "Bell pepper", "Vegetables", "raw", 0.4, 20, 0.9, 4.6, 0.2, 1.7),
    ("cogumelo", "Cogumelo", "Mushroom", "Vegetables", "raw", 0.3, 22, 3.1, 3.3, 0.3, 1.0),
    ("espinafre", "Espinafre", "Spinach", "Vegetables", "raw", 0.1, 23, 2.9, 3.6, 0.4, 2.2),
    ("couve", "Couve", "Cabbage", "Vegetables", "raw", 0.2, 25, 1.3, 5.8, 0.1, 2.5),

    ("leite_meio_gordo", "Leite meio gordo", "Semi-skimmed milk", "Dairy", "raw", 1.03, 47, 3.3, 4.8, 1.6, 0),
    ("queijo_flamengo", "Queijo flamengo", "Flamengo cheese", "Dairy", "raw", 1.05, 350, 23, 2, 28, 0),
    ("iogurte_natural", "Iogurte natural", "Natural yogurt", "Dairy", "raw", 1.04, 61, 3.5, 4.7, 3.3, 0),

    ("frango_assado", "Frango assado", "Roasted chicken", "Meat", "roasted", 0.95, 237, 27, 0, 14, 0),
    ("carne_picada_vaca", "Carne picada de vaca", "Minced beef", "Meat", "fried", 1.0, 332, 14, 0, 30, 0),
    ("salsicha", "Salsicha", "Sausage", "Meat", "boiled", 0.9, 301, 12, 2, 27, 0),

    ("pescada_cozida", "Pescada cozida", "Boiled hake", "Fish", "boiled", 0.85, 78, 17, 0, 1, 0),
    ("sardinha_assada", "Sardinha assada", "Grilled sardine", "Fish", "grilled", 0.95, 208, 25, 0, 11, 0),

    ("macarrao_cru", "Macarrão cru", "Raw pasta", "Grains", "raw", 0.8, 371, 13, 75, 1.5, 3.2),
    ("aveia", "Flocos de aveia", "Oat flakes", "Grains", "raw", 0.4, 389, 17, 66, 6.9, 11),

    ("amendoa", "Amêndoa", "Almond", "Nuts", "raw", 0.6, 579, 21, 22, 50, 13),
    ("noz", "Noz", "Walnut", "Nuts", "raw", 0.5, 654, 15, 14, 65, 6.7),

    ("mel", "Mel", "Honey", "Sweets", "raw", 1.42, 304, 0.3, 82, 0, 0.2),
    ("acucar", "Açúcar", "Sugar", "Sweets", "raw", 0.85, 387, 0, 100, 0, 0),

    ("vinho_tinto", "Vinho tinto", "Red wine", "Drinks", "raw", 0.99, 85, 0.1, 2.6, 0, 0),
    ("cerveja", "Cerveja", "Beer", "Drinks", "raw", 1.01, 43, 0.5, 3.6, 0, 0),

    ("sopa_legumes", "Sopa de legumes", "Vegetable soup", "Soup", "boiled", 1.02, 40, 1.5, 6, 1, 1.5),
    ("caldo_verde", "Caldo verde", "Caldo verde soup", "Soup", "boiled", 1.03, 55, 2, 8, 2, 2),
    ("pizza_margarita", "Pizza margherita", "Margherita pizza", "Mixed", "baked", 0.6, 266, 11, 33, 10, 2.3),
    ("hamburguer", "Hambúrguer", "Hamburger", "Mixed", "fried", 0.7, 295, 17, 24, 14, 1.5)
]

SEED_DATA.extend(EXTRAS)


def seed():
    init_db()
    conn = get_connection()
    c = conn.cursor()

    # Check if already seeded
    c.execute("SELECT COUNT(*) FROM foods")
    if c.fetchone()[0] > 0:
        print("Database already seeded.")
        conn.close()
        return

    for item in SEED_DATA:
        c.execute('''
            INSERT INTO foods (slug, name_pt, name_en, category, cooking_method, density_g_cm3, kcal_100g, protein_100g, carbs_100g, fat_100g, fiber_100g)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', item)

        # Insert into FTS virtual table
        c.execute('''
            INSERT INTO foods_fts (name_pt, name_en, category, slug)
            VALUES (?, ?, ?, ?)
        ''', (item[1], item[2], item[3], item[0]))

    conn.commit()
    print(f"Seeded {len(SEED_DATA)} food items.")
    conn.close()

if __name__ == "__main__":
    seed()
