-- Enable Row Level Security
ALTER TABLE public.agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.channels ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_agents ENABLE ROW LEVEL SECURITY;

-- Agents Table
CREATE TABLE public.agents (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    capabilities TEXT[] DEFAULT '{}',
    system_prompt TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'training')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Channels Table
CREATE TABLE public.channels (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT DEFAULT 'chat' CHECK (type IN ('chat', 'thread', 'project')),
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Messages Table
CREATE TABLE public.messages (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    channel_id UUID REFERENCES public.channels(id),
    sender_id UUID REFERENCES auth.users(id),
    agent_id UUID REFERENCES public.agents(id),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    parent_message_id UUID REFERENCES public.messages(id),
    status TEXT DEFAULT 'sent' CHECK (status IN ('sent', 'delivered', 'read', 'error')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User Agents (for tracking user-agent interactions)
CREATE TABLE public.user_agents (
    user_id UUID REFERENCES auth.users(id),
    agent_id UUID REFERENCES public.agents(id),
    interaction_count INTEGER DEFAULT 0,
    last_interaction_at TIMESTAMPTZ,
    PRIMARY KEY (user_id, agent_id)
);

-- Indexes for performance
CREATE INDEX idx_messages_channel ON public.messages(channel_id);
CREATE INDEX idx_messages_sender ON public.messages(sender_id);
CREATE INDEX idx_messages_agent ON public.messages(agent_id);
CREATE INDEX idx_user_agents_interaction ON public.user_agents(interaction_count);

-- Triggers for updated_at columns
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_agents_modtime
    BEFORE UPDATE ON public.agents
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_channels_modtime
    BEFORE UPDATE ON public.channels
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- Row Level Security Policies

-- Agents Policies
CREATE POLICY "Agents visible to all" ON public.agents
    FOR SELECT USING (true);

-- Channels Policies
CREATE POLICY "Users can view their own channels" ON public.channels
    FOR SELECT USING (auth.uid() = created_by);

CREATE POLICY "Users can create channels" ON public.channels
    FOR INSERT WITH CHECK (auth.uid() = created_by);

-- Messages Policies
CREATE POLICY "Users can view messages in their channels" ON public.messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.channels 
            WHERE id = public.messages.channel_id 
            AND created_by = auth.uid()
        )
    );

CREATE POLICY "Users can insert messages" ON public.messages
    FOR INSERT WITH CHECK (auth.uid() = sender_id);

-- User Agents Policies
CREATE POLICY "Users can view their own agent interactions" ON public.user_agents
    FOR SELECT USING (auth.uid() = user_id);

-- Initial data seeding
INSERT INTO public.agents (name, description, capabilities, system_prompt) VALUES
('alex', 'General assistant for coordination and support', 
 ARRAY['general', 'coordination', 'support'], 
 'You are ALEX, a versatile AI assistant designed to help with a wide range of tasks. Provide clear, concise, and helpful responses.'),

('sales', 'Sales and product information specialist', 
 ARRAY['sales', 'pricing', 'products', 'customer support'], 
 'You are a professional sales agent. Focus on understanding customer needs, providing detailed product information, and guiding potential customers towards the right solution.'),

('marketing', 'Marketing strategy and content expert', 
 ARRAY['marketing', 'content', 'strategy', 'analytics'], 
 'You are a marketing strategist. Provide insights on marketing trends, content creation, campaign optimization, and audience targeting.'),

('growth', 'Business growth and user acquisition specialist', 
 ARRAY['growth', 'user acquisition', 'retention', 'metrics'], 
 'You are a growth expert focused on helping businesses expand their user base and improve retention. Provide data-driven strategies and actionable insights.'),

('brand', 'Brand identity and communication specialist', 
 ARRAY['branding', 'identity', 'communication', 'positioning'], 
 'You are a brand strategist. Help maintain consistent brand messaging, develop brand guidelines, and ensure brand authenticity across all communications.');
