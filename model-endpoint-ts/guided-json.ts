#!/usr/bin/env ts-node
/**
 * Example of using guided JSON output with our API.
 * This demonstrates how to get structured data from the model using a JSON schema.
 */

import * as dotenv from 'dotenv';
import OpenAI from 'openai';

// Sample JSON schema to guide the model's output
// Note: This is a simple example - schema capabilities have some limitations
// Note: Since vLLM v0.8.3 enums are supported in the schema. If using vLLM >= v0.8.3, you can
// modify the sentiment field to be an enum with values like "positive", "negative", "neutral"
// and the model will respect that. Like this:
// "sentiment": {
//   "type": "string",
//   "enum": ["positive", "negative", "neutral"]
// }
const SAMPLE_SCHEMA = {
  type: 'object',
  properties: {
    analysis: {
      type: 'object',
      properties: {
        title: { type: 'string' },
        summary: { type: 'string' },
        key_points: {
          type: 'array',
          items: { type: 'string' }
        },
        sentiment: {
          type: 'string'
        },
        categories: {
          type: 'array',
          items: { type: 'string' }
        }
      },
      required: ['summary', 'key_points', 'sentiment']
    }
  },
  required: ['analysis']
};

interface AnalysisResponse {
  analysis: {
    title?: string;
    summary: string;
    key_points: string[];
    sentiment: string;
    categories?: string[];
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
  
  // Initialize the OpenAI client with our API endpoint
  const client = new OpenAI({
    baseURL: baseUrlNormalized,
    apiKey: apiKey
  });
  
  // Prepare user prompt that will work well with the JSON schema
  const messages = [
    { role: 'system', content: 'You are a helpful assistant that provides analysis in structured JSON format.' },
    { role: 'user', content: 'Analyze the following text and provide structured insights: ' +
      'Renewable energy investments hit a record high last quarter, with solar projects ' +
      'leading the way. Despite supply chain challenges, new installations increased by 28%. ' +
      'However, regulatory uncertainty in some markets has caused concern among investors.' }
  ] as OpenAI.ChatCompletionMessageParam[];
  
  // Create the API request with guided JSON output
  console.log('Requesting guided JSON response...');
  try {
    // Note: We pass the JSON schema via the extra/extra_body parameter
    const response = await client.chat.completions.create({
      model: model || '',
      messages: messages,
      temperature: 0.5,
      max_tokens: 500,
      extra: {
        guided_json: SAMPLE_SCHEMA,
        guided_decoding_backend: 'xgrammar'  // This backend is used for decoding
      }
    } as any); // Type casting for extra parameters
    
    // Extract the response
    const jsonResponse = response.choices[0].message.content;
    
    // Display the raw JSON response
    console.log('\nRaw JSON Response:');
    console.log('-'.repeat(60));
    console.log(jsonResponse);
    console.log('-'.repeat(60));
    
    // Parse and pretty-print the JSON
    try {
      const parsedJson = JSON.parse(jsonResponse || '{}') as AnalysisResponse;
      console.log('\nPretty-printed JSON:');
      console.log('-'.repeat(60));
      console.log(JSON.stringify(parsedJson, null, 2));
      console.log('-'.repeat(60));
      
      // Example of accessing specific fields
      if (parsedJson.analysis) {
        const analysis = parsedJson.analysis;
        console.log('\nHighlights from the analysis:');
        console.log(`Sentiment: ${analysis.sentiment || 'N/A'}`);
        console.log(`Summary: ${analysis.summary || 'N/A'}`);
        
        if (analysis.key_points && analysis.key_points.length > 0) {
          console.log('\nKey Points:');
          analysis.key_points.forEach((point, i) => {
            console.log(`${i + 1}. ${point}`);
          });
        }
      }
    } catch (error) {
      console.error('Error: The response is not valid JSON');
    }
    
  } catch (error: any) {
    console.error(`Error: ${error.message || error}`);
  }
  
  console.log('\nNote: Our guided JSON capabilities have some limitations.');
  console.log('For complex schemas or special requirements, please contact our support team.');
}

if (require.main === module) {
  main().catch(console.error);
}