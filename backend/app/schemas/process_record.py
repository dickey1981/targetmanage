"""
过程记录相关的Pydantic模式
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProcessRecordType(str, Enum):
    """过程记录类型枚举"""
    PROGRESS = "progress"        # 进度记录
    PROCESS = "process"          # 过程记录
    MILESTONE = "milestone"      # 里程碑
    DIFFICULTY = "difficulty"    # 困难
    METHOD = "method"           # 方法
    REFLECTION = "reflection"    # 反思
    ADJUSTMENT = "adjustment"    # 调整
    ACHIEVEMENT = "achievement"  # 成就
    INSIGHT = "insight"         # 洞察
    OTHER = "other"             # 其他


class ProcessRecordSource(str, Enum):
    """过程记录来源枚举"""
    VOICE = "voice"             # 语音输入
    MANUAL = "manual"           # 手动输入
    PHOTO = "photo"             # 拍照
    IMPORT = "import"           # 导入
    AUTO = "auto"               # 自动生成


class ProcessRecordBase(BaseModel):
    """过程记录基础模式"""
    title: Optional[str] = Field(None, max_length=200, description="记录标题")
    content: str = Field(..., description="记录内容")
    record_type: ProcessRecordType = Field(ProcessRecordType.PROCESS, description="记录类型")
    source: ProcessRecordSource = Field(ProcessRecordSource.MANUAL, description="记录来源")
    
    # 时间信息
    event_date: Optional[datetime] = Field(None, description="事件发生时间")
    
    # 情感和状态
    mood: Optional[str] = Field(None, description="心情状态")
    energy_level: Optional[int] = Field(None, ge=1, le=10, description="精力水平：1-10")
    difficulty_level: Optional[int] = Field(None, ge=1, le=10, description="困难程度：1-10")
    
    # 标签和分类
    tags: Optional[List[str]] = Field(None, description="标签列表")
    keywords: Optional[List[str]] = Field(None, description="关键词列表")
    
    # 重要程度
    is_important: bool = Field(False, description="是否重要")
    is_milestone: bool = Field(False, description="是否里程碑")
    is_breakthrough: bool = Field(False, description="是否突破")
    
    # 附加信息
    attachments: Optional[Dict[str, Any]] = Field(None, description="附件信息")
    location: Optional[str] = Field(None, max_length=200, description="记录地点")
    weather: Optional[str] = Field(None, max_length=50, description="天气情况")
    
    # 关联字段
    goal_id: Optional[str] = Field(None, description="目标ID")
    parent_record_id: Optional[int] = Field(None, description="父记录ID")


class ProcessRecordCreate(ProcessRecordBase):
    """创建过程记录模式"""
    pass


class ProcessRecordUpdate(BaseModel):
    """更新过程记录模式"""
    title: Optional[str] = Field(None, max_length=200, description="记录标题")
    content: Optional[str] = Field(None, description="记录内容")
    record_type: Optional[ProcessRecordType] = Field(None, description="记录类型")
    goal_id: Optional[str] = Field(None, description="关联目标ID")
    
    # 情感和状态
    mood: Optional[str] = Field(None, description="心情状态")
    energy_level: Optional[int] = Field(None, ge=1, le=10, description="精力水平：1-10")
    difficulty_level: Optional[int] = Field(None, ge=1, le=10, description="困难程度：1-10")
    
    # 标签和分类
    tags: Optional[List[str]] = Field(None, description="标签列表")
    keywords: Optional[List[str]] = Field(None, description="关键词列表")
    
    # 重要程度
    is_important: Optional[bool] = Field(None, description="是否重要")
    is_milestone: Optional[bool] = Field(None, description="是否里程碑")
    is_breakthrough: Optional[bool] = Field(None, description="是否突破")
    
    # 附加信息
    location: Optional[str] = Field(None, max_length=200, description="记录地点")
    weather: Optional[str] = Field(None, max_length=50, description="天气情况")


class ProcessRecordResponse(ProcessRecordBase):
    """过程记录响应模式"""
    id: int
    user_id: str
    recorded_at: datetime
    sentiment: Optional[str] = Field(None, description="情感分析")
    confidence_score: Optional[int] = Field(None, description="置信度分数")
    like_count: int = Field(0, description="点赞数")
    comment_count: int = Field(0, description="评论数")
    view_count: int = Field(0, description="查看数")
    created_at: datetime
    updated_at: datetime
    
    # 分析属性
    is_positive_sentiment: bool = Field(False, description="是否为积极情感")
    is_negative_sentiment: bool = Field(False, description="是否为消极情感")
    is_high_energy: bool = Field(False, description="是否为高精力状态")
    is_high_difficulty: bool = Field(False, description="是否为高难度")
    
    class Config:
        from_attributes = True


class ProcessRecordListResponse(BaseModel):
    """过程记录列表响应模式"""
    records: List[ProcessRecordResponse]
    total: int
    page: int
    page_size: int
    has_next: bool


class ProcessRecordTimelineResponse(BaseModel):
    """过程记录时间线响应模式"""
    date: str  # YYYY-MM-DD
    records: List[ProcessRecordResponse]
    milestone_count: int = 0
    breakthrough_count: int = 0


class ProcessRecordStatsResponse(BaseModel):
    """过程记录统计响应模式"""
    total_records: int
    records_by_type: Dict[str, int]
    records_by_mood: Dict[str, int]
    milestone_count: int
    breakthrough_count: int
    avg_energy_level: Optional[float] = None
    avg_difficulty_level: Optional[float] = None
    positive_sentiment_ratio: Optional[float] = None


class VoiceProcessRecordRequest(BaseModel):
    """语音过程记录请求模式"""
    voice_text: str = Field(..., description="语音转文字内容")
    goal_id: Optional[str] = Field(None, description="关联目标ID")
    event_date: Optional[datetime] = Field(None, description="事件发生时间")


class VoiceProcessRecordResponse(BaseModel):
    """语音过程记录响应模式"""
    success: bool
    message: str
    record: Optional[ProcessRecordResponse] = None
    analysis: Optional[Dict[str, Any]] = None
