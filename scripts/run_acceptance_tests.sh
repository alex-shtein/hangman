#!/bin/sh

# Note: script is expected to be run from root directory during the pipeline

echo 'Running acceptance tests...'

export CI_PROJECT_NAME="$1"
export DOCKERFILE="$2"

tag="$CI_PROJECT_NAME"
echo "Building Docker image hangman:$tag"
docker build -f "$DOCKERFILE" . -t hangman:"$tag"

testNumber=0
failedTests=0

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

assertExitCode() {
  echo "Exit code: actual=$1, expected=$2"
  if [ "$1" -ne "$2" ]; then
     printf "${RED}Test №%d failed${NC}\\n" ${testNumber}
     failedTests=$((failedTests+1))
  else
     printf "${GREEN}Test №%d passed${NC}\\n" ${testNumber}
  fi
}

assertResultEquals() {
  echo "Comparing results..."
  actual_clean=$(echo "$1" | tr -d '\r')
  echo "actual:[$actual_clean]"
  expected_clean=$(echo "$2" | tr -d '\r')
  echo "expected:[$expected_clean]"
  actual_file=$(mktemp)
  expected_file=$(mktemp)
  echo "$actual_clean" > "$actual_file"
  echo "$expected_clean" > "$expected_file"
  diff "$actual_file" "$expected_file"
  exit_code=$?
  rm -f "$actual_file" "$expected_file"
  assertExitCode $exit_code 0
}

verifyAllTestsPassed() {
  printf "\\nVerifying all tests passed...\\n"
  echo "Total failed tests: $failedTests"
  if [ "$failedTests" -ne 0 ]; then
     printf "${RED}Some tests have failed!${NC}\\n"
     exit 1
  else
     printf "${GREEN}All tests passed${NC}\\n"
     exit 0
  fi
}

runTest() {
  echo "Test [№$testNumber][$1]; expected exit code: $2; args: $3"
  word1=$(echo "$3" | cut -d ' ' -f 1)
  word2=$(echo "$3" | cut -d ' ' -f 2)
  expected=$(echo "$3" | cut -d ' ' -f 3)
  actual=$(docker run --rm --memory=256m --cpus=1 hangman:"$tag" "$word1" "$word2")
  assertResultEquals "$actual" "$expected"
  testNumber=$((testNumber + 1))
}

printf "\\nRunning positive tests...\\n"
while IFS= read -r line; do
  runTest "positive" 0 "$line"
done < "scripts/data/positive_tests.txt"

printf "\\nRunning negative tests...\\n"
while IFS= read -r line; do
  runTest "negative" 0 "$line"
done < "scripts/data/negative_tests.txt"

verifyAllTestsPassed
