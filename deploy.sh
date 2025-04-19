CUR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
git pull 
cd "$CUR_DIR"

docker-compose down --remove-orphans 
docker-compose up -d --build
