# Агентный глубокий исследователь

Мы создаем мультиагентного глубокого исследователя на базе MCP, который может выполнять глубокий поиск в Интернете с помощью [Linkup](https://www.linkup.so/), а агенты координируются с помощью CrewAI.

Мы используем:

- [LinkUp](https://www.linkup.so/) (инструмент поиска)
- CrewAI (агентный дизайн)
- Deepseek R1 (LLM)
- Streamlit для обертывания логики в интерактивный пользовательский интерфейс

### Настройка

Запустите эти команды в корневом каталоге проекта

```
uv sync
```


### Запуск приложения

Запустите приложение с помощью:

```bash
streamlit run app.py
```

### Использование в качестве сервера MCP

```json
{
  «mcpServers»: {
    «crew_research»: {
      «command»: «uv»,
      «args»: [
        «--directory»,
        «./Multi-Agent-deep-researcher-mcp-windows-linux»,
        «run»,
        «server.py»
      ],
      «env»: {
        «LINKUP_API_KEY»: «your_linkup_api_key_here»
      }
    }
  }
}
```
[Получите ключи API Linkup здесь](https://www.linkup.so/)
