# Генератор резюме мультиагентного рабочего процесса с ACP

Простая демонстрация протокола связи агентов (ACP), показывающая, как два агента, построенные с использованием разных фреймворков (CrewAI и Smolagents), могут беспрепятственно сотрудничать для генерации и проверки резюме исследования.

---

## Настройка и установка

1. **Установите Ollama:**
```bash
# Настройка Ollama в Linux
curl -fsSL https://ollama.com/install.sh | sh

# Загрузите модель Qwen2.5
ollama pull qwen2.5:14b
```

2. **Установите зависимости проекта:**

Убедитесь, что в вашей системе установлен Python 3.10 или более поздней версии.

Сначала установите `uv` и настройте среду:
```bash
# MacOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c «irm https://astral.sh/uv/install.ps1 | iex»
```

Установите зависимости:
```bash
# Создайте новый каталог для нашего проекта
uv init acp-project
cd acp-project

# Создайте виртуальную среду и активируйте ее
uv venv
source .venv/bin/activate  # MacOS/Linux

.venv\Scripts\activate     # Windows

# Установите зависимости
uv add acp-sdk crewai smolagents duckduckgo-search ollama
```

Вы также можете использовать любых других поставщиков LLM, таких как OpenAI или Anthropic. Создайте файл `.env` и добавьте свои ключи API
```
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

## Использование
Запустите два сервера ACP в отдельных терминалах:

```bash
# Терминал 1
uv run crew_acp_server.py

# Терминал 2
uv run smolagents_acp_server.py
```

Запустите клиент ACP, чтобы запустить рабочий процесс агента:

```bash
uv run acp_client.py
```

Вывод:

Общее резюме от первого агента.

Проверенная и обновленная версия от второго агента.
