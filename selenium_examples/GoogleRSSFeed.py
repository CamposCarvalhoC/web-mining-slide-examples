from selenium import webdriver
from bs4 import BeautifulSoup
import argparse
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder

import matplotlib.pyplot as plt
import seaborn as sns


GOOGLE_RSS_FEED = "https://news.google.com/rss/search?q="

THEMES = ["science", "technology", "business", "education"]

def get_rss_titles(theme):
    url = f"{GOOGLE_RSS_FEED}{theme}"
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")  # Run in headless mode for automation
    driver = webdriver.Firefox(options=options)
    driver.get(url)

    xml_content = driver.page_source
    soup = BeautifulSoup(xml_content, 'xml')

    titles = []
    for title in soup.find_all('title'):
        titles.append(title.text)

    driver.close()
    return titles[2:] # Skip Google's own titles

def remove_ticks_plot(ax):
    ax.set_xticks([])
    ax.set_xticks([], minor=True)
    ax.set_yticks([])
    ax.set_yticks([], minor=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch RSS feed titles for specified themes.")
    parser.add_argument("--themes", nargs="+", 
                        help="Themes to fetch RSS feed titles for (theme1 theme2 ... themeN).", 
                        default=THEMES)

    args = parser.parse_args()
    print(f'Themes to collect from RSS feed : {args.themes}.')

    if len(args.themes) > 0:

        df = pd.DataFrame(columns=["theme", "title"])
        for theme in args.themes:
            print(f"Fetching titles for theme: {theme}")
            titles = get_rss_titles(theme)
            df = pd.concat([df, pd.DataFrame({"theme": [theme]*len(titles), "title": titles})])

        print(f"Vectorizing titles...")
        vectorizer = TfidfVectorizer()
        matrix = vectorizer.fit_transform(df['title'])

        print(f"PCA + Kmeans clustering...")
        pca = PCA(n_components=2)
        reduced_matrix = pca.fit_transform(matrix.toarray())
        kmeans = KMeans(n_clusters=len(args.themes), random_state=42)
        kmeans.fit(reduced_matrix)

        print(f"Plotting results...")
        fig, axs = plt.subplots(ncols=2, figsize=(12, 6))
        sns.scatterplot(x=reduced_matrix[:, 0], y=reduced_matrix[:, 1], hue=kmeans.labels_, ax=axs[0])
        sns.scatterplot(x=reduced_matrix[:, 0], y=reduced_matrix[:, 1], hue=df['theme'], ax=axs[1])

        axs[0].set_title("KMeans Clustering")
        axs[1].set_title("Themes")
        
        remove_ticks_plot(axs[0])
        remove_ticks_plot(axs[1])

        le = LabelEncoder()
        true_labels_encoded = le.fit_transform(df['theme'])
        mask_not_equal = true_labels_encoded != kmeans.labels_

        print(f"Mismatched labels (titles):")
        for group, df_theme in df[mask_not_equal].groupby("theme"):
            print(f"Theme: {group}")
            for title in df_theme['title']:
                print(f"  - {title}")

        plt.show()