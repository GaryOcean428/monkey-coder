# Contributing

## Local quality checks

- Install deps: `yarn install`
- Typecheck all: `yarn typecheck`
- Lint all: `yarn lint`
- Tests with coverage: `yarn test:coverage`

## Docs build and link checks

- Build docs: `yarn workspace docs run build`
- Serve locally: `yarn workspace docs run serve --no-open --port 4000`
- Validate links: `npx -y linkinator http://localhost:4000/monkey-coder/ --recurse --format csv`

## CI artifacts

- Node JUnit: `node-junit` artifact (packages/*/coverage/junit/*.xml)
- Node coverage: `node-coverage` artifact
- Python JUnit: `python-junit` artifact (pytest-results.xml)
- Quantum metrics: `python-quantum-metrics` artifact (artifacts/quantum/metrics.json)
