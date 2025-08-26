# Мультимодальный RAG с ColiVara и DeepSeek-Janus-Pro

В этом проекте реализован мультимодальный RAG с использованием новейшей модели DeepSeek Janus-Pro и ColiVara.

Мы используем следующие инструменты
- DeepSeek-Janus-Pro в качестве мультимодального LLM.
- [ColiVara](https://colivara.com/) для понимания и поиска документов SOTA.
- [Firecrawl](https://www.firecrawl.dev/i/api) для веб-парсинга.
- Streamlit в качестве веб-интерфейса.

## Демонстрация

Демонстрация проекта доступна ниже:

![demo](./video-demo.mp4)

---
## Настройка и установка

**Настройка Janus**:
```
git clone https://github.com/deepseek-ai/Janus.git
pip install -e ./Janus
```

**Получение ключей API**:
- [ColiVara](https://colivara.com/) для понимания и поиска документов SOTA.
- [Firecrawl](https://www.firecrawl.dev/i/api) для веб-парсинга.

Создайте файл .env и сохраните их следующим образом:
```python
COLIVARA_API_KEY="<COLIVARA-API-KEY>"
FIRECRAWL_API_KEY="<FIRECRAWL-API-KEY>"
```


**Установите зависимости**:
   Убедитесь, что у вас установлен Python 3.11 или более поздней версии.
```bash
   pip install streamlit-pdf-viewer colivara-py streamlit fastembed flash-attn transformers
   ```

---

## Запустите проект

Наконец, запустите проект, выполнив следующую команду:

```bash
streamlit run app.py
```
