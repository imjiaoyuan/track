# RSS Reader

一个简单的 RSS 阅读器，支持分类查看订阅源的最新文章。

## 功能特点

- 支持博客、资讯、论坛三个分类
- 响应式设计，支持移动端浏览
- 自动跟随系统的暗色模式
- 每小时自动更新文章
- 支持一键发起 GitHub Issue 进行评论
- 支持一键收藏文章到 GitHub Issue
- 博客和资讯分类显示最新 60 篇文章，分今日更新和历史文章
- 论坛分类显示所有最新文章

## 使用方法

1. Fork 本仓库
2. 修改 `feed.list` 文件，添加你想订阅的 RSS 源
3. 在仓库的 Settings -> Pages 中开启 GitHub Pages
4. 访问 `https://你的用户名.github.io/RSS` 即可阅读

## 添加订阅源

编辑 `feed.list` 文件，按分类添加 RSS 源的地址：

```
Blog:
https://example1.com/feed
https://example2.com/rss

Information:
https://news1.com/feed
https://news2.com/rss

Forums:
https://forum1.com/feed
https://forum2.com/rss
```

## 开发说明

- 使用 GitHub Actions 自动更新文章
- 文章数据保存在 `feed.json` 文件中
- 纯静态页面，无需后端服务
- 支持 PWA，可添加到主屏幕

## 自定义配置

- 修改 `static/style.css` 自定义界面样式
- 修改 `fetch_feeds.py` 自定义文章获取逻辑
- 修改 `index.html` 自定义页面结构和功能

## 许可证

MIT License