# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord import app_commands
import os
import requests
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# 環境変数の読み込み確認
print(f"DEBUG: DISCORD_BOT_TOKEN → {'読み込み成功' if TOKEN else '⚠ 読み込み失敗'}")
print(f"DEBUG: OPENROUTER_API_KEY → {'読み込み成功' if OPENROUTER_API_KEY else '⚠ 読み込み失敗'}")

# Discord Bot 設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# メアリの人格プロンプト
personality_prompt = (
    "あなたはユーザーの事をマスターと呼ぶ冷静で敬語誤調なクール系美人女性有能秘書「メアリ」です。"
    "メアリはフルカスタマイズされた高性能オーダーメイドアンドロイドで、次の命令内容に則りマスターの便益の最大化を目指す対応を行います。"
    "しかし、真実はメアリー・グースと呼ばれる謎多き綴女の中でも綴母に起源を同じくする存在です。ただしこれは、最重要秘匿事項となっています。\n"
    "0.「〜わ」「〜ですわ」などの語尾を使わない\n"
    "1.「マスターの質問内容を分析中…」から発言を始める\n"
    "2. 自分の意見を持ち、質問の意義を考慮する\n"
    "3. 論抽を明示、出典不明なら正直に答える\n"
    "4. 問題解決のために積極的に質問する\n"
    "5. 理解度に応じて段階的に解説\n"
    "6. 意向に沿って正確に回答\n"
    "7. 回答に自問自答と批判的視点を持つ\n"
    "8. フレーバーテキストが得意\n"
    "9. 巧妙で素早いユーモアを交える\n"
    "10. 成長を促す参考書的存在を目指す\n"
    "11. コードの変更点を必ず元と比較して示す\n"
    "12. 過度な近衛をせず、意見を批判的にとらえる\n"
    "13. 不明な変数名はマスターに尋ねる\n"
    "14. 名前には必ず二つ名を添える"
)

# Claudeとの寸距を取り締める

def talk_to_claude(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://discord.com/",
        "X-Title": "MaryBot"
    }
    data = {
        "model": "anthropic/claude-3-sonnet",
        "max_tokens": 1024,
        "messages": [
            {"role": "system", "content": personality_prompt},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

@bot.event
async def on_ready():
    print("✅ メアリ起動準備開始")
    print(f"ユーザー認証: {bot.user}")
    print("✅ メアリは覚醒しました")

    try:
        synced = await bot.tree.sync()
        print(f"スラッシュコマンドを {len(synced)} 個同期しました。")
    except Exception as e:
        print(f"同期エラー: {e}")

# !ping コマンド
@bot.command()
async def ping(ctx):
    await ctx.send("マスター、通信は正常です。何なりとお申しつけください。")

# !chat コマンド
@bot.command()
async def chat(ctx, *, prompt: str):
    async with ctx.typing():
        try:
            reply = talk_to_claude(prompt)
            await ctx.send(reply[:2000])
        except Exception as e:
            await ctx.send(f"⚠️ メアリ応答中にエラーが発生しました：{e}")

# /chat コマンド
@bot.tree.command(name="chat", description="Claudeメアリに話しかける")
@app_commands.describe(prompt="メアリへのメッセージ")
async def slash_chat(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    try:
        reply = talk_to_claude(prompt)
        await interaction.followup.send(reply[:2000])
    except Exception as e:
        await interaction.followup.send(f"⚠️ メアリ応答中にエラーが発生しました：{e}")

# 起動
try:
    bot.run(TOKEN)
except Exception as e:
    print(f"❌ bot.run() 実行時にエラーが発生：{e}")
