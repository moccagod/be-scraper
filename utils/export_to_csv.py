import csv

def export_to_csv(data, path="output.csv"):
    if not data:
        raise ValueError("Tidak ada data untuk disimpan")

    # Ambil semua field (key) dari dict pertama
    fieldnames = list(data[0].keys())

    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
