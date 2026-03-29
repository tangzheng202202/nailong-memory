# HEARTBEAT.md - 定期任务

```markdown
# 任务1: 每日备份检查
## 触发条件
- 每天 21:00 (Asia/Shanghai)

## 执行内容
1. 运行 backup.sh 并记录结果
2. 检查 git 远程仓库连接状态
3. 如果备份失败，输出警告信息

## 命令
~/.openclaw/workspace-smart/backup.sh

# 任务2: Memory 索引健康检查
## 触发条件
- 每周一 09:00

## 执行内容
1. 检查 memory 索引状态
2. 重建 dirty 的索引
3. 清理过期缓存

# 任务3: 知识库更新检查
## 触发条件
- 每天 20:00

## 执行内容
1. 检查 知识库/待整理 目录是否有新文件
2. 整理新文件到对应分类
3. 更新 知识管理配置.md
```

## 当前配置状态

| 项目 | 状态 | 说明 |
|------|------|------|
| git remote | ❌ 未配置 | 需要添加远程仓库 |
| backup.sh | ✅ 已创建 | 路径: ~/.openclaw/workspace-smart/backup.sh |
| HEARTBEAT | ✅ 已更新 | 包含3个定期任务 |
| cron 任务 | ✅ 已配置 | 每日20:00/22:00, 周日21:00 |

## 下一步
配置 git remote 后，backup.sh 将自动推送到远程仓库。