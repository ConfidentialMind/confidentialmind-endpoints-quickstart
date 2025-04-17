#!/usr/bin/env ts-node
/**
 * Example of using multimodal capabilities with guided JSON output and streaming.
 * This demonstrates how to extract structured data from images with real-time feedback.
 */

import * as dotenv from 'dotenv';
import OpenAI from 'openai';
import * as fs from 'fs';
import * as path from 'path';

// Sample JSON schema for document/image analysis
// Note: This is a simple example - schema capabilities have some limitations
const DOCUMENT_SCHEMA = {
  type: 'object',
  properties: {
    document: {
      type: 'object',
      properties: {
        title: { type: 'string' },
        content: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              type: { type: 'string' },
              text: { type: 'string' },
              items: { type: 'array', items: { type: 'string' } },
              headers: { type: 'array', items: { type: 'string' } },
              rows: { type: 'array', items: { type: 'array', items: { type: 'string' } } },
              description: { type: 'string' }
            }
          }
        },
        metadata: {
          type: 'object',
          properties: {
            has_tables: { type: 'boolean' },
            has_images: { type: 'boolean' }
          }
        }
      },
      required: ['content']
    }
  },
  required: ['document']
};

interface DocumentResponse {
  document: {
    title?: string;
    content: Array<{
      type: string;
      text?: string;
      items?: string[];
      headers?: string[];
      rows?: string[][];
      description?: string;
    }>;
    metadata?: {
      has_tables?: boolean;
      has_images?: boolean;
    };
  };
}

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const options: { image?: string; output?: string } = { 
    image: 'test-data/image_table.png',
    output: 'output.json'
  };
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--image' && i + 1 < args.length) {
      options.image = args[i + 1];
      i++;
    } else if (args[i] === '--output' && i + 1 < args.length) {
      options.output = args[i + 1];
      i++;
    }
  }
  
  return options;
}

/**
 * Encode an image file to base64 string.
 */
function encodeImage(imagePath: string): string {
  const imageBuffer = fs.readFileSync(imagePath);
  return imageBuffer.toString('base64');
}

/**
 * Determine content type based on file extension.
 */
function getContentType(filePath: string): string {
  const extension = path.extname(filePath).toLowerCase();
  switch (extension) {
    case '.png':
      return 'image/png';
    case '.jpg':
    case '.jpeg':
      return 'image/jpeg';
    case '.gif':
      return 'image/gif';
    case '.webp':
      return 'image/webp';
    default:
      // Default to png if unknown
      return 'image/png';
  }
}

async function main(): Promise<void> {
  const options = parseArgs();
  const imagePath = options.image || 'test-data/image_table.png';
  const outputPath = options.output || 'output.json';
  
  // Load environment variables from .env file
  dotenv.config();
  
  // Get API credentials from environment variables
  // Note that the model deployed in the API must support multimodal capabilities
  const baseUrl = process.env.BASE_URL;
  const apiKey = process.env.API_KEY;
  const model = process.env.MODEL_NAME || 'cm-llm';
  
  // Verify credentials are available
  if (!baseUrl || !apiKey) {
    console.error('Error: BASE_URL and API_KEY must be set in .env file');
    return;
  }
  
  // Ensure baseUrl ends with /v1
  const baseUrlNormalized = !baseUrl.endsWith('/v1') 
    ? baseUrl.replace(/\/+$/, '') + '/v1'
    : baseUrl;
  
  // Check if image file exists
  if (!fs.existsSync(imagePath)) {
    console.error(`Error: Image file '${imagePath}' not found`);
    return;
  }
  
  // Initialize the OpenAI client with our API endpoint
  const client = new OpenAI({
    baseURL: baseUrlNormalized,
    apiKey: apiKey
  });
  
  try {
    // Encode the image to base64
    const base64Image = encodeImage(imagePath);
    const contentType = getContentType(imagePath);
    
    // Prepare the messages with image
    const messages = [
      {
        role: 'user',
        content: [
          { 
            type: 'text', 
            text: 'Extract the content of this image as structured data. Identify any text, tables, lists, and other elements.' 
          },
          {
            type: 'image_url',
            image_url: {
              url: `data:${contentType};base64,${base64Image}`
            }
          }
        ]
      }
    ];
    
    console.log(`Processing image: ${imagePath}`);
    console.log('Note: This may take some time depending on the image size and content.');
    console.log('Requesting structured JSON extraction with streaming...');
    
    // Make the API request with guided JSON output and streaming
    const stream = await client.chat.completions.create({
      model: model,
      messages: messages as any, // Type casting for OpenAI SDK compatibility
      temperature: 0.3,
      max_tokens: 3000,
      stream: true,  // Enable streaming
      extra: {
        guided_json: DOCUMENT_SCHEMA,
        guided_decoding_backend: 'xgrammar'  // This backend is used for decoding
      }
    } as any); // Type casting for extra parameters
    
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
    
    // Parse and save the JSON
    try {
      const parsedJson = JSON.parse(fullResponse) as DocumentResponse;
      
      // Save to file
      fs.writeFileSync(outputPath, JSON.stringify(parsedJson, null, 2), 'utf-8');
      console.log(`\nStructured data saved to: ${outputPath}`);
      
      // Display summary
      const document = parsedJson.document;
      const content = document.content || [];
      
      console.log('\nExtracted Content Summary:');
      const contentTypes: Record<string, number> = {};
      
      for (const item of content) {
        const itemType = item.type || 'unknown';
        contentTypes[itemType] = (contentTypes[itemType] || 0) + 1;
      }
      
      for (const [contentType, count] of Object.entries(contentTypes)) {
        console.log(`  - ${contentType}: ${count} items`);
      }
      
    } catch (error) {
      console.error('Error: The response is not valid JSON');
    }
    
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
  
  console.log('\nNote: Our guided JSON capabilities have some limitations.');
  console.log('For complex schemas or special requirements, please contact our support team.');
}

if (require.main === module) {
  main().catch(console.error);
}