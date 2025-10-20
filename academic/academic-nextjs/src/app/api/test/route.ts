import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const cwd = process.cwd();
    console.log(`Test API: Current working directory: ${cwd}`);
    
    // List files in current directory
    const files = fs.readdirSync(cwd);
    console.log(`Test API: Files in current directory: ${files.join(', ')}`);
    
    // Check if public directory exists
    const publicPath = path.join(cwd, 'public');
    const publicExists = fs.existsSync(publicPath);
    console.log(`Test API: Public directory exists: ${publicExists}`);
    
    if (publicExists) {
      const publicFiles = fs.readdirSync(publicPath);
      console.log(`Test API: Files in public directory: ${publicFiles.join(', ')}`);
    }
    
    // Check if scraped_events.json exists in public
    const scrapedEventsPath = path.join(publicPath, 'scraped_events.json');
    const scrapedEventsExists = fs.existsSync(scrapedEventsPath);
    console.log(`Test API: scraped_events.json exists in public: ${scrapedEventsExists}`);
    
    return NextResponse.json({
      cwd,
      files,
      publicExists,
      publicFiles: publicExists ? fs.readdirSync(publicPath) : [],
      scrapedEventsExists,
      scrapedEventsPath
    });
  } catch (error) {
    console.error('Test API error:', error);
    return NextResponse.json(
      { error: 'Test API failed', details: error },
      { status: 500 }
    );
  }
}
