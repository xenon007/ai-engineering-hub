# LaTeX-OCR

Этот проект использует Llama 3.2 vision и Streamlit для создания приложения LaTeX OCR, которое преобразует изображения уравнений LaTeX в код LaTeX.

## Демонстрационное видео

Нажмите ниже, чтобы посмотреть демонстрационное видео работы AI Assistant:

[Посмотреть видео](LaTeX-OCR.mp4)

## Установка и настройка

**Настройка Ollama**:

*В Linux*:
```bash 
curl -fsSL https://ollama.com/install.sh | sh
# загрузить модель Llama 3.2 Vision
ollama run llama3.2-vision 
```

*В MacOS*:
```bash 
/bin/bash -c «$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)»    # получить homebrew
xcode-select --install
brew install ollama    # установить ollama
ollama pull llama3.2-vision    # загрузить модель llama 3.2 vision
ollama run llama3.2-vision 
```


**Установка зависимостей**:
Убедитесь, что у вас установлен Python 3.11 или более поздней версии.
```bash
pip install streamlit ollama
```
