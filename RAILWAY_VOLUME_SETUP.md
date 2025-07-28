# Railway Volume Configuration Guide

## Setting Up Persistent Storage

Railway mounts volumes at dynamic paths. To ensure your application finds the volume, you need to set an environment variable.

### Steps:

1. **In Railway Dashboard:**
   - Go to your service settings
   - Navigate to the "Variables" tab
   - Add a new variable:
     ```
     RAILWAY_VOLUME_MOUNT_PATH=/var/lib/containers/railwayapp/bind-mounts/[YOUR_VOLUME_ID]
     ```
   - Replace `[YOUR_VOLUME_ID]` with your actual volume path from the logs

2. **From Your Logs:**
   Your volume is mounted at:
   ```
   /var/lib/containers/railwayapp/bind-mounts/6ff6b026-376a-4589-a15e-01b17a6b148d/vol_l1xdc0l5fe959627
   ```

3. **Set the Environment Variable:**
   ```
   RAILWAY_VOLUME_MOUNT_PATH=/var/lib/containers/railwayapp/bind-mounts/6ff6b026-376a-4589-a15e-01b17a6b148d/vol_l1xdc0l5fe959627
   ```

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

After setting these variables and redeploying:

1. Check logs for: "Using Railway volume at /var/lib/... for persistent storage"
2. Anthropic provider should initialize without errors
3. All providers (OpenAI, Anthropic, Google) should be registered

## Current Status

✅ **Working:**
- OpenAI provider
- Google provider (fixed!)
- Qwen provider (mock mode)
- Volume is mounted (needs env var)

⚠️ **Needs Attention:**
- Anthropic API key (401 error)
- Volume path environment variable
