"""
过程记录模型
Process record model for goal management
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .base import BaseModel


class ProcessRecordType(enum.Enum):
    """过程记录类型枚举"""
    progress = "progress"        # 进度记录
    process = "process"          # 过程记录
    milestone = "milestone"      # 里程碑
    difficulty = "difficulty"    # 困难
    method = "method"           # 方法
    reflection = "reflection"    # 反思
    adjustment = "adjustment"    # 调整
    achievement = "achievement"  # 成就
    insight = "insight"         # 洞察
    other = "other"             # 其他


class ProcessRecordSource(enum.Enum):
    """过程记录来源枚举"""
    voice = "voice"             # 语音输入
    manual = "manual"           # 手动输入
    photo = "photo"             # 拍照
    import_ = "import"          # 导入
    auto = "auto"               # 自动生成


class ProcessRecord(BaseModel):
    """过程记录模型"""
    
    __tablename__ = "process_records"
    
    # 基本信息
    title = Column(String(200), nullable=True, comment="记录标题")
    content = Column(Text, nullable=False, comment="记录内容")
    record_type = Column(Enum(ProcessRecordType), default=ProcessRecordType.process, comment="记录类型")
    source = Column(Enum(ProcessRecordSource), default=ProcessRecordSource.manual, comment="记录来源")
    
    # 时间信息
    recorded_at = Column(DateTime, default=datetime.utcnow, comment="记录时间")
    event_date = Column(DateTime, nullable=True, comment="事件发生时间")
    
    # 情感和状态
    mood = Column(String(20), nullable=True, comment="心情状态：positive, neutral, negative")
    energy_level = Column(Integer, nullable=True, comment="精力水平：1-10")
    difficulty_level = Column(Integer, nullable=True, comment="困难程度：1-10")
    
    # 标签和分类
    tags = Column(JSON, nullable=True, comment="标签列表")
    keywords = Column(JSON, nullable=True, comment="关键词列表")
    sentiment = Column(String(20), nullable=True, comment="情感分析：positive, neutral, negative")
    
    # 重要程度
    is_important = Column(Boolean, default=False, comment="是否重要")
    is_milestone = Column(Boolean, default=False, comment="是否里程碑")
    is_breakthrough = Column(Boolean, default=False, comment="是否突破")
    
    # 附加信息
    attachments = Column(JSON, nullable=True, comment="附件信息")
    location = Column(String(200), nullable=True, comment="记录地点")
    weather = Column(String(50), nullable=True, comment="天气情况")
    
    # 数据来源详情
    source_data = Column(JSON, nullable=True, comment="源数据详情")
    confidence_score = Column(Integer, nullable=True, comment="置信度分数：0-100")
    
    # 关联字段
    user_id = Column(String(36), nullable=False, comment="用户ID")
    goal_id = Column(String(36), nullable=True, comment="目标ID")
    parent_record_id = Column(Integer, nullable=True, comment="父记录ID")
    
    # 统计字段
    like_count = Column(Integer, default=0, comment="点赞数")
    comment_count = Column(Integer, default=0, comment="评论数")
    view_count = Column(Integer, default=0, comment="查看数")
    
    def __repr__(self):
        return f"<ProcessRecord(id={self.id}, type='{self.record_type.value}', content='{self.content[:50]}...')>"
    
    @property
    def is_positive_sentiment(self) -> bool:
        """是否为积极情感"""
        return self.sentiment == "positive"
    
    @property
    def is_negative_sentiment(self) -> bool:
        """是否为消极情感"""
        return self.sentiment == "negative"
    
    @property
    def is_high_energy(self) -> bool:
        """是否为高精力状态"""
        return bool(self.energy_level and self.energy_level >= 7)
    
    @property
    def is_high_difficulty(self) -> bool:
        """是否为高难度"""
        return bool(self.difficulty_level and self.difficulty_level >= 7)
    
    def to_dict_with_analysis(self):
        """包含分析信息的字典"""
        data = self.to_dict()
        data.update({
            "is_positive_sentiment": self.is_positive_sentiment,
            "is_negative_sentiment": self.is_negative_sentiment,
            "is_high_energy": self.is_high_energy,
            "is_high_difficulty": self.is_high_difficulty
        })
        return data
