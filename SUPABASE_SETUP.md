# Supabase Setup Guide for Multi-Agent Chat System

## Overview
This guide explains how to set up the Supabase backend for the multi-agent chat system. The system uses:
- Supabase Database for message storage
- Supabase Auth for user authentication
- Supabase Real-time for live updates
- Edge Functions for agent processing

## Setup Steps

### 1. Create Supabase Project

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Click "New Project"
3. Fill in project details
4. Note down your project URL and anon key

### 2. Database Setup

1. Run the initial migration:
   ```bash
   supabase db push migrations/20250110_init.sql
   ```

2. Run the trigger migration:
   ```bash
   supabase db push migrations/20250110_message_trigger.sql
   ```

### 3. Edge Function Deployment

1. Deploy the message processing function:
   ```bash
   supabase functions deploy process-message
   ```

2. Set up secrets:
   ```bash
   supabase secrets set --env-file ./supabase/.env
   ```

### 4. Real-time Configuration

1. Enable real-time in Supabase Dashboard:
   - Go to Database → Real-time
   - Enable real-time for `messages` table
   - Set up broadcast mode for real-time updates

### 5. Initial Data Setup

1. Create default agents:
   ```sql
   insert into public.agents (name, description, capabilities) values
   ('alex', 'General chat agent', '["general", "coordination"]'),
   ('sales', 'Sales specialist', '["sales", "pricing", "products"]'),
   ('marketing', 'Marketing specialist', '["marketing", "campaigns", "analytics"]'),
   ('growth', 'Growth specialist', '["growth", "acquisition", "retention"]'),
   ('brand', 'Brand specialist', '["brand", "identity", "messaging"]');
   ```

### 6. Environment Variables

Create `.env.local` in your frontend project:
```bash
REACT_APP_SUPABASE_URL=your_project_url
REACT_APP_SUPABASE_ANON_KEY=your_anon_key
```

### 7. Authentication Setup

1. Enable email auth in Supabase Dashboard:
   - Go to Authentication → Providers
   - Enable Email provider
   - Configure email templates

2. (Optional) Add additional auth providers:
   - Google
   - GitHub
   - Microsoft

## Security Configuration

### 1. Row Level Security (RLS)

The migrations include RLS policies for:
- Messages
- Channels
- Agents
- Session contexts

Review and modify policies as needed in SQL Editor.

### 2. API Security

1. Configure CORS in Supabase Dashboard:
   - Go to API Settings
   - Add your frontend domain to allowed origins

2. Review and restrict API permissions:
   - Go to Database → API
   - Review enabled APIs
   - Restrict as needed

## Monitoring

### 1. Database

Monitor in Supabase Dashboard:
- Database health
- Query performance
- Storage usage

### 2. Edge Functions

Monitor in Supabase Dashboard:
- Function invocations
- Error rates
- Response times

### 3. Real-time

Monitor in Supabase Dashboard:
- Connected clients
- Message throughput
- Channel usage

## Maintenance

### 1. Backups

1. Enable point-in-time recovery:
   - Go to Database → Backups
   - Enable PITR
   - Set retention period

2. Schedule regular backups:
   - Configure backup schedule
   - Test restore procedures

### 2. Updates

1. Database migrations:
   ```bash
   supabase db push
   ```

2. Edge Functions:
   ```bash
   supabase functions deploy
   ```

## Troubleshooting

### 1. Real-time Issues

1. Check connection status:
   ```javascript
   const status = supabase.realtime.status;
   ```

2. Monitor subscription:
   ```javascript
   const subscription = supabase
     .channel('*')
     .on('presence', console.log)
     .subscribe();
   ```

### 2. Edge Function Issues

1. Check logs:
   ```bash
   supabase functions logs process-message
   ```

2. Test locally:
   ```bash
   supabase functions serve process-message
   ```

### 3. Database Issues

1. Check performance:
   - Go to Database → Performance
   - Review slow queries
   - Optimize indexes

2. Monitor connections:
   - Check active connections
   - Review connection limits

## Next Steps

1. Implement additional features:
   - File attachments
   - Message reactions
   - Thread support

2. Scale considerations:
   - Monitor performance
   - Optimize queries
   - Add caching

3. Enhance security:
   - Add rate limiting
   - Implement audit logging
   - Enhanced RLS policies
