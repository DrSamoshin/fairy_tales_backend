# Streaming Story Generation API

## Overview
The streaming endpoint `/api/v1/stories/generate-stream/` allows real-time story generation with Server-Sent Events (SSE).

## Features
- ✅ Real-time streaming of story content
- ✅ Authentication required
- ✅ Automatic story saving upon completion
- ✅ Disconnect detection (no save if interrupted)
- ✅ Error handling and reporting

## Endpoint Details

### POST `/api/v1/stories/generate-stream/`

**Authentication:** Required (JWT Bearer token)

**Request Body:**
```json
{
  "story_name": "The Magic Forest Adventure",
  "hero_name": "Alice",
  "story_idea": "A young girl discovers a magical forest",
  "story_style": "Fantasy",
  "language": "en",
  "age": 8
}
```

**Response Format:** Server-Sent Events (SSE)

## Response Messages

### 1. Started Message
```json
{
  "type": "started",
  "message": "Starting generation of 'The Magic Forest Adventure'"
}
```

### 2. Content Chunks
```json
{
  "type": "content", 
  "data": "Once upon a time, there was a brave little girl named Alice..."
}
```

### 3. Completion Message
```json
{
  "type": "completed",
  "story_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Story generated and saved successfully",
  "story_length": 1234
}
```

### 4. Error Message
```json
{
  "type": "error",
  "message": "Generation failed: OpenAI API error"
}
```

## Usage Examples

### cURL Example
```bash
curl -X POST "http://localhost:8080/api/v1/stories/generate-stream/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "story_name": "Test Story",
    "hero_name": "Hero",
    "story_idea": "A magical adventure",
    "story_style": "Fantasy", 
    "language": "en",
    "age": 8
  }' \
  --no-buffer
```

### JavaScript (EventSource)
```javascript
const eventSource = new EventSource('/api/v1/stories/generate-stream/', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
});

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'started':
      console.log('Generation started:', data.message);
      break;
      
    case 'content':
      // Append content to display
      document.getElementById('story').innerHTML += data.data;
      break;
      
    case 'completed':
      console.log('Story saved with ID:', data.story_id);
      eventSource.close();
      break;
      
    case 'error':
      console.error('Error:', data.message);
      eventSource.close();
      break;
  }
};

eventSource.onerror = function(event) {
  console.error('SSE error:', event);
  eventSource.close();
};
```

### Python (aiohttp)
```python
import aiohttp
import json

async def stream_story():
    story_data = {
        "story_name": "Test Story",
        "hero_name": "Alice", 
        "story_idea": "A magical forest adventure",
        "story_style": "Fantasy",
        "language": "en", 
        "age": 8
    }
    
    headers = {
        "Authorization": "Bearer YOUR_JWT_TOKEN",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'http://localhost:8080/api/v1/stories/generate-stream/',
            json=story_data,
            headers=headers
        ) as response:
            
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    
                    if data['type'] == 'content':
                        print(data['data'], end='', flush=True)
                    elif data['type'] == 'completed':
                        print(f"\nStory saved: {data['story_id']}")
```

## Behavior Details

### Connection Management
- **Client Disconnect:** If client disconnects during generation, story is NOT saved
- **Server Error:** If generation fails, error message is sent via SSE
- **Completion:** Story is saved to database only after full generation

### Performance
- **Real-time Streaming:** Content appears as it's generated
- **No Buffering:** Headers disable server-side buffering
- **Efficient:** Uses async generators for memory efficiency

### Error Handling
- **Authentication:** 401 if no valid JWT token
- **OpenAI Errors:** Gracefully handled and reported
- **Network Issues:** Client-side reconnection recommended

## Testing

Use the provided test script:
```bash
python test_streaming.py
```

Or test with curl to see raw SSE output.

## Security Notes
- JWT authentication required for all requests
- Stories are associated with authenticated user
- Rate limiting recommended for production use
- HTTPS required in production
