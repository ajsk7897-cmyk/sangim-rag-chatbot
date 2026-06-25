@echo off
title SangImBeob RAG Chatbot
echo ===================================================
echo   Starting SangImBeob RAG Chatbot...
echo   Please keep this window open while using the chatbot.
echo   To stop the chatbot, close this window.
echo ===================================================
echo.

cd /d "%~dp0"

start "" "http://localhost:8501"

streamlit run app.py --server.headless true --browser.gatherUsageStats false
