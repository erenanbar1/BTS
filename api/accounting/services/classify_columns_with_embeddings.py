#!/usr/bin/env python3
"""
Classify Excel columns into 5 categories using OpenAI embeddings + centroids.

Targets:
- name
- phone_number
- debt_amount
- debt_date
- other_date

Usage (macOS/Linux):
  python classify_columns_with_embeddings.py --excel "your_file.xlsx" [--sheet "Sheet1"] [--samples 10] [--threshold 0.6]

Requirements:
  pip install openai pandas python-dateutil chardet

Environment:
  export OPENAI_API_KEY="sk-..."
"""

import argparse
import json
import math
import os
import re
from typing import Dict, List, Tuple

import pandas as pd

try:
    from openai import OpenAI
except Exception as e:
    raise SystemExit("Please install the OpenAI SDK v1: pip install openai\n" + str(e))


# -------------------------------
# Configuration
# -------------------------------

DEFAULT_EMBED_MODEL = "text-embedding-3-small"



# Hybrid prototypes: brief definition + TR/EN synonyms + varied fake examples
TARGET_EXEMPLARS: Dict[str, List[str]] = {
    "cari_hesap_kodu": [
        "TR: ERP'de müşteri/tedarikçiyi tanımlayan kısa alfasayısal kod. EN: Customer/vendor account code/ID.",
        "Eşanlamlılar: Cari Kod, Cari Hesap Kodu, Cari No, Cari Kodu, Hesap No, Hesap Kodu, CH Kodu, CARIKOD, CHCODE, Müşteri Kodu, Tedarikçi Kodu",
        # Yaygın format örnekleri (tamamen uydurma):
        "M-000123", "MUS-00045", "CARI-TR-000045", "CH000567", "CARI_00125",
        "TED-00056", "ACC-120-001", "A-019283", "LOGO-0001",
        "120.01.001", "120-0001-01", "120-01-0005",  # tekdüzen hesap planı benzeri formatlar
        "000123", "001-ABC", "M/00023", "CL-TR-2025-007"
    ],
    "cari_hesap_ismi": [
        "TR: Kişinin adı soyadı (gerçek kişi). EN: Person’s full name.",
        "Eşanlamlılar: Ad Soyad, İsim, Adı Soyadı, Müşteri Adı, Yetkili Adı, Hesap Ünvanı, Cari Ünvanı, Cari Adı",
        # Çeşitli örnekler (tamamen uydurma):
        "Ali Veli",
        "Ayşe Demir",
        "Mehmet Eren Anbar",
        "Zeynep Kılıç",
        "Hakan Çelik",
        "İlker Öztürk",
        "Şule Karahan",
        "Çağrı Ünsal",
        "Gökçe Aydın",
        "Emre Can Yıldız",
        "Elif Su Koç",
        "Ali İhsan Doğan",
        "Oğuzhan Şahin",
        "Nazlı Yücel",
        "Seda Gür",
        "Barış Öz",
        "N. Can Aksoy",    
        "AHMET KAYA",    
        "ahmet kaya"  
    ],
    "telefon_no": [
    "TR: Telefon numarası; +90, boşluk, parantez, tire ve 'ext/dahili' içerebilir. EN: Phone number.",
    "Eşanlamlı/başlıklar: Telefon, GSM, Cep, Tel, Tel No, Telefon No, Mobile, Cell, Phone, İrtibat No",

    # Başlık sinyalleri (kolon adı az veriliyse yardımcı olur)
    "Tel", "Telefon", "GSM", "Cep", "Tel No", "Telefon No",

    # Yaygın biçimler (tamamen uydurma örnekler)
    "+90 532 123 45 67",
    "0532 123 45 67",
    "5321234567",
    "905321234567",
    "+905321234567",
    "+90 (212) 345 67 89",
    "(0312) 290 00 00",
    "0216 555 22 11",
    "0 216 555 22 11",
    "+90-533-987-65-43",
    "0850 000 00 00",
    "444 12 34",
    "+90 242 312 00 00 ext 123",
    "+90 242 312 00 00 dahili 123"
    ],
    "bakiye": [
    "TR: TL/TRY cinsinden para tutarı (virgül ondalık, nokta binlik olabilir). EN: Money amount in TRY.",
    "Eşanlamlı/başlıklar: Borç, Borç Tutarı, Tutar, Bakiye, Borç Bakiyesi, Toplam Borç, Ödenecek Tutar",

    # Başlık sinyalleri (kolon adı sinyali için kısa ipuçları)
    "Borç", "Tutar", "Bakiye", "Borç Tutarı", "Toplam Borç", "Ödenecek Tutar",

    # Türkiye’de yaygın biçimler (tamamen uydurma örnekler)
    "₺1.234,50",
    "12.345,67 TL",
    "1.750,00",
    "250,00 TL",
    "3.500,00",
    "0,00 TL",
    "-125,00 TL",            # eksi (indirim/iadeye benzer durumlar)
    "(250,00)",              # muhasebe negatif parantez kullanımı
    "TRY 1.234,50",
    "1.234,50 ₺",
    "1750 TL",
    "12.000"
    ],
    "son_fatura_tarihi": [
        "TR: Son kesilen/düzenlenen faturanın tarihi. EN: Last invoice issue date.",
        "Eşanlamlı/başlıklar: Son Fatura Tarihi, En Son Fatura, Fatura Kesim Tarihi, Son Düzenleme Tarihi, son FT. TAR., Latest Invoice Date, Last Invoice Issue Date",
        "Son Fatura", "Son Fatura Tarihi", "Fatura Kesim", "En Son Fatura",

        # Çeşitli tarih biçimleri (tamamen örnek)
        "2025-08-01",
        "01/08/2025",
        "01.08.2025",
        "2025/08/01",
        "11 Ağustos 2025",
        "Ağu 2025",
        "2024-12-31 13:45",
        "2024-09-31 10:52:01"

    ],
    "son_tahsilat_tarihi": [
        "TR: En son yapılan tahsilat/ödemenin tarihi (kasa/banka). EN: Last payment/collection date.",
        "Eşanlamlı/başlıklar: Son Tahsilat Tarihi, Tahsilat Tarihi, En Son Tahsilat, Son Ödeme Tarihi, Ödeme Tarihi, Tahsil Tarihi, Last Payment Date, Last Collection Date",

        # Başlık sinyalleri (zayıf başlıklarda yardımcı olur)
        "Son Tahsilat", "SON TAHS. TAR.", "Tahsilat", "Son Ödeme", "Ödeme Tarihi",

        # Çeşitli tarih biçimleri (tamamen örnek)
        "2025-08-10",
        "10/08/2025",
        "10.08.2025",
        "2025/08/10",
        "10 Ağu 2025",
        "Ağustos 2025",
        "2025-08-10 14:35",
        "2025-08-10T14:35:00",
        "10-08-25"
    ],
}

# Heuristic keywords for post-adjustment between two date-like columns
DATE_HINTS = {
    "debt_date": [
        "borç", "issue", "issued", "created", "düzenlenme", "fatura", "oluşturma"
    ],
    "other_date": [
        "vade", "due", "ödeme", "payment", "son güncelleme", "update", "tahsilat"
    ]
}


# -------------------------------
# Utilities
# -------------------------------

def cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    denom = (na * nb)
    if denom == 0:
        return 0.0
    return dot / denom


def average_vectors(vecs: List[List[float]]) -> List[float]:
    if not vecs:
        return []
    n = len(vecs[0])
    sums = [0.0] * n
    for v in vecs:
        for i in range(n):
            sums[i] += v[i]
    return [s / len(vecs) for s in sums]


def likely_phone(texts: List[str]) -> bool:
    """Light heuristic: if many rows look like TR phone numbers (+90 or 10+ digits)."""
    phone_like = 0
    total = 0
    for t in texts:
        s = re.sub(r"[^\d+]", "", str(t))
        if not s:
            continue
        total += 1
        if s.startswith("+90") or len(re.sub(r"\D", "", s)) >= 10:
            phone_like += 1
    return total > 0 and (phone_like / total) >= 0.4


def likely_amount(texts: List[str]) -> bool:
    """Heuristic for TRY amounts: TL/TRY/₺ or numeric with thousand/decimal separators."""
    patt = re.compile(r"(TL|TRY|₺)|^\s*\d{1,3}([.,]\d{3})*([.,]\d{2})?\s*$", re.IGNORECASE)
    hits = 0
    total = 0
    for t in texts:
        s = str(t).strip()
        if not s:
            continue
        total += 1
        if patt.search(s):
            hits += 1
    return total > 0 and (hits / total) >= 0.4


def likely_date(texts: List[str]) -> bool:
    """Heuristic for common date patterns."""
    patt = re.compile(r"\b(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b")
    hits = 0
    total = 0
    for t in texts:
        s = str(t)
        if not s.strip():
            continue
        total += 1
        if patt.search(s):
            hits += 1
    return total > 0 and (hits / total) >= 0.4


def keyword_score(header: str, keywords: List[str]) -> int:
    h = (header or "").lower()
    return sum(1 for k in keywords if k in h)


# -------------------------------
# Embedding helpers
# -------------------------------

def embed_text(client: OpenAI, text: str, model: str = DEFAULT_EMBED_MODEL) -> List[float]:
    # truncate to be safe; embeddings models accept long inputs but we keep it short
    text = text.strip()
    if len(text) > 8000:
        text = text[:8000]
    resp = client.embeddings.create(model=model, input=text)
    return resp.data[0].embedding


def build_centroids(client: OpenAI, exemplars: Dict[str, List[str]], model: str) -> Dict[str, List[float]]:
    centroids = {}
    for label, items in exemplars.items():
        vecs = [embed_text(client, it, model=model) for it in items]
        centroids[label] = average_vectors(vecs)
    return centroids


# -------------------------------
# Classification logic
# -------------------------------

def classify_columns(
    df: pd.DataFrame,
    centroids: Dict[str, List[float]],
    client: OpenAI,
    model: str,
    samples_per_col: int = 10,
    threshold: float = 0.6
) -> Tuple[List[dict], Dict[str, List[int]]]:
    """
    Returns:
        - mappings: list of dict with predictions per column
        - by_label: indices per predicted label
    """
    mappings = []
    by_label: Dict[str, List[int]] = {k: [] for k in centroids.keys()}

    for idx, col in enumerate(df.columns):
        col_series = df[col].dropna().astype(str)
        samples = col_series.head(samples_per_col).tolist()
        payload = f"HEADER: {col}\nSAMPLES: " + " ; ".join(samples)
        vec = embed_text(client, payload, model=model)

        # similarity to each centroid
        scored = sorted(
            ((label, cosine_similarity(vec, centroid)) for label, centroid in centroids.items()),
            key=lambda x: x[1], reverse=True
        )
        top_label, top_score = scored[0]

        # Heuristic nudges (do not override if score is clearly strong)
        # - If phone/amount/date patterns are detected, bump corresponding label if close
        nudged_label = top_label
        header_lower = str(col).lower()
        if likely_phone(samples):
            # bump phone if it's close (within margin) or top is not overwhelmingly strong
            for label, score in scored:
                if label == "phone_number" and (score + 0.05) >= top_score:
                    nudged_label, top_score = label, max(top_score, score)
                    break

        if likely_amount(samples):
            for label, score in scored:
                if label == "debt_amount" and (score + 0.05) >= top_score:
                    nudged_label, top_score = label, max(top_score, score)
                    break

        if likely_date(samples):
            # keep whichever date label scores higher; we'll disambiguate later
            pass

        prediction = {
            "column_index": idx,
            "column_header": str(col),
            "predicted_category": nudged_label if top_score >= threshold else "unknown",
            "confidence": round(float(top_score), 3),
            "alternatives": [
                {"label": l, "score": round(float(s), 3)} for l, s in scored[1:3]
            ],
            "sample_preview": samples,
        }
        mappings.append(prediction)
        if prediction["predicted_category"] in by_label:
            by_label[prediction["predicted_category"]].append(idx)

    # Post-pass: if we have multiple date-like columns, try to separate debt_date vs other_date
    date_indices = [m["column_index"] for m in mappings
                    if m["predicted_category"] in ("debt_date", "other_date", "unknown")]
    # Evaluate keywords to break ties
    for i in date_indices:
        m = mappings[i]
        header = m["column_header"]
        # Only adjust if currently date-ish or unknown but looks like a date
        looks_like_date = likely_date(m.get("sample_preview", []))
        if not looks_like_date:
            continue

        debt_kw = keyword_score(header, DATE_HINTS["debt_date"])
        other_kw = keyword_score(header, DATE_HINTS["other_date"])

        if debt_kw > other_kw and m["predicted_category"] in ("other_date", "unknown"):
            m["predicted_category"] = "debt_date"
        elif other_kw > debt_kw and m["predicted_category"] in ("debt_date", "unknown"):
            m["predicted_category"] = "other_date"

    # Rebuild by_label after adjustments
    by_label = {k: [] for k in centroids.keys()}
    for m in mappings:
        if m["predicted_category"] in by_label:
            by_label[m["predicted_category"]].append(m["column_index"])

    return mappings, by_label


# -------------------------------
# Main
# -------------------------------

def main():
    parser = argparse.ArgumentParser(description="Classify Excel columns with OpenAI embeddings.")
    parser.add_argument("--excel", required=True, help="Path to the Excel file (.xlsx/.xls).")
    parser.add_argument("--sheet", default=None, help="Sheet name or index (optional).")
    parser.add_argument("--samples", type=int, default=10, help="Sample values per column (default 10).")
    parser.add_argument("--threshold", type=float, default=0.6, help="Confidence threshold (default 0.6).")
    parser.add_argument("--embed-model", default=DEFAULT_EMBED_MODEL, help="Embeddings model name.")
    parser.add_argument("--output-prefix", default="mapping", help="Output file prefix (default 'mapping').")
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("Please set OPENAI_API_KEY in your environment. Example:\n  export OPENAI_API_KEY='sk-...'")

    client = OpenAI(api_key=api_key)

    # Load Excel
    try:
        if args.sheet is None:
            df = pd.read_excel(args.excel)
        else:
            # allow sheet index (int) or name (str)
            try:
                sheet = int(args.sheet)
            except ValueError:
                sheet = args.sheet
            df = pd.read_excel(args.excel, sheet_name=sheet)
    except Exception as e:
        raise SystemExit(f"Failed to read Excel: {e}")

    # Build centroids
    print("Building class centroids from exemplars...")
    centroids = build_centroids(client, TARGET_EXEMPLARS, model=args.embed_model)

    # Classify
    print(f"Classifying {len(df.columns)} columns from: {args.excel}")
    mappings, by_label = classify_columns(
        df=df,
        centroids=centroids,
        client=client,
        model=args.embed_model,
        samples_per_col=args.samples,
        threshold=args.threshold
    )

    # Save outputs
    json_path = f"{args.output_prefix}.json"
    csv_path = f"{args.output_prefix}.csv"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"mappings": mappings}, f, ensure_ascii=False, indent=2)

    pd.DataFrame(mappings).to_csv(csv_path, index=False, encoding="utf-8")

    print(f"\nResults written to:\n  {json_path}\n  {csv_path}\n")
    print("Preview:")
    for m in mappings:
        print(f"[{m['column_index']}] '{m['column_header']}' -> {m['predicted_category']} "
              f"(conf {m['confidence']}) alts={m['alternatives']}")

if __name__ == "__main__":
    main()
