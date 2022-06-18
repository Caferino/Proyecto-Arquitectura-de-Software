import csv

# Report movie data in a CSV
def CSVReport(list):
    # Creación de CSV
    fields = ["preference_key", "movie_title", "star_cast", "rating", "year", "place", "vote", "link"]
    with open("movie_results.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for movie in list:
            writer.writerow({**movie})

# Report movie data in Console
def MovieReport(list):
    print("preference_key   movie_title     star_cast      rating    year   place   vote    link")
    with open("movie_results.csv", "r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            print(row)