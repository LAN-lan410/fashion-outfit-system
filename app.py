import os
import json
import random
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime

# -------------------------- 核心配置 --------------------------
# 初始化Flask应用（只初始化一次！）
app = Flask(__name__)
app.secret_key = "fashion_2025_secure_key"  # 会话加密密钥

# 配置路径
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static/images/uploads")
AVATAR_FOLDER = os.path.join(os.path.dirname(__file__), "static/images/avatars")  # 新增：头像上传目录
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 默认头像列表
DEFAULT_AVATARS = [
    '/static/images/avatar1.jpg',
    '/static/images/avatar2.jpg',
    '/static/images/avatar3.jpg',
    '/static/images/avatar4.jpg'
]

# 创建上传目录
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AVATAR_FOLDER, exist_ok=True)  # 新增：创建头像目录
# 确保data目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# -------------------------- 辅助函数 --------------------------
# 读取JSON文件
def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # 如果文件不存在，创建初始数据
        if filename == 'tips.json':
            return {}
        elif filename == 'closet.json':
            return {}
        elif filename == 'posts.json':
            return []
        elif filename == 'users.json':
            # 创建默认用户
            default_users = {
                'fashionista': {
                    'password': '123456',
                    'nickname': '时尚达人',
                    'avatar': '/static/images/avatar1.jpg',
                    'intro': '热爱时尚的穿搭爱好者',
                    'fans': 98,
                    'follow': 105,
                    'posts': [],
                    'created_at': '2025-01-01 00:00:00'
                },
                'stylefan': {
                    'password': '123456',
                    'nickname': '风格爱好者',
                    'avatar': '/static/images/avatar2.jpg',
                    'intro': '探索不同穿搭风格',
                    'fans': 45,
                    'follow': 62,
                    'posts': [],
                    'created_at': '2025-01-01 00:00:00'
                }
            }
            return default_users
        elif filename == 'calendar.json':
            return {}
        elif filename == 'wishlist.json':
            return {}
        return {}

# 写入JSON文件
def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 检查文件扩展名
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 验证用户名
def validate_username(username):
    if not username:
        return False, "用户名不能为空"
    if len(username) < 3:
        return False, "用户名至少需要3个字符"
    if len(username) > 20:
        return False, "用户名不能超过20个字符"
    if not username.isalnum():
        return False, "用户名只能包含字母和数字"
    return True, ""

# 验证密码
def validate_password(password):
    if not password:
        return False, "密码不能为空"
    if len(password) < 6:
        return False, "密码至少需要6个字符"
    if len(password) > 30:
        return False, "密码不能超过30个字符"
    return True, ""

# 验证昵称
def validate_nickname(nickname):
    if not nickname:
        return False, "昵称不能为空"
    if len(nickname) < 2:
        return False, "昵称至少需要2个字符"
    if len(nickname) > 20:
        return False, "昵称不能超过20个字符"
    return True, ""

# -------------------------- 原有核心路由（登录/注册等） --------------------------
# 登录页（保留原有根路由，不覆盖！）
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_json('users.json')

        if username in users and users[username]['password'] == password:
            session['username'] = username  # 保存登录状态
            flash('登录成功！欢迎来到时尚穿搭系统~', 'success')
            return redirect(url_for('profile'))
        else:
            flash('账号或密码错误！', 'danger')

    return render_template('login.html')

# 注册页
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        nickname = request.form['nickname'].strip()

        users = load_json('users.json')

        # 验证用户名
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            flash(f'用户名错误：{error_msg}', 'danger')
            return redirect(url_for('register'))

        # 检查用户名是否已存在
        if username in users:
            flash('用户名已存在！请选择其他用户名', 'danger')
            return redirect(url_for('register'))

        # 验证密码
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            flash(f'密码错误：{error_msg}', 'danger')
            return redirect(url_for('register'))

        # 确认密码
        if password != confirm_password:
            flash('两次输入的密码不一致！', 'danger')
            return redirect(url_for('register'))

        # 验证昵称
        is_valid, error_msg = validate_nickname(nickname)
        if not is_valid:
            flash(f'昵称错误：{error_msg}', 'danger')
            return redirect(url_for('register'))

        # 随机选择一个默认头像
        avatar = random.choice(DEFAULT_AVATARS)

        # 创建新用户
        new_user = {
            'password': password,
            'nickname': nickname,
            'avatar': avatar,
            'intro': '新的穿搭爱好者，记录我的时尚旅程',
            'fans': 0,
            'follow': 0,
            'posts': [],
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        users[username] = new_user
        save_json('users.json', users)

        # 初始化用户的衣橱数据
        closet_data = load_json('closet.json')
        if username not in closet_data:
            closet_data[username] = []
            save_json('closet.json', closet_data)

        # 初始化用户的心得数据
        tips_data = load_json('tips.json')
        if username not in tips_data:
            tips_data[username] = {
                'tips': [],
                'categories': ['穿搭技巧', '搭配经验', '购物心得', '风格灵感', '保养建议']
            }
            save_json('tips.json', tips_data)

        flash('注册成功！请登录您的账号', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# 登出
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('已成功登出，期待下次相遇~', 'info')
    return redirect(url_for('login'))

# 个人主页
@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    users = load_json('users.json')
    user = users[username]
    posts = load_json('posts.json')
    # 筛选当前用户的动态
    user_posts = sorted([p for p in posts if p['author'] == username],
                        key=lambda x: x['time'], reverse=True)

    return render_template('profile.html', user=user, user_posts=user_posts)

# -------------------------- 新增：编辑个人资料路由 --------------------------
@app.route('/profile/edit', methods=['GET'])
def edit_profile():
    """编辑个人资料页面"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    users = load_json('users.json')
    user = users.get(username, {})
    return render_template('edit_profile.html', user=user)

@app.route('/profile/save', methods=['POST'])
def save_profile():
    """保存个人资料"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    users = load_json('users.json')
    user = users.get(username, {})
    
    # 更新基本信息
    if 'nickname' in request.form:
        user['nickname'] = request.form.get('nickname', user.get('nickname', ''))
    if 'intro' in request.form:
        user['intro'] = request.form.get('intro', user.get('intro', ''))
    
    # 处理头像上传
    if 'avatar' in request.files:
        file = request.files['avatar']
        if file and allowed_file(file.filename):
            # 生成唯一文件名
            filename = f"avatar_{username}_{uuid.uuid4()}.{file.filename.rsplit('.', 1)[1].lower()}"
            file_path = os.path.join(AVATAR_FOLDER, filename)
            file.save(file_path)
            # 更新头像路径
            user['avatar'] = f"/static/images/avatars/{filename}"
    
    # 保存用户数据
    users[username] = user
    save_json('users.json', users)
    
    flash('个人资料修改成功！', 'success')
    return redirect(url_for('profile'))

# -------------------------- 原有功能路由（无修改） --------------------------
# 智能衣橱
@app.route('/closet', methods=['GET', 'POST'])
def closet():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    closet_data = load_json('closet.json')
    # 初始化用户衣橱
    if username not in closet_data:
        closet_data[username] = []

    if request.method == 'POST':
        # 处理服装上传
        if 'file' not in request.files:
            flash('未选择图片！请选择服装图片后上传', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('未选择图片！请选择服装图片后上传', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # 保存图片（避免重名）
            filename = f"{username}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            # 保存服装信息
            category = request.form['category']
            style = request.form.getlist('style')  # 多选风格标签
            clothing = {
                'id': len(closet_data[username]) + 1,
                'img': f"/static/images/uploads/{filename}",
                'category': category,
                'style': style,
                'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            closet_data[username].append(clothing)
            save_json('closet.json', closet_data)
            flash('服装上传成功！已加入你的智能衣橱', 'success')
            return redirect(url_for('closet'))

    # 按分类筛选衣橱数据
    tops = [c for c in closet_data.get(username, []) if c['category'] == '上衣']
    bottoms = [c for c in closet_data.get(username, []) if c['category'] == '下装']
    skirts = [c for c in closet_data.get(username, []) if c['category'] == '裙子']

    return render_template('closet.html', tops=tops, bottoms=bottoms, skirts=skirts)

# 智能搭配生成
@app.route('/match', methods=['GET', 'POST'])
def match():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    closet_data = load_json('closet.json')
    match_result = None
    # 所有可选风格
    style_options = ['甜酷风', '通勤风', '休闲风', '约会风']

    if request.method == 'POST':
        style = request.form['style']
        # 获取用户衣橱中对应风格的服装
        user_closet = closet_data.get(username, [])
        style_clothes = [c for c in user_closet if style in c['style']]

        if not style_clothes:
            flash(f'暂无「{style}」风格的服装！请先上传该风格的服装', 'warning')
            return redirect(url_for('match'))

        # 分类筛选
        style_tops = [c for c in style_clothes if c['category'] == '上衣']
        style_bottoms = [c for c in style_clothes if c['category'] == '下装']
        style_skirts = [c for c in style_clothes if c['category'] == '裙子']

        # 生成搭配方案
        match_result = {}
        # 方案A：上衣+下装（如果有）
        if style_tops and style_bottoms:
            match_result['A'] = {
                'top': random.choice(style_tops),
                'bottom': random.choice(style_bottoms),
                'type': '上衣+下装'
            }
        # 方案B：裙子（如果有）
        if style_skirts:
            match_result['B'] = {
                'skirt': random.choice(style_skirts),
                'type': '裙子'
            }

        if not match_result:
            flash(f'无法生成「{style}」风格的搭配！请补充对应品类的服装', 'warning')

    return render_template('match.html',
                           style_options=style_options,
                           match_result=match_result)

# 穿搭社区
@app.route('/community', methods=['GET', 'POST'])
def community():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    users = load_json('users.json')
    posts = load_json('posts.json')

    # 处理发布动态/点赞/评论
    if request.method == 'POST':
        # 1. 发布新动态
        if 'post_content' in request.form:
            content = request.form['post_content'].strip()
            if not content:
                flash('动态内容不能为空！请输入想分享的穿搭心得', 'danger')
                return redirect(url_for('community'))

            # 处理动态图片
            img_path = None
            if 'post_file' in request.files:
                file = request.files['post_file']
                if file.filename != '' and allowed_file(file.filename):
                    filename = f"post_{username}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                    img_path = f"/static/images/uploads/{filename}"
                    file.save(os.path.join(UPLOAD_FOLDER, filename))

            # 生成动态ID
            post_id = len(posts) + 1 if posts else 1
            new_post = {
                'id': post_id,
                'author': username,
                'avatar': users[username]['avatar'],
                'nickname': users[username]['nickname'],
                'content': content,
                'img': img_path,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'likes': 0,
                'liked_by': [],
                'comments': []
            }
            posts.append(new_post)
            save_json('posts.json', posts)
            # 更新用户动态列表
            users[username]['posts'].append(post_id)
            save_json('users.json', users)
            flash('动态发布成功！分享你的时尚态度~', 'success')
            return redirect(url_for('community'))

        # 2. 点赞操作
        elif 'like_post_id' in request.form:
            post_id = int(request.form['like_post_id'])
            for post in posts:
                if post['id'] == post_id:
                    if username in post['liked_by']:
                        # 取消点赞
                        post['likes'] -= 1
                        post['liked_by'].remove(username)
                    else:
                        # 点赞
                        post['likes'] += 1
                        post['liked_by'].append(username)
                    save_json('posts.json', posts)
                    return redirect(url_for('community'))

        # 3. 评论操作
        elif 'comment_post_id' in request.form:
            post_id = int(request.form['comment_post_id'])
            comment_content = request.form['comment_content'].strip()
            if not comment_content:
                flash('评论内容不能为空！', 'danger')
                return redirect(url_for('community'))

            for post in posts:
                if post['id'] == post_id:
                    post['comments'].append({
                        'author': username,
                        'nickname': users[username]['nickname'],
                        'content': comment_content,
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    save_json('posts.json', posts)
                    flash('评论成功！', 'success')
                    return redirect(url_for('community'))

    # 按时间倒序排列动态
    posts_sorted = sorted(posts, key=lambda x: x['time'], reverse=True)

    return render_template('community.html',
                           posts=posts_sorted,
                           current_user=username)

# -------------------------- 穿搭心得功能 --------------------------
@app.route('/tips')
def tips():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    tips_data = load_json('tips.json')

    # 初始化用户心得数据
    if username not in tips_data:
        tips_data[username] = {
            'tips': [],
            'categories': ['穿搭技巧', '搭配经验', '购物心得', '风格灵感', '保养建议']
        }
        save_json('tips.json', tips_data)

    user_tips = tips_data[username].get('tips', [])
    categories = tips_data[username].get('categories', [])

    # 按分类筛选
    selected_category = request.args.get('category', '')
    if selected_category:
        filtered_tips = [tip for tip in user_tips if tip.get('category') == selected_category]
    else:
        filtered_tips = user_tips

    # 按时间倒序排序
    sorted_tips = sorted(filtered_tips, key=lambda x: x.get('time', ''), reverse=True)

    return render_template('tips.html',
                           tips=sorted_tips,
                           categories=categories,
                           selected_category=selected_category)

@app.route('/tips/add', methods=['GET', 'POST'])
def add_tip():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    tips_data = load_json('tips.json')

    if username not in tips_data:
        tips_data[username] = {'tips': [], 'categories': []}

    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content'].strip()
        category = request.form.get('category', '')
        is_public = 'is_public' in request.form

        if not title or not content:
            flash('标题和内容不能为空！', 'danger')
            return redirect(url_for('add_tip'))

        # 生成心得ID
        tip_id = len(tips_data[username]['tips']) + 1

        new_tip = {
            'id': tip_id,
            'title': title,
            'content': content,
            'category': category,
            'is_public': is_public,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'likes': 0,
            'comments': []
        }

        tips_data[username]['tips'].append(new_tip)
        save_json('tips.json', tips_data)

        flash('心得添加成功！', 'success')

        # 如果选择公开，同时发布到社区
        if is_public:
            users = load_json('users.json')
            posts = load_json('posts.json')

            post_id = len(posts) + 1 if posts else 1
            new_post = {
                'id': post_id,
                'author': username,
                'avatar': users[username]['avatar'],
                'nickname': users[username]['nickname'],
                'content': f"📝 分享穿搭心得：{title}\n\n{content}",
                'img': None,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'likes': 0,
                'liked_by': [],
                'comments': []
            }
            posts.append(new_post)
            save_json('posts.json', posts)

            users[username]['posts'].append(post_id)
            save_json('users.json', users)
            flash('心得已同步分享到社区！', 'info')

        return redirect(url_for('tips'))

    return render_template('add_tip.html')

@app.route('/tips/edit/<int:tip_id>', methods=['GET', 'POST'])
def edit_tip(tip_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    tips_data = load_json('tips.json')

    if username not in tips_data:
        return redirect(url_for('tips'))

    # 查找心得
    tip_to_edit = None
    for tip in tips_data[username]['tips']:
        if tip['id'] == tip_id:
            tip_to_edit = tip
            break

    if not tip_to_edit:
        flash('心得不存在！', 'danger')
        return redirect(url_for('tips'))

    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content'].strip()
        category = request.form.get('category', '')
        is_public = 'is_public' in request.form

        if not title or not content:
            flash('标题和内容不能为空！', 'danger')
            return render_template('edit_tip.html', tip=tip_to_edit)

        # 更新心得
        tip_to_edit['title'] = title
        tip_to_edit['content'] = content
        tip_to_edit['category'] = category
        tip_to_edit['is_public'] = is_public

        save_json('tips.json', tips_data)

        flash('心得修改成功！', 'success')
        return redirect(url_for('tips'))

    return render_template('edit_tip.html', tip=tip_to_edit)

@app.route('/tips/delete/<int:tip_id>', methods=['POST'])
def delete_tip(tip_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    tips_data = load_json('tips.json')

    if username not in tips_data:
        return redirect(url_for('tips'))

    # 删除心得
    tips_data[username]['tips'] = [tip for tip in tips_data[username]['tips'] if tip['id'] != tip_id]

    # 重新编号
    for i, tip in enumerate(tips_data[username]['tips'], 1):
        tip['id'] = i

    save_json('tips.json', tips_data)

    flash('心得已删除！', 'success')
    return redirect(url_for('tips'))

# -------------------------- 原有天气穿搭占位功能 --------------------------
def generate_weather_suggestion(param, param1):
    pass

def generate_recommended_items(param, param1):
    pass

def generate_match_suggestions(param, param1):
    pass

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    if 'username' not in session:
        return redirect(url_for('login'))

    # 初始化变量
    weather_data = None
    match_suggestions = []
    city = '北京'
    weather_type = 'auto'

    if request.method == 'POST':
        city = request.form.get('city', '北京')
        weather_type = request.form.get('weather_type', 'auto')

        # 模拟天气数据
        weather_conditions = {
            'sunny': {'temp': 28, 'condition': 'sunny', 'condition_text': '晴朗'},
            'cloudy': {'temp': 22, 'condition': 'cloudy', 'condition_text': '多云'},
            'rainy': {'temp': 18, 'condition': 'rainy', 'condition_text': '小雨'},
            'snowy': {'temp': -2, 'condition': 'snowy', 'condition_text': '小雪'},
            'windy': {'temp': 15, 'condition': 'windy', 'condition_text': '大风'},
            'auto': {'temp': 25, 'condition': 'sunny', 'condition_text': '晴朗'}
        }

        if weather_type in weather_conditions:
            base_data = weather_conditions[weather_type]
        else:
            base_data = weather_conditions['auto']

        # 生成天气数据
        weather_data = {
            'city': city,
            'temp': base_data['temp'],
            'temp_min': base_data['temp'] - 3,
            'temp_max': base_data['temp'] + 3,
            'condition': base_data['condition'],
            'condition_text': base_data['condition_text'],
            'date': datetime.now().strftime('%Y年%m月%d日'),
            'humidity': random.randint(40, 80) if random.choice([True, False]) else None,
            'advice_level': random.randint(1, 5),
            'suggestion': generate_weather_suggestion(base_data['condition'], base_data['temp']),
            'recommended_items': generate_recommended_items(base_data['condition'], base_data['temp'])
        }

        # 生成搭配建议
        match_suggestions = generate_match_suggestions(weather_data['condition'], weather_data['temp'])

    # 确保所有变量都传递给模板
    return render_template('weather.html',
                           weather_data=weather_data,
                           match_suggestions=match_suggestions,
                           city=city,
                           weather_type=weather_type)


# -------------------------- 穿搭日历功能 --------------------------
@app.route('/calendar')
def calendar():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    calendar_data = load_json('calendar.json')

    # 初始化用户日历数据
    if username not in calendar_data:
        calendar_data[username] = {'outfits': [], 'settings': {}}
        save_json('calendar.json', calendar_data)

    user_outfits = calendar_data[username].get('outfits', [])

    # 计算统计信息
    stats = calculate_calendar_stats(user_outfits)

    # 准备日历事件
    calendar_events = []
    for outfit in user_outfits[-20:]:  # 只显示最近20条
        calendar_events.append({
            'id': outfit.get('id', 0),
            'title': f"💃 {outfit.get('description', '')[:20]}...",
            'date': outfit.get('date', ''),
            'color': get_style_color(outfit.get('styles', [])),
            'description': outfit.get('description', ''),
            'image': outfit.get('image_url', ''),
            'styles': outfit.get('styles', [])
        })

    # 准备最近穿搭记录
    recent_outfits = sorted(user_outfits[-6:], key=lambda x: x.get('date', ''), reverse=True)
    for outfit in recent_outfits:
        outfit['weekday'] = get_weekday(outfit.get('date', ''))

    # 准备样式和心情选项
    style_options = ['甜酷风', '通勤', '休闲', '约会', '复古', '简约']
    mood_options = [
        {'value': 'happy', 'icon': 'bi bi-emoji-smile', 'text': '开心'},
        {'value': 'relaxed', 'icon': 'bi bi-emoji-neutral', 'text': '放松'},
        {'value': 'confident', 'icon': 'bi bi-emoji-wink', 'text': '自信'},
        {'value': 'casual', 'icon': 'bi bi-emoji-sunglasses', 'text': '随意'}
    ]

    return render_template('calendar.html',
                           stats=stats,
                           calendar_events=calendar_events,
                           recent_outfits=recent_outfits,
                           today=datetime.now().strftime('%Y-%m-%d'),
                           style_options=style_options,
                           mood_options=mood_options)

def calculate_calendar_stats(outfits):
    if not outfits:
        return {
            'total_days': 0,
            'this_month': 0,
            'most_used_style': None,
            'last_record': '暂无记录'
        }

    current_month = datetime.now().strftime('%Y-%m')
    this_month_count = len([o for o in outfits if o.get('date', '').startswith(current_month)])

    # 计算最常用风格
    style_counter = {}
    for outfit in outfits:
        for style in outfit.get('styles', []):
            style_counter[style] = style_counter.get(style, 0) + 1

    most_used_style = max(style_counter.items(), key=lambda x: x[1])[0] if style_counter else None

    # 获取最后记录日期
    if outfits:
        latest = max(outfits, key=lambda x: x.get('date', ''))
        last_record = latest.get('date', '')
    else:
        last_record = '暂无记录'

    return {
        'total_days': len(outfits),
        'this_month': this_month_count,
        'most_used_style': most_used_style,
        'last_record': last_record
    }

def get_style_color(styles):
    color_map = {
        '甜酷风': '#ff6b6b',
        '通勤': '#4ecdc4',
        '休闲': '#45b7d1',
        '约会': '#96ceb4',
        '复古': '#ffbe0b',
        '简约': '#a9a9a9'
    }

    for style in styles:
        if style in color_map:
            return color_map[style]
    return '#6c5ce7'

def get_weekday(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        return weekdays[date_obj.weekday()]
    except:
        return ''

@app.route('/calendar/add', methods=['POST'])
def add_calendar_outfit():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    calendar_data = load_json('calendar.json')

    # 获取表单数据
    date = request.form.get('date')
    description = request.form.get('description')
    styles = request.form.getlist('styles')
    weather = request.form.get('weather')
    temperature = request.form.get('temperature')
    mood = request.form.get('mood')

    # 处理图片上传
    image_url = None
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '' and allowed_file(file.filename):
            filename = f"calendar_{username}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
            image_url = f"/static/images/uploads/{filename}"
            file.save(os.path.join(UPLOAD_FOLDER, filename))

    # 创建新记录
    new_outfit = {
        'id': len(calendar_data[username]['outfits']) + 1,
        'date': date,
        'description': description,
        'styles': styles,
        'weather': weather,
        'temperature': temperature,
        'mood': mood,
        'image_url': image_url,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    calendar_data[username]['outfits'].append(new_outfit)
    save_json('calendar.json', calendar_data)

    flash('穿搭记录已保存！', 'success')
    return redirect(url_for('calendar'))


# -------------------------- 愿望单功能 --------------------------
@app.route('/wishlist')
def wishlist():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    wishlist_data = load_json('wishlist.json')

    # 初始化用户愿望单数据
    if username not in wishlist_data:
        wishlist_data[username] = {
            'items': [],
            'budget': 0,
            'settings': {}
        }
        save_json('wishlist.json', wishlist_data)

    user_items = wishlist_data[username].get('items', [])
    budget = wishlist_data[username].get('budget', 0)

    # 筛选
    filter_type = request.args.get('filter', 'all')
    if filter_type == 'high':
        filtered_items = [item for item in user_items if item.get('priority') == 'high']
    elif filter_type == 'medium':
        filtered_items = [item for item in user_items if item.get('priority') == 'medium']
    elif filter_type == 'low':
        filtered_items = [item for item in user_items if item.get('priority') == 'low']
    elif filter_type == 'purchased':
        filtered_items = [item for item in user_items if item.get('purchased', False)]
    elif filter_type == 'unpurchased':
        filtered_items = [item for item in user_items if not item.get('purchased', False)]
    else:
        filtered_items = user_items

    # 计算统计信息
    stats = calculate_wishlist_stats(user_items, budget)

    # 样式选项
    style_options = ['甜酷风', '通勤', '休闲', '约会', '复古', '简约']

    return render_template('wishlist.html',
                           wishlist_items=filtered_items,
                           stats=stats,
                           style_options=style_options)

def calculate_wishlist_stats(items, budget):
    total_items = len(items)
    purchased_items = len([item for item in items if item.get('purchased', False)])
    high_priority = len([item for item in items if item.get('priority') == 'high'])

    # 计算总价格
    total_price = 0
    for item in items:
        price = item.get('price', 0)
        if isinstance(price, (int, float)):
            total_price += price
        elif isinstance(price, str):
            try:
                total_price += float(price)
            except ValueError:
                pass

    # 计算已购价格
    purchased_price = 0
    for item in items:
        if item.get('purchased', False):
            price = item.get('price', 0)
            if isinstance(price, (int, float)):
                purchased_price += price
            elif isinstance(price, str):
                try:
                    purchased_price += float(price)
                except ValueError:
                    pass

    return {
        'total_items': total_items,
        'purchased_items': purchased_items,
        'high_priority': high_priority,
        'total_price': f"{total_price:.0f}" if total_price > 0 else None,
        'purchased_price': purchased_price,
        'budget': budget
    }

@app.route('/wishlist/add', methods=['POST'])
def add_wishlist_item():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    wishlist_data = load_json('wishlist.json')

    # 获取表单数据
    name = request.form.get('name')
    category = request.form.get('category')
    price = request.form.get('price')
    priority = request.form.get('priority', 'medium')
    description = request.form.get('description')
    styles = request.form.getlist('styles')
    store_url = request.form.get('store_url')
    image_url = request.form.get('image_url')
    notes = request.form.get('notes')

    # 转换价格
    try:
        price_value = float(price) if price and price.strip() else 0
    except ValueError:
        price_value = 0

    # 创建新愿望单品
    new_item = {
        'id': len(wishlist_data[username]['items']) + 1,
        'name': name,
        'category': category,
        'price': price_value,
        'priority': priority,
        'description': description,
        'styles': styles,
        'store_url': store_url,
        'image_url': image_url,
        'notes': notes,
        'purchased': False,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    wishlist_data[username]['items'].append(new_item)
    save_json('wishlist.json', wishlist_data)

    flash('愿望单品已添加！', 'success')
    return redirect(url_for('wishlist'))

@app.route('/wishlist/set_budget', methods=['GET'])
def set_budget():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    budget = request.args.get('budget', 0)

    wishlist_data = load_json('wishlist.json')

    try:
        budget_value = float(budget)
        wishlist_data[username]['budget'] = budget_value
        save_json('wishlist.json', wishlist_data)
        flash(f'预算已设置为 {budget_value} 元', 'success')
    except ValueError:
        flash('请输入有效的数字', 'danger')

    return redirect(url_for('wishlist'))

@app.route('/wishlist/purchase/<int:item_id>', methods=['GET'])
def purchase_wishlist_item(item_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    wishlist_data = load_json('wishlist.json')

    for item in wishlist_data[username]['items']:
        if item['id'] == item_id:
            item['purchased'] = True
            item['purchased_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            break

    save_json('wishlist.json', wishlist_data)
    flash('已标记为已购买！', 'success')
    return redirect(url_for('wishlist'))

# -------------------------- 新增：天气穿搭独立路由（不覆盖原有功能） --------------------------
# 导入天气穿搭核心逻辑
try:
    import weather_clothing
except ImportError:
    # 如果没有weather_clothing模块，创建模拟函数
    def get_weather_clothing_advice(city):
        return {
            'weather': {
                'city': city,
                'temperature': 25,
                'condition': 'sunny',
                'humidity': 60,
                'wind_speed': 2
            },
            'advice': ['今日适合穿轻薄的短袖+牛仔裤', '建议搭配帆布鞋，清爽又时尚']
        }
    # 模拟模块
    class weather_clothing:
        get_weather_clothing_advice = get_weather_clothing_advice

# 天气穿搭页面（独立路由，不影响原有登录页）
@app.route('/weather-clothing')
def weather_clothing_page():
    """天气穿搭建议页面（独立入口）"""
    return render_template('index.html')

# 天气穿搭API接口（支持中文城市名）
@app.route('/api/weather-advice', methods=['GET'])
def api_weather_advice():
    """
    天气穿搭建议API接口
    请求示例：/api/weather-advice?city=北京
    """
    city = request.args.get('city', '北京')  # 默认北京，支持中文
    result = weather_clothing.get_weather_clothing_advice(city)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)  # 新端口5001