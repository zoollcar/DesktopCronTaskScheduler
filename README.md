❗ power by ChatGPT, include this README ❗

❗ It works well for me, so I’m sharing it ❗

---

# Cron Task Scheduler

## Description

Cron Task Scheduler is a lightweight Python desktop application that lets you define and execute scheduled tasks using standard 5-field cron expressions. You can specify commands and their working directories, view the next run time, and minimize the app to the system tray.

## Features

- Add multiple cron-based scheduled tasks
- Specify the command and the working directory for each task
- Display the next scheduled run time for debugging
- Save/load task configurations to/from a local JSON file
- System tray support with minimize and restore
- Example cron expressions included in the UI for reference
- Runs tasks in the background even when the UI is hidden

## Requirements

- Python 3.7+
- Packages listed in `requirements.txt`

Install dependencies:

```bash
pip install -r requirements.txt
```

## How to Use

1. Run `CronTaskScheduler.py`
2. Fill in:
   - Cron expression (e.g. `0 9 * * *` for daily at 9 AM)
   - Command (e.g. `run_script.bat`)
   - Folder (e.g. `C:/Users/You/Scripts`)
3. Click “Add Task” to define more
4. Click “Save Tasks” to save all
5. The app will execute matching tasks in the background
6. Close the window to minimize to tray
7. Right-click or left-click tray icon to restore

**Note**: This app uses 5-field cron syntax: `minute hour day month weekday` (no seconds).

## License

MIT License

---

# 桌面定时任务调度器

## 简介

定时任务调度器 是一个轻量级的 Python 桌面程序，允许你通过标准的 5 字段 Cron 表达式来设置并执行定时任务。你可以指定命令及其工作目录，查看下次运行时间，并将程序最小化到系统托盘。

## 功能特色

- 支持添加多个 Cron 定时任务
- 每个任务可指定执行命令和目录
- 支持显示下次执行时间，方便调试
- 任务配置保存在本地 JSON 文件中
- 支持最小化至系统托盘运行
- 界面底部提供可复制的 Cron 表达式示例
- 即使主界面关闭，任务也会在后台执行

## 环境需求

- Python 3.7 及以上版本
- 所需库请见 `requirements.txt`

安装依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行 `CronTaskScheduler.py`
2. 填写：
   - Cron 表达式（例如：`0 9 * * *` 表示每天上午9点）
   - 命令（例如：`run_script.bat`）
   - 工作目录（例如：`C:/Users/你/Scripts`）
3. 点击“Add Task”添加更多任务
4. 点击“Save Tasks”保存所有任务
5. 程序将在后台按时间自动执行任务
6. 关闭窗口将最小化到托盘
7. 点击或右键托盘图标可还原窗口

**注意**：本程序使用标准的 5 字段 Cron 表达式（不支持秒）：`分钟 小时 日 月 星期`

## 开源许可

MIT License