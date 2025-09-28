from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, time
import os

from models import db, User, Artist, Demo, Evaluation
from utils import save_file
from config import UPLOAD_FOLDER, DATABASE_URI
from flask import Response
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_URI}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False

db.init_app(app)


# 注册静态文件路由用于访问上传内容
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


def response(code=0, msg="success", data=None):
    body = {"code": code, "msg": msg, "data": data or {}}
    return Response(
        json.dumps(body, ensure_ascii=False),  # 👈 ensure_ascii=False 强制输出中文
        mimetype='application/json'
    )


# ==================== 上传文件 ====================
@app.route('/api/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    name = request.form.get('name')  # 可选用途标识
    if not file:
        return response(code=400, msg="缺少文件")

    url = save_file(file)
    if not url:
        return response(code=400, msg="不支持的文件类型")

    return response(data={"url": url})


# ==================== 用户管理 ====================

# 新增用户
@app.route('/api/user/add', methods=['POST'])
def add_user():
    req = request.get_json()
    params = req.get('params', {})

    name = params.get('name')
    password = params.get('password')
    role = params.get('role')

    if not name or not password or role is None:
        return response(code=400, msg="参数缺失")

    if User.query.filter_by(user_name=name).first():
        return response(code=400, msg="用户名已存在")

    user = User(user_name=name, password=password, role=role)
    db.session.add(user)
    db.session.commit()

    return response()


# 用户登录
@app.route('/api/user/login', methods=['POST'])
def login():
    req = request.get_json()
    params = req.get('params', {})

    name = params.get('name')
    password = params.get('password')

    user = User.query.filter_by(user_name=name, password=password).first()
    if not user:
        return response(code=401, msg="用户名或密码错误")

    return response(data={"role": user.role})


# ==================== 艺人信息管理 ====================

# 新增艺人
@app.route('/api/artist/add', methods=['POST'])
def add_artist():
    req = request.get_json()
    params = req.get('params', {})

    artist = Artist.query.filter_by(nickName=params['nickName']).first()
    if artist:
        return response(code=400, msg="艺人已存在")

    required = ['avatar', 'name', 'nickName', 'job', 'address', 'qq', 'wechat',
                'telephone', 'emergencyTelphone', 'creditCardNum',
                'identityCardFront', 'identityCardReverse', 'salary', 'gender']
    for field in required:
        if not params.get(field):
            return response(code=400, msg=f"缺少必填字段: {field}")

    artist = Artist(
        avatar=params['avatar'],
        name=params['name'],
        nickName=params['nickName'],
        job=params['job'],
        address=params['address'],
        ID=params['ID'],
        qq=params['qq'],
        wechat=params['wechat'],
        telephone=params['telephone'],
        emergencyTelphone=params['emergencyTelphone'],
        creditCardNum=params['creditCardNum'],
        recommendWord1=params.get('recommendWord1'),
        recommendWord2=params.get('recommendWord2'),
        recommendWord3=params.get('recommendWord3'),
        identityCardFront=params['identityCardFront'],
        identityCardReverse=params['identityCardReverse'],
        salary=params['salary'],
        priorityRating=params.get('priorityRating'),
        gender=params['gender'],
        create_time=int(datetime.now().timestamp())
    )
    db.session.add(artist)
    db.session.commit()

    artist = Artist.query.filter_by(nickName=params['nickName']).first()
    if not artist:
        return response(code=404, msg="艺人不存在")

    data = {c.name: getattr(artist, c.name) for c in artist.__table__.columns}
    return response(data=data)

# 修改艺人信息
@app.route('/api/artist/update', methods=['POST'])
def update_artist():
    req = request.get_json()
    params = req.get('params', {})
    artist_id = params.get('artistId":')

    artist = Artist.query.get(artist_id)
    if not artist:
        return response(code=404, msg="艺人不存在")

    # 更新字段
    fields = ['avatar', 'name', 'nickName', 'jobId', 'address', 'ID','qq', 'wechat',
              'telephone', 'emergencyTelphone', 'creditCardNum',
              'recommendWord1', 'recommendWord2', 'recommendWord3',
              'identityCardFront', 'identityCardReverse', 'salary', 'priorityRating', 'gender']
    for field in fields:
        value = params.get(field)
        if value is not None:
            if field == 'jobId':
                artist.job = value
            else:
                setattr(artist, field, value)

    db.session.commit()
    return response()


# 删除艺人（连带删除小样和评价）
@app.route('/api/artist/delete', methods=['POST'])
def delete_artist():
    req = request.get_json()
    params = req.get('params', {})
    artist_id = params.get('artistId')

    artist = Artist.query.get(artist_id)
    if not artist:
        return response(code=404, msg="艺人不存在")

    # 删除关联数据
    Demo.query.filter_by(artistId=artist_id).delete()
    Evaluation.query.filter_by(artistId=artist_id).delete()
    db.session.delete(artist)
    db.session.commit()

    return response()


# 查看艺人信息
@app.route('/api/artist/get', methods=['POST'])
def get_artist():
    req = request.get_json()
    params = req.get('params', {})
    nickName = params.get('nickName')

    artist = Artist.query.filter_by(nickName=nickName).first()
    if not artist:
        return response(code=404, msg="艺人不存在")

    data = {c.name: getattr(artist, c.name) for c in artist.__table__.columns}
    return response(data=data)


# ==================== 小样信息录入 ====================
@app.route('/api/demo/add', methods=['POST'])
def add_demo():
    req = request.get_json()
    params = req.get('params', {})

    demo_type = params.get('demoType')
    file_url = params.get('fileUrl')
    artist_id = params.get('artistId')

    if not demo_type or not file_url or not artist_id:
        return response(code=400, msg="参数缺失")

    if not Artist.query.get(artist_id):
        return response(code=404, msg="艺人不存在")

    demo = Demo(artistId=artist_id, demoType=demo_type, fileUrl=file_url)
    db.session.add(demo)
    db.session.commit()
    return response()


# ==================== 评价管理 ====================

# 添加评价
@app.route('/api/eval/add', methods=['POST'])
def add_evaluation():
    req = request.get_json()
    params = req.get('params', {})

    required = ['content', 'time', 'director', 'artistId', 'evaluate', 'score']
    for field in required:
        if params.get(field) is None:
            return response(code=400, msg=f"缺少字段: {field}")

    if len(params['evaluate']) < 30:
        return response(code=400, msg="评价不少于30个字")

    if not Artist.query.get(params['artistId']):
        return response(code=404, msg="艺人不存在")

    eval_obj = Evaluation(
        content=params['content'],
        time=params['time'],
        director=params['director'],
        artistId=params['artistId'],
        evaluate=params['evaluate'],
        score=params['score']
    )
    db.session.add(eval_obj)
    db.session.commit()
    return response()


# 查询评价
@app.route('/api/eval/list', methods=['POST'])
def list_evaluations():
    req = request.get_json()
    params = req.get('params', {})
    artist_id = params.get('artistId')

    if not artist_id:
        return response(code=400, msg="缺少artistId")

    evaluations = Evaluation.query.filter_by(artistId=artist_id).order_by(Evaluation.time.desc()).all()
    result = []
    for e in evaluations:
        result.append({
            "evalId": e.evalId,
            "artistId": e.artistId,
            "time": e.time,
            "content": e.content,
            "director": e.director,
            "score": e.score,
            "evaluate": e.evaluate
        })

    return response(data=result)


# ==================== 分类查询 ====================

# 最新演员（按创建时间倒序取前若干）
@app.route('/api/stats/latest', methods=['POST'])
def latest_artists():
    req = request.get_json()
    params = req.get('params', {})
    job = params.get('job')
    now = int(datetime.now().timestamp())

    # 查询该 job 下的所有艺人
    artists = Artist.query.filter_by(job=job).all()

    novices = []

    for artist in artists:
        # 判断是否为老手：合作是否超过 2 个月（约 60 天）
        if artist.create_time:
            duration_days = (now - artist.create_time) / (24 * 3600)
            if duration_days > 60:
                continue  # 跳过老手

        # ✅ 假设有评分逻辑（示例：需要查询 Score 表）
        score_count = Evaluation.query.filter_by(artistId=artist.artistId).count()
        if score_count >= 3:
            continue  # 跳过老手

        # 当前逻辑：只要没超过 2 个月，就算新手

        # 提取三个推荐词（过滤空值）
        words = []
        for word in [artist.recommendWord1, artist.recommendWord2, artist.recommendWord3]:
            if word and word.strip():
                words.append(word.strip())
        # 只取前3个（最多3个）
        recommendWords = words[:3]

        novices.append({
            "artistId": artist.artistId,
            "avatar": artist.avatar,
            "nickName": artist.nickName,
            "recommendWord1": artist.recommendWord1,
            "recommendWord2": artist.recommendWord2,
            "recommendWord3": artist.recommendWord3,
            "priorityRating": artist.priorityRating or 0,
            "create_time": artist.create_time
        })

    # 排序规则：
    # 1. priorityRating > 0 的在前，按 priorityRating 降序
    # 2. priorityRating == 0 的在后，按 create_time 升序（越早创建越靠前）
    novices.sort(
        key=lambda x: (
            0 if x['priorityRating'] > 0 else 1,  # 分组：优先级高的在前
            -x['priorityRating'] if x['priorityRating'] > 0 else x['create_time']
        )
    )

    # 构造返回数据（只保留要求字段）
    result = [
        item for item in novices
    ]

    return response(0, "success", result)


# 合作默契榜（按评价数量排序）
@app.route('/api/stats/partnership', methods=['POST'])
def partnership_rank():
    req = request.get_json()
    params = req.get('params', {})
    job = params.get('job')
    now = int(datetime.now().timestamp())

    # 查询该 job 下的所有艺人
    artists = Artist.query.filter_by(job=job).all()
    veterans = []

    for artist in artists:
        # 获取该艺人在当前 job 下的评分（按时间倒序）
        scores = Evaluation.query.filter_by(artistId=artist.artistId) \
            .order_by(Evaluation.create_time.desc()) \
            .limit(3).all()

        score_count = len(scores)

        # 判断是否为老手
        is_veteran = False

        # 条件1：合作超过2个月
        if artist.create_time:
            duration_days = (now - artist.create_time) / (24 * 3600)
            if duration_days > 60:
                is_veteran = True

        # 条件2：有3次及以上评分
        if score_count >= 3:
            is_veteran = True

        if not is_veteran:
            continue  # 不是老手，跳过

        # 计算最终得分
        final_score = 0.0

        if score_count > 0:
            # 有评分，取最近1~3次的平均分
            total = sum(s.score for s in scores)
            final_score = round(total / score_count, 2)
        else:
            # 无评分
            if artist.priorityRating and artist.priorityRating > 0:
                final_score = 0.0  # 特殊情况：无评分但有优先级 → 得分=0
            else:
                final_score = 0.0  # 默认0

        priority = artist.priorityRating or 0

        veterans.append({
            "artistId": artist.artistId,
            "avatar": artist.avatar,
            "nickName": artist.nickName,
            "score": final_score,
            "priorityRating": priority,
            "has_scores": score_count > 0
        })

    # 排序：priorityRating > 0 的在前，按 priorityRating 降序
    # priorityRating == 0 的在后，按 score 降序（高分在前）
    veterans.sort(
        key=lambda x: (
            0 if x['priorityRating'] > 0 else 1,
            -x['priorityRating'] if x['priorityRating'] > 0 else -x['score']
        )
    )

    # 返回最终列表
    result = [
        {
            "artistId": v["artistId"],
            "nickName": v["nickName"],
            "score": v["score"]
        }
        for v in veterans
    ]

    return response(0, "success", result)


# 选角（根据标签+岗位筛选小样）
@app.route('/api/casting/select', methods=['POST'])
def select_casting():
    req = request.get_json()
    params = req.get('params', {})

    tag_id = params.get('tagId')
    job_id = params.get('jobId')
    avatar_name = params.get('avatarName')
    price_low = params.get('priceLow')
    price_high = params.get('priceHigh')

    query = db.session.query(Demo, Artist).join(Artist, Demo.artistId == Artist.artistId)
    query = query.filter(Demo.demoType == tag_id)

    if job_id:
        query = query.filter(Artist.job == job_id)
    if avatar_name:
        query = query.filter(Artist.nickName.like(f"%{avatar_name}%"))
    if price_low is not None:
        query = query.filter(Artist.salary >= price_low)
    if price_high is not None:
        query = query.filter(Artist.salary <= price_high)

    demos = query.all()
    result = []
    for demo, artist in demos:
        result.append({
            "demoId": demo.demoId,
            "artistId": demo.artistId,
            "demoType": demo.demoType,
            "fileUrl": demo.fileUrl,
            "artistName": artist.nickName,
            "artistAvatar": artist.avatar,
            "salary": artist.salary
        })

    return response(data={"auditions": result})


if __name__ == "__main__":
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("✅ 数据库连接成功，开始检查表结构...")

        # 创建一个默认管理员用户（仅当用户表为空时）
        if User.query.count() == 0:
            admin = User(user_name="admin", password="admin123", role=1)
            db.session.add(admin)
            db.session.commit()
            print("✅ 初始化成功：已创建默认管理员账号")
            print("   用户名: admin")
            print("   密码: admin123")
            print("   请在生产环境中修改密码并删除此提示！")
        else:
            print("ℹ️  数据库已存在用户，跳过初始化。")

    print("\n🚀 音视管理平台后端服务已启动！")

    # 启动开发服务器
    app.run(host="0.0.0.0", port=5001, debug=True)
