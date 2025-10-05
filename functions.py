import streamlit as st
import os
import time
import random
from pathlib import Path
import wave
import pyaudio
from pydub import AudioSegment
from audiorecorder import audiorecorder
import numpy as np
from scipy.io.wavfile import write
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from langchain.memory import ConversationSummaryBufferMemory
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
import constants as ct

def record_audio(audio_input_file_path):
    """
    音声入力を受け取って音声ファイルを作成
    """

    audio = audiorecorder(
        start_prompt="発話開始",
        pause_prompt="やり直す",
        stop_prompt="発話終了",
        start_style={"color":"white", "background-color":"black"},
        pause_style={"color":"gray", "background-color":"white"},
        stop_style={"color":"white", "background-color":"black"}
    )

    if len(audio) > 0:
        audio.export(audio_input_file_path, format="wav")
    else:
        st.stop()

def transcribe_audio(audio_input_file_path):
    """
    音声入力ファイルから文字起こしテキストを取得
    Args:
        audio_input_file_path: 音声入力ファイルのパス
    """

    with open(audio_input_file_path, 'rb') as audio_input_file:
        transcript = st.session_state.openai_obj.audio.transcriptions.create(
            model="whisper-1",
            file=audio_input_file,
            language="en",
            temperature=0.0  # より確定的な結果のため
        )
    
    # 音声入力ファイルを削除
    os.remove(audio_input_file_path)

    return transcript

def save_to_wav(llm_response_audio, audio_output_file_path):
    """
    一旦mp3形式で音声ファイル作成後、wav形式に変換
    Args:
        llm_response_audio: LLMからの回答の音声データ
        audio_output_file_path: 出力先のファイルパス
    """

    temp_audio_output_filename = f"{ct.AUDIO_OUTPUT_DIR}/temp_audio_output_{int(time.time())}.mp3"
    with open(temp_audio_output_filename, "wb") as temp_audio_output_file:
        temp_audio_output_file.write(llm_response_audio)
    
    audio_mp3 = AudioSegment.from_file(temp_audio_output_filename, format="mp3")
    audio_mp3.export(audio_output_file_path, format="wav")

    # 音声出力用に一時的に作ったmp3ファイルを削除
    os.remove(temp_audio_output_filename)

def play_wav(audio_output_file_path, speed=1.0):
    """
    音声ファイルの読み上げ
    Args:
        audio_output_file_path: 音声ファイルのパス
        speed: 再生速度（1.0が通常速度、0.5で半分の速さ、2.0で倍速など）
    """

    # 音声ファイルの読み込み
    audio = AudioSegment.from_wav(audio_output_file_path)
    
    # 速度を変更
    if speed != 1.0:
        # frame_rateを変更することで速度を調整
        modified_audio = audio._spawn(
            audio.raw_data, 
            overrides={"frame_rate": int(audio.frame_rate * speed)}
        )
        # 元のframe_rateに戻すことで正常再生させる（ピッチを保持したまま速度だけ変更）
        modified_audio = modified_audio.set_frame_rate(audio.frame_rate)

        modified_audio.export(audio_output_file_path, format="wav")

    # PyAudioで再生
    with wave.open(audio_output_file_path, 'rb') as play_target_file:
        p = pyaudio.PyAudio()
        stream = p.open(
            format=p.get_format_from_width(play_target_file.getsampwidth()),
            channels=play_target_file.getnchannels(),
            rate=play_target_file.getframerate(),
            output=True
        )

        data = play_target_file.readframes(1024)
        while data:
            stream.write(data)
            data = play_target_file.readframes(1024)

        stream.stop_stream()
        stream.close()
        p.terminate()
    
    # LLMからの回答の音声ファイルを削除
    os.remove(audio_output_file_path)

def create_chain(system_template):
    """
    LLMによる回答生成用のChain作成（レベル別対応）
    """
    # レベル別のプロンプト調整
    if hasattr(st.session_state, 'englv'):
        level = st.session_state.englv
        if "{level}" in system_template:
            system_template = system_template.format(level=level)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_template),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    chain = ConversationChain(
        llm=st.session_state.llm,
        memory=st.session_state.memory,
        prompt=prompt
    )

    return chain

def create_problem_and_play_audio():
    """
    問題生成と音声ファイルの再生（レベル別対応）
    """
    # レベルに応じた単語数を決定
    level = st.session_state.englv
    word_limits = ct.WORD_LIMITS.get(level, {"min": 10, "max": 15})
    word_count = random.randint(word_limits["min"], word_limits["max"])
    
    # レベル別の問題生成プロンプトを準備
    problem_template = ct.SYSTEM_TEMPLATE_CREATE_PROBLEM.format(
        level=level, 
        word_count=word_count
    )
    
    # 問題生成用チェーンを作成（既存のものがあれば更新）
    if not hasattr(st.session_state, 'chain_create_problem') or st.session_state.current_level != level:
        st.session_state.chain_create_problem = create_chain(problem_template)
        st.session_state.current_level = level

    # 問題文を生成するChainを実行し、問題文を取得
    problem = st.session_state.chain_create_problem.predict(input="")

    # LLMからの回答を音声データに変換
    llm_response_audio = st.session_state.openai_obj.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=problem
    )

    # 音声ファイルの作成
    audio_output_file_path = f"{ct.AUDIO_OUTPUT_DIR}/audio_output_{int(time.time())}.wav"
    save_to_wav(llm_response_audio.content, audio_output_file_path)

    # 音声ファイルの読み上げ
    play_wav(audio_output_file_path, st.session_state.speed)

    return problem, llm_response_audio

def create_evaluation():
    """
    ユーザー入力値の評価生成（建設的フィードバック重視）
    """
    llm_response_evaluation = st.session_state.chain_evaluation.predict(input="")
    
    # 励ましメッセージを追加
    level = st.session_state.englv
    
    # 簡単なスコア計算（実際の評価をもとに改良可能）
    problem_words = st.session_state.problem.lower().split()
    user_words = st.session_state.get('last_user_input', '').lower().split()
    
    # 単語一致率の簡易計算
    matching_words = len(set(problem_words) & set(user_words))
    accuracy = matching_words / len(problem_words) if problem_words else 0
    
    # レベル別閾値で評価判定
    thresholds = ct.PROGRESS_THRESHOLDS[level]
    if accuracy * 100 >= thresholds["excellent"]:
        category = "excellent"
    elif accuracy * 100 >= thresholds["good"]:
        category = "good"
    else:
        category = "needs_improvement"
    
    # ランダムに励ましメッセージを選択
    encouragement = random.choice(ct.ENCOURAGEMENT_MESSAGES[category])
    
    # 評価結果に励ましメッセージを追加
    enhanced_evaluation = f"{llm_response_evaluation}\n\n{encouragement}"
    
    return enhanced_evaluation