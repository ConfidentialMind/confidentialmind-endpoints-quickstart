#!/usr/bin/env ts-node
/**
 * Simple example of using our RAG-enabled chat completion API.
 */

import * as dotenv from 'dotenv';
import axios, { AxiosError } from 'axios';
import chalk from 'chalk';
import * as readline from 'readline';
import { Command } from 'commander';

interface Message {
  role: string;
  content: string;
}

interface ChatCompletionResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: {
    index: number;
    message: Message;
    finish_reason: string;
  }[];
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

async function chatCompletion(
  baseUrl: string, 
  apiKey: string | undefined, 
  model: string, 
  messages: Message[], 
  maxChunks: number = 4, 
  temperature: number = 0.5
): Promise<ChatCompletionResponse> {
  const url = `${baseUrl}/v1/chat/completions`;
  
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (apiKey) {
    headers['Authorization'] = `Bearer ${apiKey}`;
  }
  
  const data = {
    model,
    messages,
    temperature,
    max_chunks: maxChunks
  };
  
  const response = await axios.post(url, data, { headers });
  return response.data;
}

function createReadlineInterface(): readline.Interface {
  return readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
}

async function interactiveChat(
  baseUrl: string, 
  apiKey: string | undefined, 
  model: string, 
  maxChunks: number = 4, 
  temperature: number = 0.5
): Promise<void> {
  console.log(chalk.bold('RAG Chat Session'));
  console.log(chalk.dim("Type 'exit', 'quit', or press Ctrl+C to end the session."));
  console.log();
  
  // Initialize message history
  const messages: Message[] = [];
  
  // Create readline interface
  const rl = createReadlineInterface();
  
  try {
    // Loop for interactive chat
    while (true) {
      // Get user input (wrapped in a promise for async/await)
      const userMessage = await new Promise<string>((resolve) => {
        rl.question(chalk.bold.blue('You: '), resolve);
      });
      
      // Check for exit commands
      if (userMessage.toLowerCase() === 'exit' || userMessage.toLowerCase() === 'quit') {
        break;
      }
      
      // Add user message to history
      messages.push({ role: 'user', content: userMessage });
      
      try {
        // Get completion
        const result = await chatCompletion(
          baseUrl,
          apiKey,
          model,
          messages,
          maxChunks,
          temperature
        );
        
        // Display the assistant's response
        if (result.choices && result.choices.length > 0) {
          const message = result.choices[0].message;
          const content = message.content;
          
          console.log(`\n${chalk.bold.green('Assistant:')}`);
          // In a full implementation, we'd use a markdown renderer here
          console.log(content);
          
          // Add assistant response to history
          messages.push(message);
          
          // Show token usage if available
          if (result.usage) {
            const usage = result.usage;
            console.log(chalk.dim('\nToken Usage:'));
            console.log(chalk.dim(`- Prompt tokens: ${usage.prompt_tokens || 'N/A'}`));
            console.log(chalk.dim(`- Completion tokens: ${usage.completion_tokens || 'N/A'}`));
            console.log(chalk.dim(`- Total tokens: ${usage.total_tokens || 'N/A'}`));
          }
        }
      } catch (error: any) {
        console.error(chalk.bold.red(`Error: ${error.message || error}`));
        if (axios.isAxiosError(error)) {
          const axiosError = error as AxiosError;
          if (axiosError.response) {
            console.error(`Response: ${JSON.stringify(axiosError.response.data)}`);
          }
        }
      }
    }
  } catch (error: any) {
    console.error(chalk.bold.red(`Error: ${error.message || error}`));
  } finally {
    rl.close();
    console.log(chalk.dim('\nChat session ended.'));
  }
}

async function main(): Promise<number> {
  // Load environment variables from .env file
  dotenv.config();
  
  // Get API URL and key from environment
  const ragApiUrl = process.env.RAG_API_URL;
  const ragApiKey = process.env.RAG_API_KEY;
  const ragModel = process.env.RAG_MODEL || 'cm-llm';
  
  // Ensure we have the required environment variables
  if (!ragApiUrl) {
    console.error('Error: RAG_API_URL not set in environment or .env file');
    return 1;
  }
  
  // Parse command line arguments using Commander
  const program = new Command();
  program
    .option('-q, --query <query>', 'Single query mode (non-interactive)')
    .option('-c, --max-chunks <number>', 'Maximum number of context chunks to retrieve', '4')
    .option('-t, --temperature <number>', 'Temperature for text generation', '0.5')
    .parse(process.argv);
  
  const options = program.opts();
  
  try {
    if (options.query) {
      // Single query mode
      const messages: Message[] = [{ role: 'user', content: options.query }];
      
      // Get completion
      const result = await chatCompletion(
        ragApiUrl,
        ragApiKey,
        ragModel,
        messages,
        parseInt(options.maxChunks, 10),
        parseFloat(options.temperature)
      );
      
      // Display the result
      if (result.choices && result.choices.length > 0) {
        const message = result.choices[0].message;
        const content = message.content;
        
        console.log(`\n${chalk.bold.green('Assistant:')}`);
        // In a full implementation, we'd use a markdown renderer here
        console.log(content);
        
        // Show token usage if available
        if (result.usage) {
          const usage = result.usage;
          console.log(chalk.dim('\nToken Usage:'));
          console.log(chalk.dim(`- Prompt tokens: ${usage.prompt_tokens || 'N/A'}`));
          console.log(chalk.dim(`- Completion tokens: ${usage.completion_tokens || 'N/A'}`));
          console.log(chalk.dim(`- Total tokens: ${usage.total_tokens || 'N/A'}`));
        }
      }
    } else {
      // Interactive chat mode
      await interactiveChat(
        ragApiUrl,
        ragApiKey,
        ragModel,
        parseInt(options.maxChunks, 10),
        parseFloat(options.temperature)
      );
    }
  } catch (error: any) {
    console.error(`Error: ${error.message || error}`);
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        console.error(`Response: ${JSON.stringify(axiosError.response.data)}`);
      }
    }
    return 1;
  }
  
  return 0;
}

if (require.main === module) {
  main().then(process.exit).catch(err => {
    console.error(err);
    process.exit(1);
  });
}