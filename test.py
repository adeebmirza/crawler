from firecrawl import FirecrawlApp

FIRECRAWL_API_KEY= "fc-40a0fc219f654a3baf77aebbb88f8f70"
app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

def scrape_firecrawl(url: str) -> str:
    response = app.scrape_url(url, formats=["markdown"])
    return f"🌐 WEBSITE: {url}\n\n" + response.markdown


print(scrape_firecrawl("https://www.ndtv.com/world-news/iran-launches-missiles-towards-us-air-base-in-qatar-report-8742588"))


# scrape_result = app.scrape_url('https://www.ndtv.com/world-news/iran-launches-missiles-towards-us-air-base-in-qatar-report-8742588', formats=['markdown', 'html'])
# print(scrape_result)

# def scrape_firecrawl(url: str) -> str:
#     response = app.scrape_url({
#         "url": url,
#         "formats": ["markdown", "html"]
#     })
#     return f"🌐 WEBSITE: {url}\n\n" + response["markdown"]