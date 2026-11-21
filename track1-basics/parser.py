import csv
import re
from pathlib import Path

from bs4 import BeautifulSoup
import matplotlib
matplotlib.use("Agg")          # рисуем в файл, без всплывающего окна
import matplotlib.pyplot as plt


# ============================================================
# 0. Подготовка: создаём HTML-снимки, если их нет
# ============================================================
SNAPSHOT_1 = """<!DOCTYPE html>
<html lang="ru">
<head><meta charset="utf-8"><title>Каталог — снимок 1</title></head>
<body>
  <h1>Каталог товаров</h1>
  <div class="product">
    <h2 class="name">Наушники Sony WH-1000XM5</h2>
    <span class="price">29 990 ₽</span>
  </div>
  <div class="product">
    <h2 class="name">Клавиатура Logitech MX Keys</h2>
    <span class="price">9 490 ₽</span>
  </div>
  <div class="product">
    <h2 class="name">Мышь Logitech MX Master 3S</h2>
    <span class="price">7 290 ₽</span>
  </div>
  <div class="product">
    <h2 class="name">Монитор Dell UltraSharp U2723QE</h2>
    <span class="price">54 990 ₽</span>
  </div>
</body>
</html>
"""

SNAPSHOT_2 = """<!DOCTYPE html>
<html lang="ru">
<head><meta charset="utf-8"><title>Каталог — снимок 2</title></head>
<body>
  <h1>Каталог товаров</h1>
  <div class="product">
    <h2 class="name">Наушники Sony WH-1000XM5</h2>
    <span class="price">27 990 ₽</span>
  </div>
  <div class="product">
    <h2 class="name">Клавиатура Logitech MX Keys</h2>
    <span class="price">10 990 ₽</span>
  </div>
  <div class="product">
    <h2 class="name">Мышь Logitech MX Master 3S</h2>
    <span class="price">7 290 ₽</span>
  </div>
  <div class="product">
    <h2 class="name">Монитор Dell UltraSharp U2723QE</h2>
    <span class="price">49 990 ₽</span>
  </div>
</body>
</html>
"""


def ensure_snapshots() -> None:
    """Создаёт snapshot_1.html / snapshot_2.html, если их нет."""
    for fname, content in [("snapshot_1.html", SNAPSHOT_1),
                           ("snapshot_2.html", SNAPSHOT_2)]:
        p = Path(fname)
        if not p.exists():
            p.write_text(content, encoding="utf-8")
            print(f"📄 создан {fname}")


# ============================================================
# 1. Парсинг HTML
# ============================================================
def parse_html(file_path: str) -> list[dict]:
    """Возвращает список {'name': str, 'price': int}."""
    html = Path(file_path).read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    products = []
    for card in soup.select("div.product"):
        name_tag = card.select_one(".name")
        price_tag = card.select_one(".price")
        if not name_tag or not price_tag:
            continue

        name = name_tag.get_text(strip=True)
        # "29 990 ₽" -> 29990
        digits = re.sub(r"[^\d]", "", price_tag.get_text(strip=True))
        price = int(digits) if digits else 0

        products.append({"name": name, "price": price})
    return products


# ============================================================
# 2. Сохранение в CSV
# ============================================================
def save_to_csv(products: list[dict], csv_path: str) -> None:
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "price"])
        writer.writeheader()
        writer.writerows(products)
    print(f"✅ {csv_path} — {len(products)} строк")


# ============================================================
# 3. График изменения цен
# ============================================================
def build_price_chart(csv1: str, csv2: str, out_png: str) -> None:
    def load(path):
        with open(path, encoding="utf-8-sig") as f:
            return {r["name"]: int(r["price"]) for r in csv.DictReader(f)}

    d1, d2 = load(csv1), load(csv2)
    names = sorted(set(d1) | set(d2))
    p1 = [d1.get(n, 0) for n in names]
    p2 = [d2.get(n, 0) for n in names]

    x = range(len(names))
    plt.figure(figsize=(11, 6))
    plt.plot(x, p1, marker="o", linewidth=2, label="Снимок 1")
    plt.plot(x, p2, marker="s", linewidth=2, label="Снимок 2")
    plt.xticks(list(x), names, rotation=20, ha="right")
    plt.ylabel("Цена, ₽")
    plt.title("Изменение цен по двум снимкам")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_png, dpi=130)
    plt.close()
    print(f"📈 {out_png}")


# ============================================================
# 4. Сводка изменений
# ============================================================
def print_changes(p1: list[dict], p2: list[dict]) -> None:
    map1 = {x["name"]: x["price"] for x in p1}
    map2 = {x["name"]: x["price"] for x in p2}
    print("\nИзменения цен:")
    for name in sorted(set(map1) | set(map2)):
        old, new = map1.get(name), map2.get(name)
        if old is None:
            print(f"  + {name}: появился ({new} ₽)")
        elif new is None:
            print(f"  - {name}: исчез (был {old} ₽)")
        else:
            diff = new - old
            mark = "🔺" if diff > 0 else "🔻" if diff < 0 else "➖"
            sign = "+" if diff > 0 else ""
            print(f"  {mark} {name}: {old} → {new} ({sign}{diff} ₽)")


# ============================================================
# main
# ============================================================
if __name__ == "__main__":
    ensure_snapshots()

    products_1 = parse_html("snapshot_1.html")
    products_2 = parse_html("snapshot_2.html")

    save_to_csv(products_1, "prices_1.csv")
    save_to_csv(products_2, "prices_2.csv")

    build_price_chart("prices_1.csv", "prices_2.csv", "price_changes.png")
    print_changes(products_1, products_2)