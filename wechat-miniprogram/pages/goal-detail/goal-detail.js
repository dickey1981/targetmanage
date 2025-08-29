// pages/goal-detail/goal-detail.js
Page({
  data: {
    goalId: '',
    goalData: {},
    isEditing: false,
    categories: [
      { name: '学习', value: '学习' },
      { name: '工作', value: '工作' },
      { name: '健康', value: '健康' },
      { name: '财务', value: '财务' },
      { name: '人际关系', value: '人际关系' },
      { name: '个人发展', value: '个人发展' },
      { name: '兴趣爱好', value: '兴趣爱好' },
      { name: '其他', value: '其他' }
    ],
    categoryIndex: 0,
    progressPercentage: 0,
    statusClass: 'status-active',  // 新增：状态CSS类名
    remainingDaysClass: ''         // 新增：剩余天数CSS类名
  },

  onLoad(options) {
    if (options.id) {
      this.setData({
        goalId: options.id
      });
      this.loadGoalDetail();
    }
  },

  // 加载目标详情
  loadGoalDetail() {
    const app = getApp();
    const token = app.globalData.token;
    const baseUrl = app.globalData.baseUrl;
    
    console.log('调试信息:', {
      token: token ? '已设置' : '未设置',
      baseUrl: baseUrl,
      goalId: this.data.goalId
    });
    
    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      });
      return;
    }

    if (!baseUrl) {
      wx.showToast({
        title: 'API地址未配置',
        icon: 'none'
      });
      console.error('API基础URL未配置:', app.globalData);
      return;
    }

    wx.showLoading({
      title: '加载中...'
    });

    const apiUrl = `${baseUrl}/api/goals/${this.data.goalId}`;
    console.log('请求URL:', apiUrl);

    wx.request({
      url: apiUrl,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${token}`
      },
      success: (res) => {
        wx.hideLoading();
        console.log('API响应:', res);
        if (res.statusCode === 200) {
          const goalData = res.data;
          this.setData({
            goalData: goalData,
            categoryIndex: this.findCategoryIndex(goalData.category)
          });
          this.calculateProgress();
          this.updateStatusClass(); // 调用更新状态CSS类名的函数
        } else {
          wx.showToast({
            title: '加载失败',
            icon: 'none'
          });
        }
      },
      fail: (error) => {
        wx.hideLoading();
        console.error('加载目标详情失败:', error);
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
      }
    });
  },

  // 查找分类索引
  findCategoryIndex(category) {
    const index = this.data.categories.findIndex(item => item.value === category);
    return index >= 0 ? index : 0;
  },

  // 计算进度百分比
  calculateProgress() {
    const { targetValue, currentValue } = this.data.goalData;
    if (targetValue && currentValue) {
      const target = parseFloat(targetValue);
      const current = parseFloat(currentValue);
      if (target > 0) {
        const percentage = Math.min(Math.round((current / target) * 100), 100);
        this.setData({
          progressPercentage: percentage
        });
      }
    }
  },

  // 更新状态CSS类名
  updateStatusClass() {
    const { goalData } = this.data;
    let statusClass = 'status-active';
    let remainingDaysClass = '';

    // 根据状态设置CSS类名
    if (goalData.status) {
      switch (goalData.status) {
        case '进行中':
          statusClass = 'status-active';
          break;
        case '未开始':
          statusClass = 'status-pending';
          break;
        case '延期':
          statusClass = 'status-overdue';
          break;
        case '结束':
          statusClass = 'status-completed';
          break;
        default:
          statusClass = 'status-active';
      }
    }

    // 根据剩余天数设置CSS类名
    if (goalData.remaining_days !== undefined) {
      if (goalData.remaining_days <= 0) {
        remainingDaysClass = 'status-overdue-text';
      }
    }

    this.setData({
      statusClass,
      remainingDaysClass
    });
  },

  // 切换编辑模式
  toggleEditMode() {
    this.setData({
      isEditing: !this.data.isEditing
    });
  },

  // 标题输入
  onTitleChange(e) {
    this.setData({
      'goalData.title': e.detail.value
    });
  },

  // 分类选择
  onCategoryChange(e) {
    const index = e.detail.value;
    this.setData({
      categoryIndex: index,
      'goalData.category': this.data.categories[index].value
    });
  },

  // 描述输入
  onDescriptionChange(e) {
    this.setData({
      'goalData.description': e.detail.value
    });
  },

  // 开始时间选择
  onStartDateChange(e) {
    this.setData({
      'goalData.startDate': e.detail.value
    });
  },

  // 结束时间选择
  onEndDateChange(e) {
    this.setData({
      'goalData.endDate': e.detail.value
    });
  },

  // 目标值输入
  onTargetValueChange(e) {
    this.setData({
      'goalData.targetValue': e.detail.value
    });
  },

  // 当前值输入
  onCurrentValueChange(e) {
    this.setData({
      'goalData.currentValue': e.detail.value
    });
  },

  // 单位输入
  onUnitChange(e) {
    this.setData({
      'goalData.unit': e.detail.value
    });
  },

  // 优先级选择
  selectPriority(e) {
    const priority = e.currentTarget.dataset.priority;
    this.setData({
      'goalData.priority': priority
    });
  },

  // 每日提醒开关
  onDailyReminderChange(e) {
    this.setData({
      'goalData.dailyReminder': e.detail.value
    });
  },

  // 截止提醒开关
  onDeadlineReminderChange(e) {
    this.setData({
      'goalData.deadlineReminder': e.detail.value
    });
  },

  // 保存修改
  saveChanges() {
    const app = getApp();
    const token = app.globalData.token;
    const baseUrl = app.globalData.baseUrl;
    
    console.log('保存调试信息:', {
      token: token ? '已设置' : '未设置',
      baseUrl: baseUrl,
      goalId: this.data.goalId
    });
    
    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      });
      return;
    }

    if (!baseUrl) {
      wx.showToast({
        title: 'API地址未配置',
        icon: 'none'
      });
      console.error('API基础URL未配置:', app.globalData);
      return;
    }

    // 验证必填字段
    if (!this.data.goalData.title || !this.data.goalData.title.trim()) {
      wx.showToast({
        title: '请输入目标标题',
        icon: 'none'
      });
      return;
    }

    wx.showLoading({
      title: '保存中...'
    });

    // 准备要发送的数据
    const goalDataToSend = {
      title: this.data.goalData.title,
      category: this.data.goalData.category,
      description: this.data.goalData.description,
      startDate: this.data.goalData.startDate,
      endDate: this.data.goalData.endDate,
      targetValue: this.data.goalData.targetValue,
      currentValue: this.data.goalData.currentValue,
      unit: this.data.goalData.unit,
      priority: this.data.goalData.priority,
      dailyReminder: this.data.goalData.dailyReminder,
      deadlineReminder: this.data.goalData.deadlineReminder
    };

    const apiUrl = `${baseUrl}/api/goals/${this.data.goalId}`;
    console.log('保存请求URL:', apiUrl);
    console.log('保存数据:', goalDataToSend);

    wx.request({
      url: apiUrl,
      method: 'PUT',
      header: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      data: goalDataToSend,
      success: (res) => {
        wx.hideLoading();
        console.log('保存API响应:', res);
        if (res.statusCode === 200) {
          wx.showToast({
            title: '保存成功',
            icon: 'success'
          });
          
          // 更新本地数据
          this.setData({
            goalData: { ...this.data.goalData, ...goalDataToSend },
            isEditing: false
          });
          
          // 重新计算进度
          this.calculateProgress();
          this.updateStatusClass(); // 调用更新状态CSS类名的函数
          
          // 通知上一页刷新
          const pages = getCurrentPages();
          if (pages.length > 1) {
            const prevPage = pages[pages.length - 2];
            if (prevPage && prevPage.refreshGoals) {
              prevPage.refreshGoals();
            }
          }
        } else {
          wx.showToast({
            title: '保存失败',
            icon: 'none'
          });
        }
      },
      fail: (error) => {
        wx.hideLoading();
        console.error('保存目标失败:', error);
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
      }
    });
  },

  // 返回上一页
  goBack() {
    wx.navigateBack();
  }
});
