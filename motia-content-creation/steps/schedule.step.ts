import { EventConfig, Handlers } from 'motia'
import { z } from 'zod'
import axios from 'axios'

const appConfig = require('../config')

const typefullyApiUrl = 'https://api.typefully.com/v1/drafts/'
const headers = {
  'X-API-KEY': `Bearer ${appConfig.typefully.apiKey}`,
  'Content-Type': 'application/json'
}

export const config: EventConfig = {
  type: 'event',
  name: 'ScheduleContent',
  description: 'Schedules generated content using Typefully API',
  subscribes: ['schedule-content'],
  emits: [],
  input: z.object({
    requestId: z.string(),
    url: z.string().url(),
    title: z.string(),
    content: z.object({
      twitter: z.any(),
      linkedin: z.any()
    }),
    metadata: z.any()
  }),
  flows: ['content-generation']
}

export const handler: Handlers['ScheduleContent'] = async (input, { emit, logger }) => {
  logger.info(`📅 Scheduling your content...`)

  try {
    // Schedule Twitter thread
    logger.info(`📱 Scheduling Twitter thread...`)

    // Convert Twitter thread to Typefully format
    const twitterThread = input.content.twitter.thread.map((tweet: any) => tweet.content).join('\n\n\n\n')

    const twitterPayload = {
      content: twitterThread,
      schedule_date: null // Will be posted as draft
    }

    const twitterResponse = await axios.post(`${typefullyApiUrl}`, twitterPayload, { headers })

    const twitterResult = twitterResponse.data
    logger.info(`✅ Twitter thread scheduled successfully`)

    // Schedule LinkedIn post
    logger.info(`💼 Scheduling LinkedIn post...`)

    const linkedinPayload = {
      content: input.content.linkedin.post,
      schedule_date: null // Will be posted as draft
    }

    const linkedinResponse = await axios.post(`${typefullyApiUrl}`, linkedinPayload, { headers })

    const linkedinResult = linkedinResponse.data
    logger.info(`✅ LinkedIn post scheduled successfully`)

    logger.info(`🎉 Content scheduling completed!`)
    logger.info(`🐦 Twitter thread URL: ${twitterResult.url || twitterResult.data?.url}`)
    logger.info(`💼 LinkedIn post URL: ${linkedinResult.url || linkedinResult.data?.url}`)
    logger.info(`👀 Visit Typefully to review and publish your content!`)

  } catch (error) {
    logger.error(`❌ Content scheduling failed: ${error.message}`)
    throw error
  }
}