import time
import random
import requests
from requests.exceptions import RequestException
import requests
from bs4 import BeautifulSoup
import csv
import os
from urllib.parse import urljoin
import yaml
from dotenv import load_dotenv
load_dotenv()
import logging
import os

# === Logging Setup ===
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

log = logging.getLogger("autoscrape")


def scrape_generic(target):
    url = target["url"]
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    items = []
    for el in soup.select(target["item"]):
        row = {}
        for field, selector in target["fields"].items():
            if "::attr(" in selector:
                css, rest = selector.split("::attr(", 1)
                attr = rest.rstrip(")")
                node = el.select_one(css.strip())
                val = node.get(attr) if node else None
                if field.lower() in ("link", "url") and val:
                    val = urljoin(url, val)
                row[field] = val
            elif selector.endswith("::text"):
                css = selector[:-6].strip()
                node = el.select_one(css)
                row[field] = node.get_text(strip=True) if node else None
            else:
                node = el.select_one(selector)
                row[field] = node.get_text(strip=True) if node else None
                
        if any(v for v in row.values()):
            row["source"] = target.get("name")
            items.append(row)

    seen_rows = set()
    deduped = []
    for r in items:
        key_tuple = tuple(sorted((k, r.get(k)) for k in r.keys()))
        if key_tuple not in seen_rows:
            seen_rows.add(key_tuple)
            deduped.append(r)
    return deduped

def load_existing_set(csv_path, unique_key):
    """Lit le CSV et retourne l'ensemble des valeurs pour unique_key."""
    if not os.path.exists(csv_path) or os.stat(csv_path).st_size == 0:
        return set()
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or unique_key not in reader.fieldnames:
            return set()
        return {row[unique_key] for row in reader if row.get(unique_key)}

def append_csv(csv_path, rows):
    """Écrit uniquement les rows passées (ajout), en gérant dynamiquement les colonnes."""
    if not rows:
        return
    fieldnames = sorted({k for r in rows for k in r.keys()})
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    file_exists = os.path.exists(csv_path) and os.stat(csv_path).st_size > 0

    if file_exists:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                fieldnames = reader.fieldnames

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})
            
def send_alerts(new_items, unique_key, source_name):
    """Envoie une alerte Telegram et/ou Discord si de nouveaux items sont trouvés."""
    if not new_items:
        return

    lines = [f"🔔 {len(new_items)} nouvel(le)s entrée(s) détectée(s) pour {source_name}:"]
    preview = new_items[:10]
    for it in preview:
        parts = []
        if it.get(unique_key):
            parts.append(str(it.get(unique_key)))
        for k in ("title", "company", "price", "posted"):
            if k in it and it.get(k):
                parts.append(str(it[k]))
                break
        lines.append("• " + " — ".join(parts))
    text = "\n".join(lines)

    # Telegram
    tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tg_chat  = os.getenv("TELEGRAM_CHAT_ID")
    if tg_token and tg_chat:
        try:
            requests.post(
                f"https://api.telegram.org/bot{tg_token}/sendMessage",
                data={"chat_id": tg_chat, "text": text, "disable_web_page_preview": True},
                timeout=15
            )
            log.info("Alerte Telegram envoyée.")
        except Exception as e:
            log.error("Telegram error: %s", e)

    # Discord
    webhook = os.getenv("DISCORD_WEBHOOK_URL")
    if webhook:
        try:
            requests.post(webhook, json={"content": text}, timeout=15)
            log.info("Alerte Discord envoyée.")
        except Exception as e:
            log.error("Discord error: %s", e)
            
def fetch_html(url, max_retries=3, base_delay=1.0, timeout=15):
    """GET avec retries exponentiels + jitter."""
    ua = "Mozilla/5.0 (compatible; AutoScrapeAlerts/1.0; +https://example.com)"
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(url, headers={"User-Agent": ua}, timeout=timeout)
            r.raise_for_status()
            return r.text
        except RequestException as e:
            if attempt == max_retries:
                raise
            sleep_s = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
            log.warning(f"Retry {attempt}/{max_retries} pour {url}: {e}")
            time.sleep(sleep_s)

def cli_menu(alerts_enabled):
    print("\n=== AutoScrape Alerts ===")
    print("[1] Scraper tous les sites")
    print("[2] Choisir un site à scraper")
    print("[3] Scraper en mode dry-run (test)")
    print("[4] Scraper avec limite d'items")
    print("[o] Options d'alertes: " + ("Activées 🔔" if alerts_enabled else "Désactivées 🔕"))
    print("[q] Quitter")
    choice = input("→ Choix : ").strip()
    return choice


if __name__ == "__main__":
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    csv_path = config["storage"]["csv_path"]
    unique_key = config["storage"].get("unique_key", "link")
    alerts_enabled = config["alerts"].get("enabled", False)

    while True:
        choice = cli_menu(alerts_enabled)
        if choice == "o":
            print("\n=== Options d'alertes ===")
            alerts_enabled = not alerts_enabled
            config["alerts"]["enabled"] = alerts_enabled
            print(f"Alertes {'activées 🔔' if alerts_enabled else 'désactivées 🔕'}")
            continue
        if choice == "1":
            for target in config["targets"]:
                log.info(f"Scraping: {target['name']}")
                scraped = scrape_generic(target)
                target_csv = target.get("csv_path", csv_path)
                existing = load_existing_set(target_csv, unique_key)
                new_items = [r for r in scraped if r.get(unique_key) and r[unique_key] not in existing]
                if new_items:
                    log.info(f"{len(new_items)} nouvelles entrées pour {target['name']}")
                    append_csv(target_csv, new_items)
                    if alerts_enabled:
                        try: send_alerts(new_items, unique_key, target['name'])
                        except: pass
                else:
                    log.info(f"Aucune nouvelle entrée pour {target['name']}")

        elif choice == "2":
            print("\nSites disponibles :")
            for i, target in enumerate(config["targets"], start=1):
                print(f"[{i}] {target['name']}")
            idx = int(input("→ Choisir un site : ")) - 1
            target = config["targets"][idx]
            log.info(f"Scraping: {target['name']}")
            scraped = scrape_generic(target)
            target_csv = target.get("csv_path", csv_path)
            existing = load_existing_set(target_csv, unique_key)
            new_items = [r for r in scraped if r.get(unique_key) and r[unique_key] not in existing]
            if new_items:
                log.info(f"{len(new_items)} nouvelles entrées pour {target['name']}")
                append_csv(target_csv, new_items)
                if alerts_enabled:
                    try: send_alerts(new_items, unique_key, target['name'])
                    except: pass
            else:
                log.info(f"Aucune nouvelle entrée pour {target['name']}")

        elif choice == "3":
            print("Mode dry-run : rien n'est écrit / envoyé.")
            target = config["targets"][0]
            scraped = scrape_generic(target)
            print(f"Exemple: {scraped[:5]}")

        elif choice == "4":
            limit = int(input("Limite d’items : "))
            for target in config["targets"]:
                print(f"🔍 Scraping: {target['name']}")
                scraped = scrape_generic(target)[:limit]
                print(f"Prévisualisation ({limit} items) :")
                for it in scraped:
                    print("•", it.get(unique_key), it.get("title") or "")

        elif choice.lower() == "q":
            print("👋 Bye")
            break

        else:
            print("❌ Choix invalide")
