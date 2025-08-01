```markdown
# 🎭 Asura Scan DL Bot

A Telegram bot that converts manga chapters from [AsuraScanz](https://asurascanz.com/) into clean, high-quality PDF files and sends them directly to your chat — with a thumbnail cover and proper formatting.

> ⚙️ Built and maintained by [MrAbhi2k3](https://github.com/MrAbhi2k3)  
> 🌟 If you find this project helpful, please [**star**](https://github.com/MrAbhi2k3/AsuraScanDLBot/stargazers) and [**fork**](https://github.com/MrAbhi2k3/AsuraScanDLBot/fork) the repository!

---

## 🧠 Features

- 📥 Download a **single chapter** or a **chapter range**
- 📚 Automatically compiles high-quality PDFs
- 🖼️ Adds a thumbnail cover image
- 🔗 Decodes and cleans image URLs (supports `imagemanga.online`)
- ⚡ Uses async and concurrent execution for faster downloads

---

## 🚀 Deployment

You can deploy this bot on **Heroku**, **Railway**, **Replit**, or any environment that supports Python 3.8+.

### 🔐 Environment Variables

| Variable     | Required | Description                                            |
|--------------|----------|--------------------------------------------------------|
| `API_ID`     | ✅       | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH`   | ✅       | Telegram API Hash from [my.telegram.org](https://my.telegram.org) |
| `BOT_TOKEN`  | ✅       | Token from [@BotFather](https://t.me/BotFather)         |

### 📦 Set them on Heroku:

```bash
heroku config:set API_ID=1234567
heroku config:set API_HASH=your_api_hash
heroku config:set BOT_TOKEN=your_bot_token
```

---

## 🐍 Local Setup

```bash
git clone https://github.com/MrAbhi2k3/AsuraScanDLBot.git
cd AsuraScanDLBot
pip install -r requirements.txt
export API_ID=your_id
export API_HASH=your_hash
export BOT_TOKEN=your_token
python bot.py
```

---

## 💬 How to Use

Once the bot is running, you can send it:

### ✅ Single Chapter:

```
https://asurascanz.com/solo-leveling-chapter-1/
```

### ✅ Range of Chapters:

```
https://asurascanz.com/solo-leveling-chapter-1/ 1 5
```

It will:
- Fetch all pages
- Create a PDF file
- Send it with a nice thumbnail and title

---

## 🖼️ Output Example

```
📚 Solo Leveling – Chapter 1

Shared via @AnimeZFlix
```

With a beautiful preview thumbnail and properly sorted pages.

---

## 📁 File Naming Format

```
[@AnimeZFlix] Chapter 1.pdf
```

---

## 👨‍💻 Developer

- GitHub: [MrAbhi2k3](https://github.com/MrAbhi2k3)
- Telegram: [@MrAbhi2k3](https://t.me/TeleroidGroup)

---

## ⭐ Contribute / Star / Fork

Help keep this project alive:

- 👉 [Star the repo ⭐](https://github.com/MrAbhi2k3/AsuraScanDLBot/stargazers)
- 👉 [Fork it 🍴](https://github.com/MrAbhi2k3/AsuraScanDLBot/fork)
- 💬 Submit issues and feature requests

---

## 📄 License

MIT License © 2025 [MrAbhi2k3](https://github.com/MrAbhi2k3)
```
