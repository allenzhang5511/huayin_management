from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 用户表
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # 推荐哈希存储
    role = db.Column(db.Integer, nullable=False)  # 1: 管理员, 2: 导演

# 艺人信息表
class Artist(db.Model):
    artistId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    avatar = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    nickName = db.Column(db.String(80), nullable=False, unique=True)
    job = db.Column(db.Integer, nullable=False)  # 岗位ID
    address = db.Column(db.String(200), nullable=False)
    ID = db.Column(db.String(200), nullable=False)
    qq = db.Column(db.String(20), nullable=False)
    wechat = db.Column(db.String(50), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)
    emergencyTelphone = db.Column(db.String(20), nullable=False)
    creditCardNum = db.Column(db.String(50), nullable=False)
    recommendWord1 = db.Column(db.String(50))
    recommendWord2 = db.Column(db.String(50))
    recommendWord3 = db.Column(db.String(50))
    identityCardFront = db.Column(db.String(200), nullable=False)
    identityCardReverse = db.Column(db.String(200), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    priorityRating = db.Column(db.Integer)
    gender = db.Column(db.Integer, nullable=False)  # 0:男, 1:女
    create_time = db.Column(db.Integer, default=0)  # 时间戳

# 小样信息表
class Demo(db.Model):
    demoId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artistId = db.Column(db.Integer, db.ForeignKey('artist.artistId'), nullable=False)
    demoType = db.Column(db.Integer, nullable=False)  # 类型ID
    fileUrl = db.Column(db.String(200), nullable=False)

# 评价信息表
class Evaluation(db.Model):
    evalId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artistId = db.Column(db.Integer, db.ForeignKey('artist.artistId'), nullable=False)
    time = db.Column(db.Integer, nullable=False)  # 时间戳
    content = db.Column(db.String(100), nullable=False)  # 项目名称
    director = db.Column(db.String(80), nullable=False)
    score = db.Column(db.Integer, nullable=False)  # 1~10
    evaluate = db.Column(db.Text, nullable=False)