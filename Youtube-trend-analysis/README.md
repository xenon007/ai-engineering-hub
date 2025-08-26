# Анализ трендов YouTube с помощью CrewAI и BrightData

В этом проекте реализован анализ трендов YouTube с помощью CrewAI и BrightData.
- [Bright Data](https://brdta.com/dailydoseofds) используется для сбора видео с YouTube.
- CrewAI используется для анализа транскриптов видео и создания сводки.
- Streamlit используется для создания веб-интерфейса для проекта.


---
## Настройка и установка

**Получите ключ API BrightData**:
- Перейдите на сайт [Bright Data](https://brdta.com/dailydoseofds) и зарегистрируйте аккаунт.
- После создания аккаунта перейдите на страницу API Key и скопируйте свой ключ API.
- Вставьте ключ API, создав файл `.env` следующим образом:

```
BRIGHT_DATA_API_KEY=your_api_key
```

**Настройка Ollama**:
```bash
   # настройка ollama в Linux 
   curl -fsSL https://ollama.com/install.sh | sh
   # загрузка модели llama 3.2
   ollama pull llama3.2 
   ```


**Установка зависимостей**:
   Убедитесь, что у вас установлен Python 3.11 или более поздней версии.
```bash
   pip install streamlit ollama crewai crewai-tools
   ```

---

## Запуск проекта

Наконец, запустите проект, выполнив следующую команду:

```bash
streamlit run app.py
```
