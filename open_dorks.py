import webbrowser
import time

def open_dorks(urls):
    for url in urls:
        webbrowser.open_new_tab(url)
        time.sleep(2)  # Polite delay to avoid hammering Google

# Example usage — replace with your actual PhoneInfoga URL list
if __name__ == "__main__":
    dork_urls = [
        "https://www.google.com/search?q=site%3Afacebook.com+intext%3A%222086807334%22...",
        "https://www.google.com/search?q=site%3Atwitter.com+intext%3A%222086807334%22...",
        # Paste the rest of your URLs here
    ]
    open_dorks(dork_urls)