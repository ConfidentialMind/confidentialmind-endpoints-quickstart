#!/usr/bin/env ts-node
/**
 * Example of using our chat completion API with streaming responses via the OpenAI SDK.
 * This demonstrates real-time text generation with a simple implementation.
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
    { role: 'user', content: 'Explain the concept of transfer learning in AI.' }
  ];
  
  // Make the streaming API request
  console.log('Sending streaming request to chat completions API...');
  try {
    // Create a streaming completion
    const stream = await client.chat.completions.create({
      model: model || '',
      messages: messages,
      temperature: 0.7,
      max_tokens: 300,
      stream: true  // Enable streaming
    });
    
    console.log('\nStreaming response:');
    console.log('-'.repeat(60));
    
    // Process the streaming response
    let fullResponse = '';
    for await (const chunk of stream) {
      const content = chunk.choices[0]?.delta?.content || '';
      if (content) {
        process.stdout.write(content);
        fullResponse += content;
      }
    }
    
    console.log('\n' + '-'.repeat(60));
    console.log(`\nFull response length: ${fullResponse.length} characters`);
    
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
}

if (require.main === module) {
  main().catch(console.error);
}