CUR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
git pull 
cd "$CUR_DIR"

docker-compose down --remove-orphans 
docker images | grep ai-tutor-groq | awk '{print \$3}' | xargs -r docker rmi -f
docker-compose up -d --build
