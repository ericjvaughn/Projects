-- Function to invoke Edge Function for message processing
CREATE OR REPLACE FUNCTION process_new_message()
RETURNS TRIGGER AS $$
DECLARE
    payload JSONB;
    response JSONB;
BEGIN
    -- Prepare the payload with the new message record
    payload := jsonb_build_object(
        'record', row_to_json(NEW)
    );

    -- Invoke Edge Function asynchronously
    -- Note: Replace with your actual Edge Function URL
    PERFORM net.http_post(
        url := ((SELECT value FROM secrets.edge_functions WHERE key = 'process_message_url')),
        headers := jsonb_build_object(
            'Content-Type', 'application/json',
            'Authorization', 'Bearer ' || (SELECT value FROM secrets.edge_functions WHERE key = 'process_message_key')
        ),
        body := payload
    );

    -- Update user-agent interaction tracking
    INSERT INTO public.user_agents (user_id, agent_id, interaction_count, last_interaction_at)
    VALUES (
        NEW.sender_id, 
        NEW.agent_id, 
        COALESCE((
            SELECT interaction_count + 1 
            FROM public.user_agents 
            WHERE user_id = NEW.sender_id AND agent_id = NEW.agent_id
        ), 1),
        NOW()
    )
    ON CONFLICT (user_id, agent_id) 
    DO UPDATE SET 
        interaction_count = EXCLUDED.interaction_count + 1,
        last_interaction_at = NOW();

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for new messages
DROP TRIGGER IF EXISTS trigger_process_new_message ON public.messages;
CREATE TRIGGER trigger_process_new_message
AFTER INSERT ON public.messages
FOR EACH ROW 
EXECUTE FUNCTION process_new_message();
