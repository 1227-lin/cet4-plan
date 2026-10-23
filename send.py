#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""四级每日提醒：在 GitHub Actions 上跑，每天把任务发到邮箱（或企业微信）。

环境变量：
  SMTP_USER   发件邮箱（QQ 邮箱地址）
  SMTP_AUTH   QQ 邮箱 SMTP 授权码（不是密码）
  MAIL_TO     收件邮箱，留空则发给 SMTP_USER
  WECOM_KEY   企业微信群机器人 key（填了就走企业微信，忽略 SMTP）
  FORCE_DATE  手动测试用：按指定日期生成，如 2026-10-23
用法：python3 send.py [--dry]
"""

import json
import os
import smtplib
import ssl
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from email.header import Header
from email.mime.text import MIMEText

TZ = timezone(timedelta(hours=8))
PLAN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan.json")


def load_plan():
    with open(PLAN_FILE, encoding="utf-8") as f:
        return json.load(f)


def pick_day(plan, date_str):
    for d in plan["days"]:
        if d["date"] == date_str:
            return d
    return None


def compose(plan, day, today):
    exam = datetime.strptime(plan["exam"], "%Y-%m-%d").replace(tzinfo=TZ)
    left = max(0, (exam.date() - today.date()).days)
    total = sum(t.get("min", 0) for t in day["tasks"])
    n = len(day["tasks"])

    lines = [
        "四级倒计时 %d 天" % left,
        "%s %s · %s" % (day["date"], day["wd"], day["phaseName"]),
    ]
    if n == 1:
        lines.append("今天 1 件事，约 %d 分钟：" % total)
    else:
        lines.append("今天 %d 件事，约 %d 分钟：" % (n, total))
    for i, t in enumerate(day["tasks"], 1):
        if t.get("min"):
            lines.append("%d) %s（%d 分钟）" % (i, t["label"], t["min"]))
        else:
            lines.append("%d) %s" % (i, t["label"]))
    if day.get("tip"):
        lines.append("")
        lines.append("提示：" + day["tip"])

    title = "四级 D-%d · %s · %d 件事" % (left, day["wd"], n)
    return title, "\n".join(lines)


def send_smtp(title, body):
    user = os.environ["SMTP_USER"].strip()
    auth = os.environ["SMTP_AUTH"].strip()
    to = (os.environ.get("MAIL_TO") or user).strip()

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header(title, "utf-8")
    msg["From"] = user
    msg["To"] = to

    ctx = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.qq.com", 465, timeout=25, context=ctx) as s:
            s.login(user, auth)
            s.sendmail(user, [to], msg.as_string())
        print("已发送（SMTP_SSL:465）->", to)
        return
    except Exception as e:
        print("465 失败：%s，改试 587 STARTTLS" % e)

    with smtplib.SMTP("smtp.qq.com", 587, timeout=25) as s:
        s.starttls(context=ctx)
        s.login(user, auth)
        s.sendmail(user, [to], msg.as_string())
    print("已发送（587 STARTTLS）->", to)


def send_wecom(body):
    key = os.environ["WECOM_KEY"].strip()
    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + key
    payload = json.dumps({"msgtype": "text", "text": {"content": body}}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=25) as r:
        data = json.loads(r.read().decode("utf-8"))
    if data.get("errcode") != 0:
        raise RuntimeError("企业微信返回错误：%s" % data)
    print("已发送（企业微信机器人）")


def main():
    dry = "--dry" in sys.argv
    plan = load_plan()

    force = (os.environ.get("FORCE_DATE") or "").strip()
    today = datetime.now(TZ)
    date_str = force or today.strftime("%Y-%m-%d")
    if force:
        today = datetime.strptime(force, "%Y-%m-%d").replace(tzinfo=TZ)

    day = pick_day(plan, date_str)
    if not day:
        if date_str > plan["exam"]:
            print("考试已过（%s），不再提醒。" % plan["exam"])
        else:
            print("今天（%s）不在计划区间内，跳过。" % date_str)
        return 0

    title, body = compose(plan, day, today)
    print("=" * 40)
    print(title)
    print("-" * 40)
    print(body)
    print("=" * 40)

    if dry:
        print("[dry-run] 不算发送")
        return 0

    if os.environ.get("WECOM_KEY", "").strip():
        send_wecom(body)
    elif os.environ.get("SMTP_USER", "").strip():
        send_smtp(title, body)
    else:
        print("没有配置 SMTP_USER 或 WECOM_KEY，跳过发送。")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
