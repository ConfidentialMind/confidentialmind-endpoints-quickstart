#!/usr/bin/env ts-node
/**
 * Example of using the multimodal capabilities of our API to process images.
 * This script sends an image to the model and asks for a simple description.
 */

import * as dotenv from 'dotenv';
import OpenAI from 'openai';
import * as fs from 'fs';
import * as path from 'path';

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const options: { image?: string } = { image: 'test-data/image.png' };
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--image' && i + 1 < args.length) {
      options.image = args[i + 1];
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
  const imagePath = options.image || 'test-data/image.png';
  
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
          { type: 'text', text: 'Please describe what you see in this image.' },
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
    
    // Make the API request
    const response = await client.chat.completions.create({
      model: model,
      messages: messages as any, // Type casting for OpenAI SDK compatibility
      temperature: 0.7,
      max_tokens: 300
    });
    
    // Extract and print the response
    const result = response.choices[0].message.content;
    
    console.log('\nImage Description:');
    console.log('-'.repeat(60));
    console.log(result);
    console.log('-'.repeat(60));
    
  } catch (error) {
    console.error(`Error: ${error.message}`);
  }
}

if (require.main === module) {
  main().catch(console.error);
}