# Railway Volume Configuration Guide

## Setting Up Persistent Storage

When creating a volume in Railway, you specify the mount path. The application is configured to use `/data`.

### Steps:

1. **In Railway Dashboard:**
   - Go to your service settings
   - Navigate to the "Volumes" section
   - Create or edit your volume
   - Set the mount path to: `/data`

2. **That's it!** 
   The application will automatically detect and use the volume at `/data` for persistent storage.

## Anthropic API Key Troubleshooting

The Anthropic API key is showing a 401 error. To fix this:

1. **Verify the API Key Format:**
   - Should start with `sk-ant-api03-`
   - No extra spaces before or after
   - Full example: `sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

2. **In Railway Dashboard:**
   - Check the `ANTHROPIC_API_KEY` variable
   - Make sure there are no quotes around the key
   - Try deleting and re-adding the key

3. **Get a New Key (if needed):**
   - Visit [console.anthropic.com](https://console.anthropic.com)
   - Navigate to API Keys
   - Create a new key
   - Update in Railway

## Verifying Everything Works

After setting the volume mount path to `/data` and fixing the Anthropic key:

1. Check logs for: "Using volume at /data for persistent storage"
2. Anthropic provider should initialize without errors
3. All providers (OpenAI, Anthropic, Google) should be registered

## Current Status

✅ **Working:**
- OpenAI provider
- Google provider (fixed!)
- Qwen provider (mock mode)
- Volume mounting (just set mount path to `/data`)

⚠️ **Needs Attention:**
- Anthropic API key (401 error - needs valid key)
