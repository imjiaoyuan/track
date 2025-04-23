import os
import logging
from rss import RSSFetcher
from qweather import WeatherFetcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('echo')

def main():
    rss_fetcher = RSSFetcher()
    weather_fetcher = WeatherFetcher()
    
    try:
        # Fetch and update weather
        logger.info("Fetching weather data...")
        weather = weather_fetcher.get_all_weather()
        weather_fetcher.update_content(weather)
        
        # Fetch and update RSS
        logger.info("Fetching RSS feeds...")
        entries = rss_fetcher.fetch()
        rss_fetcher.update_content(entries)
        
        logger.info("Content updated successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return False

if __name__ == '__main__':
    main()
