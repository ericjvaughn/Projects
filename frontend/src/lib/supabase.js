import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Real-time subscription for chat messages
export const subscribeToMessages = (channelId, callback) => {
  const subscription = supabase
    .channel(`chat:${channelId}`)
    .on('postgres_changes', {
      event: '*',
      schema: 'public',
      table: 'messages',
      filter: `channel_id=eq.${channelId}`
    }, callback)
    .subscribe();

  return () => {
    supabase.removeChannel(subscription);
  };
};

// Message operations
export const messageService = {
  async sendMessage({ content, channelId, agentMention, metadata = {} }) {
    const user = supabase.auth.user();
    
    return await supabase
      .from('messages')
      .insert({
        content,
        channel_id: channelId,
        user_id: user?.id,
        agent_mention: agentMention,
        metadata
      });
  },

  async getMessages(channelId, limit = 50) {
    return await supabase
      .from('messages')
      .select(`
        *,
        user:user_id (
          id,
          email,
          user_metadata
        )
      `)
      .eq('channel_id', channelId)
      .order('created_at', { ascending: false })
      .limit(limit);
  }
};

// Channel operations
export const channelService = {
  async createChannel({ name, metadata = {} }) {
    return await supabase
      .from('channels')
      .insert({
        name,
        metadata
      });
  },

  async getChannels() {
    return await supabase
      .from('channels')
      .select('*')
      .order('created_at', { ascending: false });
  }
};

// Agent operations
export const agentService = {
  async getAgents() {
    return await supabase
      .from('agents')
      .select('*')
      .order('name');
  },

  async updateAgentStatus(agentId, status) {
    return await supabase
      .from('agents')
      .update({ status })
      .eq('id', agentId);
  }
};
