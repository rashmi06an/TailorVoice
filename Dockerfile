# Single-image deploy for lite mode (template rewriter + lighter models).
# PLACEHOLDER — finalised in Phase 10. Claude Code never builds, pushes, or deploys this;
# you run it by hand (spec rule 10, Section 18.8).

FROM python:3.11-slim

WORKDIR /app

# System deps kept minimal; ffmpeg only added in Phase 6 if ASR is enabled in the image.
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY configs ./configs

# API module wired up in Phase 8.
# EXPOSE 8000
# CMD ["uvicorn", "tailorvoice.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

CMD ["python", "-c", "import tailorvoice; print('TailorVoice', tailorvoice.__version__, '- image placeholder, finalised in Phase 10')"]
