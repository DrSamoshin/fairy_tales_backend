#!/usr/bin/env python3
"""
Simple test script for streaming story generation endpoint.
This script demonstrates how to consume the streaming API.
"""

import asyncio
import aiohttp
import json
import sys


async def test_streaming_endpoint():
    """Test the streaming story generation endpoint"""
    
    # Test data
    story_data = {
        "story_name": "Test Streaming Story",
        "hero_name": "Alice",
        "story_idea": "A magical adventure in a enchanted forest",
        "story_style": "Fantasy",
        "language": "en",
        "age": 8
    }
    
    # Headers (you'll need to add actual JWT token)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_JWT_TOKEN_HERE"
    }
    
    url = "http://localhost:8080/api/v1/stories/generate-stream/"
    
    print("Testing streaming story generation...")
    print(f"Story: {story_data['story_name']}")
    print(f"Hero: {story_data['hero_name']}")
    print("-" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=story_data, headers=headers) as response:
                
                if response.status != 200:
                    print(f"Error: HTTP {response.status}")
                    print(await response.text())
                    return
                
                print("Streaming response:")
                print("-" * 50)
                
                # Read streaming response
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove 'data: ' prefix
                        
                        try:
                            data = json.loads(data_str)
                            message_type = data.get('type')
                            
                            if message_type == 'started':
                                print(f"🚀 {data['message']}")
                                print()
                            
                            elif message_type == 'content':
                                # Print story content in real-time
                                print(data['data'], end='', flush=True)
                            
                            elif message_type == 'completed':
                                print("\n")
                                print("-" * 50)
                                print(f"✅ {data['message']}")
                                print(f"📝 Story ID: {data['story_id']}")
                                print(f"📏 Length: {data['story_length']} characters")
                            
                            elif message_type == 'error':
                                print("\n")
                                print(f"❌ Error: {data['message']}")
                        
                        except json.JSONDecodeError:
                            print(f"Invalid JSON: {data_str}")
    
    except aiohttp.ClientError as e:
        print(f"Network error: {e}")
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")


async def main():
    """Main function"""
    print("Streaming Story Generation Test")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
Usage: python test_streaming.py

This script tests the streaming story generation endpoint.

Before running:
1. Make sure the server is running on http://localhost:8080
2. Replace 'YOUR_JWT_TOKEN_HERE' with a valid JWT token
3. You can get a token by logging in through /api/v1/auth/login/

The script will show real-time story generation progress.
        """)
        return
    
    await test_streaming_endpoint()


if __name__ == "__main__":
    asyncio.run(main())
