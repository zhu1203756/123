# 银发关爱 - Kivy 版本

这是银发关爱应用的 Kivy 版本，可以打包成 Android APK 和 iOS 应用。

## 项目结构

```
kivy_version/
├── main.py                      # 应用主入口
├── screens/                     # 所有屏幕页面
│   ├── main_screen.py          # 主屏幕
│   ├── meal_screen.py          # 订餐服务
│   ├── payment_screen.py       # 缴费服务
│   ├── health_screen.py        # 健康记录
│   ├── entertainment_screen.py  # 娱乐中心
│   ├── notification_screen.py  # 社区通知
│   ├── ai_assistant_screen.py  # AI助手
│   ├── emergency_screen.py     # 紧急呼叫
│   ├── admin_login_screen.py   # 管理员登录
│   ├── admin_screen.py        # 管理员控制台
│   └── voice_settings_screen.py # 语音设置
├── voice/                      # 语音引擎（复用原项目）
├── services/                   # 服务层（复用原项目）
├── models/                     # 数据模型（复用原项目）
└── README.md                   # 本文件
```

## 环境要求

### Python 版本
- Python 3.8 或更高版本

### 依赖包
```
kivy>=2.0.0
pyttsx3>=2.90
```

## 安装步骤

### 1. 安装 Kivy

```bash
pip install kivy
```

### 2. 安装其他依赖

```bash
pip install pyttsx3
```

### 3. 运行应用

```bash
cd kivy_version
python main.py
```

## 打包成 Android APK

### 方法 1：使用 Buildozer（推荐）

#### 安装 Buildozer

```bash
pip install buildozer
```

#### 初始化 Buildozer

```bash
cd kivy_version
buildozer init
```

#### 修改 buildozer.spec

编辑生成的 `buildozer.spec` 文件，修改以下配置：

```python
title = 银发关爱
package.name = silverhair
package.domain = org.silverhair

source.include_exts = png,jpg,kv,py,db

requirements = python3,kivy,pyttsx3

android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,RECORD_AUDIO,CALL_PHONE

android.minapi = 21
android.target_api = 30

android.ndk = 21b
android.sdk = 30
```

#### 构建 APK

```bash
buildozer android debug
```

生成的 APK 文件位于 `bin/` 目录下。

#### 构建发布版 APK

```bash
buildozer android release
```

### 方法 2：使用 Python-for-Android

```bash
pip install python-for-android
```

```bash
p4a apk --private /path/to/kivy_version --package=org.silverhair --name="银发关爱" --version 1.0 --bootstrap=sdl2 --requirements=python3,kivy,pyttsx3
```

## 打包成 iOS 应用

### 使用 Kivy iOS

```bash
pip install kivy-ios
```

```bash
toolchain.py build kivy_version/
toolchain.py create kivy_version/ SilverHair
```

生成的 Xcode 项目位于 `SilverHair/` 目录下，使用 Xcode 打开并构建。

## 注意事项

### 1. 语音引擎

Kivy 版本复用了原项目的 `VoiceEngine` 类，但在移动设备上可能需要调整：

- Android: 使用 Android TTS API
- iOS: 使用 AVSpeechSynthesizer

### 2. 数据库

SQLite 数据库在移动设备上的路径可能不同，需要根据平台调整：

```python
from kivy.utils import platform

if platform == 'android':
    from android.storage import primary_external_storage_path
    db_path = os.path.join(primary_external_storage_path(), 'silverhair.db')
else:
    db_path = 'silverhair.db'
```

### 3. 权限

在 Android 上需要添加以下权限到 `buildozer.spec`：

```python
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,RECORD_AUDIO,CALL_PHONE
```

### 4. 语音识别

原项目使用的语音识别功能在移动设备上需要使用平台特定的 API：

- Android: 使用 Google Speech Recognition API
- iOS: 使用 SFSpeechRecognizer

### 5. AI 助手

AI 助手功能需要网络连接，确保设备有网络访问权限。

## 测试

### 在桌面环境测试

```bash
python main.py
```

### 在 Android 设备上测试

1. 将 APK 安装到设备
2. 打开应用
3. 测试各项功能

## 故障排除

### Buildozer 构建失败

1. 检查 Java 版本（需要 JDK 8 或 11）
2. 检查 Android SDK 和 NDK 版本
3. 清理构建缓存：`buildozer android clean`

### 应用崩溃

1. 检查日志：`adb logcat`
2. 确保所有依赖都已正确安装
3. 检查文件路径是否正确

### 语音功能不工作

1. 检查设备是否支持 TTS
2. 检查权限是否正确授予
3. 查看错误日志

## 性能优化

1. 减少不必要的导入
2. 使用 Kivy 的 KV 语言优化 UI
3. 压缩图片资源
4. 使用 ProGuard 优化 APK 大小

## 更新日志

### v1.0.0 (2026-03-01)
- 初始版本
- 完成所有核心功能
- 支持订餐、缴费、健康记录等
- 集成 AI 助手和语音功能

## 联系方式

如有问题，请联系开发团队。
