from google_play_scraper import reviews, Sort

def scrape_playstore(app_id, count=100):
    result, _ = reviews(
        app_id,
        lang='id',
        country='id',
        sort=Sort.NEWEST,
        count=count,
    )

    reviews_data = []
    for r in result:
        reviews_data.append({
            "username": r['userName'],
            "date": r['at'].isoformat(),
            "rating": r['score'],
            "content": r['content']
        })

    return reviews_data
