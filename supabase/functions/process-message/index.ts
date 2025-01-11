import { serve } from 'https://deno.land/std@0.190.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import OpenAI from 'https://esm.sh/openai@4.0.0'

// Configuration
const OPENAI_MODEL = 'gpt-4-turbo'
const MAX_CONTEXT_MESSAGES = 10
const MAX_RESPONSE_TOKENS = 500

// Interfaces
interface Agent {
  id: string
  name: string
  capabilities: string[]
  system_prompt: string
}

interface Message {
  id: string
  channel_id: string
  sender_id: string
  content: string
  agent_mention?: string
  metadata?: Record<string, any>
}

// CORS Headers
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

// OpenAI Client setup
const openaiApiKey = Deno.env.get('OPENAI_API_KEY')
if (!openaiApiKey) {
  throw new Error('OPENAI_API_KEY is not set')
}
const openai = new OpenAI({
  apiKey: openaiApiKey
})

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Initialize Supabase client
    const supabaseUrl = Deno.env.get('SUPABASE_URL')
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
    
    if (!supabaseUrl || !supabaseServiceKey) {
      throw new Error('Supabase URL or Service Key is missing')
    }

    const supabase = createClient(supabaseUrl, supabaseServiceKey)

    // Parse incoming message
    const { record } = await req.json()
    const message = record as Message

    // Fetch available agents
    const { data: agents, error: agentError } = await supabase
      .from('agents')
      .select('*')
      .eq('status', 'active')

    if (agentError) throw agentError

    // Process message and get response
    const response = await processMessage(message, agents as Agent[], supabase)

    // Update message with AI response
    const { error: updateError } = await supabase
      .from('messages')
      .update({
        content: response.content,
        agent_id: response.agent_id,
        metadata: {
          ...message.metadata,
          tokens_used: response.tokens_used,
          agent_confidence: response.confidence
        },
        status: 'delivered'
      })
      .eq('id', message.id)

    if (updateError) throw updateError

    return new Response(JSON.stringify(response), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 200,
    })

  } catch (error) {
    console.error('Message Processing Error:', error)
    return new Response(JSON.stringify({ 
      error: 'Failed to process message', 
      details: error instanceof Error ? error.message : 'Unknown error' 
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 500,
    })
  }
})

async function processMessage(
  message: Message, 
  agents: Agent[], 
  supabase: any
): Promise<{
  content: string
  agent_id: string
  confidence: number
  tokens_used: {
    input: number
    output: number
    total: number
  }
}> {
  // Retrieve conversation context
  const { data: contextMessages, error: contextError } = await supabase
    .from('messages')
    .select('content, sender_id, agent_id')
    .eq('channel_id', message.channel_id)
    .order('created_at', { ascending: false })
    .limit(MAX_CONTEXT_MESSAGES)

  if (contextError) throw contextError

  // Determine best agent
  const selectedAgent = selectBestAgent(message, agents)

  // Prepare conversation history
  const conversationHistory = contextMessages.reverse().map(msg => ({
    role: msg.sender_id === message.sender_id ? 'user' : 'assistant',
    content: msg.content
  }))

  // Generate AI response
  const aiResponse = await generateAIResponse(
    message, 
    selectedAgent, 
    conversationHistory
  )

  return {
    content: aiResponse.content,
    agent_id: selectedAgent.id,
    confidence: aiResponse.confidence,
    tokens_used: aiResponse.tokens_used
  }
}

function selectBestAgent(message: Message, agents: Agent[]): Agent {
  // If agent is mentioned, prioritize that agent
  if (message.agent_mention) {
    const mentionedAgent = agents.find(agent => 
      agent.name.toLowerCase() === message.agent_mention?.toLowerCase()
    )
    if (mentionedAgent) return mentionedAgent
  }

  // Otherwise, use a simple capability matching algorithm
  const rankedAgents = agents
    .map(agent => ({
      agent,
      score: calculateAgentRelevance(message.content, agent)
    }))
    .sort((a, b) => b.score - a.score)

  return rankedAgents[0].agent
}

function calculateAgentRelevance(content: string, agent: Agent): number {
  const contentLower = content.toLowerCase()
  return agent.capabilities.reduce((score, capability) => {
    return score + (contentLower.includes(capability.toLowerCase()) ? 1 : 0)
  }, 0) / agent.capabilities.length
}

async function generateAIResponse(
  message: Message, 
  agent: Agent, 
  conversationHistory: Array<{role: string, content: string}>
) {
  try {
    const systemMessage = {
      role: 'system',
      content: agent.system_prompt || `You are an AI assistant specializing in ${agent.capabilities.join(', ')}.`
    }

    const completion = await openai.chat.completions.create({
      model: OPENAI_MODEL,
      messages: [systemMessage, ...conversationHistory, {
        role: 'user',
        content: message.content
      }],
      max_tokens: MAX_RESPONSE_TOKENS,
      temperature: 0.7
    })

    const responseContent = completion.choices[0]?.message?.content || 
      "I apologize, but I couldn't generate a response."

    return {
      content: responseContent,
      confidence: 0.8,
      tokens_used: {
        input: completion.usage?.prompt_tokens || 0,
        output: completion.usage?.completion_tokens || 0,
        total: completion.usage?.total_tokens || 0
      }
    }
  } catch (error) {
    console.error('OpenAI API Error:', error)
    return {
      content: "I'm experiencing technical difficulties. Please try again later.",
      confidence: 0,
      tokens_used: {
        input: 0,
        output: 0,
        total: 0
      }
    }
  }
}
