import requests
import re  # 用于清洗风力数据的正则库

# -------------------------- 配置项 --------------------------
# 替换成你自己的高德Web服务API密钥（必须修改！）
AMAP_API_KEY = "52a2ae825ca762ad5037244dc6818a17"
AMAP_WEATHER_URL = "https://restapi.amap.com/v3/weather/weatherInfo"

# -------------------------- 核心函数 --------------------------
def get_weather_info(city):
    """
    高德地图API获取国内城市天气（支持中文城市名，如"北京"）
    适配返回格式：{"status":"1","count":"1","info":"OK","infocode":"10000","lives":[{"province":"北京","city":"北京市",...}]}
    :param city: 城市名称（中文，如"北京"）
    :return: 包含温度、天气状况的字典，失败返回None
    """
    # 构建请求参数
    params = {
        'key': AMAP_API_KEY,
        'city': city,         # 传入中文城市名（如北京）
        'extensions': 'base', # base=实时天气，all=预报（免费版仅支持base）
        'output': 'json'      # 返回JSON格式
    }
    
    try:
        # 发送请求（超时10秒）
        response = requests.get(AMAP_WEATHER_URL, params=params, timeout=10)
        response.raise_for_status()  # 抛出HTTP错误（如400/403/500）
        data = response.json()
        
        # 解析高德天气数据（核心修复）
        if data.get('status') == '1' and len(data.get('lives', [])) > 0:
            live_data = data['lives'][0]
            
            # 修复1：清洗城市名（北京市→北京、上海市→上海）
            city_name = live_data['city'].replace('市', '')
            
            # 修复2：清洗风力数据（处理≤3、3-4、5级等格式）
            windpower = live_data['windpower']
            wind_num_list = re.findall(r'\d+', windpower)  # 提取所有数字
            wind_speed = float(wind_num_list[0]) if wind_num_list else 0.0  # 取第一个数字
            
            # 组装天气信息字典
            weather_info = {
                'city': city_name,                          # 清洗后的城市名
                'temperature': float(live_data['temperature']),  # 实时温度（转浮点数）
                'condition': live_data['weather'],          # 天气状况（如霾、晴、小雨）
                'humidity': int(live_data['humidity']),      # 湿度（转整数）
                'wind_speed': wind_speed                    # 清洗后的风速（级）
            }
            return weather_info
        
        else:
            # 打印错误信息，方便调试
            error_info = data.get('info', '未知错误')
            error_code = data.get('infocode', '无错误码')
            print(f"获取天气失败：{error_info}（错误码：{error_code}）")
            return None
        
    except requests.exceptions.RequestException as e:
        # 网络错误（如超时、连接失败）
        print(f"网络请求失败：{str(e)}")
        return None
    except KeyError as e:
        # 数据字段缺失（如live_data中没有windpower）
        print(f"数据解析失败，缺少字段：{str(e)}")
        return None
    except ValueError as e:
        # 类型转换失败（如温度不是数字）
        print(f"数据类型转换失败：{str(e)}")
        return None

def generate_clothing_advice(weather_info):
    """
    根据天气信息生成穿搭建议
    :param weather_info: get_weather_info返回的天气信息字典
    :return: 穿搭建议列表
    """
    # 无天气数据时返回提示
    if not weather_info:
        return ["无法获取天气信息，无法生成穿搭建议"]
    
    # 提取核心参数
    temp = weather_info['temperature']
    condition = weather_info['condition']
    humidity = weather_info['humidity']
    wind_speed = weather_info['wind_speed']
    
    advice = []
    # 1. 基础温度建议
    advice.append(f"当前{weather_info['city']}温度：{temp}℃，天气状况：{condition}")
    
    # 按温度区间给出建议
    if temp >= 30:
        advice.append("🔥 高温天气：建议穿短袖、短裤、凉鞋，优先选择透气吸汗的棉质衣物")
        advice.append("   注意：做好防晒，多喝水，避免长时间在户外暴晒")
    elif 25 <= temp < 30:
        advice.append("☀️ 温暖天气：建议穿短袖、薄长裤、连衣裙、帆布鞋，可搭配薄外套备用")
    elif 20 <= temp < 25:
        advice.append("🌤️ 舒适天气：建议穿长袖衬衫、薄针织衫、休闲裤、单鞋，早晚可加薄外套")
    elif 10 <= temp < 20:
        advice.append("🍂 微凉天气：建议穿毛衣、厚外套、牛仔裤、运动鞋，注意防风保暖")
    elif 0 <= temp < 10:
        advice.append("❄️ 寒冷天气：建议穿羽绒服、厚毛衣、加绒裤、靴子，出门戴围巾手套")
    else:
        advice.append("🥶 严寒天气：建议穿厚羽绒服、保暖内衣、加绒裤、雪地靴，做好全身保暖")
    
    # 2. 天气状况补充建议
    if "霾" in condition:
        advice.append("😷 雾霾提示：尽量减少外出，外出佩戴口罩，回家及时清洁皮肤和衣物")
    elif "雨" in condition:
        advice.append("🌧️ 降雨提示：记得带雨伞/雨衣，穿防水鞋，避免穿浅色易脏衣物")
    elif "雪" in condition:
        advice.append("☃️ 降雪提示：穿防滑鞋，多穿保暖层，注意路面结冰，避免穿光滑底鞋")
    elif "风" in condition or wind_speed > 5:
        advice.append("💨 大风提示：建议穿防风外套，帽子/围巾固定好，避免穿宽松易被风吹起的衣物")
    
    # 3. 湿度补充建议
    if humidity > 80:
        advice.append("💧 高湿度提示：空气潮湿，建议穿透气速干的衣物，避免棉质衣物贴肤")
    elif humidity < 30:
        advice.append("🌬️ 低湿度提示：空气干燥，建议穿柔软的棉质衣物，多喝水补充水分")
    
    return advice

def get_weather_clothing_advice(city):
    """
    一站式获取天气+穿搭建议（对外统一接口）
    :param city: 城市名称（中文）
    :return: 包含天气信息和穿搭建议的字典
    """
    # 获取天气数据
    weather_info = get_weather_info(city)
    # 生成穿搭建议
    advice = generate_clothing_advice(weather_info)
    
    # 返回统一格式
    return {
        'weather': weather_info,  # 天气信息（None/字典）
        'advice': advice          # 穿搭建议列表
    }