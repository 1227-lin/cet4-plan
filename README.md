# 四级计划 · 一个仓库，两件事

1. **每天 19:30 微信提醒**（GitHub Actions，在云端跑，你的电脑不用开机）
2. **计划表网页 + 永久网址**（GitHub Pages，可以加到 iPad 主屏幕，装好后断网也能用）

---

## 一、建仓库

1. 打开 https://github.com/new
2. 名字随便，比如 `cet4-plan`
3. **必须选 Public**（私有仓库开 Pages 要付费）
4. 不要勾 README / .gitignore / license
5. Create repository

## 二、上传文件

在空仓库页面点 **uploading an existing file**，把这些**全部**拖进去，然后 Commit：

```
.github/workflows/daily.yml
send.py
plan.json
README.md
index.html
manifest.json
sw.js
icon-180.png
icon-192.png
icon-512.png
```

> `.github` 拖不进去就用 **Add file → Create new file**，文件名输 `.github/workflows/daily.yml`（斜杠会自动建目录），把内容粘进去。

## 三、开 Pages，拿永久网址

1. 仓库 **Settings** → 左侧 **Pages**
2. **Source** 选 `Deploy from a branch`
3. Branch 选 `main`，目录选 `/ (root)`
4. **Save**
5. 等 1–3 分钟，刷新页面，顶部会出现网址：

```
https://你的用户名.github.io/cet4-plan/
```

**iPad 上：** Safari 打开这个网址 → 分享 → **添加到主屏幕**。
装好后从主屏图标打开一次（让离线缓存生效），之后断网、甚至删掉仓库都不影响本机使用。

## 四、准备发信凭据（只给提醒用）

1. 电脑打开 **mail.qq.com** → 设置 → 账户
2. 「POP3/IMAP/SMTP 服务」→ **开启 SMTP** → 发短信验证 → 拿到 16 位**授权码**
3. 微信搜索并关注 **「QQ邮箱提醒」**

## 五、填 Secrets

仓库 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**：

| Name | Value |
|---|---|
| `SMTP_USER` | 你的 QQ 邮箱，如 `123456789@qq.com` |
| `SMTP_AUTH` | 16 位授权码 |
| `MAIL_TO` | 可选，不填就发给 `SMTP_USER` |

> 想改用企业微信收：再加 `WECOM_KEY`（群机器人 key），填了就走企业微信，忽略邮箱。

## 六、立刻测试提醒

1. 仓库 → **Actions** 标签
2. 若提示未启用，点 **I understand my workflows, go ahead and enable them**
3. 左侧选 **四级每日提醒** → **Run workflow**
4. `force_date` 填 `2026-10-23`（或留空=当天）→ **Run workflow**
5. 20 秒后看日志，出现 `已发送（SMTP_SSL:465）-> xxx@qq.com` 即成功

---

## 说明

- **时间**：GitHub cron 用 UTC，`30 11 * * *` = 北京时间 19:30。实际会有几分钟浮动。
- **改发送时间**：改 `.github/workflows/daily.yml` 的 cron，换算：`北京时间 − 8 小时`。
- **改任务内容**：`plan.json` 是提醒的数据源，但 `index.html` 里的计划是**生成时内嵌**的，改 `plan.json` 不会自动更新网页。要改任务，跟我说一声，我重新生成 `index.html` 再给你。
- **免费额度**：这个任务每天约 20 秒；Pages 对公开仓库免费。
- **定时任务被暂停**：仓库连续 60 天无提交，GitHub 会暂停 schedule。本计划到 12/19，够用；想保险就 11 月中旬改一下 README 提交一次。
- **安全**：授权码只存在 Secrets，不会进代码和日志，随时可在 QQ 邮箱作废重发。
