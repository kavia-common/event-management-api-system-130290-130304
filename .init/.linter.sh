#!/bin/bash
cd /home/kavia/workspace/code-generation/event-management-api-system-130290-130304/event_api_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

