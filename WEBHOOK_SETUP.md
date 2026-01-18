# Make.com Webhook Setup (Quick Guide)

## Step 1: Create Webhook in Make.com

1. Go to https://make.com
2. Click "Create a new scenario"
3. Click the **+** button to add a module
4. Search for "Webhooks"
5. Select **"Custom webhook"**
6. Click **"Create a webhook"**
7. Give it a name: "BuilderFeed Tweets"
8. Click **"Save"**
9. **Copy the webhook URL** (looks like: `https://hook.us1.make.com/abc123xyz...`)

```
Send the API key using the x-make-apikey HTTP header.

Add one or more API keys to enable authentication. If any key matches, access is granted.
https://hook.us2.make.com/isbfj2cwrb5wp6nu7trm5hbmpx37rpie
Name: uAWSBuilderFeed
Api Key Value: q3RewcYfJXByy-2
```

## Step 2: Add Webhook URL to .env

```bash
cd /Users/robertoallende/code/builderfeed
cp .env.example .env
```

Edit `.env` and add:
```
MAKECOM_WEBHOOK_URL=https://hook.us1.make.com/your_webhook_url_here
```

## Step 3: Complete Make.com Scenario

Back in Make.com, continue building the scenario:

1. **After Webhook module, add: Buffer - Create a Post**
   - Search for "Buffer"
   - Select "Create a Post"
   - Connect your Buffer account
   - Map fields:
     - **Text**: Click and select `text` from webhook data
     - **Profile IDs**: Select your Twitter profile
     - **Now**: Set to `false` (schedule for optimal time)

2. **Save and Activate**
   - Click "Save"
   - Toggle scenario "ON"

## Step 4: Test It!

```bash
cd /Users/robertoallende/code/builderfeed
source .venv/bin/activate

# Post one tweet
PYTHONPATH=. python -c "from src.twitter import post_tweet; result = post_tweet(); print(f'Mode: {result[\"mode\"]}')"
```

**Expected output:** `Mode: webhook`

**Check:**
1. Make.com execution history - should show 1 execution
2. Buffer dashboard - should show scheduled tweet
3. Twitter - wait for Buffer to post (or post manually from Buffer)

## How It Works

```
Pipeline → HTTP POST → Make.com Webhook → Buffer → Twitter
```

**Instant delivery!** No file watching, no delays. Tweet goes straight to Make.com.

## Troubleshooting

**Mode shows "json_fallback":**
- Webhook URL not set in .env
- Webhook URL incorrect
- Make.com scenario not active

**Make.com shows error:**
- Check Buffer connection
- Verify Twitter profile selected
- Check webhook data format

**Buffer not posting:**
- Verify Buffer has Twitter connected
- Check Buffer posting permissions
- Try posting manually from Buffer first

## Cost

- **Make.com Free**: 1,000 operations/month
- **Buffer Free**: 10 scheduled posts
- **Total**: $0 (or $6/month for unlimited Buffer)

## Advantages over File Method

✅ Instant delivery (no 15-minute wait)  
✅ No Dropbox/Drive needed  
✅ Simpler setup  
✅ More reliable  
✅ Real-time monitoring in Make.com  

---

**Ready?** Get your webhook URL from Make.com and add it to `.env`!
