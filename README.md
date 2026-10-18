# Payment service test 

## Running the service

1. Create an .env file `cp .env.example .env`, adjust variables if needed
2. Build the images `make build`
3. Run `make up` (Migrations should apply automatically)

## Development

- `uv run pytest` for tests 
- `uv run format .` && `uv run check .` for format and lint
- `make revision message='new message'` for new revision 

