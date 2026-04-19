# 竞对动态监控 — GitHub Actions 自动推送飞书

每 5 分钟自动检测 Binance、Bitget、Bybit、MEXC/抹茶、KuCoin、WEEX、JuCoin 等交易所动态，
命中关键词立即推送飞书卡片消息，无需服务器，完全免费。

## 部署步骤（5分钟完成）

### 第一步：Fork 或上传到你自己的 GitHub 仓库

把这个文件夹上传到一个 **私有仓库**（推荐私有，防止 Webhook 泄露）。

### 第二步：配置飞书 Webhook Secret

1. 在飞书群里添加自定义机器人，复制 Webhook 地址
2. 打开 GitHub 仓库 → **Settings → Secrets and variables → Actions**
3. 点击 **New repository secret**
   - Name: `FEISHU_WEBHOOK_URL`
   - Value: 你的飞书 Webhook 地址（`https://open.feishu.cn/open-apis/bot/v2/hook/xxx`）

### 第三步：启用 GitHub Actions

1. 打开仓库的 **Actions** 标签页
2. 如果提示需要启用，点击 **Enable Actions**
3. 找到「竞对动态监控」workflow，点击 **Enable workflow**
4. 点击 **Run workflow** 手动触发一次，验证推送是否正常

之后每 5 分钟会自动运行，检测到新消息立即推送飞书。

## 文件结构

```
├── .github/
│   └── workflows/
│       └── monitor.yml     # GitHub Actions 定时任务配置
├── monitor.py              # 主程序
├── config.py               # 关键词配置（在这里增删交易所）
├── feishu.py               # 飞书卡片消息构建 & 发送
├── dedup.py                # 去重（seen_guids.json 存入仓库）
├── seen_guids.json         # 已推送记录，自动维护，不要手动编辑
└── requirements.txt
```

## 自定义关键词

编辑 `config.py` 里的 `EXCHANGE_KEYWORDS`：

```python
EXCHANGE_KEYWORDS = {
    "Binance": ["binance", "币安", "BNB"],
    "新交易所": ["关键词1", "关键词2"],   # 添加新竞对
}
```

修改后 push 到仓库，下次运行自动生效。

## 飞书消息分类颜色

| 分类 | 卡片颜色 |
|------|--------|
| 🪙 上新币种 | 蓝色 |
| 🎁 活动促销 | 绿色 |
| ⚡ 产品上线 | 青色 |
| 💰 费率变更 | 黄色 |
| ⚠️ 风险公告 | 红色 |
| 📢 行业动态 | 灰色 |

## 注意事项

- GitHub Actions 免费额度：每月 2000 分钟，每次运行约 30 秒，每天运行 288 次 ≈ 144 分钟/天，**完全够用**
- `seen_guids.json` 会被自动 commit 回仓库，用来跨次去重，不要手动修改
- 如果某次 Actions 运行失败，下次会重试，不会漏推
