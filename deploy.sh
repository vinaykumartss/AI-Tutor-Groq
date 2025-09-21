CUR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
git pull origin production 
cd "$CUR_DIR"

docker compose down --remove-orphans

# build with cache for speed
docker compose up -d --build

# cleanup old cache/images
docker builder prune -af --filter "until=24h"
docker image prune -af



