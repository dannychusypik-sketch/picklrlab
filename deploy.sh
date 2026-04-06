#!/bin/bash
echo "🚀 Deploying PicklrLab..."
git add -A
git commit -m "Update: $(date +%Y-%m-%d)" --allow-empty
git push origin main
ssh -i ~/.ssh/sypik_vps root@206.189.144.88 "cd /var/www/picklrlab && git pull && npm install && npm run build && pm2 restart picklrlab"
echo "✅ Deploy complete: https://picklrlab.com"
