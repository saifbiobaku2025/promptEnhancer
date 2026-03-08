


# 1. Push to GitHub
git init && git add . && git commit -m "initial"
git remote add origin https://github.com/YOUR_USER/prompt-enhancer.git
git push -u origin main

# 2. Go to https://share.streamlit.io
# 3. Connect GitHub repo, set main file: app.py
# 4. Add secrets (replaces .env):
#    Settings → Secrets → paste your .env content as TOML:


### additional installation 
This resolve module not found 
python -m pip install streamlit-extras