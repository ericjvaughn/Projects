const dotenv = require('dotenv');
const result = dotenv.config();
console.log('Dotenv Config Result:', result);

const OpenAI = require('openai');
const { createClient } = require('@supabase/supabase-js');

// Debugging environment variables
console.log('Environment Variables:');
console.log('OPENAI_API_KEY:', process.env.OPENAI_API_KEY ? 'SET' : 'NOT SET');
console.log('SUPABASE_URL:', process.env.SUPABASE_URL);
console.log('SUPABASE_ANON_KEY:', process.env.SUPABASE_ANON_KEY ? 'SET' : 'NOT SET');

// Test OpenAI Connection
async function testOpenAI() {
    const openai = new OpenAI({
        apiKey: process.env.OPENAI_API_KEY,
    });
    
    try {
        const response = await openai.chat.completions.create({
            model: "gpt-4",
            messages: [{ role: "user", content: "Hello, are you working?" }],
        });
        console.log("OpenAI Connection: SUCCESS ✅");
        console.log("Response:", response.choices[0].message.content);
    } catch (error) {
        console.error("OpenAI Connection: FAILED ❌");
        console.error("Error:", error.message);
    }
}

// Test Supabase Connection
async function testSupabase() {
    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_ANON_KEY;
    
    console.log("Using Supabase URL:", supabaseUrl);
    console.log("Using Supabase Key:", supabaseKey ? 'SET' : 'NOT SET');
    
    const supabase = createClient(supabaseUrl, supabaseKey);
    
    try {
        const { data, error } = await supabase.from('agents').select('*').limit(1);
        if (error) throw error;
        console.log("Supabase Connection: SUCCESS ✅");
        console.log("Data:", data);
    } catch (error) {
        console.error("Supabase Connection: FAILED ❌");
        console.error("Error:", error.message);
    }
}

// Run tests
async function runTests() {
    console.log("🔄 Testing OpenAI Connection...");
    await testOpenAI();
    console.log("\n🔄 Testing Supabase Connection...");
    await testSupabase();
}

runTests();
