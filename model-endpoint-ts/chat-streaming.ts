#!/usr/bin/env ts-node
/**
 * Example of using our chat completion API with streaming responses via HTTP requests.
 * This demonstrates how to process server-sent events for real-time text generation.
 */

import * as dotenv from 'dotenv';
import axios, { AxiosError } from 'axios';
import { performance } from 'perf_hooks';

interface Message {
  role: string;
  content: string;
}

interface StreamChunk {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: {
    index: number;
    delta: {
      content?: string;
      role?: string;
    };
    finish_reason: string | null;
  }[];
  usage?: {
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
    { role: 'user', content: 'Write a paragraph explaining how machine learning works.' }
  ];
  
  // Create the request payload with streaming enabled
  const payload = {
    model: model || '',
    messages: messages,
    temperature: 0.7,
    max_tokens: 500,
    include_usage: true,
    stream: true  // Enable streaming
  };
  
  console.log(`Sending streaming request to ${endpoint}...`);
  
  try {
    const startTime = performance.now();
    
    // Make a streaming request
    const response = await axios.post(endpoint, payload, {
      headers,
      responseType: 'stream'
    });
    
    console.log('\nStreaming response:');
    console.log('-'.repeat(60));
    
    // Process the streaming response
    const collectedChunks: StreamChunk[] = [];
    
    // Handle the stream data
    response.data.on('data', (chunk: Buffer) => {
      // Convert Buffer to string
      const lines = chunk.toString().split('\n').filter(line => line.trim() !== '');
      
      for (const line of lines) {
        console.log(line);
        
        // Skip lines that don't start with "data:"
        if (!line.startsWith('data:')) {
          continue;
        }
        
        // Remove the "data:" prefix
        const data = line.substring(5).trim();
        
        // Check for the end of the stream
        if (data === '[DONE]') {
          return;
        }
        
        // Parse the JSON data
        try {
          const jsonData: StreamChunk = JSON.parse(data);
          collectedChunks.push(jsonData);
          
          // You can also extract and process content like this:
          // const content = jsonData.choices[0]?.delta?.content || '';
          // process.stdout.write(content);
        } catch (error) {
          console.error(`Error parsing JSON from: ${data}`);
        }
      }
    });
    
    // Wait for the response to complete
    await new Promise<void>((resolve) => {
      response.data.on('end', () => {
        console.log('\n' + '-'.repeat(60));
        
        // Calculate token usage from the collected chunks (if available)
        const lastChunk = collectedChunks[collectedChunks.length - 1];
        if (lastChunk && lastChunk.usage) {
          console.log(`\nCompletion tokens: ${lastChunk.usage.completion_tokens || 'N/A'}`);
          console.log(`Total tokens: ${lastChunk.usage.total_tokens || 'N/A'}`);
        }
        
        const endTime = performance.now();
        const elapsedTime = (endTime - startTime) / 1000;
        console.log(`Request completed in ${elapsedTime.toFixed(2)} seconds`);
        
        resolve();
      });
    });
    
  } catch (error: any) {
    console.error(`Error: ${error.message || error}`);
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