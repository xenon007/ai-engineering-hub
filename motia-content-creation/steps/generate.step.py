import os
import asyncio
import json
from pydantic import BaseModel, HttpUrl
from openai import OpenAI
from openai import AsyncOpenAI
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class GenerateInput(BaseModel):
    requestId: str
    url: HttpUrl
    title: str
    content: str
    timestamp: int

config = {
    'type': 'event',
    'name': 'GenerateContent',
    'description': 'Generates Twitter and LinkedIn content in parallel',
    'subscribes': ['generate-content'],
    'emits': ['schedule-content'],
    'input': GenerateInput.model_json_schema(),
    'flows': ['content-generation']
}

async def handler(input, context):
    context.logger.info(f"✍️ Generating content for: {input['title']}")

    try:
        # Read prompt templates
        with open("prompts/twitter-prompt.txt", "r", encoding='utf-8') as f:
            twitterPromptTemplate = f.read()

        with open("prompts/linkedin-prompt.txt", "r", encoding='utf-8') as f:
            linkedinPromptTemplate = f.read()
            
        twitterPrompt = twitterPromptTemplate.replace('{{title}}', input['title']).replace('{{content}}', input['content'])
        linkedinPrompt = linkedinPromptTemplate.replace('{{title}}', input['title']).replace('{{content}}', input['content'])

        context.logger.info("🔄 Twitter and LinkedIn content generation started in parallel...")

        openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

        twitter_response, linkedin_response = await asyncio.gather(
            openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{'role': 'user', 'content': twitterPrompt}],
                temperature=0.7,
                max_tokens=2000,
                response_format={'type': 'json_object'}
            ),  
            openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{'role': 'user', 'content': linkedinPrompt}],
                temperature=0.7,
                max_tokens=2000,
                response_format={'type': 'json_object'}
            )   
        ) 

        twitter_content = json.loads(twitter_response.choices[0].message.content)
        linkedin_content = json.loads(linkedin_response.choices[0].message.content)

        context.logger.info(f"🎉 Content generated successfully!")
        # context.logger.info(f"📱 Twitter: {twitter_content.totalTweets} tweet(s) in thread")
        # context.logger.info(f"💼 LinkedIn: {linkedin_content.characterCount} characters")

        await context.emit({
            'topic': 'schedule-content',
            'data': {
                'requestId': input['requestId'],
                'url': input['url'],
                'title': input['title'],
                'content': {
                    'twitter': twitter_content,
                    'linkedin': linkedin_content
                },
                'metadata': {
                    'generatedAt': datetime.now().isoformat(),
                    
                    'originalUrl': input['url']
                }
            }
        })
    except Exception as e:
        context.logger.error(f"❌ Content generation failed: {e}")
        raise e