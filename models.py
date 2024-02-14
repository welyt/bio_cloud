from flask import url_for
from app import db
import datetime
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re


user2project = db.Table(
    'user2project',
    db.Column('user_id', db.String(128), db.ForeignKey('user.id')),
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'))
    is_book = db.Column(db.bool, default=0)  # 收藏按钮
    # share = db.Column(db.Integer, default=0)  # 分享按钮
    permission  = db.Column(db.String(128))  # 枚举类型
    # download = db.Column(db.Integer, default=0)  # 下载按钮
    # delete = db.Column(db.Integer, default=0)  # 删除按钮
    # edit = db.Column(db.Integer, default=0)  # 编辑/查看按钮
)  # 用户和项目的关系


class Project(db.Model):  # 我的项目
    __tablename__ = "project"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    species = db.Column(db.String(128))
    sample_number = db.Column(db.Integer)
    path = db.Column(db.String(1024), nullable=False)  # 文件夹路径,用于解析结果和下载结果
    create_time = db.Column(
        db.DateTime(), default=datetime.now, nullable=False)
    update_time = db.Column(
        db.DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False)
    pipeline_id = db.Column(
        db.String(128), db.ForeignKey("Pipeline.id"), nullable=False
    )   # 一个项目对应一个pipeline
    tasks = db.relationship(
        "Task", backref="project", lazy="dynamic")  # 一个项目对应多个任务
    users = db.relationship(
        'User', secondary=user2project,  # 多对多，一个项目对应多个用户
        backref=db.backref('users', lazy="dynamic"), lazy="dynamic")

    def __repr__(self):
        return f"<Project {self.name}>"

    # 项目 UI json
    def ui_json(self, which):
        # which = ["all", "summary", "qc", 'pipeline']
        pass

    # 合并相同类型的两个项目
    def merge_project(self):
        pass


class Task(db.Model):  # 我的任务
    __tablename__ = "task"
    id = db.Column(db.Integer, primary_key=True)
    rules = db.Column(db.String(512), nullable=False, default=None)
    path = db.Column(db.String(512), nullable=False, default="./")
    status = db.Column(db.String(128), default="分析中")  # 改为枚举类型
    start = db.Column(db.DateTime)  # 开始时间
    end = db.Column(db.DateTime)  # 结束时间
    # 改成bool 值
    is_booked = db.Column(db.Integer, default=0)  # 收藏按钮
    is_deleted = db.Column(db.Integer, default=0)  # 删除按钮
    edit = db.Column(db.Integer, default=0)
    user_id = db.Column(  # 一个任务对应一个用户, 一个用户对应多个任务
        db.String(128), db.ForeignKey("user.id"), nullable=False)
    project_id = db.Column(  # 一个任务对应一个项目，一个项目对应多个任务
        db.Integer, db.ForeignKey("project.id"), nullable=False)
    create_time = db.Column(
        db.DateTime(), default=datetime.now, nullable=False)
    update_time = db.Column(
        db.DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return f"<Project {self.snakefile}>"

    def gen_path(self):  # 生成分析路径
        pass

    def task_status(self):  # 更新任务状态
        pass

    def ui_json(self, which):  # 任务 UI json
        # which = ["", "body", "qc", 'tool', 'pipeline']
        pass

    def gen_report(self):  # 生成报告, 用于下载
        pass


class Tool(db.Model):  # 工具配置
    __tablename__ = "tool"
    id = db.Column(db.String(128), primary_key=True)
    name = db.Column(db.String(128))
    category = db.Column(db.String(128))
    version = db.Column(db.String(128))
    version_note = db.Column(db.String(1024))
    description = db.Column(db.String(1024))
    user_id = db.Column(db.String(128)) # 上传人的用户ID
    configure = db.Column(db.String(512))  # 工具配置文件
    status = db.Column(db.String(128), default="测试")  # 测试/上线/下线/删除
    function_id = db.Column(
        db.String(128), db.ForeignKey("toolset.id"), nullable=False)
    create_time = db.Column(
        db.DateTime(), default=datetime.now, nullable=False)
    update_time = db.Column(
        db.DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return f"<Project {self.configure}>"

    def add_tool(self):  # 新增工具按钮
        pass

    def gen_rule(self):  # 生成snakemake rule
        pass

    def ui_json(self):  # 工具 UI配置json, 分析页面布局
        pass


class Function(db.Model):
    __tablename__ = "function"
    id = db.Column(db.String(128), primary_key=True)
    name = db.Column(db.String(128))
    version = db.Column(db.String(128))
    version_note = db.Column(db.String(1024))
    description = db.Column(db.String(1024))
    user_id = db.Column(db.String(128))
    configure = db.Column(db.String(512))  # 分析模块配置文件
    status = db.Column(db.String(128), default="测试")  # 测试/上线/下线/删除
    pipeline_id = db.Column(
        db.String(128), db.ForeignKey("Pipeline.id"), nullable=False
    )
    create_time = db.Column(
        db.DateTime(), default=datetime.now, nullable=False)
    update_time = db.Column(
        db.DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False)
    tools = db.relationship(  # 一个模块对应多个工具
        "Tool", backref="function", lazy="dynamic")

    def __repr__(self):
        return f"<Project {self.configure}>"

    def add_function(self):  # 新增功能按钮
        pass

    def ui_json(self):  # 模块 结果和UI配置json
        pass


class Pipeline(db.Model):
    __tablename__ = "pipeline"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    version = db.Column(db.String(128))
    version_note = db.Column(db.String(1024))
    description = db.Column(db.String(1024))
    user_id = db.Column(db.String(128))
    configure = db.Column(db.String(512))  # 分析模块配置文件
    status = db.Column(db.String(128), default="测试")  # 测试/上线/下线/删除
    create_time = db.Column(
        db.DateTime(), default=datetime.now, nullable=False)
    update_time = db.Column(
        db.DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False)
    functions = db.relationship(  # 一个流程对应多个功能
        "Function", backref="pipeline", lazy="dynamic")

    def __repr__(self):
        return f"<Project {self.configure}>"

    def add_pipeline(self):
        pass

    def gen_snakefile(self):  # 生成snakemake file
        pass

    def ui_json(self):  # 流程 UI配置json
        pass


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128))
    phone = db.Column(db.String(128))
    organization = db.Column(db.String(128))
    comment = db.Column(db.String(128))  # 备注
    create_time = db.Column(
        db.DateTime(), default=datetime.now, nullable=False)
    update_time = db.Column(
        db.DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False)
    tasks = db.relationship(
        "Task", backref="user", lazy="dynamic")  # 一个用户对应多个任务

    def __repr__(self):
        return f"<User {self.name}>"

    def user_project(self):  # 用户项目列表 & 添加ProjectSearch条目
        pass

    def user_task(self):  # 用户任务列表 & 添加TaskSearch条目
        pass


class ProjectSearch(db.Model):  # 项目搜索
    __tablename__ = "task_search"
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(128))
    project_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    create_time = db.Column(
        db.DateTime(), default=datetime.now, nullable=False)
    update_time = db.Column(
        db.DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return f"<Task {self.keyword}>"


class TaskSearch(db.Model):  # 任务搜索
    __tablename__ = "task_search"
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(128))
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    create_time = db.Column(
        db.DateTime(), default=datetime.now, nullable=False)
    update_time = db.Column(
        db.DateTime(), default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        return f"<Task {self.keyword}>"
