docker build ./add -t smixi/add-ms &
docker build ./eval -t smixi/eval-ms &
docker build ./sub -t smixi/sub-ms &
docker build ./mult -t smixi/mult-ms &
docker build ./div -t smixi/div-ms &
docker build ./parse -t smixi/parse-ms

docker push smixi/add-ms
docker push smixi/eval-ms
docker push smixi/sub-ms
docker push smixi/mult-ms
docker push smixi/div-ms
docker push smixi/parse-ms