FROM python:3.11-alpine

WORKDIR /alma

RUN apk add --no-cache sqlite

COPY pyproject.toml .
COPY meta/schema.sql .
COPY src/ ./src/

RUN pip install --no-cache-dir -e .
RUN mkdir -p db

# Entry point directo
CMD ["python", "-c", "from alma.alma import main; main()"]