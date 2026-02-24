#!/bin/bash
# Claude hook: lint files after Edit/Write
# Supports Python (ruff + black), TypeScript/JS (eslint + prettier), Kotlin (ktlint), Swift (swiftlint)

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ -z "$FILE_PATH" ]] || [[ ! -f "$FILE_PATH" ]]; then
    exit 0
fi

ERRORS=""

case "$FILE_PATH" in
    *.py)
        # Python: ruff + black
        if command -v ruff &> /dev/null; then
            RUFF_OUTPUT=$(ruff check --fix "$FILE_PATH" 2>&1)
            if [[ $? -ne 0 ]]; then
                ERRORS+="ruff: $RUFF_OUTPUT"$'\n'
            fi
        fi
        if command -v black &> /dev/null; then
            BLACK_OUTPUT=$(black --quiet "$FILE_PATH" 2>&1)
            if [[ $? -ne 0 ]]; then
                ERRORS+="black: $BLACK_OUTPUT"$'\n'
            fi
        fi
        ;;

    *.ts|*.tsx|*.js|*.jsx)
        # TypeScript/JavaScript: eslint + prettier
        PROJECT_DIR=$(echo "$FILE_PATH" | sed 's|\(/frontend\)/.*|\1|; t; s|\(/web\)/.*|\1|; t')
        if [[ -z "$PROJECT_DIR" ]]; then
            PROJECT_DIR="$CLAUDE_PROJECT_DIR"
        fi
        if command -v npx &> /dev/null; then
            if [[ -f "$PROJECT_DIR/.eslintrc" ]] || [[ -f "$PROJECT_DIR/.eslintrc.js" ]] || [[ -f "$PROJECT_DIR/.eslintrc.json" ]] || [[ -f "$PROJECT_DIR/eslint.config.js" ]] || [[ -f "$PROJECT_DIR/eslint.config.mjs" ]]; then
                ESLINT_OUTPUT=$(npx eslint --fix "$FILE_PATH" 2>&1)
                if [[ $? -ne 0 ]]; then
                    ERRORS+="eslint: $ESLINT_OUTPUT"$'\n'
                fi
            fi
            if [[ -f "$PROJECT_DIR/.prettierrc" ]] || [[ -f "$PROJECT_DIR/.prettierrc.js" ]] || [[ -f "$PROJECT_DIR/.prettierrc.json" ]] || [[ -f "$PROJECT_DIR/prettier.config.js" ]]; then
                PRETTIER_OUTPUT=$(npx prettier --write "$FILE_PATH" 2>&1)
                if [[ $? -ne 0 ]]; then
                    ERRORS+="prettier: $PRETTIER_OUTPUT"$'\n'
                fi
            fi
        fi
        ;;

    *.kt|*.kts)
        # Kotlin: ktlint
        if command -v ktlint &> /dev/null; then
            KTLINT_OUTPUT=$(ktlint --format "$FILE_PATH" 2>&1)
            if [[ $? -ne 0 ]]; then
                ERRORS+="ktlint: $KTLINT_OUTPUT"$'\n'
            fi
        fi
        ;;

    *.swift)
        # Swift: swiftlint
        if command -v swiftlint &> /dev/null; then
            SWIFTLINT_OUTPUT=$(swiftlint lint --fix --path "$FILE_PATH" 2>&1)
            SWIFTLINT_OUTPUT+=$(swiftlint lint --path "$FILE_PATH" 2>&1)
            if [[ $? -ne 0 ]]; then
                ERRORS+="swiftlint: $SWIFTLINT_OUTPUT"$'\n'
            fi
        fi
        ;;
esac

if [[ -n "$ERRORS" ]]; then
    echo "$ERRORS" >&2
fi

exit 0
