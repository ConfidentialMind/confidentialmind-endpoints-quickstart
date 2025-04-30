#!/usr/bin/env ts-node
/**
 * Simple example of retrieving a list of files from the RAG API.
 */

import * as dotenv from 'dotenv';
import axios, { AxiosError } from 'axios';
import chalk from 'chalk';
import { Command } from 'commander';
import Table from 'cli-table3';

interface FileInfo {
  id: string;
  filename: string;
  status: string;
  created_at: string;
  [key: string]: any; // For any other fields
}

async function getFiles(baseUrl: string, apiKey?: string): Promise<FileInfo[]> {
  const url = `${baseUrl}/files`;
  
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (apiKey) {
    headers['Authorization'] = `Bearer ${apiKey}`;
  }
  
  const response = await axios.get(url, { headers });
  const result = response.data;
  
  // The API returns an object with a 'files' key containing the array of files
  if (typeof result === 'object' && 'files' in result) {
    return result.files;
  }
  
  // Fallback for different API response formats
  return result;
}

function displayFiles(files: any[]): void {
  if (!files || files.length === 0) {
    console.log(chalk.yellow('No files found in the system.'));
    return;
  }

  // Check if files is a valid list of objects
  if (!Array.isArray(files) || (files.length > 0 && typeof files[0] !== 'object')) {
    console.log(chalk.red('Error: Unexpected response format from the API'));
    console.log(chalk.dim(`Response: ${JSON.stringify(files)}`));
    return;
  }
  
  // Create a table for display
  const columns = Object.keys(files[0]);
  const table = new Table({
    head: columns.map(col => chalk.white.bold(col)),
    style: {
      head: [], // No additional style for header
      border: [] // No additional style for border
    }
  });
  
  // Add rows for each file
  for (const file of files) {
    const row = columns.map(col => file[col]?.toString() || '');
    table.push(row);
  }
  
  console.log(chalk.bold('Files in RAG System:'));
  console.log(table.toString());
}

async function main(): Promise<number> {
  // Load environment variables from .env file
  dotenv.config();
  
  // Get API URL and key from environment
  const ragApiUrl = process.env.RAG_API_URL;
  const ragApiKey = process.env.RAG_API_KEY;
  
  // Ensure we have the required environment variables
  if (!ragApiUrl) {
    console.error('Error: RAG_API_URL not set in environment or .env file');
    return 1;
  }
  
  // Parse command line arguments
  const program = new Command();
  program.parse(process.argv);
  
  try {
    // Get and display files
    const files = await getFiles(ragApiUrl, ragApiKey);
    displayFiles(files);
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