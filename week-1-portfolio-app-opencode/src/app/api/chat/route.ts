import { NextResponse } from 'next/server'
import { AI_MODEL, AI_SYSTEM_PROMPT } from '@/lib/constants'

export async function POST(req: Request) {
  try {
    const { messages } = await req.json()

    const apiKey = process.env.OPENROUTER_API_KEY
    if (!apiKey) {
      return NextResponse.json({ error: 'API key not configured' }, { status: 500 })
    }

    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
        'HTTP-Referer': 'https://localhost:3000',
        'X-Title': 'Elias Hridoy Portfolio',
      },
      body: JSON.stringify({
        model: AI_MODEL,
        messages: [
          { role: 'system', content: AI_SYSTEM_PROMPT },
          ...messages,
        ],
        stream: true,
      }),
    })

    if (!response.ok) {
      const error = await response.text()
      return NextResponse.json({ error: `API error: ${error}` }, { status: response.status })
    }

    const stream = new ReadableStream({
      async start(controller) {
        const reader = response.body?.getReader()
        if (!reader) {
          controller.close()
          return
        }

        const decoder = new TextDecoder()
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          const lines = chunk.split('\n').filter(line => line.startsWith('data: '))

          for (const line of lines) {
            const data = line.slice(6)
            if (data === '[DONE]') continue
            try {
              const parsed = JSON.parse(data)
              const content = parsed.choices?.[0]?.delta?.content || ''
              if (content) {
                controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify({ content })}\n\n`))
              }
            } catch {
              // skip parse errors
            }
          }
        }
        controller.close()
      },
    })

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    })
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
