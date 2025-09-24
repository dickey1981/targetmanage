from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import datetime

# 目标数据模型
class GoalItem(BaseModel):
    id: str
    title: str
    category: str
    progress: int
    status: str  # 目标状态
    remaining_days: int  # 剩余天数
    startDate: Optional[str] = None  # 开始日期
    endDate: Optional[str] = None    # 结束日期
    created_at: Optional[str] = None

# 创建目标请求模型
class GoalCreate(BaseModel):
    title: str
    category: str
    description: str
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    targetValue: Optional[str] = None
    currentValue: Optional[str] = None
    unit: Optional[str] = None
    priority: Optional[str] = "medium"
    dailyReminder: Optional[bool] = True
    deadlineReminder: Optional[bool] = True

# 更新目标请求模型
class GoalUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    targetValue: Optional[str] = None
    currentValue: Optional[str] = None
    unit: Optional[str] = None
    priority: Optional[str] = None
    dailyReminder: Optional[bool] = None
    deadlineReminder: Optional[bool] = None

# 响应模型
class GoalResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Union[dict, List[GoalItem]]] = None

# 语音目标创建相关模型
class VoiceGoalCreate(BaseModel):
    voice_text: str

class VoiceGoalParseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    validation: Optional[dict] = None
    parsing_hints: Optional[dict] = None  # 添加解析提示信息

class VoiceRecognitionResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
