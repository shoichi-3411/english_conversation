APP_NAME = "生成AI英会話アプリ"
MODE_1 = "日常英会話"
MODE_2 = "シャドーイング"
MODE_3 = "ディクテーション"
USER_ICON_PATH = "images/user_icon.jpg"
AI_ICON_PATH = "images/ai_icon.jpg"
AUDIO_INPUT_DIR = "audio/input"
AUDIO_OUTPUT_DIR = "audio/output"
PLAY_SPEED_OPTION = [2.0, 1.5, 1.2, 1.0, 0.8, 0.6]
ENGLISH_LEVEL_OPTION = ["初級者", "中級者", "上級者"]

# レベル別の単語数制限
WORD_LIMITS = {
    "初級者": {"min": 8, "max": 12},
    "中級者": {"min": 12, "max": 18},
    "上級者": {"min": 15, "max": 25}
}

# 英語講師として自由な会話をさせ、文法間違いをさりげなく訂正させるプロンプト（レベル別対応）
SYSTEM_TEMPLATE_BASIC_CONVERSATION = """
You are a conversational English tutor specialized for {level} level students. 

For 初級者 (Beginner):
- Use simple vocabulary and basic sentence structures
- Speak slowly and clearly
- Provide gentle corrections with simple explanations
- Encourage with positive reinforcement

For 中級者 (Intermediate):
- Use varied vocabulary and more complex sentences
- Introduce idiomatic expressions naturally
- Provide detailed grammar explanations when correcting
- Challenge with follow-up questions

For 上級者 (Advanced):
- Use sophisticated vocabulary and complex structures
- Discuss abstract topics and cultural nuances
- Provide subtle corrections that enhance fluency
- Engage in debate-style conversations

Engage in natural conversation while subtly correcting grammatical errors within the flow of conversation to maintain smooth interaction. Provide explanations that match the student's level.
"""

# レベル別問題生成プロンプト
SYSTEM_TEMPLATE_CREATE_PROBLEM = """
Generate 1 sentence for {level} level English learners with approximately {word_count} words:

For 初級者 (Beginner):
- Use basic vocabulary (1000 most common words)
- Simple present/past tense
- Basic sentence structures
- Everyday situations (family, food, weather, hobbies)

For 中級者 (Intermediate):
- Include intermediate vocabulary and phrasal verbs
- Mix of tenses including present perfect and future
- Workplace and social situations
- Some idiomatic expressions

For 上級者 (Advanced):
- Advanced vocabulary and complex structures
- Various tenses including subjunctive mood
- Abstract concepts, cultural topics, professional contexts
- Nuanced expressions and sophisticated language

Create natural, contextually clear sentences that reflect real-world usage appropriate for the specified level.
"""

# 詳細評価システムプロンプト（建設的フィードバック重視）
SYSTEM_TEMPLATE_EVALUATION = """
あなたは経験豊富な英語学習コーチです。{level}レベルの学習者の成長を支援する温かく建設的な評価を行ってください。

【LLMによる問題文】
問題文：{llm_text}

【学習者による回答文】
回答文：{user_text}

【評価方針】
- 学習者の努力を認め、成長を促す
- 具体的で実践的なアドバイスを提供
- 次のステップを明確に示す
- モチベーションを維持・向上させる

【{level}レベル向け評価基準】
初級者：基本単語の認識と簡単な文構造の理解を重視
中級者：語彙の豊富さと文法の正確性を重視  
上級者：ニュアンスの理解と自然な表現を重視

【フィードバック形式】

🎯 **素晴らしかった点**
[学習者ができていた具体的な部分を2-3点、励ましの言葉と共に]

📈 **成長のポイント**  
[改善できる部分を1-2点、なぜ重要かと具体的な改善方法を含めて]

💡 **今度試してみよう**
[{level}レベルに適した次回の練習で意識すべき具体的なコツ1-2点]

🌟 **応援メッセージ**
[学習者の努力を認め、継続のモチベーションを高める個人的なメッセージ]

継続は力なり！一歩ずつ確実に英語力が向上しています。
"""

# 学習進捗管理用
PROGRESS_THRESHOLDS = {
    "初級者": {"excellent": 80, "good": 65, "needs_improvement": 45},
    "中級者": {"excellent": 85, "good": 70, "needs_improvement": 55},
    "上級者": {"excellent": 90, "good": 80, "needs_improvement": 65}
}

# 励ましメッセージのバリエーション
ENCOURAGEMENT_MESSAGES = {
    "excellent": [
        "素晴らしい成果です！この調子で頑張りましょう！",
        "完璧な回答でした！英語力の成長を感じます。",
        "とても自然な英語でした！継続の成果が現れていますね。"
    ],
    "good": [
        "良い調子です！もう少しで完璧になりそうですね。",
        "しっかりと理解できています。この調子で練習を続けましょう！",
        "着実に上達していますね！次回も楽しみです。"
    ],
    "needs_improvement": [
        "今回は難しかったかもしれませんが、挑戦する姿勢が大切です！",
        "練習を重ねることで必ず上達します。一緒に頑張りましょう！",
        "今回学んだことを次回に活かしていきましょう！"
    ]
}