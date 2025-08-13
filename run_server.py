import os
import uvicorn

def main():
  # Read PORT from env (Railway sets this). Default to 8000 for local dev.
  port_str = os.getenv("PORT", "8000")
  try:
    port = int(port_str)
  except ValueError:
    # Fallback to default if non-integer provided
    port = 8000

  uvicorn.run(
    "monkey_coder.app.main:app",
    host="0.0.0.0",
    port=port,
    log_level="info",
    reload=False
  )

if __name__ == "__main__":
  main()
