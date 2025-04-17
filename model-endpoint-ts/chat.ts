#!/usr/bin/env ts-node
/**
 * Simple example of using our chat completion API with HTTP requests.
 */

import * as dotenv from 'dotenv';
import axios, { AxiosError } from 'axios';

interface Message {
  role: string;
  content: string;
}

interface RequestPayload {
  model: string;
  messages: Message[];
  temperature: number;
  max_tokens: number;
}

interface CompletionResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: {
    index: number;
    message: {
      role: string;
      content: string;
    };
    finish_reason: string;
  }[];
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

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
  
  // Prepare the API endpoint URL
  const endpoint = `${baseUrlNormalized}/chat/completions`;
  
  // Set up headers with authentication
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${apiKey}`
  };
  
  // Example messages for the chat
  const messages: Message[] = [
    { role: 'system', content: 'You are a helpful assistant.' },
    { role: 'user', content: 'Tell me a quick fact about artificial intelligence.' }
  ];
  
  // Create the request payload
  const payload: RequestPayload = {
    model: model || '',
    messages: messages,
    temperature: 0.7,
    max_tokens: 150
  };
  
  // Make the API request
  console.log(`Sending request to ${endpoint}...`);
  try {
    const response = await axios.post<CompletionResponse>(
      endpoint, 
      payload, 
      { headers }
    );
    
    // Parse and print the response
    const result = response.data;
    const assistantResponse = result.choices[0].message.content;
    
    console.log('\nAPI Response:');
    console.log('-'.repeat(40));
    console.log(assistantResponse);
    console.log('-'.repeat(40));
    
    // Print some additional information about the response
    console.log(`\nInput tokens: ${result.usage?.prompt_tokens || 'N/A'}`);
    console.log(`Completion tokens: ${result.usage?.completion_tokens || 'N/A'}`);
    console.log(`Total tokens: ${result.usage?.total_tokens || 'N/A'}`);
    
  } catch (error) {
    console.error(`Error: ${error.message}`);
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        console.error(`Response: ${JSON.stringify(axiosError.response.data)}`);
      }
    }
  }
}

if (require.main === module) {
  main().catch(console.error);
}