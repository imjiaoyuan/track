import requests
from datetime import datetime
import os
import logging
import re
import pytz

try:
    from local_env import QWEATHER_KEY as LOCAL_KEY, QWEATHER_PUBLIC_ID as LOCAL_PUBLIC_ID
except ImportError:
    LOCAL_KEY = None
    LOCAL_PUBLIC_ID = None
from config import CITIES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherFetcher:
    def __init__(self):
        self.api_key = LOCAL_KEY or os.getenv('QWEATHER_KEY')
        self.public_id = LOCAL_PUBLIC_ID or os.getenv('QWEATHER_PUBLIC_ID')
        self.base_url = "https://geoapi.qweather.com"
        self.index_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'content/_index.md'
        )
        self.weather_map = {
            '100': '☀️',  # 晴
            '101': '🌤️',  # 多云
            '104': '☁️',  # 阴
            '150': '🌙',  # 晴夜
            '300': '🌧️',  # 阵雨
            '301': '🌧️',  # 强阵雨
            '302': '⛈️',  # 雷阵雨
            '305': '🌧️',  # 小雨
            '306': '🌧️',  # 中雨
            '307': '🌧️',  # 大雨
            '499': '🌨️',  # 雪
        }
        self.indices_map = {
            '1': '运动指数',
            '2': '洗车指数',
            '3': '穿衣指数',
            '15': '交通指数',  # 我们主要关注交通指数
        }
        self.indices_level = {
            '15': {  # 交通指数的等级说明
                '1': '良好',
                '2': '较好',
                '3': '一般',
                '4': '较差',
                '5': '很差'
            }
        }
        self.params = {
            'key': self.api_key,
            'public_id': self.public_id,
            'lang': 'zh'  # 请求中文响应
        }
        logger.debug(f"Initialized WeatherFetcher with key: {self.api_key[:4]}...")

    def get_city_weather(self, city):
        try:
            # City lookup
            location_url = f"{self.base_url}/v2/city/lookup"
            params = {**self.params, 'location': city}
            
            location_resp = requests.get(location_url, params=params, timeout=10)
            location_resp.raise_for_status()
            location_data = location_resp.json()
            
            if location_data.get('code') != '200':
                raise Exception(f"API Error: {location_data.get('code')}")
            
            # Get location info
            loc = location_data['location'][0]
            city_id = loc['id']
            
            # Use English names directly from API response
            full_location = '/'.join(filter(None, [
                loc.get('adm1', ''),  # Province/State
                loc.get('adm2', ''),  # City
                loc.get('name', '')   # District/Location
            ]))
            
            # Weather data with city_id
            weather_params = {**self.params, 'location': city_id}
            
            # Get warnings first
            warning_url = "https://devapi.qweather.com/v7/warning/now"
            warning_resp = requests.get(warning_url, params=weather_params)
            warning_resp.raise_for_status()
            
            # Get weather and air quality
            weather_url = "https://devapi.qweather.com/v7/weather/3d"
            weather_resp = requests.get(weather_url, params=weather_params)
            weather_resp.raise_for_status()
            
            air_url = "https://devapi.qweather.com/v7/air/5d"
            air_params = {**self.params, 'location': city_id}
            air_resp = requests.get(air_url, params=air_params)
            air_resp.raise_for_status()
            
            # 获取生活指数
            indices_url = "https://devapi.qweather.com/v7/indices/1d"
            indices_params = {**weather_params, 'type': 15}  # 只获取交通指数
            indices_resp = requests.get(indices_url, params=indices_params)
            indices_resp.raise_for_status()
            
            return self._format_weather(full_location, weather_resp.json(), 
                                      air_resp.json(), warning_resp.json(),
                                      indices_resp.json())
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {city}: {str(e)}")
            return f"**{city}**\n- Failed: Network Error"
        except Exception as e:
            logger.error(f"Error processing {city}: {str(e)}")
            return f"**{city}**\n- Failed: {str(e)}"

    def _get_weather(self, city_id):
        weather_url = "https://devapi.qweather.com/v7/weather/3d"
        params = {**self.params, 'location': city_id}
        weather_resp = requests.get(weather_url, params=params)
        return weather_resp.json()

    def _get_air_quality(self, city_id):
        air_url = "https://devapi.qweather.com/v7/air/5d"
        params = {**self.params, 'location': city_id}
        air_resp = requests.get(air_url, params=params)
        return air_resp.json()

    def _format_weather(self, city, weather_data, air_data, warning_data, indices_data):
        now = datetime.now(pytz.timezone('Asia/Shanghai'))
        lines = [f"**{city} {now.strftime('%Y年%m月%d日 %H:%M')}**"]
        
        # Add warnings if any
        if warning_data.get('warning') and len(warning_data['warning']) > 0:
            warnings = []
            for warn in warning_data['warning']:
                severity = {
                    'White': '⚪️',
                    'Blue': '🔵',
                    'Yellow': '🟡',
                    'Orange': '🟠',
                    'Red': '🔴'
                }.get(warn.get('level', ''), '')
                warnings.append(f"{severity} {warn.get('title')} - {warn.get('text')}")
            
            lines.append("⚠️ **预警信息**")
            lines.extend(f"- {w}" for w in warnings)
            lines.append("")

        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        day_names = ['今天', '明天']
        
        if 'daily' in weather_data and 'daily' in air_data:
            # 只获取今明两天的天气
            for idx, day in enumerate(weather_data['daily'][:2]):
                date = day_names[idx]
                weekday = weekdays[datetime.strptime(day['fxDate'], '%Y-%m-%d').weekday()]
                
                weather_icon = self.weather_map.get(day['iconDay'], '')
                weather_line = f"- {date}{weekday}，白天{weather_icon}{day['textDay']}({day['tempMin']}°~{day['tempMax']}°)"
                
                # 添加空气质量
                air_info = next((a for a in air_data['daily'] if a['fxDate'] == day['fxDate']), None)
                if air_info:
                    weather_line += f"，空气{air_info['category']}({air_info['aqi']})"
                
                # 如果夜间天气与白天不同，添加夜间天气
                if day.get('textNight') != day.get('textDay'):
                    weather_line += f"，夜间{day.get('textNight', '')}"
                
                lines.append(weather_line)

            # 添加交通指数信息，作为列表项
            if indices_data.get('daily') and len(indices_data['daily']) > 0:
                traffic_index = indices_data['daily'][0]
                if traffic_index['type'] == '15':  # 交通指数
                    lines.append(f"- {traffic_index['text']}")

        return '\n'.join(lines)

    def _get_air_color(self, level):
        """Get air quality color based on level"""
        colors = {
            '1': '🟢',  # 优
            '2': '🟢',  # 良
            '3': '🟡',  # 轻度污染
            '4': '🟠',  # 中度污染
            '5': '🔴',  # 重度污染
            '6': '🟤',  # 严重污染
        }
        return colors.get(str(level), '⚪')

    def update_content(self, weather_content):
        with open(self.index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = re.sub(
            r'<!--qweather:start-->.*<!--qweather:end-->', 
            f'<!--qweather:start-->\n{weather_content}\n<!--qweather:end-->', 
            content, 
            flags=re.DOTALL
        )
        
        with open(self.index_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def get_all_weather(self):
        """Fetch weather for all configured cities"""
        weather_info = []
        for city in CITIES:
            try:
                weather_data = self.get_city_weather(city)
                weather_info.append(weather_data)
            except Exception as e:
                logger.error(f"Failed to fetch weather for {city}: {str(e)}")
                weather_info.append(f"**{city}**\n- Failed to fetch weather data")
        
        return '\n\n'.join(weather_info)
