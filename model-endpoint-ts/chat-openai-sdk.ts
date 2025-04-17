#!/usr/bin/env ts-node
/**
 * Simple example of using our chat completion API with the OpenAI TypeScript SDK.
 */

import * as dotenv from 'dotenv';
import OpenAI from 'openai';

async function main(): Promise<void> {
  // Load environment variables from .env file
  dotenv.config();
  
  // Get API credentials from environment variables
  const baseUrl = process.env.BASE_URL;
  const apiKey = process.env.API_KEY;
  const model = process.env.MODEL_NAME;
  
  // Verify credentials are available
  if (!baseUrl || !apiKey) {
    console.error('Error: BASE_URL and API_KEY must be set in .env file');
    return;
  }
  
  // Ensure baseUrl ends with /v1
  const baseUrlNormalized = !baseUrl.endsWith('/v1') 
    ? baseUrl.replace(/\/+$/, '') + '/v1'
    : baseUrl;
  
  console.log(`Initializing client with ${baseUrlNormalized}...`);
  
  // Initialize the OpenAI client with our API endpoint
  const client = new OpenAI({
    baseURL: baseUrlNormalized,
    apiKey: apiKey
  });
  
  // Example messages for the chat
  const messages = [
    { role: 'system', content: 'You are a helpful assistant.' },
    { role: 'user', content: 'Write a short haiku about technology.' }
  ] as OpenAI.ChatCompletionMessageParam[];
  
  // Make the API request
  console.log('Sending request to chat completions API...');
  try {
    const response = await client.chat.completions.create({
      model: model || '',
      messages: messages,
      temperature: 0.7,
      max_tokens: 150
    });
    
    // Extract and print the response
    const assistantResponse = response.choices[0].message.content;
    
    console.log('\nAPI Response:');
    console.log('-'.repeat(40));
    console.log(assistantResponse);
    console.log('-'.repeat(40));
    
    // Print some additional information about the response
    console.log(`\nInput tokens: ${response.usage?.prompt_tokens}`);
    console.log(`Completion tokens: ${response.usage?.completion_tokens}`);
    console.log(`Total tokens: ${response.usage?.total_tokens}`);
    
  } catch (error: any) {
    console.error(`Error: ${error.message || error}`);
  }
}

if (require.main === module) {
  main().catch(console.error);
}