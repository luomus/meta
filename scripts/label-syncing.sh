# download labels
curl https://raw.githubusercontent.com/luomus/meta/refs/heads/main/labels.json -o labels.json

# install label syncer https://github.com/Financial-Times/github-label-sync
npm install -g github-label-sync

# sync labels with <REPO>
github-label-sync --access-token $GITHUB_PAT -A luomus/<REPO>
