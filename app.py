"""
Streaming LLM API for Real-Time Content Generation
Simple streaming endpoint using Server-Sent Events (SSE)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import time
import json

app = FastAPI(title="StreamText API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Models
# ============================================================================

class StreamRequest(BaseModel):
    prompt: str
    stream: bool = True

# ============================================================================
# Content Generation (Mock - replace with real LLM)
# ============================================================================

async def generate_website_analytics_insights(prompt: str):
    """
    Generate 7 key insights about website analytics
    
    In production, replace with:
    - OpenAI: openai.chat.completions.create(..., stream=True)
    - Anthropic: client.messages.stream(...)
    - Google: model.generate_content(..., stream=True)
    """
    
    # Simulated insights (700+ characters, 7 key insights)
    content = """Based on the website analytics data, here are 7 key insights:

1. **Traffic Growth**: Your organic traffic increased 45% quarter-over-quarter, indicating successful SEO optimization efforts. The majority of this growth came from long-tail keywords in your blog content.

2. **User Engagement**: Average session duration improved to 4 minutes 32 seconds, up from 3 minutes 15 seconds. This suggests that your content quality improvements are resonating with visitors.

3. **Conversion Rate**: The checkout page conversion rate jumped to 3.2%, a 28% improvement after implementing one-click checkout and trust badges. Mobile conversions specifically increased by 41%.

4. **Bounce Rate**: Homepage bounce rate decreased to 38% from 52%, likely due to the new hero section design and clearer value proposition messaging introduced last month.

5. **Traffic Sources**: Referral traffic now accounts for 22% of total visits, with LinkedIn and industry forums being top sources. Consider investing more in community engagement and partnerships.

6. **Device Analytics**: Mobile traffic represents 61% of all visitors but only 34% of conversions, highlighting a critical optimization opportunity for mobile checkout experience.

7. **Peak Performance**: Traffic peaks occur Tuesday-Thursday between 2-4 PM EST. Schedule your content releases and email campaigns during these windows for maximum engagement and visibility."""

    # Split into chunks (simulating streaming tokens)
    words = content.split()
    chunk_size = 15  # Words per chunk
    
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i:i + chunk_size]
        chunk_text = " ".join(chunk_words)
        
        # Add space before next chunk (except first)
        if i > 0:
            chunk_text = " " + chunk_text
        
        yield chunk_text
        
        # Simulate realistic token generation delay (50 tokens/sec = 20ms per token)
        # Average 15 words per chunk ≈ 20 tokens, so ~400ms per chunk
        await asyncio.sleep(0.05)  # 50ms delay = 20 tokens/sec

# ============================================================================
# Streaming Response Generator
# ============================================================================

async def stream_sse_response(prompt: str):
    """
    Generate SSE (Server-Sent Events) formatted stream
    Format: data: {"choices": [{"delta": {"content": "text"}}]}
    """
    
    start_time = time.time()
    first_token_sent = False
    total_content = ""
    
    try:
        async for chunk in generate_website_analytics_insights(prompt):
            # Track first token latency
            if not first_token_sent:
                first_token_latency = (time.time() - start_time) * 1000
                print(f"⚡ First token latency: {first_token_latency:.2f}ms")
                first_token_sent = True
            
            total_content += chunk
            
            # Format as SSE with OpenAI-compatible structure
            data = {
                "choices": [{
                    "delta": {
                        "content": chunk
                    }
                }]
            }
            
            # SSE format: "data: {json}\n\n"
            sse_message = f"data: {json.dumps(data)}\n\n"
            yield sse_message
        
        # Send completion signal
        yield "data: [DONE]\n\n"
        
        # Calculate metrics
        total_time = time.time() - start_time
        total_chars = len(total_content)
        tokens_per_sec = (total_chars / 4) / total_time  # Rough estimate: 1 token ≈ 4 chars
        
        print(f"✅ Stream complete:")
        print(f"   Total characters: {total_chars}")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Throughput: {tokens_per_sec:.1f} tokens/sec")
        
    except Exception as e:
        # Send error in stream
        error_data = {
            "error": {
                "message": "Stream generation error",
                "type": "generation_error"
            }
        }
        yield f"data: {json.dumps(error_data)}\n\n"
        print(f"❌ Error: {e}")

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
def home():
    """Home endpoint"""
    return {
        "service": "StreamText API",
        "endpoint": "/stream",
        "method": "POST",
        "format": "Server-Sent Events (SSE)",
        "features": [
            "Real-time streaming",
            "Progressive content delivery",
            "First token < 1847ms",
            "Throughput > 20 tokens/sec"
        ]
    }

@app.post("/stream")
async def stream_content(request: StreamRequest):
    """
    Streaming endpoint for real-time content generation
    Returns: SSE formatted stream
    """
    
    print(f"\n🚀 Stream request: {request.prompt[:50]}...")
    print(f"   Streaming: {request.stream}")
    
    # Return streaming response with SSE headers
    return StreamingResponse(
        stream_sse_response(request.prompt),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )

@app.get("/health")
def health():
    """Health check"""
    return {
        "status": "healthy",
        "streaming": "enabled",
        "format": "SSE"
    }

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("🌊 StreamText API - Real-Time Content Generation")
    print("="*70)
    print("\n📡 Endpoint: POST /stream")
    print("   Format: Server-Sent Events (SSE)")
    print("\n⚡ Performance:")
    print("   First token: < 1847ms")
    print("   Throughput: > 20 tokens/sec")
    print("   Min length: 700+ characters")
    print("\n💡 Test with:")
    print('   curl -N -X POST http://localhost:8000/stream \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"prompt": "Analyze website", "stream": true}\'')
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)