# Docker Setup Guide for Ness Automation Project

This guide explains how to run the Playwright automation tests in a Docker container.

## Prerequisites

- Docker Desktop installed on Windows
- Docker version 29.2.0 or higher (confirmed in your screenshot)

## Project Files

### 1. Dockerfile
Main container definition with:
- Python 3.14 slim base image
- All Playwright system dependencies
- Chromium browser installation
- Project dependencies from requirements.txt

### 2. .dockerignore
Excludes unnecessary files from the image:
- Virtual environments
- Test artifacts
- IDE files
- Git files

### 3. docker-compose.yml
Simplified container orchestration with:
- Volume mounts for test results
- Environment variables
- Easy command customization

---

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Build and run tests
docker-compose up --build

# Run specific tests
docker-compose run --rm ness-automation pytest tests/test_login.py -v

# Run with markers
docker-compose run --rm ness-automation pytest tests/ -m smoke -v

# Clean up
docker-compose down
```

### Option 2: Using Docker Commands

```bash
# Build the image
docker build -t ness-automation .

# Run all tests
docker run --rm -v "%cd%/allure-results:/app/allure-results" ness-automation

# Run specific test file
docker run --rm ness-automation pytest tests/test_login.py -v

# Run with markers
docker run --rm ness-automation pytest tests/ -m smoke -v

# Interactive mode (for debugging)
docker run -it --rm ness-automation /bin/bash
```

---

## Volume Mounts Explained

The setup mounts these directories to your host machine:

```
Host (Windows)           →  Container
./allure-results         →  /app/allure-results
./allure-report          →  /app/allure-report
./logs                   →  /app/logs
./screenshots            →  /app/screenshots
```

This means test results, reports, logs, and screenshots are automatically saved to your project folder.

---

## Common Commands

### Build the Image
```bash
docker build -t ness-automation .
```

### Run All Tests
```bash
docker-compose up
```

### Run Specific Test Suite
```bash
# Login tests only
docker-compose run --rm ness-automation pytest tests/test_login.py -v

# Shopping tests
docker-compose run --rm ness-automation pytest tests/test_shopping.py -v

# E2E tests
docker-compose run --rm ness-automation pytest tests/test_login_and_shop.py -v
```

### Run by Marker
```bash
# Smoke tests
docker-compose run --rm ness-automation pytest tests/ -m smoke -v

# Regression tests
docker-compose run --rm ness-automation pytest tests/ -m regression -v

# E2E tests
docker-compose run --rm ness-automation pytest tests/ -m e2e -v
```

### Run with Parallel Execution
```bash
# Run with 2 workers
docker-compose run --rm ness-automation pytest tests/ -n 2 -v

# Run with 3 workers
docker-compose run --rm ness-automation pytest tests/ -n 3 -v
```

### Generate Allure Report
```bash
# Generate report from results
docker-compose run --rm ness-automation allure generate allure-results --clean -o allure-report

# Or use PowerShell on your host machine
allure generate allure-results --clean -o allure-report
allure open allure-report
```

### Interactive Shell (Debugging)
```bash
docker-compose run --rm ness-automation /bin/bash
```

---

## Troubleshooting

### Issue: Permission denied on mounted volumes
**Solution (Windows):** Make sure Docker Desktop has access to your drive:
1. Docker Desktop → Settings → Resources → File Sharing
2. Add your project directory

### Issue: Tests fail with "Browser not found"
**Solution:** Rebuild the image to ensure browsers are installed:
```bash
docker-compose build --no-cache
```

### Issue: Slow test execution
**Solution:** 
- Reduce parallel workers if running with `-n` flag
- Check Docker Desktop resource allocation (Settings → Resources)
- Increase CPU and memory if needed

### Issue: Container exits immediately
**Solution:** Check logs:
```bash
docker-compose logs
```

---

## Best Practices

1. **Always rebuild after dependency changes:**
   ```bash
   docker-compose up --build
   ```

2. **Clean up old containers:**
   ```bash
   docker-compose down
   docker system prune -f
   ```

3. **Use `--rm` flag for one-off runs:**
   ```bash
   docker-compose run --rm ness-automation pytest tests/ -v
   ```

4. **Mount only necessary volumes** to improve performance

5. **Use `.dockerignore`** to keep images small

---

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Playwright Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t ness-automation .
      
      - name: Run tests
        run: docker run --rm -v $PWD/allure-results:/app/allure-results ness-automation
      
      - name: Generate Allure report
        if: always()
        run: |
          docker run --rm -v $PWD/allure-results:/app/allure-results \
                          -v $PWD/allure-report:/app/allure-report \
                          ness-automation \
                          allure generate allure-results --clean -o allure-report
      
      - name: Upload Allure report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: allure-report
          path: allure-report
```

---

## Environment Variables

You can customize behavior with environment variables in `docker-compose.yml`:

```yaml
environment:
  - BASE_URL=https://automationexercise.com
  - BROWSER=chromium
  - HEADLESS=true
  - PYTEST_TIMEOUT=300
```

---

## Image Size Optimization

The current image uses `python:3.14-slim` to keep size small. To further optimize:

```dockerfile
# Multi-stage build example
FROM python:3.14-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.14-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
# ... rest of Dockerfile
```

---

## Comparison: Docker vs Local Execution

| Aspect | Docker | Local |
|--------|--------|-------|
| Setup | One-time build | Virtual env setup |
| Consistency | ✅ Same everywhere | ⚠️ OS-dependent |
| Browser install | ✅ Automated | Manual |
| CI/CD | ✅ Ready | Needs setup |
| Performance | Slight overhead | Faster |
| Isolation | ✅ Complete | Shared environment |

---

## Next Steps

1. Copy the 3 Docker files to your project root:
   - `Dockerfile`
   - `.dockerignore`
   - `docker-compose.yml`

2. Build the image:
   ```bash
   docker-compose build
   ```

3. Run your first test:
   ```bash
   docker-compose up
   ```

4. View results in the mounted directories on your host machine

---

For questions or issues, check the main README.md or open an issue on GitHub.
