# 物联网接口集成指南

## 目录
1. [概述](#概述)
2. [基本步骤](#基本步骤)
3. [详细流程](#详细流程)
4. [最佳实践](#最佳实践)
5. [示例](#示例)

## 概述
本文档详细说明了如何在系统中添加新的物联网(IoT)接口。通过遵循这些步骤，可以确保新的IoT设备能够顺利集成到现有系统中。

## 基本步骤
1. 创建新的Thing类
2. 实现必要的接口方法
3. 注册设备到系统
4. 添加命令处理
5. 测试集成

## 详细流程

### 1. 创建新的Thing类
- 在 `src/things` 目录下创建新的Python文件
- 继承基础的 `Thing` 类
- 实现必要的初始化方法

示例：
```python
from .thing import Thing

class NewThing(Thing):
    def __init__(self, thing_id: str):
        super().__init__(thing_id)
        self.name = "NewThing"
        self.description = "这是一个新的IoT设备"
```

### 2. 实现必要的接口方法
每个Thing类需要实现以下基本方法：
- `initialize()`: 设备初始化
- `process_command()`: 处理接收到的命令
- `get_status()`: 获取设备状态
- 其他特定功能方法

示例：
```python
def initialize(self) -> bool:
    # 初始化设备
    return True

def process_command(self, command: str, params: dict) -> dict:
    # 处理命令
    return {"status": "success"}

def get_status(self) -> dict:
    # 返回设备状态
    return {"status": "online"}
```

### 3. 注册设备到系统
在 `src/application.py` 的 `_initialize_iot_devices` 方法中注册新设备：

```python
def _initialize_iot_devices(self):
    # 添加新设备实例
    new_thing = NewThing("new_thing_001")
    self.thing_manager.add_thing(new_thing)
```

### 4. 添加命令处理
实现设备特定的命令处理逻辑：
```python
def process_command(self, command: str, params: dict) -> dict:
    if command == "自定义命令":
        return self._handle_custom_command(params)
    return {"status": "error", "message": "未知命令"}
```

### 5. 测试集成
- 单元测试：创建设备的测试用例
- 集成测试：测试与系统的交互
- 功能测试：验证所有命令和功能

## 最佳实践

1. 错误处理
- 实现完善的错误处理机制
- 提供清晰的错误信息
- 记录关键操作日志

2. 代码规范
- 遵循PEP 8编码规范
- 添加详细的代码注释
- 使用类型提示

3. 文档
- 编写API文档
- 提供使用示例
- 记录重要的配置参数

4. 安全性
- 实现必要的安全检查
- 保护敏感数据
- 限制访问权限

## 示例

### 提醒功能集成示例

以下是添加提醒功能的示例代码：

```python
from .thing import Thing
from datetime import datetime

class ReminderThing(Thing):
    def __init__(self, thing_id: str):
        super().__init__(thing_id)
        self.name = "ReminderThing"
        self.description = "提醒功能管理器"
        self.reminders = {}

    def set_reminder(self, time: datetime, message: str) -> dict:
        reminder_id = str(len(self.reminders) + 1)
        self.reminders[reminder_id] = {
            "time": time,
            "message": message,
            "status": "active"
        }
        return {
            "status": "success",
            "message": f"提醒已设置: {message}"
        }

    def process_command(self, command: str, params: dict) -> dict:
        if command == "set":
            return self.set_reminder(params["time"], params["message"])
        elif command == "list":
            return {"reminders": self.reminders}
        return {"status": "error", "message": "未知命令"}
```

## 注意事项

1. 初始化顺序
- 确保设备初始化在系统启动时完成
- 处理初始化失败的情况

2. 资源管理
- 正确管理设备资源
- 实现清理方法

3. 兼容性
- 确保与现有系统兼容
- 考虑版本升级的影响

4. 性能
- 优化处理逻辑
- 避免资源浪费

## 常见问题

1. 设备注册失败
- 检查设备ID是否唯一
- 验证初始化参数

2. 命令处理错误
- 确认命令格式正确
- 检查参数完整性

3. 状态更新问题
- 验证状态更新逻辑
- 检查数据一致性 