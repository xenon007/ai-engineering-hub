# Chat with Code using Qwen3-Coder

We're building a Streamlit app that allows users to chat with code using the Qwen3 Coder model. The app provides a user-friendly interface for querying code and receiving responses, with the added benefit of validating the responses using Cleanlab.

We use:

- [Llama_Index](https://docs.llamaindex.ai/en/stable/) for orchestration
- [Milvus](https://milvus.io/) to self-host a vectorDB
- [Cleanlab](https://help.cleanlab.ai/codex/) codex to validate the response
- [OpenRouterAI](https://openrouter.ai/docs/quick-start) to access Alibaba's Qwen3 Coder

## Set Up

Follow these steps one by one:

### Setup Milvus VectorDB

Milvus provides an installation script to install it as a docker container.

To install Milvus in Docker, you can use the following command:

```bash
curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed.sh

bash standalone_embed.sh start
```

### Install Dependencies

```bash
uv sync
```

## Run the Application

To run the Streamlit app, use the following command:

```bash
streamlit run app.py
```

## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

## Contribution

Contributions are welcome! Feel free to fork this repository and submit pull requests with your improvements.
