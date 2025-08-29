#!/usr/bin/env ts-node
/**
 * Simple example of uploading files to the RAG API.
 */

import * as dotenv from 'dotenv';
import axios, { AxiosError, AxiosResponse } from 'axios';
import chalk from 'chalk';
import { Command } from 'commander';
import * as fs from 'fs';
import * as path from 'path';
import Table from 'cli-table3';
import FormData from 'form-data';

interface UploadResult {
  id: string;
  filename: string;
  [key: string]: any;
}

interface UploadedDocs {
  [path: string]: string; // path -> doc_id
}

async function uploadFile(baseUrl: string, filePath: string, apiKey?: string): Promise<UploadResult> {
  const url = `${baseUrl}/files`;
  
  const headers: Record<string, string> = {};
  if (apiKey) {
    headers['Authorization'] = `Bearer ${apiKey}`;
  }
  
  if (!fs.existsSync(filePath)) {
    throw new Error(`File not found: ${filePath}`);
  }
  
  // Create FormData for file upload
  const formData = new FormData();
  
  // Determine content type based on file extension
  const fileExtension = path.extname(filePath).toLowerCase();
  let contentType = 'application/octet-stream'; // Default
  
  switch (fileExtension) {
    case '.pdf':
      contentType = 'application/pdf';
      break;
    case '.docx':
      contentType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
      break;
    case '.md':
      contentType = 'text/markdown';
      break;
    case '.txt':
      contentType = 'text/plain';
      break;
  }
  
  // Append file to form data
  const fileStream = fs.createReadStream(filePath);
  formData.append('file', fileStream, {
    filename: path.basename(filePath),
    contentType: contentType
  });
  
  // Set headers from FormData
  const formHeaders = formData.getHeaders();
  Object.assign(headers, formHeaders);
  
  const response = await axios.post(url, formData, { headers });
  return response.data;
}

async function checkConnection(baseUrl: string, apiKey?: string): Promise<[boolean, string | number]> {
  const headers: Record<string, string> = {};
  if (apiKey) {
    headers['Authorization'] = `Bearer ${apiKey}`;
  }
  
  try {
    // Try to connect to the base URL
    const response = await axios.get(baseUrl, { headers, timeout: 5000 });
    return [response.status >= 200 && response.status < 300, response.status];
  } catch (error: any) {
    return [false, error.message || 'Unknown error'];
  }
}

function findDocuments(directoryPath: string): string[] {
  const documentPaths: string[] = [];
  const allowedExtensions = new Set(['.pdf', '.docx', '.md', '.txt']);
  
  if (!fs.existsSync(directoryPath)) {
    throw new Error(`Directory not found: ${directoryPath}`);
  }
  
  // Walk through files in directory (non-recursive)
  const files = fs.readdirSync(directoryPath);
  for (const file of files) {
    const filePath = path.join(directoryPath, file);
    if (fs.statSync(filePath).isFile() && allowedExtensions.has(path.extname(filePath).toLowerCase())) {
      documentPaths.push(path.resolve(filePath));
    }
  }
  
  return documentPaths;
}

async function uploadDirectory(baseUrl: string, directoryPath: string, apiKey?: string): Promise<UploadedDocs> {
  // Find all documents
  const documentPaths = findDocuments(directoryPath);
  
  if (documentPaths.length === 0) {
    console.log(chalk.yellow('No documents found with supported extensions (.pdf, .docx, .md, .txt)'));
    return {};
  }
  
  console.log(chalk.green(`Found ${documentPaths.length} documents`));
  
  // Create a table to track upload progress
  const uploadTable = new Table({
    head: [
      chalk.white.bold('File'),
      chalk.white.bold('Status'),
      chalk.white.bold('Document ID')
    ],
    style: { head: [], border: [] }
  });
  
  // Create an error table to show full error details
  const errorTable = new Table({
    head: [
      chalk.white.bold('File'),
      chalk.white.bold('Error Details')
    ],
    style: { head: [], border: [] },
    wordWrap: true
  });
  
  const uploadedDocs: UploadedDocs = {};
  let hasErrors = false;
  
  // Upload each document and record its ID
  for (const docPath of documentPaths) {
    const fileName = path.basename(docPath);
    try {
      const result = await uploadFile(baseUrl, docPath, apiKey);
      const docId = result?.id;
      
      if (docId) {
        uploadedDocs[docPath] = docId;
        uploadTable.push([fileName, chalk.green('Success'), docId]);
      } else {
        uploadTable.push([fileName, chalk.red('Failed'), 'N/A']);
        errorTable.push([fileName, 'No document ID returned']);
        hasErrors = true;
      }
    } catch (error: any) {
      uploadTable.push([fileName, chalk.red('Failed'), 'N/A']);
      
      // Generate detailed error message
      let errorMessage = error.message || 'Unknown error';
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError;
        if (axiosError.response) {
          errorMessage += `\nStatus code: ${axiosError.response.status}`;
          try {
            // Try to parse response as JSON
            const errorJson = axiosError.response.data;
            errorMessage += `\nResponse: ${JSON.stringify(errorJson, null, 2)}`;
          } catch {
            // Otherwise show text response
            errorMessage += `\nResponse: ${String(axiosError.response.data)}`;
          }
        }
      }
      
      errorTable.push([fileName, errorMessage]);
      hasErrors = true;
    }
  }
  
  console.log(uploadTable.toString());
  
  // Display error table if there were errors
  if (hasErrors) {
    console.log(errorTable.toString());
  }
  
  // Generate output filename
  const timestamp = new Date().toISOString().replace(/[:.]/g, '').slice(0, 15);
  const outputFile = `uploaded_files_${timestamp}.json`;
  
  // Only save the document IDs to a file if we successfully uploaded any documents
  if (Object.keys(uploadedDocs).length > 0) {
    fs.writeFileSync(outputFile, JSON.stringify(uploadedDocs, null, 2));
    console.log(chalk.green(`Document IDs saved to ${outputFile}`));
  } else {
    console.log(chalk.yellow('No documents were successfully uploaded, skipping file creation'));
  }
  
  return uploadedDocs;
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
  program
    .option('--dir <directory>', 'Directory containing files to upload', './test-data')
    .option('-f, --file <filepath>', 'Upload a single file instead of a directory')
    .parse(process.argv);
  
  const options = program.opts();
  
  // Check connection to the API first
  const [isConnected, status] = await checkConnection(ragApiUrl, ragApiKey);
  if (!isConnected) {
    console.error(chalk.bold.red(`Connection to the RAG API failed: ${status}`));
    return 1;
  }
  
  try {
    if (options.file) {
      // Upload a single file
      try {
        const result = await uploadFile(ragApiUrl, options.file, ragApiKey);
        
        // Create a table to show the result
        const table = new Table({
          head: [
            chalk.white.bold('File'),
            chalk.white.bold('Status'),
            chalk.white.bold('Document ID')
          ],
          style: { head: [], border: [] }
        });
        
        const fileName = path.basename(options.file);
        const docId = result?.id;
        
        if (docId) {
          table.push([fileName, chalk.green('Success'), docId]);
          
          // Save the document ID to the output file
          const timestamp = new Date().toISOString().replace(/[:.]/g, '').slice(0, 15);
          const outputFile = `uploaded_files_${timestamp}.json`;
          
          fs.writeFileSync(outputFile, JSON.stringify({ [options.file]: docId }, null, 2));
          
          console.log(chalk.green(`Document ID saved to ${outputFile}`));
        } else {
          table.push([fileName, chalk.red('Failed'), 'N/A']);
        }
        
        console.log(table.toString());
      } catch (error: any) {
        console.error(chalk.bold.red('Error uploading file:'));
        
        // Show detailed error information
        if (axios.isAxiosError(error)) {
          const axiosError = error as AxiosError;
          if (axiosError.response) {
            console.error(`Status code: ${axiosError.response.status}`);
            try {
              // Try to parse response as JSON
              const errorJson = axiosError.response.data;
              console.error('Response:');
              console.error(JSON.stringify(errorJson, null, 2));
            } catch {
              // Otherwise show text response
              console.error(`Response: ${String(axiosError.response.data)}`);
            }
          } else {
            console.error(error.message || 'Unknown error');
          }
        } else {
          console.error(error.message || 'Unknown error');
        }
        
        return 1;
      }
    } else {
      // Upload all files in the directory
      await uploadDirectory(ragApiUrl, options.dir, ragApiKey);
    }
  } catch (error: any) {
    console.error(chalk.bold.red(`Error: ${error.message || error}`));
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