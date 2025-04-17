#!/usr/bin/env ts-node
/**
 * Simple example of deleting files from the RAG API.
 */

import * as dotenv from 'dotenv';
import axios, { AxiosError } from 'axios';
import chalk from 'chalk';
import { Command } from 'commander';
import * as fs from 'fs';
import * as path from 'path';
import * as inquirer from 'inquirer';
import Table from 'cli-table3';
import * as glob from 'glob';

interface DeleteResult {
  success: boolean;
  message?: string;
  [key: string]: any;
}

interface UploadedDocs {
  [path: string]: string; // path -> doc_id
}

interface DeleteStatistics {
  files_found: number;
  deleted: number;
  failed: number;
}

async function deleteFile(baseUrl: string, fileId: string, apiKey?: string): Promise<DeleteResult> {
  const url = `${baseUrl}/files/${fileId}`;
  
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (apiKey) {
    headers['Authorization'] = `Bearer ${apiKey}`;
  }
  
  const response = await axios.delete(url, { headers });
  return response.data;
}

async function deleteFilesFromJson(
  baseUrl: string, 
  jsonFile: string, 
  skipConfirmation: boolean = false, 
  apiKey?: string
): Promise<Record<string, boolean>> {
  // Load document IDs from file
  let uploadedDocs: UploadedDocs;
  try {
    uploadedDocs = JSON.parse(fs.readFileSync(jsonFile, 'utf-8'));
  } catch (error: any) {
    if (error.code === 'ENOENT') {
      console.error(chalk.red(`Error: File '${jsonFile}' not found`));
      return {};
    } else {
      console.error(chalk.red(`Error: File '${jsonFile}' is not a valid JSON file`));
      return {};
    }
  }
  
  // Extract document IDs and display what will be deleted
  const fileIds = Object.values(uploadedDocs);
  const docPaths = Object.keys(uploadedDocs);
  
  console.log(chalk.green(`Found ${fileIds.length} files to delete:`));
  docPaths.forEach((filePath, i) => {
    const fileName = path.basename(filePath);
    console.log(`  ${i+1}. ${chalk.cyan(fileName)} (ID: ${fileIds[i]})`);
  });
  
  // Confirm deletion if needed
  if (!skipConfirmation && fileIds.length > 0) {
    const answer = await inquirer.prompt([{
      type: 'confirm',
      name: 'confirm',
      message: `Delete ${fileIds.length} files?`,
      default: false
    }]);
    
    if (!answer.confirm) {
      console.log(chalk.yellow('Deletion cancelled'));
      return {};
    }
  }
  
  // Create a table to track deletion progress
  const table = new Table({
    head: [
      chalk.white.bold('File'),
      chalk.white.bold('ID'),
      chalk.white.bold('Status')
    ],
    style: { head: [], border: [] }
  });
  
  const results: Record<string, boolean> = {};
  
  // Delete each file
  for (let i = 0; i < fileIds.length; i++) {
    const filePath = docPaths[i];
    const fileName = path.basename(filePath);
    const fileId = fileIds[i];
    
    try {
      const result = await deleteFile(baseUrl, fileId, apiKey);
      const success = result.success === true;
      results[fileId] = success;
      
      if (success) {
        table.push([fileName, fileId, chalk.green('Success')]);
      } else {
        const message = result.message || 'Unknown error';
        table.push([fileName, fileId, chalk.red(`Failed: ${message}`)]);
      }
    } catch (error: any) {
      results[fileId] = false;
      const errorMessage = error.message || 'Unknown error';
      table.push([fileName, fileId, chalk.red(`Error: ${errorMessage.substring(0, 50)}...`)]);
    }
  }
  
  console.log(table.toString());
  
  // Update the JSON file to remove successfully deleted documents
  if (Object.values(results).some(v => v)) {
    const updatedDocs: UploadedDocs = {};
    for (const [path, fileId] of Object.entries(uploadedDocs)) {
      if (!results[fileId]) {
        updatedDocs[path] = fileId;
      }
    }
    
    if (Object.keys(updatedDocs).length > 0) {
      fs.writeFileSync(jsonFile, JSON.stringify(updatedDocs, null, 2));
      console.log(chalk.yellow(`Updated ${jsonFile} with remaining ${Object.keys(updatedDocs).length} files`));
    } else {
      // All documents were deleted, so remove the file
      try {
        fs.unlinkSync(jsonFile);
        console.log(chalk.green(`All files deleted. Removed ${jsonFile}`));
      } catch (error: any) {
        if (error.code !== 'ENOENT') {
          console.error(chalk.yellow(`Warning: Could not remove ${jsonFile}: ${error.message}`));
        }
      }
    }
  }
  
  return results;
}

async function deleteAllFromJsonFiles(
  baseUrl: string, 
  skipConfirmation: boolean = false, 
  apiKey?: string
): Promise<DeleteStatistics> {
  // Find all uploaded_files_*.json files
  const jsonFiles = glob.sync('uploaded_files_*.json');
  
  if (jsonFiles.length === 0) {
    console.log(chalk.yellow('No uploaded_files_*.json files found in the current directory.'));
    return { files_found: 0, deleted: 0, failed: 0 };
  }
  
  console.log(chalk.green(`Found ${jsonFiles.length} JSON files with file IDs.`));
  
  // Collect all file IDs
  const allFileIds: Record<string, [string, string]> = {}; // Map from file_id to [filename, json_file]
  
  for (const jsonFile of jsonFiles) {
    try {
      const uploadedDocs: UploadedDocs = JSON.parse(fs.readFileSync(jsonFile, 'utf-8'));
      
      for (const [filePath, fileId] of Object.entries(uploadedDocs)) {
        // Store the file name and json file that contains this ID
        allFileIds[fileId] = [path.basename(filePath), jsonFile];
      }
    } catch (error: any) {
      console.log(chalk.yellow(`Warning: Could not process ${jsonFile}: ${error.message}`));
    }
  }
  
  // Display summary
  if (Object.keys(allFileIds).length === 0) {
    console.log(chalk.yellow('No file IDs found in the JSON files.'));
    return { files_found: jsonFiles.length, deleted: 0, failed: 0 };
  }
  
  console.log(chalk.green(`Found ${Object.keys(allFileIds).length} unique file IDs to delete.`));
  
  // Confirm deletion if needed
  if (!skipConfirmation) {
    const answer = await inquirer.prompt([{
      type: 'confirm',
      name: 'confirm',
      message: `Delete all ${Object.keys(allFileIds).length} files?`,
      default: false
    }]);
    
    if (!answer.confirm) {
      console.log(chalk.yellow('Deletion cancelled.'));
      return { files_found: jsonFiles.length, deleted: 0, failed: 0 };
    }
  }
  
  // Create a table to track deletion progress
  const table = new Table({
    head: [
      chalk.white.bold('File'),
      chalk.white.bold('ID'),
      chalk.white.bold('Status')
    ],
    style: { head: [], border: [] }
  });
  
  const statistics: DeleteStatistics = {
    files_found: jsonFiles.length,
    deleted: 0,
    failed: 0
  };
  
  // Process deletions
  for (const [fileId, [fileName, _]] of Object.entries(allFileIds)) {
    try {
      const result = await deleteFile(baseUrl, fileId, apiKey);
      const success = result.success === true;
      
      if (success) {
        statistics.deleted++;
        table.push([fileName, fileId, chalk.green('Success')]);
      } else {
        statistics.failed++;
        const message = result.message || 'Unknown error';
        table.push([fileName, fileId, chalk.red(`Failed: ${message}`)]);
      }
    } catch (error: any) {
      statistics.failed++;
      const errorMessage = error.message || 'Unknown error';
      table.push([fileName, fileId, chalk.red(`Error: ${errorMessage.substring(0, 50)}...`)]);
    }
  }
  
  console.log(table.toString());
  
  // Update or delete the JSON files
  for (const jsonFile of jsonFiles) {
    try {
      fs.unlinkSync(jsonFile);
      console.log(chalk.green(`Removed ${jsonFile}`));
    } catch (error: any) {
      console.log(chalk.yellow(`Could not remove ${jsonFile}: ${error.message}`));
    }
  }
  
  console.log(chalk.green(`Summary: ${statistics.deleted} files deleted, ${statistics.failed} failed`));
  
  return statistics;
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
    .option('--id <id>', 'Delete a single file by ID')
    .option('-j, --from-json <jsonFile>', 'Delete files listed in a JSON file')
    .option('-a, --all', 'Delete all files from all uploaded_files_*.json files')
    .option('-y, --yes', 'Skip confirmation prompts')
    .parse(process.argv);
  
  const options = program.opts();
  
  // Check if at least one deletion method is specified
  if (!options.id && !options.fromJson && !options.all) {
    console.error('Error: Please specify either --id, --from-json, or --all');
    program.help();
    return 1;
  }
  
  try {
    if (options.id) {
      // Confirm deletion if needed
      if (!options.yes) {
        const answer = await inquirer.prompt([{
          type: 'confirm',
          name: 'confirm',
          message: `Delete file with ID '${options.id}'?`,
          default: false
        }]);
        
        if (!answer.confirm) {
          console.log(chalk.yellow('Deletion cancelled'));
          return 0;
        }
      }
      
      // Delete a single file
      const result = await deleteFile(ragApiUrl, options.id, ragApiKey);
      
      if (result.success) {
        console.log(chalk.green(`Successfully deleted file with ID: ${options.id}`));
      } else {
        const message = result.message || 'Unknown error';
        console.log(chalk.red(`Failed to delete file: ${message}`));
      }
    
    } else if (options.fromJson) {
      // Delete files from JSON file
      await deleteFilesFromJson(ragApiUrl, options.fromJson, options.yes, ragApiKey);
      
    } else if (options.all) {
      // Delete all files from all JSON files
      await deleteAllFromJsonFiles(ragApiUrl, options.yes, ragApiKey);
    }
  } catch (error: any) {
    console.error(chalk.bold.red(`Error: ${error.message || error}`));
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        console.error(chalk.dim(`Response: ${JSON.stringify(axiosError.response.data)}`));
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