from flask import Flask, request, jsonify
from flask_cors import CORS
from scrapers.playstore_scraper import scrape_playstore
from utils.export_to_csv import export_to_csv
from supabase_client import supabase
import os
from datetime import datetime
import uuid
import traceback

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "API Ready"

@app.route("/scrape/playstore", methods=["POST"])
def playstore():
    data = request.get_json()
    app_id = data.get("appId")
    limit = int(data.get("limit", 20))
    user_id = data.get("userId")

    print(f"Incoming scrape request: appId={app_id}, limit={limit}, userId={user_id}")

    try:
        # 1. Scrape data
        result = scrape_playstore(app_id, count=limit)
        print(f"Scraped {len(result)} items")

        # 2. Save to local CSV
        filename = f"{uuid.uuid4()}.csv"
        local_path = os.path.join("scraped", filename)
        os.makedirs("scraped", exist_ok=True)

        export_to_csv(result, path=local_path)
        print(f"Saved CSV to {local_path}")

        # 3. Upload to Supabase Storage
        with open(local_path, "rb") as f:
            supabase.storage.from_("scraped-files").upload(filename, f, file_options={"content-type": "text/csv"})
        print("Upload to Supabase Storage completed")

        # 4. Get public URL
        public_url = supabase.storage.from_("scraped-files").get_public_url(filename)
        print(f"Public URL: {public_url}")

        # 5. Save metadata
        if user_id:
            supabase.table("scrapes").insert({
                "user_id": user_id,
                "source": "playstore",
                "app_id": app_id,
                "filename": filename,
                "total_data": len(result),
                "download_url": public_url,
                "created_at": datetime.now().isoformat()
            }).execute()
            print("Metadata inserted to Supabase DB")

        return jsonify({
            "message": "Scraping berhasil",
            "data": result,
            "filename": filename,
            "publicUrl": public_url
        })

    except Exception as e:
        print("Error during scraping:", e)
        traceback.print_exc()  # log traceback lengkap di terminal
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

